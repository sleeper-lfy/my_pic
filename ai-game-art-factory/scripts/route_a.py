"""Package the recorded joint-generation experiment, retaining source failures."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw
from quality import check_frames

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'assets/characters/route_a/joint-keyposes-v001.png'
# Explicit authored cell boundaries for this generated sheet, not arbitrary future sheets.
CELLS = [(0,0,535,725), (535,0,1030,725), (1030,0,1720,725), (1720,0,2169,725)]
DURATIONS = [260, 220, 180, 340]  # Diagnostic holds, not production attack timing.


def main():
    src = Image.open(SOURCE).convert('RGBA')
    if src.size != (2169, 725):
        raise ValueError('Recorded sheet changed; re-author cell boundaries before packaging')
    out = ROOT/'exports/route_a'; out.mkdir(parents=True, exist_ok=True)
    preview = ROOT/'previews/route_a'; preview.mkdir(parents=True, exist_ok=True)
    crops = [src.crop(cell) for cell in CELLS]
    bounds = [im.getchannel('A').getbbox() for im in crops]
    if not all(bounds):
        raise ValueError('Missing diagnostic pose')
    # A common scale preserves relative size. Bottom alignment is disclosed; it is
    # only presentation registration and is never evidence of raw foot stability.
    scale = min(224/max(b[2]-b[0] for b in bounds), 216/max(b[3]-b[1] for b in bounds))
    frames, metadata, paths = [], [], []
    for i, (crop, bbox) in enumerate(zip(crops, bounds)):
        tight = crop.crop(bbox)
        patch = tight.resize((round(tight.width*scale), round(tight.height*scale)), Image.Resampling.LANCZOS)
        frame = Image.new('RGBA', (256,256))
        offset = ((256-patch.width)//2, 232-patch.height)
        frame.alpha_composite(patch, offset)
        path = out/f'key_{i:02}.png'; frame.save(path); paths.append(path); frames.append(frame)
        metadata.append({'index':i, 'duration_ms':DURATIONS[i], 'source_cell':CELLS[i],
                         'raw_bbox':bbox, 'presentation_offset':offset,
                         'source_edge_touch':bbox[0]==0 or bbox[1]==0 or bbox[2]>=crop.width or bbox[3]>=crop.height})
    sheet = Image.new('RGBA', (1024,256))
    for i, frame in enumerate(frames): sheet.alpha_composite(frame,(256*i,0))
    sheet.save(out/'sheet.png')
    # APNG retains alpha and exact diagnostic durations.
    frames[0].save(preview/'diagnostic-keyposes.apng', save_all=True, append_images=frames[1:], duration=DURATIONS, loop=0, disposal=0, blend=0)
    contact = Image.new('RGB',(1056,380),'#17212c'); d=ImageDraw.Draw(contact)
    d.text((16,12),'A / joint image-conditioned redraw / FOUR DIAGNOSTIC KEYS ONLY',fill='white')
    for i,frame in enumerate(frames):
        contact.paste(frame,(16+i*256,42),frame)
        d.text((24+i*256,308),['ready','anticipation','strike: direction flips','recovery: source clipped'][i],fill='#f2c67a')
    d.text((16,346),'VISUAL FAIL: orientation / grip side inconsistency. Not an accepted animation.',fill='#ff9d90')
    contact.save(preview/'contact-sheet.png')
    qa=check_frames(paths,DURATIONS)
    qa['source_failures']=[f'key_{i}:source_edge_clipping_risk' for i,m in enumerate(metadata) if m['source_edge_touch']]
    qa['raw_bottom_range_px']=max(b[3] for b in bounds)-min(b[3] for b in bounds)
    qa['registration']='Common resize scale; each alpha bbox centered and bottom registered for presentation only. Not anatomical foot tracking.'
    qa['visual_review']={'status':'failed_preliminary_ai_review','issues':['strike changes face direction and grip side','armor/hem silhouette varies','last source pose touches right canvas edge'],'human':'pending'}
    qa['overall_status']='rejected_experiment'
    (ROOT/'reports/route-a-qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
    manifest={'schema_version':1,'route':'A','status':'diagnostic_unapproved','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'scale':scale,'frame_size':[256,256],'sheet_size':[1024,256],'frames':metadata,
              'generation':'reports/generation-route-a.json','not_a_continuous_animation':True}
    (out/'metadata.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'packaging':'completed','visual_acceptance':'failed','source_failures':qa['source_failures']}))


if __name__=='__main__': main()
