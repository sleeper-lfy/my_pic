"""Read a saved native rig and validate its actual evaluated actions and socket."""
from pathlib import Path
import json
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]

def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'workflows/blender/warrior_motion.blend'))
    rig=bpy.data.objects['MakeHuman_Rig'];weapon=bpy.data.objects['WeaponSocket'];scene=bpy.context.scene
    body=bpy.data.objects['MakeHuman_Body'];socket=Matrix([list(row) for row in weapon['socket_matrix']])
    sums=[sum(g.weight for g in v.groups) for v in body.data.vertices]
    report={'actions':{},'parent':weapon.parent.name,'parent_type':weapon.parent_type,'parent_bone':weapon.parent_bone,'weight_sum_range':[min(sums),max(sums)],'unweighted_vertices':sum(v<=0 for v in sums),'sample_count':0}
    feet={n:rig.data.bones[n].head_local.copy() for n in ['foot.L','foot.R']};errors=[]
    for clip in ['idle','attack','defense']:
        action=bpy.data.actions.get('Warrior_'+clip)
        if action is None:errors.append('missing_'+clip);continue
        rig.animation_data.action=action
        entry={'range':list(action.frame_range),'curves':len(action.fcurves),'max_socket_matrix_error':0,'max_foot_movement':0,'max_bone_length_error':0,'scale_channels':[],'negative_quaternion_dots':[]}
        previous=None
        frames=sorted({int(k.co.x) for fc in action.fcurves for k in fc.keyframe_points})
        for frame in range(int(action.frame_range[0]),int(action.frame_range[1])+1):
            scene.frame_set(frame);bpy.context.view_layer.update();expected=rig.matrix_world@rig.pose.bones['wrist.R'].matrix@socket
            entry['max_socket_matrix_error']=max(entry['max_socket_matrix_error'],max(abs(weapon.matrix_world[i][j]-expected[i][j]) for i in range(4) for j in range(4)))
            entry['max_foot_movement']=max(entry['max_foot_movement'],max((rig.pose.bones[n].head-p).length for n,p in feet.items()))
            entry['max_bone_length_error']=max(entry['max_bone_length_error'],max(abs(b.length-rig.data.bones[b.name].length) for b in rig.pose.bones))
            report['sample_count']+=1
            if frame in frames:
                current={p.name:p.rotation_quaternion.copy() for p in rig.pose.bones}
                if previous:
                    entry['negative_quaternion_dots'].extend({'frame':frame,'bone':n,'dot':q.dot(previous[n])} for n,q in current.items() if q.dot(previous[n])<0)
                previous=current
        entry['scale_channels']=[fc.data_path for fc in action.fcurves if 'scale' in fc.data_path]
        if entry['negative_quaternion_dots']:errors.append(clip+'_rotation_hemisphere')
        if entry['scale_channels']:errors.append(clip+'_scale_animation')
        for key,limit in [('max_socket_matrix_error',1e-4),('max_foot_movement',1e-5),('max_bone_length_error',1e-5)]:
            if entry[key]>limit:errors.append(clip+'_'+key)
        report['actions'][clip]=entry
    if report['unweighted_vertices'] or max(abs(min(sums)-1),abs(max(sums)-1))>1e-5:errors.append('native_weight_sums')
    report['status']='technical_pass' if not errors else 'failed';report['errors']=errors
    report['limitations']=['Native Blender timing uses 24fps quantized source frames; painted sprite milliseconds are authored separately.','Palm wrapping quality is visual and not proven by zero socket drift.','This validates structural guide animation, not painted-frame identity or art approval.']
    report['corrected_issue']='Equivalent rotation quaternions use the same hemisphere before interpolation; key poses unchanged.'
    path=ROOT/'reports/warrior_motion/native-rig-audit.json';path.write_text(json.dumps(report,indent=2))
    print('WARRIOR_NATIVE_AUDIT',report['status'],report['sample_count'],errors)
    if errors:raise RuntimeError('Native rig audit failed')
if __name__=='__main__':main()
