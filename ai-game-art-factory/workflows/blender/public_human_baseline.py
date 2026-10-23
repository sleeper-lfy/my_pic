"""Import pinned CC0 MakeHuman BODY, native hierarchy and skin weights.

Blender: blender --background --threads 2 --python workflows/blender/public_human_baseline.py
The exported bend is an authored diagnostic, NOT downloaded mocap or final art.
"""
import json, math, hashlib
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'assets/public_references/makehuman'
OUT=ROOT/'previews/public_human'
REPORT=ROOT/'reports/public_human'
WIDTH,HEIGHT=640,896
SCALE=.1


def parse_obj(path):
    vertices=[]; faces=[]; group=''; skipped={}
    for line in path.read_text().splitlines():
        if line.startswith('v '):vertices.append(Vector(tuple(map(float,line.split()[1:4]))))
        elif line.startswith('g '):group=line[2:].strip()
        elif line.startswith('f '):
            if group=='body':faces.append([int(p.split('/')[0])-1 for p in line.split()[1:]])
            else:skipped[group]=skipped.get(group,0)+1
    used=sorted({v for f in faces for v in f})
    zmin=min(vertices[v].y for v in used)
    def convert(v):return Vector((v.x*SCALE,-v.z*SCALE,(v.y-zmin)*SCALE))
    return vertices,used,faces,convert,skipped


def material():
    mat=bpy.data.materials.new('Neutral_anatomical_clay_not_final_art');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(.22,.30,.37,1)
    bsdf.inputs['Roughness'].default_value=.78
    return mat


def setup_human():
    raw,used,faces,convert,skipped=parse_obj(SOURCE/'base.obj')
    skel=json.loads((SOURCE/'default.mhskel').read_text())
    weights=json.loads((SOURCE/'default_weights.mhw').read_text())['weights']
    mapping={src:dst for dst,src in enumerate(used)}
    mesh=bpy.data.meshes.new('MakeHuman_CC0_body_continuous_mesh')
    mesh.from_pydata([convert(raw[i]) for i in used],[],[[mapping[i] for i in f] for f in faces]);mesh.update()
    source_index=mesh.attributes.new('mh_source_vertex_index','INT','POINT')
    for i,src in enumerate(used):source_index.data[i].value=src
    obj=bpy.data.objects.new('MakeHuman_Body',mesh);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material())
    for polygon in mesh.polygons:polygon.use_smooth=True
    data=bpy.data.armatures.new('MakeHuman_native_163_bones');rig=bpy.data.objects.new('MakeHuman_Rig',data)
    bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    rig.show_in_front=True;data.display_type='OCTAHEDRAL'
    joints={n:convert(sum((raw[i] for i in ids),Vector())/len(ids)) for n,ids in skel['joints'].items()}
    bpy.ops.object.mode_set(mode='EDIT');roll_fallback=[]
    for name,b in skel['bones'].items():
        bone=data.edit_bones.new(name);bone.head=joints[b['head']];bone.tail=joints[b['tail']]
        plane=skel['planes'].get(b['rotation_plane'])
        if plane:
            a,c,d=[joints[n] for n in plane]
            normal=(c-a).cross(d-a)
            if normal.length>1e-8:bone.align_roll(normal.normalized())
            else:roll_fallback.append(name)
    for name,b in skel['bones'].items():
        bone=data.edit_bones[name]
        if b['parent']:
            parent=data.edit_bones[b['parent']];bone.parent=parent
            bone.use_connect=(bone.head-parent.tail).length<1e-6
    bpy.ops.object.mode_set(mode='OBJECT')
    sums={i:0.0 for i in used}
    for name,items in weights.items():
        for idx,value in items:
            if idx in sums:sums[idx]+=value
    missing=[i for i in used if sums[i]<=0]
    if missing:raise RuntimeError('Unweighted visible vertices: '+str(len(missing)))
    for name,items in weights.items():
        if name not in data.bones:raise RuntimeError('Weight bone missing: '+name)
        vg=obj.vertex_groups.new(name=name)
        for idx,value in items:
            if idx in mapping and value>0:vg.add([mapping[idx]],value/sums[idx],'REPLACE')
    modifier=obj.modifiers.new('Native_MakeHuman_skinning','ARMATURE');modifier.object=rig;modifier.use_deform_preserve_volume=True
    obj.parent=rig
    for pb in rig.pose.bones:
        pb.rotation_mode='QUATERNION';pb.location=(0,0,0);pb.scale=(1,1,1)
    obj['license']='CC0-1.0';rig['license']='CC0-1.0'
    obj['source_commit']=json.loads((SOURCE/'SOURCE.json').read_text())['commit']
    obj['source_only_body_group']=True
    return obj,rig,{'body_vertices':len(used),'body_faces':len(faces),'original_vertices':len(raw),'bones':len(data.bones),
                   'native_parent_links':sum(b.parent is not None for b in data.bones),
                   'connected_links':sum(b.use_connect for b in data.bones),
                   'unweighted_visible_vertices':len(missing),'raw_weight_sum_range':[min(sums.values()),max(sums.values())],
                   'weight_adjustment':'Native weights normalized per visible vertex; ratios preserved, no automatic reweighting',
                   'excluded_face_groups':skipped,'roll_degenerate_planes':roll_fallback,
                   'bone_roll_method':'Local Z aligned with normal of native rotation_plane; BVH rest-axis equivalence not asserted'}


