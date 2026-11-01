"""Build a safe PortableApps stage and ready-to-extract ZIP from verified binaries."""
import configparser,hashlib,json,pathlib,shutil,zipfile
from xml.sax.saxutils import escape
ROOT=pathlib.Path('stage/ThunderbirdCommunityPortable')
meta=json.loads(pathlib.Path('work/source.json').read_text('utf-8'))
targets=json.loads(pathlib.Path('work/targets.json').read_text('utf-8'))
source=pathlib.Path('work/extracted')
# Mozilla 7-Zip SFX installer stores installation payload in core/, not the setup UI.
candidates=[p for p in source.rglob('thunderbird.exe') if p.parent.name.lower() in ('core','thunderbird')]
if len(candidates)!=1:raise RuntimeError(f'Expected one extracted core/thunderbird.exe, got: {candidates}')
core=candidates[0].parent
if core.name.lower()!='core':raise RuntimeError('Unexpected Thunderbird installer layout; do not package setup files')
if ROOT.exists():shutil.rmtree(ROOT)
app=ROOT/'App/Thunderbird';app.mkdir(parents=True)
for p in core.iterdir():
    d=app/p.name
    if p.is_dir():shutil.copytree(p,d)
    else:shutil.copy2(p,d)
# The setup executable is never executed; only its verified application payload is used.
if not (app/'thunderbird.exe').is_file() or not (app/'application.ini').is_file():
    raise RuntimeError('Extracted Thunderbird application is incomplete')
# Use Thunderbird's documented installation-local enterprise policy to prevent an
# extracted portable package from mutating App/ on its own or scheduling updates.
# Users update through a new, checksum-verified builder release; Data is retained.
policies_dir=app/'distribution'
policies_dir.mkdir(exist_ok=True)
policies_file=policies_dir/'policies.json'
if policies_file.exists():
    policy=json.loads(policies_file.read_text('utf-8'))
    if not isinstance(policy,dict) or not isinstance(policy.get('policies',{}),dict):
        raise RuntimeError('Unknown upstream policies.json format; refuse to overwrite')
else:
    policy={'policies':{}}
policy['policies']['DisableAppUpdate']=True
policies_file.write_text(json.dumps(policy,indent=2)+'\n',encoding='utf-8')
launcher=pathlib.Path('work/ThunderbirdCommunityPortable.exe')
if not launcher.is_file():raise RuntimeError('Compiled portable launcher missing')
shutil.copy2(launcher,ROOT/launcher.name)
info=ROOT/'App/AppInfo';info.mkdir(parents=True)
for filename in ['appicon.ico','appicon_16.png','appicon_32.png','appicon_75.png','appicon_128.png','appicon_256.png']:
    shutil.copy2(pathlib.Path('assets')/filename,info/filename)
version_bits=(meta['version'].split('.')+['0']*4)[:4]
version_bits[-1]='1'  # revision 1: required 4-part PortableApps package version
package_version='.'.join(version_bits)
ini=f'''[Format]
Type=PortableApps.comFormat
Version=3.9

[Details]
Name=Thunderbird Community Portable
AppID=ThunderbirdCommunityPortable-vhick
BaseAppName=Thunderbird
Publisher=MZLA Technologies Corporation (Thunderbird) & independent community wrapper
Category=Internet
Description=Independent portable build of the Thunderbird email client
Language=English
Trademarks=Thunderbird is a registered trademark of the Mozilla Foundation

[License]
Shareable=true
OpenSource=true
Freeware=true
CommercialUse=true

[Version]
PackageVersion={package_version}
DisplayVersion={meta['version']} Community r1

[Dependencies]
Requires64bitOS=true
RequiresAdmin=false

[Control]
Icons=1
Start=ThunderbirdCommunityPortable.exe
'''
(info/'appinfo.ini').write_text(ini,encoding='utf-8',newline='\r\n')
(info/'installer.ini').write_text('[MainDirectories]\nRemoveDataDirectory=false\n',encoding='utf-8',newline='\r\n')
(ROOT/'Data/profile').mkdir(parents=True)
(ROOT/'Data/temp').mkdir()
(ROOT/'Data/settings').mkdir()
# No import or overwrite of existing host profiles.
other=ROOT/'Other/Source';other.mkdir(parents=True)
shutil.copy2('LICENSE-LAUNCHER.txt',other/'LICENSE-LAUNCHER.txt')
shutil.copy2('launcher/ThunderbirdCommunityPortable.cpp',other/'ThunderbirdCommunityPortable.cpp')
shutil.copy2('launcher/launcher.rc',other/'launcher.rc')
(other/'PROVENANCE.txt').write_text(f'''Unmodified official Thunderbird program files, extracted from Mozilla's checksum-verified Windows installer.
Version: {meta['version']}
Source repository: {meta['upstream_repository']}
Release source tag: {meta['source_tag']}
Release source commit: {meta['release_source_commit'] or 'not independently verified'}
Official installer: {meta['binary_url']}
SHA-256: {meta['binary_sha256']}
Wrapper: independently developed MIT-licensed native launcher; not an endorsed Thunderbird or PortableApps.com release.
Trademark and MPL rights: https://updates.thunderbird.net/en-US/thunderbird/about/rights/
''',encoding='utf-8')
# Do not include self-updating / obsolete installation metadata from source setup.
path=pathlib.Path('dist');path.mkdir(exist_ok=True)
zip_path=path/targets['zip']
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(ROOT.parent).as_posix())
    for d in [ROOT/'Data/profile',ROOT/'Data/temp',ROOT/'Data/settings']:
        z.writestr(d.relative_to(ROOT.parent).as_posix()+'/',b'')
print('Staged',ROOT,'files',len(list(ROOT.rglob('*'))),'ZIP',zip_path,zip_path.stat().st_size)
