"""Extract one atlas sprite whose rectangular cell touches a neighboring weapon.

This is region selection for sprite packing: two original rectangles preserve
the full idle sprite and its boot antialiasing. No repainting or alpha threshold.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    directory = ROOT / 'assets/characters/warrior_v002'
    source = directory / 'sheet-front_right-draft.png'
    image = Image.open(source).convert('RGBA')
    if image.size != (1254, 1254):
        raise ValueError('Source layout changed; review atlas region ownership')
    result = Image.new('RGBA', (313, 324))
    # The idle boot ends near local x201..214,y315. The next row's hammer
    # begins near x112..117,y315. Separate atlas regions without cutting boot.
    regions = [((627, 0, 940, 315), (0, 0)), ((807, 315, 887, 324), (180, 315))]
    for rect, position in regions:
        result.paste(image.crop(rect), position)
    output = directory / 'front_right-idle02-extracted.png'
    result.save(output)
    report = {'source': str(source.relative_to(ROOT)),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'output': str(output.relative_to(ROOT)),
              'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'regions': [{'rectangle': rect, 'position': pos} for rect, pos in regions],
              'operation': 'Lossless selection of two rectangles belonging to idle_02, excluding neighboring rejected attack hammer tip.',
              'alpha_threshold_applied': False, 'art_repainted': False,
              'review': 'Source significant boot pixels at row315 x201..214 retained; neighboring hammer pixels x112..117 are outside selected sprite region.'}
    (ROOT / 'reports/warrior-v002-source-regions.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
