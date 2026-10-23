"""Assemble recorded evidence; no generated quality score or automatic approval."""
from pathlib import Path
import hashlib
import json
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]


def font(size):
    for name in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf']:
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default()


def main():
    dest=ROOT/'previews';dest.mkdir(exist_ok=True)
    src=Image.open(ROOT/'assets/references/warrior-concept-v002.png').convert('RGB')
    # Static concept contains opaque paper. These crops are review references,
    # never mislabeled as game-ready RGBA exports.
    crops=[src.crop((100,0,740,610)),src.crop((840,0,1280,610))]
    board=Image.new('RGB',(1160,820),'#f8f5ee');d=ImageDraw.Draw(board)
    d.text((26,18),'STATIC ART CANDIDATE v002 / NOT APPROVED',font=font(24),fill='#263643')
    d.text((26,54),'Same concept at 96px, 256px and enlarged detail. Opaque reference crops.',font=font(15),fill='#4c5d68')
    for col,crop in enumerate(crops):
        x=30+col*580
        d.text((x,92),['FRONT LEFT','FRONT RIGHT'][col],font=font(19),fill='#263643')
        for k,size in enumerate([96,256]):
            im=crop.copy();im.thumbnail((size,size),Image.Resampling.LANCZOS)
            px=x+[0,145][k];board.paste(im,(px,390-im.height))
            d.text((px,400),f'{size}px canvas',font=font(14),fill='#4c5d68')
    detail=src.crop((350,10,690,335));detail.thumbnail((330,330),Image.Resampling.LANCZOS);board.paste(detail,(30,450))
    weapons=src.crop((345,630,1020,970));weapons.thumbnail((690,320),Image.Resampling.LANCZOS);board.paste(weapons,(435,450))
    d.text((30,790),'Open issues: 3.5-head proportion, asymmetric armor continuity, hand/weapon separation.',font=font(16),fill='#a43b35')
    board.save(dest/'static-review.png')
    compare=Image.new('RGB',(1200,1110),'#18242e');d=ImageDraw.Draw(compare)
    d.text((24,16),'ROUTE COMPARISON / evidence before production',font=font(26),fill='white')
    d.text((24,55),'A: joint redraw (4 keys) | B/C: same parts (13 samples). Different scope; no winner by score.',font=font(15),fill='#b6c6d3')
    rows=[('A: visual FAIL - direction / grip side changes','previews/route_a/contact-sheet.png'),
          ('B: authored 2D - seams / hand overlap need redraw','previews/parts_experiment/B_hammer_a-contact.png'),
          ('C: 3D projection - fixed art cannot supply foreshortening','previews/parts_experiment/C_hammer_a-contact.png')]
    for i,(label,path) in enumerate(rows):
        y=100+i*330
        d.text((24,y),label,font=font(20),fill='#e9c48b')
        im=Image.open(ROOT/path).convert('RGB');im.thumbnail((1140,285),Image.Resampling.LANCZOS)
        compare.paste(im,(24,y+34))
    compare.save(dest/'route-comparison.png')
    records={}
    for p in sorted((ROOT/'assets').rglob('*')):
        if p.is_file():records[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    (ROOT/'reports/asset-provenance.json').write_text(json.dumps({'schema_version':1,'files':records,'generation_records':'reports/generation-*.json','art_approval':'pending','model_and_seed':'not exposed by image_gen; exact regeneration not guaranteed'},indent=2),encoding='utf-8')
    print('Saved static-review.png, route-comparison.png and asset-provenance.json; art approval remains pending.')


if __name__=='__main__':main()
