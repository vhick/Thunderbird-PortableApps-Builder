import argparse,json,os,pathlib,subprocess
ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=["full","independent","ziponly"],default="full");mode=ap.parse_args().mode
names=json.loads(pathlib.Path('work/targets.json').read_text('utf-8'))
tag=names['tag']+('-ziponly' if mode=='ziponly' else '-independent-nsis' if mode=='independent' else '')
p=subprocess.run(['gh','api',f'repos/{os.environ["GITHUB_REPOSITORY"]}/releases/tags/{tag}'],capture_output=True,text=True,timeout=45,check=True)
assets={a['name'] for a in json.loads(p.stdout)['assets']}
missing=({names['zip'],names['paf' if mode=='full' else 'paf_independent']} if mode!='ziponly' else {names['zip']})-assets
if missing:raise RuntimeError('Publisher returned, but these release assets are missing: '+str(missing))
print('GitHub release assets confirmed:',tag,sorted(assets))
