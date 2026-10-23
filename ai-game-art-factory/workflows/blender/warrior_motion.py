"""MakeHuman native skin + authored combat rotations. Structural guide, not finished art.

blender --background --factory-startup --threads 2 --python workflows/blender/warrior_motion.py
Optional: -- --preview-only (first pose), --skip-render (rig + QA).
"""
import sys, json, math, argparse
from pathlib import Path
import bpy
from mathutils import Vector, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
import public_human_baseline as baseline
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'previews/warrior_motion'; REPORT=ROOT/'reports/warrior_motion'; EXPORT=ROOT/'exports/warrior_motion'
SIZE=512
CLIPS={'idle':{'durations':[250,250,250,250],'loop':True},'attack':{'durations':[100,140,120,60,70,100,120,160],'loop':False},'defense':{'durations':[120,180,220,180],'loop':False}}


def mat(name,color,rough=.8):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough
    return m


def stylize(human,rig):
    # A single continuous monotone rest-space map is applied identically to mesh AND every joint.
    # It changes proportions before skinning; animation never changes bone scale or lengths.
    def warp(p):
        blend=max(0,min(1,(p.z-1.37)/.10));blend=blend*blend*(3-2*blend)
        z=p.z*.58 if p.z<1.455 else 1.455*.58+(p.z-1.455)*1.4
        return Vector((p.x*(.9+.5*blend),p.y*(.9+.5*blend),z))
    original=[v.co.copy() for v in human.data.vertices]
    for v in human.data.vertices:v.co=warp(v.co)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    positions={b.name:(b.head.copy(),b.tail.copy(),b.use_connect) for b in rig.data.edit_bones}
    for b in rig.data.edit_bones:b.use_connect=False
    for b in rig.data.edit_bones:
        head,tail,connected=positions[b.name];b.head=warp(head);b.tail=warp(tail)
    for b in rig.data.edit_bones:b.use_connect=positions[b.name][2]
    bpy.ops.object.mode_set(mode='OBJECT')
    skin=mat('Anatomy_skin_guide',(.64,.43,.29));cloth=mat('Bluegray_suit_guide',(.12,.20,.28));pants=mat('Charcoal_trousers_guide',(.08,.10,.14));boots=mat('Brown_boots_guide',(.12,.065,.035));hair=mat('Dark_scalp_guide',(.06,.035,.022))
    human.data.materials.clear()
    for m in [skin,cloth,pants,boots,hair]:human.data.materials.append(m)
    for f in human.data.polygons:
        center=sum((original[i] for i in f.vertices),Vector())/len(f.vertices)
        is_hand=abs(center.x)>.4 and center.y<-.16
        idx=0 if center.z>1.42 or is_hand else (3 if center.z<.16 else (2 if center.z<.9 else 1))
        if center.z>1.64 or (center.z>1.55 and center.y>.02):idx=4
        f.material_index=idx
    return {'rest_space_body_vertical_scale':.58,'rest_space_head_vertical_scale':1.4,'full_height_m':max(v.co.z for v in human.data.vertices),'head_to_body_estimate':max(v.co.z for v in human.data.vertices)/(max(v.co.z for v in human.data.vertices)-warp(Vector((0,0,1.455))).z),'note':'Anatomical landmarks approximate chin; stylization is applied to original visible mesh and every native joint before skinning.'}


def update():bpy.context.view_layer.update()

def worldrotate(pb,axis,degrees):
    q=Quaternion(Vector(axis),math.radians(degrees));m=pb.matrix.copy()
    pb.matrix=Matrix.LocRotScale(m.translation,q@m.to_quaternion(),Vector((1,1,1)));update()


def aim_chain(rig,upper,endpoint,direction):
    b=rig.pose.bones[upper];v=rig.pose.bones[endpoint].head-b.head
    q=v.normalized().rotation_difference(Vector(direction).normalized());m=b.matrix.copy()
    b.matrix=Matrix.LocRotScale(m.translation,q@m.to_quaternion(),Vector((1,1,1)));update()


def arm_ik(rig,side,target,pole):
    u='upperarm01.'+side;l='lowerarm01.'+side;w='wrist.'+side
    shoulder=rig.pose.bones[u].head.copy();elbow=rig.pose.bones[l].head.copy();wrist=rig.pose.bones[w].head.copy()
    a=(elbow-shoulder).length;b=(wrist-elbow).length;t=Vector(target)-shoulder
    length=min(max(t.length,abs(a-b)+.004),a+b-.006);d=t.normalized()
    p=Vector(pole)-shoulder;p=(p-d*p.dot(d)).normalized()
    cos=max(-1,min(1,(a*a+length*length-b*b)/(2*a*length)))
    desired_elbow=shoulder+a*(d*cos+p*math.sqrt(max(0,1-cos*cos)))
    target=shoulder+d*length
    aim_chain(rig,u,l,desired_elbow-shoulder)
    aim_chain(rig,l,w,target-rig.pose.bones[l].head)
    return (rig.pose.bones[w].head-target).length


