"""Safely avoid rebuilding an already published exact version/revision asset set."""
import argparse,json,os,pathlib,subprocess,sys
ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=["full","independent","ziponly"],default="full");mode=ap.parse_args().mode
names=json.loads(pathlib.Path('work/targets.json').read_text('utf-8'))
repo=os.environ.get('GITHUB_REPOSITORY')
if not repo:raise RuntimeError('GITHUB_REPOSITORY not provided')
tag=names["tag"]+("-ziponly" if mode=="ziponly" else "-independent-nsis" if mode=="independent" else "")
ref=f'repos/{repo}/releases/tags/{tag}'
p=subprocess.run(['gh','api',ref],capture_output=True,text=True,timeout=45)
if p.returncode:
    if '404' not in p.stderr and 'Not Found' not in p.stderr:raise RuntimeError('Cannot inspect existing release: '+p.stderr[-1000:])
    print('Release tag unused. Build can proceed.');sys.exit(0)
release=json.loads(p.stdout)
assets={a['name'] for a in release['assets']}
required={names['zip'],names['paf' if mode=='full' else 'paf_independent']} if mode!='ziponly' else {names['zip']}
if required.issubset(assets):
    print('The expected package names are already published. Skipping to protect immutable release. Verify asset checksums separately for byte identity.')
    with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf-8') as output:output.write('skip=true\n')
else:
    raise RuntimeError('Release tag exists with incomplete/conflicting asset set. Increase builder revision instead of overwriting: '+str(assets))
