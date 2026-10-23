"""Publish byte-identical review copies and a portable game export archive."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
from PIL import Image, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT.parent / 'previews/ai-game-art-factory/warrior-v002'


def main():
    GALLERY.mkdir(parents=True, exist_ok=True)
    copies = []

    def copy(source, relative):
        destination = GALLERY / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == hashlib.sha256(destination.read_bytes()).hexdigest()
        record = {'source': str(source.relative_to(ROOT)), 'file': str(relative),
                  'bytes': destination.stat().st_size, 'sha256': digest}
        if source.suffix.lower() in {'.png', '.webp', '.apng', '.gif'}:
            with Image.open(source) as image:
                record.update(size=list(image.size), mode=image.mode)
                count = 0
                for frame in ImageSequence.Iterator(image):
                    frame.load()
                    count += 1
                record['decoded_frames'] = count
        copies.append(record)

    copy(ROOT / 'assets/characters/warrior_v002/design-original.png', Path('art/design-original.png'))
    for direction in ['front_left', 'front_right']:
        copy(ROOT / f'assets/characters/warrior_v002/design-{direction}.png', Path(f'art/design-{direction}.png'))
        # The packed atlas contains the reviewed source selection. A retained
        # generator draft can have rejected cells and must not be shown as final.
        copy(ROOT / f'exports/warrior_v002/{direction}/atlas.png', Path(f'art/sheet-{direction}.png'))
        for source in sorted((ROOT / f'exports/warrior_v002/{direction}').rglob('*')):
            if source.is_file():
                copy(source, Path('sprites') / direction / source.relative_to(ROOT / f'exports/warrior_v002/{direction}'))
        copy(ROOT / f'previews/warrior_motion/guide-{direction}.png', Path(f'motion-guides/guide-{direction}.png'))
        for action in ['idle', 'attack', 'defense']:
            copy(ROOT / f'previews/warrior_motion/{direction}-{action}.webp', Path(f'motion-guides/{direction}-{action}.webp'))
    for source in sorted((ROOT / 'assets/weapons/warrior_v002').glob('*.png')):
        copy(source, Path('weapons') / source.name)
    capture = ROOT / 'exports/warrior_v002/godot-actual-size.png'
    if capture.exists():
        copy(capture, Path('godot-actual-size.png'))
    for name in ['actions-comparison.gif', 'actions-comparison.png', 'comparison-gif.json']:
        copy(ROOT / 'exports/warrior_v002' / name, Path(name))
    (GALLERY / 'manifest.json').write_text(json.dumps({'copies': copies, 'original_pixels_preserved': True}, indent=2)+'\n')
    archive = GALLERY / 'warrior-v002-game-assets.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for directory in ['exports/warrior_v002', 'workflows/godot-warrior']:
            for source in sorted((ROOT / directory).rglob('*')):
                if source.is_file() and '.godot' not in source.parts:
                    output.write(source, source.relative_to(ROOT))
        for source in [ROOT / 'profiles/warrior_v002.yaml', ROOT / 'docs/持锤战士第二版.md']:
            output.write(source, source.relative_to(ROOT))
    with zipfile.ZipFile(archive) as check:
        assert check.testzip() is None
    print(json.dumps({'gallery': str(GALLERY), 'copied_files': len(copies),
                      'archive_bytes': archive.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
