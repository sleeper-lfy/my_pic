#!/usr/bin/env python3
"""Small, unapproved 2D-part experiment; never a production character generator."""
from __future__ import annotations
import argparse, hashlib, io, json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['head','torso','pelvis','cape','left_upper_arm','right_upper_arm',
         'left_forearm','right_forearm','left_hand','right_hand','left_thigh',
         'right_thigh','left_shin_boot','right_shin_boot','hammer_a','hammer_b']
SIZE = 256
DURATIONS = [37,38,37,38,40,40,40,40,72,73,72,73,100]  # keys at 0, .15, .31, .60 sec; final hold

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_parts(atlas, extract=False):
    image = Image.open(atlas).convert('RGBA')
    if image.getchannel('A').getextrema()[0] == 255:
        raise ValueError('Parts atlas has no transparent background; use an authored transparent atlas.')
    parts={}; layout={'schema_version':1,'status':'experimental_unapproved','atlas':str(atlas.relative_to(ROOT)),
                     'sha256':digest(atlas),'canvas':list(image.size),'parts':{}}
    for i,name in enumerate(NAMES):
        x,y=i%4,i//4; w,h=image.size
        # Reviewed source layout: generator did not obey equal-height grid.
        rows=[0,326,620,872,1254]; cols=[0,314,644,954,1254] if y==0 else [0,314,627,941,1254]
        box=(round(cols[x]*w/1254),round(rows[y]*h/1254),round(cols[x+1]*w/1254),round(rows[y+1]*h/1254))
        tile=image.crop(box); bbox=tile.getchannel('A').getbbox()
        if bbox is None: raise ValueError('Empty atlas part '+name)
        tile=tile.crop(bbox)
        parts[name]=tile
        layout['parts'][name]={'cell':list(box),'alpha_crop':list(bbox),'size':list(tile.size)}
    (ROOT/'templates/rig').mkdir(parents=True,exist_ok=True)
    layout_path=ROOT/'templates/rig/parts-layout.json';layout_bytes=json.dumps(layout,indent=2).encode()
    if not layout_path.exists() or layout_path.read_bytes()!=layout_bytes:layout_path.write_bytes(layout_bytes)
    part_dir=ROOT/'exports/parts_experiment/parts';part_dir.mkdir(parents=True,exist_ok=True)
    for name,img in parts.items():
        encoded=io.BytesIO();img.save(encoded,format='PNG');part_path=part_dir/(name+'.png')
        if not part_path.exists() or part_path.read_bytes()!=encoded.getvalue():part_path.write_bytes(encoded.getvalue())
        if name.startswith('hammer_'):
            editable=ROOT/'assets/weapons'/(name+'.png');editable.parent.mkdir(parents=True,exist_ok=True)
            if extract or not editable.exists():img.save(editable)
            parts[name]=Image.open(editable).convert('RGBA')
    return parts,layout

def transform_part(img,pivot,target,angle=0,scale_x=1,scale_y=None):
    """Inverse affine, exact continuous pivot mapping; avoids rounded resize pivots."""
    if scale_y is None:scale_y=scale_x
    c,s=math.cos(angle),math.sin(angle)
    a,b=c/scale_x,s/scale_x
    d,e=-s/scale_y,c/scale_y
    px,py=pivot;tx,ty=target
    return img.transform((SIZE,SIZE),Image.Transform.AFFINE,(a,b,px-a*tx-b*ty,d,e,py-d*tx-e*ty),Image.Resampling.BICUBIC)

def along(img,start,end,width,start_y=.13,end_y=.87):
    start=np.array(start,float);end=np.array(end,float);delta=end-start
    length=float(np.linalg.norm(delta)); angle=math.atan2(delta[1],delta[0])-math.pi/2
    return transform_part(img,(img.width/2,img.height*start_y),start,angle,width/img.width,
                          max(length,1)/(img.height*(end_y-start_y)))

def over(dest,layer):dest.alpha_composite(layer)

def authored_keys():
    base={'CharacterRoot':[128,232],'FootAnchor':[128,232],
      'Neck':[128,100],'Head':[127,75],'Pelvis':[128,158],
      'RightShoulder':[148,105],'LeftShoulder':[108,108],
      'RightElbow':[168,127],'LeftElbow':[94,131],
      'RightHandAnchor':[172,150],'LeftHandAnchor':[102,151],
      'RightHip':[143,163],'LeftHip':[113,163],
      'RightKnee':[147,192],'LeftKnee':[109,192],
      'RightFoot':[151,224],'LeftFoot':[103,224],
      'WeaponHead':[181,106]}
    variants=[{}, {'RightElbow':[177,97],'RightHandAnchor':[159,71],'WeaponHead':[143,33],
                   'LeftHandAnchor':[111,140]},
                 {'RightShoulder':[144,108],'RightElbow':[127,129],'RightHandAnchor':[94,155],
                  'WeaponHead':[53,175],'Neck':[123,104],'Head':[122,79],'LeftHandAnchor':[119,151]},
                 {'RightElbow':[165,130],'RightHandAnchor':[164,151],'WeaponHead':[169,106]}]
    return [{**base,**v} for v in variants]

