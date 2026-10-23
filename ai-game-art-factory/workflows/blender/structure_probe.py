"""Reproducible structure-only probe; run with Blender --background --python.

No downloaded assets, no AI models, and no claim that these primitives are art.
World: +X character-right, -Y forward, +Z up. PNG: origin top-left.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[2]
SIZE = 256
POSES = [
    ("idle", 0.0, (.55, -.13, 1.02), (-.45, -.12, 1.06), (.07, -.10, 1)),
    ("anticipation", .15, (.48, .06, 2.30), (-.49, -.31, 1.35), (-.40, .15, .88)),
    ("strike", .31, (.50, -.65, 1.35), (-.41, .10, 1.20), (.18, -.80, -.42)),
    ("recovery", .60, (.62, -.27, 1.15), (-.44, -.20, 1.13), (.15, -.28, .95)),
]
COLORS = {
    "torso": (.16, .33, .43, 1), "head": (.70, .49, .30, 1),
    "arm": (.20, .43, .56, 1), "hand": (.85, .62, .39, 1),
    "leg": (.17, .23, .31, 1), "boot": (.12, .15, .18, 1),
    "weapon": (.65, .35, .13, 1), "handle": (.30, .15, .07, 1),
}


def material(name, rgba):
    m = bpy.data.materials.new(name)
    m.diffuse_color = rgba
    m.use_nodes = True
    n = m.node_tree.nodes
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    em.inputs["Strength"].default_value = 1
    m.node_tree.links.new(em.outputs[0], out.inputs[0])
    return m


def primitive(name, kind, loc, scale, mat):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=loc)
    elif kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1, depth=2, location=loc)
    else:
        bpy.ops.mesh.primitive_cube_add(size=2, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(mat)
    return ob


def segment(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    ob = primitive(name, "cylinder", (a + b) / 2, (radius, radius, (b-a).length / 2), mat)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(b-a)
    return ob


def solve_elbow(shoulder, wrist, sign):
    a, b = Vector(shoulder), Vector(wrist)
    d = (b-a).length
    l1, l2 = .43, .40
    assert abs(l1-l2) < d < l1+l2, f"Unreachable wrist: {d}"
    axis = (b-a).normalized()
    along = (l1*l1 - l2*l2 + d*d) / (2*d)
    bend = Vector((sign, 0, 0))
    bend = (bend - axis * bend.dot(axis)).normalized()
    return a + axis*along + bend*math.sqrt(l1*l1-along*along)


def joints_for(pose):
    name, sec, right, left, direction = pose
    j = {
        "CharacterRoot": (0, 0, 0), "FootAnchor": (0, 0, 0),
        "Pelvis": (0, 0, 1.02), "Neck": (0, 0, 1.77), "Head": (0, -.015, 2.02),
        "RightShoulder": (.32, 0, 1.65), "LeftShoulder": (-.32, 0, 1.65),
        "RightHandAnchor": right, "LeftHandAnchor": left,
        "RightHip": (.18, 0, 1.02), "LeftHip": (-.18, 0, 1.02),
        "RightKnee": (.21, -.02, .56), "LeftKnee": (-.21, .02, .56),
        "RightFoot": (.24, -.03, .13), "LeftFoot": (-.24, -.03, .13),
        "WeaponSocket": right, "WeaponGripOffset": right,
    }
    j = {k: Vector(v) for k, v in j.items()}
    j["RightElbow"] = solve_elbow(j["RightShoulder"], j["RightHandAnchor"], 1)
    j["LeftElbow"] = solve_elbow(j["LeftShoulder"], j["LeftHandAnchor"], -1)
    axis = Vector(direction).normalized()
    j["WeaponHead"] = j["WeaponSocket"] + axis*.64
    j["WeaponButt"] = j["WeaponSocket"] - axis*.20
    return j


BONES = {
    "Spine": ("Pelvis", "Neck"), "Head": ("Neck", "Head"),
    "RightUpperArm": ("RightShoulder", "RightElbow"),
    "RightForearm": ("RightElbow", "RightHandAnchor"),
    "LeftUpperArm": ("LeftShoulder", "LeftElbow"),
    "LeftForearm": ("LeftElbow", "LeftHandAnchor"),
    "RightThigh": ("RightHip", "RightKnee"), "RightShin": ("RightKnee", "RightFoot"),
    "LeftThigh": ("LeftHip", "LeftKnee"), "LeftShin": ("LeftKnee", "LeftFoot"),
    "WeaponSocket": ("WeaponSocket", "WeaponHead"),
}


def armature(j):
    data = bpy.data.armatures.new("StructureSkeleton")
    ob = bpy.data.objects.new("Skeleton", data)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (a,b) in BONES.items():
        bone = data.edit_bones.new(name)
        bone.head = j[a]
        bone.tail = j[b]
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.show_in_front = True
    ob.select_set(False)
    return ob


def build_body(j, mats):
    obs = {}
    obs["torso"] = primitive("Torso_structure", "sphere", (0, 0, 1.42), (.35, .20, .43), mats["torso"])
    obs["head"] = primitive("Head_structure", "sphere", j["Head"], (.28, .24, .31), mats["head"])
    obs["nose"] = primitive("Forward_marker", "cube", (0, -.255, 2.01), (.075, .06, .07), mats["head"])
    for side in ["Right", "Left"]:
        obs[side+"UpperArm"] = segment(side+"UpperArm", j[side+"Shoulder"], j[side+"Elbow"], .105, mats["arm"])
        obs[side+"Forearm"] = segment(side+"Forearm", j[side+"Elbow"], j[side+"HandAnchor"], .09, mats["arm"])
        obs[side+"Hand"] = primitive(side+"Hand", "sphere", j[side+"HandAnchor"], (.105, .075, .10), mats["hand"])
        obs[side+"Thigh"] = segment(side+"Thigh", j[side+"Hip"], j[side+"Knee"], .135, mats["leg"])
        obs[side+"Shin"] = segment(side+"Shin", j[side+"Knee"], j[side+"Foot"], .11, mats["leg"])
        obs[side+"Boot"] = primitive(side+"Boot", "cube", j[side+"Foot"]+Vector((0,-.075,-.035)), (.13,.20,.095), mats["boot"])
    return obs


def build_weapon(j, mats, variant):
    shaft = segment("WeaponHandle", j["WeaponButt"], j["WeaponHead"], .035, mats["handle"])
    axis = (j["WeaponHead"]-j["WeaponSocket"]).normalized()
    quat = Vector((0,0,1)).rotation_difference(axis)
    head = primitive("HammerHead_"+variant, "cube" if variant=="hammer_block" else "sphere", j["WeaponHead"], (.25,.13,.12) if variant=="hammer_block" else (.29,.10,.19), mats["weapon"])
    head.rotation_mode="QUATERNION"
    head.rotation_quaternion=quat
    return shaft,head


def animate_weapon(j, shaft, head, frame):
    a,b=j['WeaponButt'],j['WeaponHead']
    shaft.location=(a+b)/2
    shaft.rotation_quaternion=Vector((0,0,1)).rotation_difference(b-a)
    shaft.scale.z=(b-a).length/2
    head.location=b
    head.rotation_quaternion=shaft.rotation_quaternion.copy()
    for ob in [shaft,head]:
        for prop in ['location','rotation_quaternion','scale']:
            ob.keyframe_insert(prop,frame=frame)


def animate(j, body, rig, frame):
    for name,(a,b) in BONES.items():
        pb=rig.pose.bones[name]
        length=(j[b]-j[a]).length
        q=Vector((0,1,0)).rotation_difference(j[b]-j[a])
        pb.matrix=Matrix.Translation(j[a]) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((1,length/pb.bone.length,1,1))
        pb.keyframe_insert("location",frame=frame)
        pb.keyframe_insert("rotation_quaternion",frame=frame)
        pb.keyframe_insert("scale",frame=frame)
    for side in ["Right","Left"]:
        for part,a,b in [("UpperArm","Shoulder","Elbow"),("Forearm","Elbow","HandAnchor")]:
            ob=body[side+part]; av,bv=j[side+a],j[side+b]
            ob.location=(av+bv)/2
            ob.rotation_quaternion=Vector((0,0,1)).rotation_difference(bv-av)
            ob.scale.z=(bv-av).length/2
            ob.keyframe_insert("location",frame=frame)
            ob.keyframe_insert("rotation_quaternion",frame=frame)
            ob.keyframe_insert("scale",frame=frame)
        ob=body[side+"Hand"]; ob.location=j[side+"HandAnchor"]; ob.keyframe_insert("location",frame=frame)


def make_camera(name, x):
    data=bpy.data.cameras.new(name)
    ob=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(ob)
    ob.location=(x,-6,3.7)
    target=Vector((0,-.08,1.38))
    ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'; data.ortho_scale=3.65
    data.lens=50; data.clip_start=.1; data.clip_end=100
    return ob


def compositor(scene, out_dir, prefix):
    scene.use_nodes=True
    tree=scene.node_tree; tree.nodes.clear()
    src=tree.nodes.new('CompositorNodeRLayers')
    def output(name,socket):
        node=tree.nodes.new('CompositorNodeOutputFile');node.base_path=str(out_dir)
        node.format.file_format='PNG';node.format.color_mode='RGBA';node.format.color_depth='8'
        node.file_slots[0].path=prefix+'_'+name+'_'
        node.file_slots[0].save_as_render = True
        if name != 'flat':
            node.format.color_management='OVERRIDE'
            node.format.view_settings.view_transform='Raw'
        tree.links.new(socket,node.inputs[0])
    # Combined emission render is the semantic flat guide.
    output('flat',src.outputs['Image'])
    # Encoded world-space normal pass; alpha is copied from rendered silhouette.
    mult=tree.nodes.new('CompositorNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(.5,.5,.5,1)
    tree.links.new(src.outputs['Normal'],mult.inputs[1])
    add=tree.nodes.new('CompositorNodeMixRGB');add.blend_type='ADD';add.inputs[0].default_value=1;add.inputs[2].default_value=(.5,.5,.5,1)
    tree.links.new(mult.outputs[0],add.inputs[1])
    alpha=tree.nodes.new('CompositorNodeSetAlpha');tree.links.new(add.outputs[0],alpha.inputs['Image']);tree.links.new(src.outputs['Alpha'],alpha.inputs['Alpha'])
    output('normal',alpha.outputs[0])
    depth=tree.nodes.new('CompositorNodeMapRange');depth.inputs['From Min'].default_value=7;depth.inputs['From Max'].default_value=11;depth.inputs['To Min'].default_value=1;depth.inputs['To Max'].default_value=0;depth.use_clamp=True
    tree.links.new(src.outputs['Depth'],depth.inputs['Value'])
    da=tree.nodes.new('CompositorNodeSetAlpha');tree.links.new(depth.outputs[0],da.inputs['Image']);tree.links.new(src.outputs['Alpha'],da.inputs['Alpha']);output('depth',da.outputs[0])
    sa=tree.nodes.new('CompositorNodeSetAlpha');sa.inputs['Image'].default_value=(1,1,1,1);tree.links.new(src.outputs['Alpha'],sa.inputs['Alpha']);output('silhouette',sa.outputs[0])


def project(scene,camera,j):
    inv=camera.matrix_world.inverted()
    out={}
    for name,point in j.items():
        uv=world_to_camera_view(scene,camera,point)
        out[name]={'xy':[round(uv.x*SIZE,5),round((1-uv.y)*SIZE,5)],'depth':round(-(inv@point).z,6),'world':[round(v,6) for v in point]}
    return out


def pose_png(path, projected):
    data=[0.0]*(SIZE*SIZE*4)
    def dot(x,y,r,color):
        for yy in range(max(0,int(y-r)),min(SIZE,int(y+r)+1)):
            for xx in range(max(0,int(x-r)),min(SIZE,int(x+r)+1)):
                if (xx-x)**2+(yy-y)**2<=r*r:
                    i=((SIZE-1-yy)*SIZE+xx)*4;data[i:i+4]=color
    for name,(a,b) in BONES.items():
        ax,ay=projected[a]['xy'];bx,by=projected[b]['xy'];steps=max(1,int(math.hypot(bx-ax,by-ay)*2))
        color=(1,.55,.12,1) if name=='WeaponSocket' else (.2,.8,1,1)
        for k in range(steps+1):
            t=k/steps;dot(ax+(bx-ax)*t,ay+(by-ay)*t,1.4,color)
    for point in projected.values():
        dot(*point['xy'],2.1,(1,.93,.7,1))
    image=bpy.data.images.new('PoseGuide',width=SIZE,height=SIZE,alpha=True)
    image.pixels.foreach_set(data);image.filepath_raw=str(path);image.file_format='PNG';image.save();bpy.data.images.remove(image)


def main():
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    parser=argparse.ArgumentParser();parser.add_argument('--output-root',type=Path,default=ROOT);parser.add_argument('--samples',type=int,default=4)
    args=parser.parse_args(argv)
    root=args.output_root.resolve();out=root/'previews/structure';report=root/'reports/structure'
    out.mkdir(parents=True,exist_ok=True);report.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=args.samples
    scene.cycles.use_denoising=False  # Emission guides need no denoiser; distro build lacks OIDN.
    scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.render.resolution_x=SIZE;scene.render.resolution_y=SIZE;scene.render.resolution_percentage=100
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    scene.render.fps=100;scene.frame_start=1;scene.frame_end=61
    layer=scene.view_layers[0];layer.use_pass_normal=True;layer.use_pass_z=True
    mats={name:material(name,color) for name,color in COLORS.items()}
    j0=joints_for(POSES[0]);rig=armature(j0);body=build_body(j0,mats)
    for pose in POSES:
        animate(joints_for(pose),body,rig,round(pose[1]*100)+1)
    cams={'front_left':make_camera('Camera_FrontLeft',-6),'front_right':make_camera('Camera_FrontRight',6)}
    records=[];max_error=0
    for direction,camera in cams.items():
        scene.camera=camera
        for variant in ['hammer_block','hammer_crescent']:
            directory=out/direction/variant;directory.mkdir(parents=True,exist_ok=True)
            for i,pose in enumerate(POSES):
                j=joints_for(pose);frame=round(pose[1]*100)+1;scene.frame_set(frame)
                shaft,head=build_weapon(j,mats,variant)
                bpy.context.view_layer.update()
                projected=project(scene,camera,j)
                # Measure the actual generated shaft transform against the actual palm,
                # rather than comparing two aliases in the joint configuration.
                handle_length=(j['WeaponHead']-j['WeaponButt']).length
                local_grip=Vector((0,0,-1+2*.20/handle_length))
                actual_grip=shaft.matrix_world@local_grip
                actual_hand=body['RightHand'].matrix_world.translation.copy()
                error=(actual_grip-actual_hand).length;max_error=max(error,max_error)
                prefix=f'attack_{i:02d}'
                compositor(scene,directory,prefix)
                bpy.ops.render.render()
                # File Output adds the Blender frame number; normalize to stable manifest paths.
                for channel in ['flat','normal','depth','silhouette']:
                    generated=directory/f'{prefix}_{channel}_{frame:04d}.png'
                    target=directory/f'{prefix}_{channel}.png'
                    generated.replace(target)
                pose_png(directory/f'{prefix}_pose.png',projected)
                records.append({'direction':direction,'weapon':variant,'index':i,'pose':pose[0],'time_seconds':pose[1],
                    'frame_number':frame,'joints':projected,'weapon_grip_error_world':error,
                    'measured_grip_world':list(actual_grip),'measured_hand_world':list(actual_hand),
                    'draw_order_far_to_near':sorted(projected,key=lambda k:projected[k]['depth'],reverse=True),
                    'files':{ch:str((directory/f'{prefix}_{ch}.png').relative_to(root)) for ch in ['flat','normal','depth','silhouette','pose']}})
                bpy.data.objects.remove(shaft,do_unlink=True);bpy.data.objects.remove(head,do_unlink=True)
    # Keep an inspectable initial weapon and both cameras in the scene snapshot.
    scene.frame_set(1);scene.camera=cams['front_left'];shaft,head=build_weapon(j0,mats,'hammer_block')
    anchors={}
    for name in ['CharacterRoot','FootAnchor','LeftHandAnchor','RightHandAnchor','WeaponSocket','WeaponGripOffset']:
        ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.empty_display_size=.06
        anchors[name]=ob
    for pose in POSES:
        j=joints_for(pose);frame=round(pose[1]*100)+1
        animate_weapon(j,shaft,head,frame)
        for name,ob in anchors.items():
            ob.location=j[name];ob.keyframe_insert('location',frame=frame)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(root/'workflows/blender/structure_probe.blend'))
    payload={'schema_version':1,'status':'structure_probe_only_not_final_art','blender_version':bpy.app.version_string,
        'canvas':[SIZE,SIZE],'coordinates':{'world':'+X character-right, -Y forward, +Z up','image':'top-left origin, +X right, +Y down'},
        'camera':{'projection':'orthographic','azimuth_degrees':[-45,45],'ortho_scale':3.65,'target':[0,-.08,1.38]},
        'depth_encoding':{'near':7,'far':11,'near_white':True,'view_transform':'Raw'},'normal_encoding':'world-space signed xyz mapped to [0,1]; Raw view transform; 8-bit PNG',
        'key_pose_count':4,'frame_count':len(records),'max_weapon_grip_error_world':max_error,
        'limitations':['Four diagnostic key poses are not a finished animation.','Hand volumes do not model fingers wrapping a handle.','Flat geometric structures are guides only, never final game assets.','C projection supplies positions/depth only; texture deformation and hidden surfaces require approved 2D art.','Crescent variant is an ellipsoid proxy, not a finished crescent design.','No ComfyUI redraw or temporal AI consistency has been validated.'],
        'records':records}
    (report/'projection.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    paths=sorted({root/path for record in records for path in record['files'].values()})
    manifest={'files':[{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (report/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('STRUCTURE_PROBE_COMPLETE',len(records),'pose-weapon-direction records',len(paths),'PNGs', 'grip error',max_error)


if __name__=='__main__':
    main()