def cube(name,loc,scale,material,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
    mod=o.modifiers.new('Forged_edge_bevel','BEVEL');mod.width=bevel;mod.segments=2
    o.modifiers.new('Weighted_corner_normals','WEIGHTED_NORMAL')
    return o


def weapon_build():
    root=bpy.data.objects.new('WeaponSocket',None);bpy.context.collection.objects.link(root)
    steel=mat('Hammer_steel_guide',(.35,.43,.49),.5);copper=mat('Hammer_copper_guide',(.5,.25,.10),.5);wood=mat('Hammer_grip_guide',(.13,.055,.025))
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.018,depth=.42,location=(0,0,.11));shaft=bpy.context.object;shaft.name='Hammer_shaft';shaft.data.materials.append(wood);shaft.parent=root
    for name,loc,scale,m in [('Hammer_head',(0,0,.32),(.22,.10,.12),steel),('Hammer_endL',(-.112,0,.32),(.025,.12,.15),copper),('Hammer_endR',(.112,0,.32),(.025,.12,.15),copper)]:
        o=cube(name,loc,scale,m,.012);o.parent=root
    root['design']='Original rectangular steel copper guide hammer; not final painted asset'
    return root


def setup_hand(rig,side):
    # Curl native phalanges about a world-space across-palm axis, keeping real skin.
    sign=-1 if side=='R' else 1
    wrist=rig.pose.bones['wrist.'+side]
    palm_forward=(rig.pose.bones['finger3-1.'+side].head-wrist.head).normalized()
    cross=Vector((sign,0,0));axis=palm_forward.cross(cross).normalized()
    for finger in [2,3,4,5]:
        for segment,degree in [(1,38),(2,60),(3,45)]:
            pb=rig.pose.bones[f'finger{finger}-{segment}.{side}']
            worldrotate(pb,axis,degree)
    for segment,degree in [(1,12),(2,25),(3,25)]:worldrotate(rig.pose.bones[f'finger1-{segment}.{side}'],axis,degree)


def wrist_and_weapon(rig,weapon,axis):
    # Establish a fixed local socket once; then every pose carries weapon with the wrist.
    pb=rig.pose.bones['wrist.R'];q=pb.matrix.to_quaternion()
    current_axis=q@Vector((1,0,0));desired=Vector(axis).normalized()
    delta=current_axis.rotation_difference(desired);m=pb.matrix.copy()
    pb.matrix=Matrix.LocRotScale(m.translation,delta@m.to_quaternion(),Vector((1,1,1)));update()
    weapon.matrix_world=pb.matrix@weapon['socket_matrix']
    update()


def pose(rig,weapon,index):
    for pb in rig.pose.bones:pb.matrix_basis.identity()
    update()
    # Positions in stylized metre coordinates; both feet stay in planted rest stance.
    settings=[
      # R wrist, L wrist, hammer axis, spine pitch, spine twist, head turn
      ((-.36,-.15,.58),(.25,-.12,.59),(0,-.12,1),0,0,0),
      ((-.36,-.145,.59),(.25,-.115,.60),(0,-.10,1),-1,0,1),
      ((-.36,-.15,.58),(.25,-.12,.59),(0,-.12,1),0,0,0),
      ((-.36,-.155,.57),(.25,-.125,.58),(0,-.15,1),1,0,-1),
      ((-.36,-.15,.58),(.25,-.12,.59),(0,-.12,1),0,0,0),
      ((-.32,.02,.69),(.25,-.19,.66),(-.25,.55,.8),-6,-12,-4),
      ((-.28,.02,.96),(.22,-.21,.71),(-.2,.5,.9),-10,-18,-4),
      ((-.25,-.20,.98),(.26,-.11,.66),(0,-.55,.85),-2,-8,0),
      ((-.17,-.33,.62),(.30,.02,.67),(.1,-.9,-.2),12,12,2),
      ((-.10,-.30,.50),(.27,.05,.65),(.15,-.5,-.8),15,16,3),
      ((-.25,-.24,.55),(.26,-.05,.62),(0,-.2,.85),6,6,1),
      ((-.36,-.15,.58),(.25,-.12,.59),(0,-.12,1),0,0,0),
      ((-.34,-.18,.66),(.22,-.23,.68),(-.4,-.1,1),1,-3,0),
      ((-.33,-.24,.76),(.12,-.30,.82),(-.4,.05,1),3,-5,0),
      ((-.32,-.22,.73),(.12,-.29,.79),(-.4,.10,1),-2,-7,0),
      ((-.34,-.18,.66),(.22,-.23,.68),(-.4,-.1,1),1,-3,0),
    ]
    right,left,axis,pitch,twist,turn=settings[index]
    for n in ['spine03','spine02','spine01']:
        worldrotate(rig.pose.bones[n],(1,0,0),pitch/3);worldrotate(rig.pose.bones[n],(0,0,1),twist/3)
    worldrotate(rig.pose.bones['head'],(0,0,1),turn)
    er=arm_ik(rig,'R',right,(-.65,.03,.65));el=arm_ik(rig,'L',left,(.65,.02,.61))
    setup_hand(rig,'R');setup_hand(rig,'L')
    wrist_and_weapon(rig,weapon,axis)
    return {'ik_target_error_m':[er,el],'spine_pitch_deg':pitch,'spine_twist_deg':twist}