def scene_setup():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32
    scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.render.resolution_x=WIDTH;scene.render.resolution_y=HEIGHT;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.72,.8,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.25
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
    for name,loc,energy,size in [('Key',(-2,-3,4),65,3),('Fill',(2,-2,2),30,2),('Rim',(0,2,3),55,2)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
        ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=loc
        ob.rotation_euler=(Vector((0,0,.9))-ob.location).to_track_quat('-Z','Y').to_euler()
    camera_data=bpy.data.cameras.new('Orthographic_review');camera_data.type='ORTHO';camera_data.ortho_scale=1.96
    cam=bpy.data.objects.new('ReviewCamera',camera_data);bpy.context.collection.objects.link(cam);scene.camera=cam
    scene.render.fps=24
    return scene,cam


def set_camera(cam,azimuth,elevation=0,target=Vector((0,-.045,.84)),scale=1.96):
    angle=math.radians(azimuth);el=math.radians(elevation);dist=5
    cam.location=target+Vector((math.sin(angle)*dist*math.cos(el),-math.cos(angle)*dist*math.cos(el),math.sin(el)*dist))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    bpy.context.view_layer.update()


def evaluated_points(obj):
    mesh=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    result=[v.co.copy() for v in mesh.vertices]
    obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    return result


def render(scene,cam,rig,name):
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    projection={}
    for bone in rig.pose.bones:
        values=[]
        for pt in [bone.head,bone.tail]:
            q=world_to_camera_view(scene,cam,rig.matrix_world@pt)
            values.append([q.x*WIDTH,(1-q.y)*HEIGHT,q.z])
        projection[bone.name]={'head':values[0],'tail':values[1],'parent':bone.parent.name if bone.parent else None}
    return {'file':str((OUT/(name+'.png')).relative_to(ROOT)),'bone_projection':projection}


def main():
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    scene,cam=scene_setup();human,rig,stats=setup_human();bpy.context.view_layer.update()
    baseline=evaluated_points(human);rest_lengths={b.name:b.length for b in rig.data.bones}
    reference_weights=[sum(vg.weight for vg in v.groups) for v in human.data.vertices]
    stats['normalized_weight_sum_range']=[min(reference_weights),max(reference_weights)]
    renders=[]
    for name,azimuth in [('front',0),('front_left',-45),('front_right',45),('side',90),('back',180)]:
        set_camera(cam,azimuth);renders.append(render(scene,cam,rig,'rest_'+name))
    # Explicitly authored skin stress test; no XYZ point interpolation, no scale keys.
    target=rig.pose.bones['lowerarm01.R'];target.rotation_mode='QUATERNION'
    for frame,degrees in [(1,0),(9,25),(17,50),(25,25),(33,0)]:
        target.rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(degrees))
        target.keyframe_insert('rotation_quaternion',frame=frame,group=target.name)
    scene.frame_start=1;scene.frame_end=33
    # Keep interpolation linear in quaternion channels then normalized by Blender;
    # the rig hierarchy and bone scales, not projected point lengths, drive mesh.
    for fc in rig.animation_data.action.fcurves:
        for kp in fc.keyframe_points:kp.interpolation='LINEAR'
    measurements=[];max_drift=0;max_displacement=0
    for frame in range(1,34):
        scene.frame_set(frame);bpy.context.view_layer.update()
        drift=max(abs(pb.length-rest_lengths[pb.name]) for pb in rig.pose.bones)
        points=evaluated_points(human);displacement=max((a-b).length for a,b in zip(points,baseline))
        max_drift=max(max_drift,drift);max_displacement=max(max_displacement,displacement)
        measurements.append({'frame':frame,'max_bone_length_error_m':drift,'max_skin_displacement_m':displacement,
                             'right_wrist_head':list(rig.pose.bones['wrist.R'].head)})
        if frame in [1,9,17,25,33]:
            set_camera(cam,-35);renders.append(render(scene,cam,rig,f'skin_bend_{frame:03}'))
    scene.frame_set(17);set_camera(cam,-35)
    hand=rig.pose.bones['wrist.R'].head;set_camera(cam,-35,10,target=hand,scale=.42)
    renders.append(render(scene,cam,rig,'right_hand_detail'))
    scene.frame_set(1);set_camera(cam,0)
    # Save the actual deforming rig, original mesh and authored action.
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'workflows/blender/public_human_baseline.blend'))
    errors=[]
    if max_drift>1e-5:errors.append('bone_length_changed')
    if max_displacement<.01:errors.append('mesh_did_not_deform')
    if stats['native_parent_links']!=162:errors.append('native_hierarchy_incomplete')
    if max(abs(v-1) for v in reference_weights)>1e-5:errors.append('weight_normalization_failed')
    report={'status':'technical_pass' if not errors else 'failed','scope':'native body mesh, parented native rig, normalized official weights, authored elbow skin stress test',
            'not_final_game_art':True,'human_art_approval':'pending','source':json.loads((SOURCE/'SOURCE.json').read_text()),
            'tool_version':bpy.app.version_string,'mesh_rig':stats,'max_bone_length_error_m':max_drift,
            'max_skin_displacement_m':max_displacement,'render_dimensions':[WIDTH,HEIGHT],
            'frames_measured':33,'errors':errors,'measurements':measurements,
            'limitations':['Native tpose/benchmark BVH are single poses and are not applied by this script.',
              'Authored elbow bend is a deformation diagnostic, not a licensed downloaded action or combat animation.',
              'Clay reference uses original neutral MakeHuman proportions; no stylization or warrior design approval.',
              'Only body faces retained; eye/teeth helper meshes excluded.','Roll aligned to native plane normals; full MakeHuman BVH rotation convention compatibility not proven.']}
    (REPORT/'baseline-qa.json').write_text(json.dumps(report,indent=2))
    (REPORT/'render-projections.json').write_text(json.dumps(renders,indent=2))
    print('PUBLIC_HUMAN_COMPLETE',json.dumps({k:report[k] for k in ['status','max_bone_length_error_m','max_skin_displacement_m','frames_measured','errors']}))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