def projected_keys(path):
    data=json.loads(path.read_text())
    records=[r for r in data['records'] if r['direction']=='front_left' and r['weapon']=='hammer_block']
    records.sort(key=lambda r:r['index'])
    if len(records)!=4:raise ValueError('Expected four Blender projected front_left keys')
    result=[]
    # Constant translation only: retain genuine camera projection, never per-frame fit-to-box.
    anchor=np.array(records[0]['joints']['FootAnchor']['xy']);offset=np.array([128,232])-anchor
    for r in records:
        result.append({k:(np.array(v['xy'])+offset).tolist() for k,v in r['joints'].items()})
    return result

def interpolate(keys):
    result=[]
    for a,b in zip(keys,keys[1:]):
        for k in range(4):
            t=k/4
            result.append({name:((1-t)*np.array(a[name])+t*np.array(b[name])).tolist() for name in a})
    result.append(keys[-1])
    return result

def mapped_source_point(point,pivot,target,angle,sx,sy=None):
    # Independently invert the resampling inverse transform, then map the source annotation.
    sy = sx if sy is None else sy
    c,s=math.cos(angle),math.sin(angle)
    inverse=np.array([[c/sx,s/sx],[-s/sy,c/sy]],float)
    offset=np.array(pivot,float)-inverse@np.array(target,float)
    return np.linalg.solve(inverse,np.array(point,float)-offset)

def render(parts,joints,weapon):
    body=Image.new('RGBA',(SIZE,SIZE)); wlayer=body.copy(); handlayer=body.copy()
    neck=np.array(joints['Neck']);hip=np.array(joints['Pelvis'])
    over(body,along(parts['cape'],neck+[0,-2],hip+[3,28],77))
    # Far limbs first. A fixed conservative order is deliberate for this limited 45 degree trial.
    # Actual C per-frame occlusion still requires a reviewed mapping of 3D depth to painted parts.
    for side in ['Left','Right']:
        low=side.lower();foot=np.array(joints[side+'Foot']);knee=joints[side+'Knee'];thigh=joints[side+'Hip']
        over(body,along(parts[low+'_shin_boot'],knee,foot,38,.15,.78))
        over(body,along(parts[low+'_thigh'],thigh,knee,40))
    over(body,along(parts['pelvis'],hip+[0,-12],hip+[0,19],76))
    over(body,along(parts['left_upper_arm'],joints['LeftShoulder'],joints['LeftElbow'],39))
    over(body,along(parts['left_forearm'],joints['LeftElbow'],joints['LeftHandAnchor'],31))
    # Upper-arm pauldrons go behind the painted torso shoulder to reduce duplicate armor.
    over(body,along(parts['right_upper_arm'],joints['RightShoulder'],joints['RightElbow'],40))
    over(body,along(parts['torso'],neck,hip,77,.08,.88))
    # Head orientation is a fixed authored front-left view: rotation is not novel-view generation.
    head=parts['head']; head_width=65
    over(body,transform_part(head,(head.width*.5,head.height*.93),neck+[0,12],0,head_width/head.width))
    over(body,along(parts['right_forearm'],joints['RightElbow'],joints['RightHandAnchor'],32))
    free=parts['left_hand'];over(body,transform_part(free,(free.width*.5,free.height*.25),joints['LeftHandAnchor'],0,21/free.width))
    palm=np.array(joints['RightHandAnchor']);headpos=np.array(joints['WeaponHead']);axis=headpos-palm
    # Shared handle grip for both weapons. Art-specific pixel pivots are still review candidates.
    item=parts[weapon]; angle=math.atan2(axis[1],axis[0])+math.pi/2
    grip=(item.width*.5,item.height*.74)
    scale=float(np.linalg.norm(axis))/(item.height*(.74-.18))
    over(wlayer,transform_part(item,grip,palm,angle,scale))
    hand=parts['right_hand'];over(handlayer,transform_part(hand,(hand.width*.5,hand.height*.55),palm,angle,23/hand.width))
    composite=body.copy();over(composite,wlayer);over(composite,handlayer)
    measured_grip=mapped_source_point((item.width*.5,item.height*.74),grip,palm,angle,scale)
    measured_palm=mapped_source_point((hand.width*.5,hand.height*.55),(hand.width*.5,hand.height*.55),palm,angle,23/hand.width)
    return composite,body,wlayer,handlayer,{'weapon_socket_px':palm.tolist(),'weapon_grip_px':measured_grip.tolist(),
                                         'grip_error_px':float(np.linalg.norm(measured_grip-measured_palm)),'foot_anchor_px':joints['FootAnchor'],
                                         'grip_pivot_normalized':[.5,.74],'occlusion_status':'fixed_order_not_fully_verified'}

