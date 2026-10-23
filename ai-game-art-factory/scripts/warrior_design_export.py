"""Extract retained original art cells without repainting or replacing pixels."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'assets/characters/warrior_v002/design-original.png'
    image = Image.open(source).convert('RGBA')
    if image.size != (1254, 1254):
        raise ValueError('Reviewed source layout changed; review extraction rectangles first')
    regions = {
        'assets/characters/warrior_v002/design-front_left.png': (0, 0, 627, 660),
        'assets/characters/warrior_v002/design-front_right.png': (627, 0, 1254, 660),
        'assets/weapons/warrior_v002/hammer_block.png': (0, 660, 627, 1254),
        'assets/weapons/warrior_v002/hammer_crescent.png': (627, 660, 1254, 1254),
    }
    records = []
    for name, rect in regions.items():
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        crop = image.crop(rect)
        crop.save(target)
        records.append({'path': name, 'source_rectangle': rect, 'size': crop.size,
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                        'alpha_bbox': crop.getchannel('A').getbbox()})
    report = {'source': str(source.relative_to(ROOT)),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'operation': 'Unmodified rectangular crops. No repainting, alpha removal or per-asset rescaling.',
              'limitations': ['Character views include the held hammer; these are not separable character/weapon animation layers.',
                             'Crescent hammer is a detached static design; animated reuse is pending.',
                             'Concept proportion remains taller than the target 3.5 heads.'],
              'files': records}
    (ROOT / 'reports/warrior-v002-design-extraction.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Extracted original character views and two detached hammer designs')


if __name__ == '__main__':
    main()
