"""Stream the official signed Mozilla installer and verify its SHA-256 prior to extraction."""
import hashlib,json,pathlib,urllib.request
meta=json.loads(pathlib.Path('work/source.json').read_text(encoding='utf-8'))
target=pathlib.Path('work/thunderbird-installer.exe')
request=urllib.request.Request(meta['binary_url'],headers={'User-Agent':'ThunderbirdCommunityPortableBuilder/1.0'})
sha=hashlib.sha256()
with urllib.request.urlopen(request,timeout=90) as source, target.open('wb') as dest:
    length=0
    while chunk:=source.read(1024*1024):
        dest.write(chunk);sha.update(chunk);length+=len(chunk)
        if length>800_000_000:raise RuntimeError('Installer unusually large; refusing download')
if length<5_000_000 or sha.hexdigest()!=meta['binary_sha256']:
    target.unlink(missing_ok=True)
    raise RuntimeError('Mozilla installer checksum or size does not match official SHA256SUMS')
with target.open('rb') as f:
    if f.read(2)!=b'MZ':raise RuntimeError('The verified installer is not Windows PE')
print('Verified Mozilla stable installer: ',meta['version'], 'bytes:',length,'sha256:',sha.hexdigest())
