"""Small experiment CLI. No automatic art approval, generation or model downloads."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT/'reports/build-state.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(paths, context=''):
    # Include paths as well as contents, avoiding ambiguous concatenation.
    values=[(str(Path(p)), digest(p)) for p in sorted(paths,key=str)]
    return hashlib.sha256(json.dumps([values,context],sort_keys=True).encode()).hexdigest()


def cache_valid(entry, key, root=ROOT):
    return bool(entry and entry.get('input_hash')==key and entry.get('outputs') and
                all((root/path).is_file() and digest(root/path)==sha for path,sha in entry['outputs'].items()))


def execute(command):
    print('+', ' '.join(str(x) for x in command),flush=True)
    if Path(command[0]).name.lower().startswith('blender'):
        script=Path(command[command.index('--python')+1]).stem if '--python' in command else 'blender'
        log=ROOT/'reports'/script/'cli-blender.log';log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('w',encoding='utf-8') as stream:
            subprocess.run([str(x) for x in command],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
        print('Blender completed; log:',log.relative_to(ROOT));return
    subprocess.run([str(x) for x in command],cwd=ROOT,check=True)


def version_context():
    import PIL
    import numpy
    return f'python={sys.version};Pillow={PIL.__version__};numpy={numpy.__version__}'


def cached(name, inputs, outputs, command, state, force=False, context=''):
    key=fingerprint(inputs,context)
    if not force and cache_valid(state.get(name),key):
        print('REUSED',name); return False
    execute(command)
    files=outputs()
    if not files or not all(p.is_file() for p in files):
        raise RuntimeError('Incomplete outputs for '+name)
    state[name]={'input_hash':key,'outputs':{str(p.relative_to(ROOT)):digest(p) for p in files}}
    STATE.write_text(json.dumps(state,indent=2),encoding='utf-8')
    print('BUILT',name); return True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,default=ROOT/'profiles/tower_defense.yaml')
    sub=parser.add_subparsers(dest='command',required=True)
    d=sub.add_parser('doctor');d.add_argument('--output',type=Path,default=ROOT/'reports/environment-local.json')
    d.add_argument('--comfy-url',default='http://127.0.0.1:8188')
    s=sub.add_parser('structure');s.add_argument('--force',action='store_true')
    s.add_argument('--legacy-diagnostic',action='store_true',help='Explicitly rerun the rejected primitive reference experiment, for regression only')
    e=sub.add_parser('experiment');e.add_argument('--route',choices=['A','B','C','all'],default='all')
    e.add_argument('--weapon',choices=['hammer_a','hammer_b','all'],default='all');e.add_argument('--force',action='store_true')
    e.add_argument('--legacy-diagnostic',action='store_true',help='Explicitly rerun the rejected 2D interpolation experiments, for regression only')
    r=sub.add_parser('reference-baseline',help='Import licensed public anatomy/skin/native-motion references without generating art')
    r.add_argument('--kind',choices=['anatomy','motion','all'],default='all')
    sub.add_parser('review');sub.add_parser('test');sub.add_parser('godot-check')
    args=parser.parse_args()
    if args.command in ['structure','experiment'] and not args.legacy_diagnostic:
        raise RuntimeError('Legacy human-form baseline was rejected. Use reference-baseline first; --legacy-diagnostic is for reproducing old failures only.')
    if args.command=='reference-baseline':
        exe=shutil.which('blender')
        if not exe:raise RuntimeError('Blender unavailable; run doctor')
        targets={'anatomy':'public_human_baseline.py','motion':'public_motion_probe.py'}
        for kind,filename in targets.items():
            if args.kind not in [kind,'all']:continue
            script=ROOT/'workflows/blender'/filename
            if not script.is_file():raise RuntimeError('Reference importer unavailable: '+filename)
            execute([exe,'--background','--factory-startup','--threads','2','--python',script]);
            review=ROOT/'workflows/blender'/('public_human_review.py' if kind=='anatomy' else 'public_motion_review.py')
            if not review.is_file():raise RuntimeError('Reference review step unavailable: '+str(review))
            execute([sys.executable,review])
        print('Public reference import complete; see reports/public_human and reports/public_motion. This is not game-art approval.');return
    if args.command=='doctor':
        execute([sys.executable,ROOT/'scripts/doctor.py','--output',args.output,'--comfy-url',args.comfy_url]); return
    if args.command=='test':
        execute([sys.executable,'-m','unittest','discover','-s','tests','-v']);return
    if args.command=='review':
        execute([sys.executable,ROOT/'scripts/review.py']);return
    if args.command=='godot-check':
        exe=shutil.which('godot') or shutil.which('godot4')
        if not exe:raise RuntimeError('Godot is not available; run doctor and supply a local installation')
        runtime=os.environ.copy()
        if os.name!='nt':
            for name,subdir in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
                path=ROOT/'.cache/godot'/subdir;path.mkdir(parents=True,exist_ok=True);runtime[name]=str(path)
        command=[exe,'--headless','--path',str(ROOT/'workflows/godot'),'--quit-after','10']
        result=subprocess.run(command,cwd=ROOT,env=runtime,capture_output=True,text=True,timeout=45)
        combined=result.stdout+'\n'+result.stderr
        (ROOT/'reports/godot-check.log').write_text(combined,encoding='utf-8')
        marker='ART_FACTORY_SCENE_READY clips=4 frames=52 dimensions=256x256; art=UNAPPROVED'
        if result.returncode!=0 or marker not in combined or 'SCRIPT ERROR' in combined:
            raise RuntimeError('Godot validation failed; see reports/godot-check.log')
        print(marker);return
    import yaml
    profile=yaml.safe_load(args.profile.read_text(encoding='utf-8'))
    if profile.get('profile_id')!='tower_defense' or profile.get('export',{}).get('width')!=256 or profile.get('export',{}).get('height')!=256:
        raise ValueError('This experiment currently supports the versioned 256px tower_defense profile only')
    # Production is deliberately not implemented behind a misleading approval toggle.
    state=json.loads(STATE.read_text()) if STATE.exists() else {}
    py=sys.executable; context=version_context()
    if args.command=='structure':
        exe=shutil.which('blender')
        if not exe:raise RuntimeError('Blender unavailable; run doctor')
        version=subprocess.check_output([exe,'--version'],text=True).splitlines()[0]
        cached('structure',[ROOT/'workflows/blender/structure_probe.py',args.profile],
               lambda:list((ROOT/'previews/structure').rglob('attack_*.png'))+[ROOT/'reports/structure/projection.json',ROOT/'workflows/blender/structure_probe.blend'],
               [exe,'--background','--threads','2','--python',ROOT/'workflows/blender/structure_probe.py'],state,args.force,version)
        execute([py,ROOT/'workflows/blender/summarize_probe.py']);return
    if args.route in ['A','all']:
        cached('route_A',[ROOT/'scripts/route_a.py',ROOT/'scripts/quality.py',ROOT/'assets/characters/route_a/joint-keyposes-v001.png',args.profile],
               lambda:list((ROOT/'exports/route_a').glob('*'))+list((ROOT/'previews/route_a').glob('*'))+[ROOT/'reports/route-a-qa.json'],
               [py,ROOT/'scripts/route_a.py'],state,args.force,context)
    for route in ['B','C']:
        if args.route not in [route,'all']:continue
        for weapon in ['hammer_a','hammer_b']:
            if args.weapon not in [weapon,'all']:continue
            source=ROOT/'assets/weapons'/f'{weapon}.png'
            if not source.exists():
                raise RuntimeError('Missing editable weapon source; explicitly run parts_experiment.py once to extract, never substitute a placeholder')
            inputs=[ROOT/'scripts/parts_experiment.py',ROOT/'scripts/quality.py',ROOT/'assets/characters/warrior-parts-v001.png',source,args.profile]
            if route=='C':inputs.append(ROOT/'reports/structure/projection.json')
            clip=f'{route}_{weapon}'
            cached(clip,inputs,
                   lambda clip=clip:list((ROOT/'exports/parts_experiment'/clip).glob('*'))+[ROOT/'previews/parts_experiment'/f'{clip}.webp',ROOT/'previews/parts_experiment'/f'{clip}-contact.png'],
                   [py,ROOT/'scripts/parts_experiment.py','--route',route,'--weapon',weapon],state,args.force,context)
    print('Experiment build complete. Technical success does not constitute art acceptance.')


if __name__=='__main__':
    try:main()
    except (RuntimeError,ValueError,OSError,subprocess.CalledProcessError) as exc:
        print('ERROR:',exc,file=sys.stderr);sys.exit(1)
