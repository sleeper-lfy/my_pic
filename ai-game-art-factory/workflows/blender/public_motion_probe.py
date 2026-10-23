"""Render an attributed public native skin/clip and inspect a separate public BVH.

Blender: --background --factory-startup --threads 2 --python this_file.py
No retargeting, invented motion, image generation or anatomy-quality claim.
"""
from pathlib import Path
import hashlib
import json
import math
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'previews/public_motion'
REPORT=ROOT/'reports/public_motion'
SAMPLES=24


def sample(scene,time):
    scene.frame_set(int(time),subframe=time-int(time))
    bpy.context.view_layer.update()


def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1)
    m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.75
    return m


def setup_scene():
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=False
    scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.world.color=(.35,.35,.35)
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
    return scene


def camera_and_light(scene,lo,hi):
    center=(lo+hi)/2;height=max(hi.z-lo.z,hi.x-lo.x,hi.y-lo.y)
    data=bpy.data.cameras.new('NativeClipCamera');cam=bpy.data.objects.new('NativeClipCamera',data);scene.collection.objects.link(cam)
    cam.location=center+Vector((height*1.7,-height*2.6,height*.55))
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=height*1.30;scene.camera=cam
    for i,(location,energy,size) in enumerate([((height*2,-height*3,height*3),1000,height*3),((-height*3,-height,height*2),650,height*3)]):
        ld=bpy.data.lights.new('Key' if i==0 else 'Fill','AREA');lo_=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(lo_)
        lo_.location=center+Vector(location);lo_.rotation_euler=(center-lo_.location).to_track_quat('-Z','Y').to_euler();ld.energy=energy*height*height/4;ld.shape='DISK';ld.size=size
    return {'center':list(center),'ortho_scale':data.ortho_scale,'fixed_across_sequence':True,'elevation_comment':'Fixed diagnostic view, not the character production style camera'}


def bounds_of_mesh(mesh):
    deps=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(deps);data=evaluated.to_mesh()
    points=[evaluated.matrix_world@v.co for v in data.vertices];evaluated.to_mesh_clear()
    return points


def riggedfigure():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/public_references/riggedfigure/RiggedFigure.glb'))
    scene=setup_scene();scene.render.fps=24
    arm=next(o for o in scene.objects if o.type=='ARMATURE')
    mesh=next(o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
    for ob in scene.objects:
        if ob.type=='MESH' and ob!=mesh:ob.hide_render=True
    mesh.data.materials.clear();mesh.data.materials.append(material('Diagnostic clay',(0.26,.47,.62)))
    actions=list(bpy.data.actions)
    start,end=actions[0].frame_range
    times=[start+(end-start)*i/(SAMPLES-1) for i in range(SAMPLES)]
    points=[];frame_records=[]
    for t in times:
        sample(scene,t);points.extend(bounds_of_mesh(mesh))
        frame_records.append({'sample_frame':float(t),'seconds':float(t/24),'bones':{b.name:{'head_world':list(arm.matrix_world@b.head),'tail_world':list(arm.matrix_world@b.tail),'length_world':(arm.matrix_world@b.tail-arm.matrix_world@b.head).length,'parent':b.parent.name if b.parent else None} for b in arm.pose.bones}})
    lo=Vector(tuple(min(p[k] for p in points) for k in range(3)));hi=Vector(tuple(max(p[k] for p in points) for k in range(3)))
    camera=camera_and_light(scene,lo,hi)
    folder=OUT/'riggedfigure';folder.mkdir(parents=True,exist_ok=True)
    for index,t in enumerate(times):
        sample(scene,t);scene.render.filepath=str(folder/f'native_{index:03}.png');bpy.ops.render.render(write_still=True)
        frame_records[index]['file']=str(Path(scene.render.filepath).relative_to(ROOT))
    weights=[sum(g.weight for g in v.groups if mesh.vertex_groups[g.group].name in arm.data.bones) for v in mesh.data.vertices]
    length_drift={name:max(f['bones'][name]['length_world'] for f in frame_records)-min(f['bones'][name]['length_world'] for f in frame_records) for name in arm.data.bones.keys()}
    # A child head need not coincide with parent tail for valid branched rigs.
    # Check hierarchy existence and finite transforms, not an invalid zero-gap assumption.
    finite=all(math.isfinite(v) for f in frame_records for b in f['bones'].values() for key in ['head_world','tail_world'] for v in b[key])
    required=['arm_joint_R_1','arm_joint_L_1','leg_joint_R_1','leg_joint_L_1','neck_joint_1']
    report={'status':'passed' if finite and min(weights)>.999 and max(weights)<1.001 and max(length_drift.values())<1e-4 else 'failed',
       'source':'KhronosGroup/glTF-Sample-Assets RiggedFigure, Cesium 2017, CC BY 4.0','mesh_vertices':len(mesh.data.vertices),'skin_joints':len(arm.data.bones),
       'native_actions':[{'name':a.name,'frames':list(a.frame_range)} for a in actions], 'sample_count':SAMPLES,'source_duration_seconds':float((end-start)/24),
       'changes':'Imported official source; diagnostic clay material, camera and lighting added. Native geometry, skin and motion left intact.',
       'weight_sum_min':min(weights),'weight_sum_max':max(weights),'unweighted_vertices':sum(v<1e-7 for v in weights),
       'required_limb_joints_present':all(n in arm.data.bones for n in required),'max_world_bone_length_variation':max(length_drift.values()),
       'finite_pose_coordinates':finite,'root_bones':[b.name for b in arm.data.bones if b.parent is None], 'camera':camera,
       'anatomy_art_status':'not_approved; low-detail sample is for native animation transfer only; no fingers or weapon grip', 'frames':frame_records}
    (REPORT/'riggedfigure.json').write_text(json.dumps(report,indent=2))
    sample(scene,start);scene.frame_start=int(start);scene.frame_end=int(end)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'workflows/blender/public_motion_probe.blend'))
    return report


def walk_skeleton():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_anim.bvh(filepath=str(ROOT/'assets/public_references/makehuman/walk1.bvh'),axis_forward='Y',axis_up='Z',use_fps_scale=False,update_scene_fps=True)
    arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');scene=bpy.context.scene
    action=arm.animation_data.action
    records=[]
    for frame in range(1,15):
        sample(scene,frame)
        records.append({'frame':frame,'bones':{b.name:{'head':list(arm.matrix_world@b.head),'tail':list(arm.matrix_world@b.tail),'parent':b.parent.name if b.parent else None} for b in arm.pose.bones}})
    report={'source':'MakeHuman official bundled walk1.bvh (CC0)', 'frames':14,'fps':scene.render.fps,'native_bones':len(arm.data.bones),
            'action_range':list(action.frame_range),'retargeted':False,'purpose':'Native old-rig skeleton reference, not applied to the new MakeHuman default mesh; walking, not attack','records':records}
    (REPORT/'walk1-native-skeleton.json').write_text(json.dumps(report,indent=2))


def main():
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    report=riggedfigure();walk_skeleton()
    print('PUBLIC_NATIVE_PROBE_COMPLETE',report['status'],report['skin_joints'],report['sample_count'])
    if report['status']!='passed':raise RuntimeError('Native skin integrity check failed')


if __name__=='__main__':main()
