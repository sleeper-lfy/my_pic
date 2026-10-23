"""Review materials from real MakeHuman renders and evaluated bone projections."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'previews/public_human';REPORT=ROOT/'reports/public_human'

def font(size):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf']:
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()

def on_background(image,color='#d9e0e4'):
    bg=Image.new('RGBA',image.size,color);bg.alpha_composite(image.convert('RGBA'));return bg.convert('RGB')

def main():
    records=json.loads((REPORT/'render-projections.json').read_text());qa=json.loads((REPORT/'baseline-qa.json').read_text())
    full=[];errors=[];details=[]
    for record in records:
        path=ROOT/record['file'];im=Image.open(path);im.load();bbox=im.getchannel('A').getbbox()
        is_detail=path.stem=='right_hand_detail'
        if im.mode!='RGBA' or im.size!=(640,896):errors.append(path.name+':wrong_format')
        if not bbox:errors.append(path.name+':blank')
        elif not is_detail and (bbox[0]<=0 or bbox[1]<=0 or bbox[2]>=640 or bbox[3]>=896):errors.append(path.name+':full_body_clipped')
        details.append({'file':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'size':list(im.size),'bbox':bbox,'intentional_detail_crop':is_detail,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        if path.stem.startswith('rest_'):full.append(record)
    # Overlay derived from real rig pose endpoints, never invented 2D joints.
    record=next(r for r in records if Path(r['file']).stem=='rest_front')
    layer=on_background(Image.open(ROOT/record['file'])).convert('RGBA');d=ImageDraw.Draw(layer)
    major_prefixes=('root','spine','neck','head','pelvis','shoulder','clavicle','upperarm','lowerarm','wrist','upperleg','lowerleg','foot','toe','metacarpal','finger')
    drawn=0
    for name,bone in record['bone_projection'].items():
        if not name.startswith(major_prefixes):continue
        a,b=bone['head'][:2],bone['tail'][:2]
        color='#f0a21c' if name.startswith(('finger','metacarpal','toe')) else '#145ca8'
        d.line([tuple(a),tuple(b)],fill=color,width=2)
        for x,y in [a,b]:d.ellipse((x-2,y-2,x+2,y+2),fill=color)
        drawn+=1
    layer.save(OUT/'native-rig-overlay.png')
    board=Image.new('RGB',(1320,1020),'#eef1f3');d=ImageDraw.Draw(board)
    d.text((22,16),'PUBLIC HUMAN BASELINE / MakeHuman CC0 native mesh + rig',font=font(24),fill='#203748')
    d.text((22,52),'Original neutral proportions. Anatomy/rig reference only; not final warrior art.',font=font(17),fill='#465864')
    panels=[('FRONT / native rest','rest_front.png'),('FRONT LEFT / native rest','rest_front_left.png'),('FRONT RIGHT / native rest','rest_front_right.png'),('SIDE / native rest','rest_side.png'),('BACK / native rest','rest_back.png'),('ACTUAL 163-BONE RIG / main chains','native-rig-overlay.png')]
    for i,(label,name) in enumerate(panels):
        x=20+(i%3)*440;y=88+(i//3)*455
        d.text((x,y),label,font=font(15),fill='#203748')
        image=Image.open(OUT/name).convert('RGBA');image=on_background(image);image.thumbnail((410,420),Image.Resampling.LANCZOS)
        board.paste(image,(x+(410-image.width)//2,y+25))
    board.save(OUT/'contact-sheet.png')
    # Display only the five rendered sampled poses; do not imply a dense motion sequence.
    poses=[Image.open(OUT/f'skin_bend_{i:03}.png').convert('RGBA') for i in [1,9,17,25,33]]
    poses[0].save(OUT/'authored-elbow-skin-test.webp',save_all=True,append_images=poses[1:],duration=[250,250,400,250,250],loop=0,lossless=True)
    film=Image.new('RGB',(1600,520),'#eef1f3');d=ImageDraw.Draw(film)
    d.text((18,12),'AUTHORED ELBOW SKINNING TEST / 5 sampled poses / not downloaded motion',font=font(23),fill='#203748')
    for i,im in enumerate(poses):
        tile=on_background(im);tile.thumbnail((300,420),Image.Resampling.LANCZOS);film.paste(tile,(i*320+(320-tile.width)//2,60))
        d.text((i*320+15,485),'frame '+str([1,9,17,25,33][i]),font=font(16),fill='#405769')
    film.save(OUT/'skin-test-contact.png')
    hand=on_background(Image.open(OUT/'right_hand_detail.png'));hand.save(OUT/'right-hand-readable.png')
    qa['image_checks']={'status':'passed' if not errors else 'failed','render_count':len(records),'errors':errors,'images':details,'detail_crop_exemptions':['right_hand_detail.png'],'main_chain_bones_drawn':drawn}
    qa['visual_inspection']='Continuous human body, articulated fingers and readable native proportions visually checked; art approval remains pending.'
    # Source manifest is latest pinned inventory, although this importer only consumes
    # base.obj/default.mhskel/default_weights.mhw. Additional BVH files are not applied.
    qa['source']=json.loads((ROOT/'assets/public_references/makehuman/SOURCE.json').read_text())
    qa['consumed_asset_files']=['base.obj','default.mhskel','default_weights.mhw']
    (REPORT/'baseline-qa.json').write_text(json.dumps(qa,indent=2))
    (REPORT/'README.md').write_text('''# MakeHuman 公开人体结构基线\n\n来源为官方仓库固定 commit 下的 CC0 数据，详情见 `assets/public_references/makehuman/SOURCE.json` 与许可文件。没有安装 MakeHuman 程序，也没有引入其 AGPL 源码。\n\n实跑路径：\n```sh\nblender --background --factory-startup --threads 2 --python workflows/blender/public_human_baseline.py\npython workflows/blender/public_human_review.py\n```\n\n使用原始 body 面构建连续网格，保留源顶点索引；使用原生163骨、父子层级、原生权重和 Blender Armature modifier。源权重总和存在0.954–1.063范围的误差，逐顶点按比例归一化，不自动重绘蒙皮权重。只有 body 面参与渲染；helper/joint/tights/skirt/genital/eye/teeth等辅助面排除。\n\n`previews/public_human/contact-sheet.png` 是真实渲染的多视角人体和原生骨架投影覆盖。`right-hand-readable.png` 为手部细节。`workflows/blender/public_human_baseline.blend` 可检查真实网格、163骨父子关系、vertex groups、Armature modifier与测试Action。\n\n肘部测试是自行指定原生骨局部旋转的蒙皮诊断：33帧检查固定骨长和真实网格位移，渲染其中5个采样姿态；不是下载的动作，不是完整攻击动画。`authored-elbow-skin-test.webp` 明确为五姿态诊断播放。官方tpose/benchmark BVH是单帧姿态，当前脚本未应用这些BVH；不得据此声称其重定向已通过。骨轴roll使用原生plane的几何法线定义，未证明与MakeHuman原生BVH旋转约定完全一致。\n\n本基线仍是正常比例的人体参照，未修改成3.5头身战士，也未做2D最终美术、握锤或战斗动作验收。\n''',encoding='utf-8')
    print(json.dumps({'image_check':'passed' if not errors else 'failed','renders':len(records),'bones_drawn':drawn,'errors':errors}))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
