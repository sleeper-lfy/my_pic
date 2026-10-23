"""Validate and make review contact sheets from the executed Blender probe."""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]


def distance(a, b):
    return math.dist(a,b)


def main():
    source=ROOT/'reports/structure/projection.json'
    data=json.loads(source.read_text(encoding='utf-8'))
    records=data['records']
    failures=[]; files_checked=0; bounds=[]
    for r in records:
        for channel,path in r['files'].items():
            p=ROOT/path
            if not p.exists():failures.append('missing '+path);continue
            im=Image.open(p)
            files_checked+=1
            if im.mode!='RGBA' or im.size!=(256,256):failures.append('format '+path)
            bbox=im.getchannel('A').getbbox()
            if not bbox:failures.append('blank '+path);continue
            if bbox[0]<=0 or bbox[1]<=0 or bbox[2]>=256 or bbox[3]>=256:failures.append('clipped '+path)
            if channel=='flat': bounds.append({'direction':r['direction'],'weapon':r['weapon'],'pose':r['pose'],'bbox':list(bbox)})
        error=distance(r['measured_grip_world'],r['measured_hand_world'])
        if error>1e-5:failures.append('grip transform '+str(r['index']))
        for side in ['Left','Right']:
            joints=r['joints']
            upper=distance(joints[side+'Shoulder']['world'],joints[side+'Elbow']['world'])
            fore=distance(joints[side+'Elbow']['world'],joints[side+'HandAnchor']['world'])
            if abs(upper-.43)>2e-6 or abs(fore-.40)>2e-6:failures.append('bone length '+str(r['index'])+side)
    foot_drift={}
    for direction in ['front_left','front_right']:
        subset=[r for r in records if r['direction']==direction]
        reference=subset[0]['joints']['FootAnchor']['xy']
        drift=max(distance(r['joints']['FootAnchor']['xy'],reference) for r in subset)
        foot_drift[direction]=drift
        if drift>1e-5:failures.append('foot anchor drift '+direction)
    report={'status':'passed' if not failures else 'failed','scope':'structure guide transforms and files, not art acceptance',
        'records_checked':len(records),'png_files_checked':files_checked,
        'max_measured_grip_error_world':max(r['weapon_grip_error_world'] for r in records),
        'foot_anchor_drift_pixels':foot_drift,'failures':failures,'frame_bounds':bounds,
        'visual_review':'not_human_approved','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    (ROOT/'reports/structure/qa.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
    except OSError:font=ImageFont.load_default()
    sheet=Image.new('RGB',(1080,1240),'#101a23');d=ImageDraw.Draw(sheet)
    d.text((20,15),'STRUCTURE ONLY / 4 diagnostic key poses / NOT final game art',font=font,fill='#ffffff')
    d.text((20,40),'Orthographic 45-degree views. Two weapon proxies. No AI redraw.',font=font,fill='#99b6ca')
    for row,(direction,weapon) in enumerate((a,b) for a in ['front_left','front_right'] for b in ['hammer_block','hammer_crescent']):
        y=80+row*286
        d.text((20,y),direction+' / '+weapon,font=font,fill='#9bc4dd')
        for r in [x for x in records if x['direction']==direction and x['weapon']==weapon]:
            x=20+r['index']*264
            im=Image.open(ROOT/r['files']['flat'])
            tile=Image.new('RGBA',im.size,'#243744');tile.alpha_composite(im)
            sheet.paste(tile.convert('RGB'),(x,y+24))
            d.text((x+8,y+28),r['pose'],font=font,fill='#f1e2c9')
    sheet.save(ROOT/'previews/structure/contact-sheet.png')
    guide=Image.new('RGB',(1360,650),'#101a23');d=ImageDraw.Draw(guide)
    d.text((20,15),'STRUCTURE GUIDE CHANNELS / data only / no art-quality claim',font=font,fill='white')
    for row,index in enumerate([0,2]):
        r=next(x for x in records if x['direction']=='front_left' and x['weapon']=='hammer_block' and x['index']==index)
        for col,ch in enumerate(['flat','pose','normal','depth','silhouette']):
            x=20+col*268;y=60+row*290
            d.text((x,y),r['pose']+' / '+ch,font=font,fill='#a9c8de')
            im=Image.open(ROOT/r['files'][ch]);bg=Image.new('RGBA',im.size,'#263440');bg.alpha_composite(im);guide.paste(bg.convert('RGB'),(x,y+24))
    guide.save(ROOT/'previews/structure/guide-channels.png')
    print(json.dumps({k:v for k,v in report.items() if k!='frame_bounds'},indent=2))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