def camera(scene,cam,angle):
    baseline.set_camera(cam,angle,12,target=Vector((0,0,0)),scale=2.08)
    # Camera local Y translation puts origin exactly at (256,448), independent of pose.
    up=cam.rotation_euler.to_quaternion()@Vector((0,1,0));cam.location+=up*(2.08*.375)
    update()


def project(scene,cam,p):
    v=world_to_camera_view(scene,cam,Vector(p));return [round(v.x*SIZE,5),round((1-v.y)*SIZE,5)]


def render(scene,path):
    path.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)



def align_quaternion_keys(action):
    """Keep adjacent equivalent quaternions on the same hemisphere before interpolation."""
    groups={}
    for fc in action.fcurves:
        if fc.data_path.endswith('rotation_quaternion'):
            groups.setdefault(fc.data_path,{})[fc.array_index]=fc
    corrected=0
    for channels in groups.values():
        if set(channels)!={0,1,2,3}:continue
        previous=None
        for index in range(len(channels[0].keyframe_points)):
            points=[channels[c].keyframe_points[index] for c in range(4)]
            current=Quaternion([p.co.y for p in points])
            if previous is not None and previous.dot(current)<0:
                for p in points:
                    p.co.y=-p.co.y;p.handle_left.y=-p.handle_left.y;p.handle_right.y=-p.handle_right.y
                current.negate();corrected+=1
            previous=current
    return corrected

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview-only',action='store_true');ap.add_argument('--skip-render',action='store_true');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for p in [OUT,REPORT,EXPORT]:p.mkdir(parents=True,exist_ok=True)
    scene,cam=baseline.scene_setup();scene.cycles.samples=12;scene.render.resolution_x=SIZE;scene.render.resolution_y=SIZE
    human,rig,stats=baseline.setup_human();proportion=stylize(human,rig);weapon=weapon_build();update()
    # Handle axis is aligned with the local palm transverse axis; socket in closed hand.
    w=rig.pose.bones['wrist.R'];center=(rig.pose.bones['finger3-1.R'].head+w.head)*.5
    center+=Vector((.006,0,.005))
    axis=w.matrix.to_quaternion()@Vector((1,0,0));rot=Vector((0,0,1)).rotation_difference(axis)
    socket=w.matrix.inverted()@Matrix.LocRotScale(center,rot,Vector((1,1,1)))
    weapon['socket_matrix']=[list(row) for row in socket]
    # Blender ID properties list-of-lists needs conversion at multiplication.
    weapon['socket_matrix_flat']=[v for row in socket for v in row]
    rest={b.name:b.length for b in rig.data.bones};records=[];all_samples=[]
    global_socket=socket.copy()
    # Pose function reads matrix; attach through Python proxy to retain exact transform.
    class SocketProxy:
        def __init__(self,obj):self.obj=obj
        def __getitem__(self,k):return global_socket if k=='socket_matrix' else self.obj[k]
        @property
        def matrix_world(self):return self.obj.matrix_world
        @matrix_world.setter
        def matrix_world(self,m):self.obj.matrix_world=m
    proxy=SocketProxy(weapon)
    rig.animation_data_create();start=1;offset=0
    for clip,info in CLIPS.items():
        action=bpy.data.actions.new('Warrior_'+clip);action.use_fake_user=True;rig.animation_data.action=action
        # Weapon animation has a matching named action with fixed socket relationship baked.
        weapon.animation_data_create();wa=bpy.data.actions.new('Hammer_'+clip);wa.use_fake_user=True;weapon.animation_data.action=wa
        frame=1
        for local,duration in enumerate(info['durations']):
            idx=offset+local;scene.frame_set(frame);m=pose(rig,proxy,idx)
            for pb in rig.pose.bones:
                pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
            weapon.rotation_mode='QUATERNION';weapon.keyframe_insert('location',frame=frame);weapon.keyframe_insert('rotation_quaternion',frame=frame)
            record={'index':idx,'action':clip,'local_frame':local,'source_frame':frame,'duration_ms':duration,'loop':info['loop'],'pose_info':m,'directions':{}}
            for direction,az in [('front_left',-45),('front_right',45)]:
                camera(scene,cam,az)
                path=OUT/direction/f'pose_{idx:02}.png'
                if not args.skip_render and (not args.preview_only or idx==0):render(scene,path)
                bones={n:{'head':project(scene,cam,p.head),'tail':project(scene,cam,p.tail)} for n,p in rig.pose.bones.items()}
                grip=weapon.matrix_world.translation
                record['directions'][direction]={'file':str(path.relative_to(ROOT)),'anchors':{'CharacterRoot':[256,448],'FootAnchor':[256,448],'RightHandAnchor':project(scene,cam,rig.pose.bones['wrist.R'].head),'LeftHandAnchor':project(scene,cam,rig.pose.bones['wrist.L'].head),'WeaponSocket':project(scene,cam,grip)},'bones':bones}
            records.append(record);frame+=max(1,round(duration*.024))
            if args.preview_only:break
        # Loop endpoint for idle, settle endpoint for one-shot clips.
        scene.frame_set(frame);pose(rig,proxy,offset if clip=='idle' else offset+len(info['durations'])-1)
        for pb in rig.pose.bones:pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
        weapon.keyframe_insert('location',frame=frame);weapon.keyframe_insert('rotation_quaternion',frame=frame)
        for a in [action,wa]:
            for fc in a.fcurves:
                for kp in fc.keyframe_points:kp.interpolation='BEZIER';kp.handle_left_type='AUTO_CLAMPED';kp.handle_right_type='AUTO_CLAMPED'
        for a in [action,wa]:align_quaternion_keys(a)
        # Weapon uses a fixed native bone parent instead of independent interpolated positions.
        for f in range(1,frame+1):
            scene.frame_set(f);update();m=rig.pose.bones['wrist.R'].matrix@global_socket
            drift=max(abs(pb.length-rest[pb.name]) for pb in rig.pose.bones)
            all_samples.append({'action':clip,'frame':f,'max_bone_length_error_m':drift,'right_wrist':list(rig.pose.bones['wrist.R'].head),'grip':list(m.translation)})
        offset+=len(info['durations'])
        if args.preview_only:break
    # Constraint maintains native hand binding throughout interpolation and action playback.
    weapon.animation_data_clear();weapon.parent=rig;weapon.parent_type='BONE';weapon.parent_bone='wrist.R'
    # Bone-parent object transforms use tail basis; compensate once for local bone length.
    weapon.matrix_parent_inverse=Matrix.Identity(4)
    weapon.matrix_basis=Matrix.Translation((0,-rig.data.bones['wrist.R'].length,0))@global_socket
    rig.animation_data.action=bpy.data.actions.get('Warrior_idle');scene.frame_start=1;scene.frame_end=25;scene.frame_set(1);update();camera(scene,cam,-45)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'workflows/blender/warrior_motion.blend'))
    report={'scope':'Structural guide from continuous MakeHuman native skinned human; authored combat, not captured public motion','source_commit':human['source_commit'],'mesh_rig':stats,'proportion':proportion,'cell_size':SIZE,'sheet_layout':[4,4],'pose_count':len(records),'clips':CLIPS,'records':records,'sample_count':len(all_samples),'max_bone_length_error_m':max(x['max_bone_length_error_m'] for x in all_samples),'samples':all_samples,'limitations':['Guide only; final hand-painted 2D art is a separate output.','Finger curls are authored anatomical guides; visual grip must be checked in painted output.','Combat is authored on native MakeHuman rig, not retargeted walk motion.','Foot anchors represent world ground origin; camera and feet are constant across keys.']}
    (REPORT/'poses.json').write_text(json.dumps(report,indent=2));print('WARRIOR_MOTION_COMPLETE',len(records),report['max_bone_length_error_m'],flush=True)
    if report['max_bone_length_error_m']>1e-4:raise RuntimeError('Bone-length drift')

if __name__=='__main__':main()
