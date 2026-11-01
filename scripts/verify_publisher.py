"""Fail early if shared publisher's real tag/action.yml contract differs."""
import json,re,urllib.request
base='https://api.github.com/repos/vhick/portable-release-publisher'
def read(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ThunderbirdPortableBuilder/1.0'}),timeout=30) as r:return r.read().decode('utf-8')
ref=json.loads(read(base+'/git/ref/tags/v1.1.1'))
assert re.fullmatch('[a-f0-9]{40}',ref['object']['sha']), 'Invalid v1.1.1 tag reference'
text=read('https://raw.githubusercontent.com/vhick/portable-release-publisher/v1.1.1/action.yml')
expected=('files','tag','release-title','tag-prefix','keep-releases','prune','dry-run')
for name in expected:
    if not re.search(r'(?m)^  '+re.escape(name)+r':\s*$',text):raise RuntimeError('Publisher action.yml lacks expected input '+name)
if '.paf.exe' not in text or '.zip' not in text:raise RuntimeError('Publisher does not declare ZIP and PAF support')
print('Verified publisher v1.1.1 tag object',ref['object']['sha'],'and action.yml inputs:',','.join(expected))
