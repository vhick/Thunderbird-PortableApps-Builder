"""Get *genuine Thunderbird Release* Windows artwork from its upstream GitHub source.

Never ship a generic generated icon: a hard failure is preferred to misleading branding.
The selected GitHub file is authenticated by Git blob SHA-1 from the Contents API,
then pinned to the source commit (or a recorded, exact main commit if a release
source tag was unavailable). The original ICO is never redrawn or modified.

Usage: python scripts/prepare_icons.py [--verify-launcher]
"""
import argparse
import base64
import hashlib
import io
import json
import os
import pathlib
import re
import struct
import urllib.parse
import urllib.request

ICON_PATH='mail/branding/thunderbird/messengerWindow.ico'
REPO='thunderbird/thunderbird-desktop'
OUTPUT=pathlib.Path('work/icons')
SIZES=(16,32,75,128,256)


def github_api(path):
    url='https://api.github.com/repos/'+REPO+'/'+path
    req=urllib.request.Request(url,headers={
        'User-Agent':'ThunderbirdCommunityPortableBuilder/3.0',
        'Accept':'application/vnd.github+json',
        'X-GitHub-Api-Version':'2022-11-28'})
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:req.add_header('Authorization','Bearer '+token)
    with urllib.request.urlopen(req,timeout=35) as resp:
        raw=resp.read(1_500_001)
    if len(raw)>1_500_000:raise RuntimeError('GitHub returned oversized icon metadata')
    return json.loads(raw)


def gitblob_sha(contents):
    return hashlib.sha1(b'blob '+str(len(contents)).encode('ascii')+b'\x00'+contents).hexdigest()


def parse_ico(file_bytes):
    if len(file_bytes)<22:raise RuntimeError('Icon too small to be a genuine multi-size Windows ICO')
    reserved,kind,count=struct.unpack_from('<HHH',file_bytes,0)
    if (reserved,kind)!=(0,1) or count<2 or count>80:
        raise RuntimeError('Unexpected Thunderbird Windows ICO header')
    items=[]
    for i in range(count):
        pos=6+i*16
        if pos+16>len(file_bytes):raise RuntimeError('Truncated Windows ICO directory')
        width,height,colors,_,planes,bpp,length,offset=struct.unpack_from('<BBBBHHII',file_bytes,pos)
        width=width or 256
        height=height or 256
        if offset+length>len(file_bytes) or length<40:raise RuntimeError('Truncated ICO image resource')
        items.append({'width':width,'height':height,'bytes':file_bytes[offset:offset+length]})
    if not any(x['width']>=128 and x['height']>=128 for x in items):
        raise RuntimeError('Upstream icon lacks sufficiently high-resolution artwork')
    return items


def create_pngs(ico_bytes,out):
    from PIL import Image
    with Image.open(io.BytesIO(ico_bytes)) as icon:
        valid_sizes=sorted(icon.ico.sizes(),key=lambda size:(max(size),size[0]),reverse=True)
        if not valid_sizes or max(max(s) for s in valid_sizes)<128:
            raise RuntimeError('Thunderbird ICO lacks a high-res image')
        for size in SIZES:
            source_size=next((s for s in reversed(valid_sizes) if min(s)>=size),valid_sizes[0])
            artwork=icon.ico.getimage(source_size).convert('RGBA')
            if artwork.size!=(size,size):
                artwork=artwork.resize((size,size),Image.Resampling.LANCZOS)
            if not artwork.getbbox():raise RuntimeError('Blank icon at '+str(size))
            artwork.save(out/f'appicon_{size}.png',format='PNG',optimize=True)
    (out/'appicon.ico').write_bytes(ico_bytes)


def validate_compiled_launcher():
    original=(OUTPUT/'appicon.ico').read_bytes()
    candidates=[entry['bytes'] for entry in parse_ico(original) if len(entry['bytes'])>1000]
    executable=pathlib.Path('work/ThunderbirdCommunityPortable.exe')
    if not executable.is_file():raise RuntimeError('Native launcher EXE not present')
    data=executable.read_bytes()
    if data[:2]!=b'MZ':raise RuntimeError('Launcher lacks Windows PE DOS header')
    pe_offset=struct.unpack_from('<I',data,0x3c)[0]
    if data[pe_offset:pe_offset+4]!=b'PE\0\0':raise RuntimeError('Launcher lacks Windows PE header')
    if not any(resource in data for resource in candidates):
        raise RuntimeError('Compiled EXE does not embed any complete image resource from Thunderbird original ICO')
    print('PASS: native launcher PE contains authentic Thunderbird source-icon resource')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--verify-launcher',action='store_true')
    args=parser.parse_args()
    if args.verify_launcher:
        validate_compiled_launcher()
        return
    from PIL import Image  # after workflow installs pinned Pillow wheel
    meta=json.loads(pathlib.Path('work/source.json').read_text('utf-8'))
    source_commit=meta.get('release_source_commit')
    if source_commit and re.fullmatch('[a-fA-F0-9]{40}',source_commit):
        commit=source_commit.lower()
        origin='stable-release-source-tag'
    else:
        response=github_api('commits/main')
        commit=response.get('sha','').lower()
        if not re.fullmatch('[0-9a-f]{40}',commit):
            raise RuntimeError('Could not pin a real upstream main commit for icon retrieval')
        origin='pinned-main-fallback-release-source-tag-unresolved'
        print('WARNING: Thunderbird release source tag was unavailable; icon from pinned upstream main commit '+commit)
    details=github_api('contents/'+ICON_PATH+'?'+urllib.parse.urlencode({'ref':commit}))
    if details.get('type')!='file' or details.get('encoding')!='base64' or details.get('path')!=ICON_PATH:
        raise RuntimeError('Expected upstream messengerWindow.ico file contents from GitHub')
    contents=base64.b64decode(details['content'],validate=False)
    expected_sha=details.get('sha','').lower()
    if not re.fullmatch('[0-9a-f]{40}',expected_sha) or gitblob_sha(contents)!=expected_sha:
        raise RuntimeError('GitHub returned icon with a mismatched Git blob digest')
    if len(contents)>500_000:raise RuntimeError('Upstream ICO exceeds expected size')
    parse_ico(contents)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    create_pngs(contents,OUTPUT)
    sha256=hashlib.sha256(contents).hexdigest()
    provenance={'upstream_repository':'https://github.com/'+REPO,
        'source_path':ICON_PATH,'upstream_icon_commit':commit,
        'source_commit_selection':origin,'git_blob_sha1':expected_sha,
        'sha256':sha256,'build_note':'Icon belongs to Thunderbird. Trademark restrictions apply to public redistribution; no upstream endorsement.'}
    (OUTPUT/'THUNDERBIRD-ICON-PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    print('PASS: authentic Thunderbird icon fetched from source commit '+commit)
    print('Official source ICO SHA-256:',sha256)
    print('PNG sizes generated: '+', '.join(str(s) for s in SIZES))

if __name__=='__main__':main()
