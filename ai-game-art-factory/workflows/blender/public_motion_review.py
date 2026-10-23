"""Package actual native motion outputs and plot the imported public BVH joints."""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'previews/public_motion'
REPORT=ROOT/'reports/public_motion'


def font(size):
    try:return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    except OSError:return ImageFont.load_default()


def native_skin():
    report=json.loads((REPORT/'riggedfigure.json').read_text())
    frames=[Image.open(ROOT/f['file']).convert('RGBA') for f in report['frames']]
    assert len(frames)==24 and all(im.size==(512,512) and im.getchannel('A').getbbox() for im in frames)
    times=[round(f['seconds']*1000) for f in report['frames']]
    durations=[b-a for a,b in zip(times,times[1:])]+[80]
    frames[0].save(OUT/'riggedfigure-native.webp',save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True)
    board=Image.new('RGB',(1120,430),'#17232e');d=ImageDraw.Draw(board)
    d.text((20,12),'NATIVE SKIN TRANSFER TEST ONLY - BOX SAMPLE, NOT ANATOMY REFERENCE',font=font(18),fill='#f3cb8b')
    d.text((20,43),'Cesium 2017 / CC BY 4.0 / official mesh, weights and clip; diagnostic material and camera added',font=font(12),fill='#bdd0dc')
    for x,index in enumerate([0,7,15,23]):
        im=frames[index].resize((256,256),Image.Resampling.LANCZOS)
        bg=Image.new('RGBA',(256,256),'#eef2f4');bg.alpha_composite(im);board.paste(bg.convert('RGB'),(20+x*275,88))
        d.text((20+x*275,354),f'sample {index} / {times[index]} ms',font=font(14),fill='white')
    d.text((20,394),'Excluded from humanoid art baseline: cube head, very low mesh detail, no fingers.',font=font(15),fill='#f1b2ab')
    board.save(OUT/'riggedfigure-transfer-only-contact.png')
    return {'frames':24,'native_source_duration_ms':1250,'preview_final_hold_ms':80,'preview_file':'previews/public_motion/riggedfigure-native.webp'}


def skeleton_viewer():
    data=json.loads((REPORT/'walk1-native-skeleton.json').read_text())
    records=data['records']
    # Display only locomotion chains for legibility; all 75 imported bones remain
    # recorded in JSON. This is an actual BVH projection, not a guessed stick rig.
    names=[n for n in records[0]['bones'] if not any(s in n.lower() for s in ['tongue','jaw','eye','finger','thumb','index','middle','ring','pinky'])]
    points=[b[key] for r in records for n,b in r['bones'].items() if n in names for key in ['head','tail']]
    zlo=min(v[2] for v in points);zhi=max(v[2] for v in points)
    scale=370/(zhi-zlo)
    view_angles=[0,math.pi/4]
    ranges=[]
    for angle in view_angles:
        xs=[math.cos(angle)*p[0]+math.sin(angle)*p[1] for p in points]
        ranges.append((min(xs)+max(xs))/2)
    frames=[]
    for r in records:
        image=Image.new('RGB',(860,510),'#17232e');d=ImageDraw.Draw(image)
        d.text((18,12),'MakeHuman official walk1.bvh - native skeleton; NO RETARGETING',font=font(19),fill='white')
        d.text((18,42),f'CC0 bundled asset | frame {r["frame"]:02}/14 | 75 source bones | locomotion chains shown',font=font(13),fill='#bad0df')
        for col,(angle,center) in enumerate(zip(view_angles,ranges)):
            def project(p):return (215+col*430+(math.cos(angle)*p[0]+math.sin(angle)*p[1]-center)*scale,465-(p[2]-zlo)*scale)
            d.text((col*430+20,77),['FRONT PROJECTION','45 DEGREE PROJECTION'][col],font=font(15),fill='#d4dce1')
            d.line((col*430+20,467,col*430+410,467),fill='#4f606c',width=1)
            for name,b in r['bones'].items():
                if name not in names:continue
                a,c=project(b['head']),project(b['tail'])
                color='#e9b374' if '_R' in name or '.R' in name else '#7bbdd7' if '_L' in name or '.L' in name else '#d1dce4'
                d.line((*a,*c),fill=color,width=4)
                for x,y in [a,c]:d.ellipse((x-3,y-3,x+3,y+3),fill=color)
        frames.append(image)
    durations=[round((i+1)*41.667)-round(i*41.667) for i in range(14)]
    frames[0].save(OUT/'walk1-native-skeleton.webp',save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True)
    board=Image.new('RGB',(1720,1050),'#17232e');d=ImageDraw.Draw(board)
    for i,index in enumerate([0,4,9,13]):board.paste(frames[index],((i%2)*860,(i//2)*510))
    d.text((18,1025),'Walking reference only. No attack, no skin retargeting, no final game-art approval.',font=font(17),fill='#f2be92')
    board.save(OUT/'walk1-native-skeleton-contact.png')
    lengths={n:[math.dist(r['bones'][n]['head'],r['bones'][n]['tail']) for r in records] for n in records[0]['bones']}
    return {'source_frames':14,'source_bones':75,'displayed_locomotion_bones':len(names),'max_native_bone_length_variation':max(max(v)-min(v) for v in lengths.values()),'finite_pose_coordinates':all(math.isfinite(v) for p in points for v in p),'retargeted_to_default_rig':False,'preview_duration_ms':sum(durations),'preview_file':'previews/public_motion/walk1-native-skeleton.webp'}


def main():
    skin=native_skin();walk=skeleton_viewer()
    files=[]
    for p in OUT.rglob('*'):
        if p.is_file() and p.suffix.lower() in ['.png','.webp']:
            with Image.open(p) as im:
                count=getattr(im,'n_frames',1)
                for i in range(count):im.seek(i);im.load()
                files.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'dimensions':list(im.size),'frames':count,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    report={'status':'native_data_verified_not_art_approved','riggedfigure':skin,'walk1':walk,'files':files,'visual_review':'RiggedFigure is a box-head low-poly test mesh; excluded as anatomy art reference. Walk1 is an actual imported old-rig BVH skeleton, no retargeting.'}
    (REPORT/'review.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'skin_samples':24,'walk_frames':14,'decoded_files':len(files),'retargeted':False}))


if __name__=='__main__':main()
