"""Resolve official Thunderbird stable version and Mozilla-hosted Windows package checksum.
No GitHub release assumption: the thunderbird-desktop GitHub repo does not publish GitHub Releases.
"""
import argparse, hashlib, json, os, pathlib, re, urllib.request, urllib.error
from urllib.parse import quote

GITHUB = 'https://api.github.com/repos/thunderbird/thunderbird-desktop'
VERSIONS = 'https://product-details.mozilla.org/1.0/thunderbird_versions.json'
HOST = 'https://releases.mozilla.org/pub/thunderbird/releases'

def get(url, limit=3_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': 'ThunderbirdPortableBuilder/1.0','Accept': 'application/vnd.github+json' if 'api.github.com' in url else '*/*'})
    with urllib.request.urlopen(req, timeout=30) as r:
        blob=r.read(limit+1)
    if len(blob)>limit: raise RuntimeError('Oversized metadata response: '+url)
    return blob

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='latest');a=ap.parse_args()
    version=(json.loads(get(VERSIONS))['LATEST_THUNDERBIRD_VERSION'] if a.version=='latest' else a.version)
    if not re.fullmatch(r'\d+(?:\.\d+){1,3}',version):raise RuntimeError('Not a stable version: '+version)
    path=f'win64/en-US/Thunderbird Setup {version}.exe'
    checksums=get(f'{HOST}/{version}/SHA256SUMS',2_000_000).decode('utf-8')
    exact=[line.split(maxsplit=1)[0].lower() for line in checksums.splitlines() if line.split(maxsplit=1)[1:] and line.split(maxsplit=1)[1].lstrip('*')==path]
    if len(exact)!=1 or not re.fullmatch(r'[0-9a-f]{64}',exact[0]):raise RuntimeError('Missing/unexpected official checksum for '+path)
    encoded_path='/'.join(quote(p,safe='') for p in path.split('/'))
    # Query release's matching source tag; avoid representing an arbitrary HEAD as its commit.
    tag='THUNDERBIRD_'+version.replace('.','_')+'_RELEASE'
    source_commit=None
    try:
        ref=json.loads(get(f'{GITHUB}/git/ref/tags/{tag}'))
        obj=ref['object']
        if obj['type']=='tag':obj=json.loads(get(obj['url']))['object']
        if obj['type']=='commit':source_commit=obj['sha']
    except (urllib.error.HTTPError,KeyError,ValueError) as exc:
        print('Release-specific Git source tag not resolvable; recording this explicitly:',exc)
    # Upstream repository is documented and retained, but its HEAD is never confused with release source.
    data={
      'version':version,'product_channel':'stable-release','upstream_repository':'https://github.com/thunderbird/thunderbird-desktop',
      'source_tag':tag,'release_source_commit':source_commit,
      'source_note':'Release tag resolved' if source_commit else 'Source release commit not verified; official checksummed binary is the distribution input',
      'binary_url':f'{HOST}/{version}/{encoded_path}','binary_relative_path':path,'binary_sha256':exact[0],
      'checksums_url':f'{HOST}/{version}/SHA256SUMS',
    }
    pathlib.Path('work').mkdir(exist_ok=True)
    pathlib.Path('work/source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    tag_name=f'portable-v{version}-r7'
    targets={'tag':tag_name,'zip':f'ThunderbirdPortable_{version}_r7_win64.zip','paf':f'ThunderbirdPortable_{version}_r7_win64.paf.exe','paf_independent':f'ThunderbirdPortable_{version}_r7_win64_IndependentNSIS.paf.exe'}
    pathlib.Path('work/targets.json').write_text(json.dumps(targets,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data,indent=2))
    with open(os.environ.get('GITHUB_OUTPUT',os.devnull),'a',encoding='utf-8') as o:
        for k,v in targets.items():o.write(k+'='+v+'\n')

if __name__=='__main__': main()
