"""Pack native human motion guides; never repaint or alter generated 2D art."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'previews/warrior_motion';REPORT=ROOT/'reports/warrior_motion'

def main():
    poses=json.loads((REPORT/'poses.json').read_text());results=[]
    for direction in ['front_left','front_right']:
        sheet=Image.new('RGBA',(2048,2048))
        frames=[]
        for i in range(16):
            p=OUT/direction/f'pose_{i:02}.png'
            with Image.open(p) as raw:
                raw.load();im=raw.convert('RGBA')
                if im.size!=(512,512):raise ValueError('Wrong dimensions '+str(p))
            bbox=im.getchannel('A').getbbox()
            if not bbox:raise ValueError('Empty guide '+str(p))
            margin=min(bbox[0],bbox[1],512-bbox[2],512-bbox[3])
            if margin<16:raise ValueError('Unsafe clipping '+str(p)+' '+str(bbox))
            sheet.alpha_composite(im,((i%4)*512,(i//4)*512));frames.append(im)
            results.append({'file':str(p.relative_to(ROOT)),'size':list(im.size),'mode':'RGBA','alpha_bbox':bbox,'margin':margin,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        sheet.save(OUT/f'guide-{direction}.png')
        offset=0
        for action,clip in poses['clips'].items():
            count=len(clip['durations']);images=frames[offset:offset+count]
            images[0].save(OUT/f'{direction}-{action}.webp',save_all=True,append_images=images[1:],duration=clip['durations'],loop=0 if clip['loop'] else 1,lossless=True)
            offset+=count
    summary={'status':'technical_pass','decoded_frames':len(results),'cell_size':[512,512],'sheets':[2048,2048],'max_bone_length_error_m':poses['max_bone_length_error_m'],'sample_count':poses['sample_count'],'frames':results,'human_art_acceptance':'pending','scope':'3D anatomical guide, original authored combat; finished painted output checked separately','limitations':['Guide hands are posed using native finger bones; palm wrap still requires visual correction in 2D art.','CharacterRoot is ground origin, not a per-frame cropped image anchor.','Public BVH walking data is not retargeted or represented as combat motion.']}
    (REPORT/'review.json').write_text(json.dumps(summary,indent=2));print('WARRIOR_MOTION_REVIEW',len(results))
if __name__=='__main__':main()