def checker(size=(256,256)):
    image=Image.new('RGBA',size,'#e1e5e8');d=ImageDraw.Draw(image)
    for y in range(0,size[1],16):
        for x in range(0,size[0],16):
            if (x//16+y//16)%2:d.rectangle((x,y,x+15,y+15),fill='#f3f4f4')
    return image

def run(atlas,projection,route_filter="all",weapon_filter="all",extract=False):
    parts,layout=load_parts(atlas,extract);out=ROOT/'exports/parts_experiment';preview=ROOT/'previews/parts_experiment'
    preview.mkdir(parents=True,exist_ok=True)
    report={'status':'experimental_unapproved','technical_checks':{},'visual_approval':'pending',
      'scope':'front_left attack only; four keys interpolated to thirteen samples; not final animation',
      'limitations':['Unapproved AI parts; local joint overlap and hands require visual redraw.',
                     'Fixed painted view cannot supply perspective changes or automatic anatomical occlusion.',
                     'Grip error measures affine pivot coincidence, not finger wrap quality.',
                     'C interpolates projected key points; it is not a fully sampled 3D animation.',
                     'Second view, idle and defense production remain gated by static art approval.',
                     'Visual inspection: collar/shoulder seams and proportions improved once through layout only; flat hand overlay and stiff elbow bends still fail art acceptance.'],
      'source_sha256':layout['sha256'],'projection_sha256':digest(projection),'clips':[]}
    for route in ['B','C']:
        if route_filter not in ['all',route]:continue
        keys=authored_keys() if route=='B' else projected_keys(projection)
        frames=interpolate(keys)
        for weapon in ['hammer_a','hammer_b']:
            if weapon_filter not in ['all',weapon]:continue
            clip=f'{route}_{weapon}';folder=out/clip;folder.mkdir(parents=True,exist_ok=True)
            rendered=[];metadata=[];issues=[];areas=[];layer_errors=[];foot_pixels=[]
            for i,joints in enumerate(frames):
                composite,body,wl,hl,meta=render(parts,joints,weapon)
                filename=f'attack_{i:03d}.png';composite.save(folder/filename)
                for suffix,im in [('body',body),('weapon',wl),('front_hand',hl)]:im.save(folder/f'attack_{i:03d}_{suffix}.png')
                rec=body.copy();rec.alpha_composite(wl);rec.alpha_composite(hl)
                layer_errors.append(int(np.abs(np.array(rec).astype(int)-np.array(composite).astype(int)).max()))
                lower=body.getchannel('A').crop((75,200,185,256)).getbbox();foot_pixels.append(lower[3]+200 if lower else None)
                alpha=composite.getchannel('A');bbox=alpha.getbbox();areas.append(int(np.count_nonzero(np.array(alpha)>0)))
                if not bbox:issues.append({'frame':i,'check':'blank','severity':'error'})
                elif min(bbox[0],bbox[1],256-bbox[2],256-bbox[3])<8:issues.append({'frame':i,'check':'edge_padding_under_8px','severity':'warning','bbox':bbox})
                if composite.mode!='RGBA':issues.append({'frame':i,'check':'alpha_channel_missing','severity':'error'})
                meta.update({'file':filename,'time_ms':sum(DURATIONS[:i]),'duration_ms':DURATIONS[i],'bbox':bbox,'joints':joints})
                metadata.append(meta);rendered.append(composite)
            sheet=Image.new('RGBA',(SIZE*len(rendered),SIZE))
            for i,im in enumerate(rendered):sheet.alpha_composite(im,(i*SIZE,0))
            sheet.save(folder/'sheet.png')
            data={'schema_version':1,'status':'experimental_unapproved','route':route,'direction':'front_left','action':'attack',
                  'weapon':weapon,'canvas':[256,256],'loop':False,'frames':metadata,
                  'sheet':{'file':'sheet.png','columns':len(rendered),'frame_width':256,'frame_height':256},
                  'body_cache_key':hashlib.sha256((layout['sha256']+route+(report['projection_sha256'] if route=='C' else '')).encode()).hexdigest()}
            (folder/'animation.json').write_text(json.dumps(data,indent=2))
            # Animated WebP preserves alpha and nonuniform timing when real timings are authored later.
            rendered[0].save(preview/(clip+'.webp'),save_all=True,append_images=rendered[1:],duration=DURATIONS,loop=0,lossless=True)
            contact=Image.new('RGB',(256*4,296),'#f1eee8');draw=ImageDraw.Draw(contact)
            for n,idx in enumerate([0,4,8,12]):
                bg=checker();bg.alpha_composite(rendered[idx]);contact.paste(bg.convert('RGB'),(256*n,32));draw.text((256*n+12,10),f'{clip} key {n} | UNAPPROVED',fill='#30343a')
            contact.save(preview/(clip+'-contact.png'))
            ratio=max(areas)/min(areas)
            if ratio>1.35:issues.append({'check':'alpha_area_variation','severity':'warning','ratio':ratio})
            drift=max(math.dist(f['foot_anchor_px'],metadata[0]['foot_anchor_px']) for f in metadata)
            report['clips'].append({'clip':clip,'frame_count':len(rendered),'dimensions':[256,256],
                'rgba':all(im.mode=='RGBA' for im in rendered),'blank_frames':sum(a==0 for a in areas),
                'max_layer_recomposition_error':max(layer_errors),'max_foot_anchor_drift_px':drift,
                'rendered_lower_body_bottom_drift_px':max(foot_pixels)-min(foot_pixels) if all(x is not None for x in foot_pixels) else None,
                'foot_metric_scope':'alpha bottom in body-only x75..185,y200..255; not semantic contact verification',
                'weapon_source_sha256':digest(ROOT/'assets/weapons'/(weapon+'.png')),
                'max_weapon_grip_pivot_error_px':max(m['grip_error_px'] for m in metadata),
                'alpha_area_ratio':ratio,'issues':issues,
                'technical_status':'fail' if any(x['severity']=='error' for x in issues) else ('pass_with_warnings' if issues else 'pass'),
                'art_status':'not_accepted'})
    old_report=ROOT/'reports/parts-experiment.json'
    if old_report.exists() and (route_filter!='all' or weapon_filter!='all'):
        rebuilt={c['clip'] for c in report['clips']}
        report['clips'] += [c for c in json.loads(old_report.read_text()).get('clips',[]) if c['clip'] not in rebuilt]
    report['technical_checks']={'expected_clips':4,'actual_clips':len(report['clips']),
      'layers_recompose_exactly':all(c['max_layer_recomposition_error']==0 for c in report['clips']),
      'no_blank_frames':all(c['blank_frames']==0 for c in report['clips']),
      'files_complete':all((out/c['clip']/'sheet.png').is_file() and len(list((out/c['clip']).glob('attack_[0-9][0-9][0-9].png')))==13 for c in report['clips'])}
    # Same pose at real game display sizes, beside enlarged view.
    board=Image.new('RGB',(900,610),'#eff0ec');d=ImageDraw.Draw(board)
    for row,route in enumerate(['B','C']):
        d.text((20,row*300+10),f'Route {route}: 64 / 96 / 128 / 256 px   -   EXPERIMENT / NOT ART APPROVED',fill='#25323a')
        if not (out/(route+'_hammer_a')/'attack_000.png').exists():continue
        src=Image.open(out/(route+'_hammer_a')/'attack_000.png').convert('RGBA');x=30
        for size in [64,96,128,256]:
            im=src.resize((size,size),Image.Resampling.LANCZOS);board.paste(im,(x,row*300+38+256-size),im);x+=size+35
    board.save(preview/'actual-size-comparison.png')
    (ROOT/'reports/parts-experiment.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':report['status'],'clips':len(report['clips']),**report['technical_checks']},indent=2))
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atlas',type=Path,default=ROOT/'assets/characters/warrior-parts-v001.png')
    parser.add_argument('--projection',type=Path,default=ROOT/'reports/structure/projection.json')
    parser.add_argument('--route',choices=['B','C','all'],default='all')
    parser.add_argument('--weapon',choices=['hammer_a','hammer_b','all'],default='all')
    parser.add_argument('--extract',action='store_true',help='Explicitly regenerate editable weapon crops from atlas (overwrites weapon edits).')
    args=parser.parse_args()
    if not args.atlas.is_file():parser.error('Authored atlas missing; will not substitute placeholder art.')
    if not args.projection.is_file():parser.error('Actual Blender projection missing.')
    report=run(args.atlas,args.projection,args.route,args.weapon,args.extract)
    if any(c['technical_status']=='fail' for c in report['clips']):return 1
    if not all(report['technical_checks'][x] for x in ['layers_recompose_exactly','no_blank_frames','files_complete']):return 1
    return 0
if __name__=='__main__':sys.exit(main())
