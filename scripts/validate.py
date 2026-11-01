import argparse,configparser,hashlib,json,pathlib,struct,subprocess,zipfile,shutil,os
p=argparse.ArgumentParser();p.add_argument('--paf',action='store_true');p.add_argument('--independent',action='store_true');args=p.parse_args()
root=pathlib.Path('stage/ThunderbirdPortable');targets=json.loads(pathlib.Path('work/targets.json').read_text('utf-8'))

def pe(path):
    f=pathlib.Path(path)
    with f.open('rb') as handle:
        h=handle.read(64)
        assert len(h)==64 and h[:2]==b'MZ',f'Missing MZ: {f}'
        offset=struct.unpack_from('<I',h,0x3c)[0]
        assert 64<=offset<1048576
        handle.seek(offset)
        assert handle.read(4)==b'PE\0\0',f'Missing PE header: {f}'

pe(root/'ThunderbirdPortable.exe');pe(root/'App/Thunderbird/thunderbird.exe')
ini=configparser.ConfigParser(interpolation=None);ini.read(root/'App/AppInfo/appinfo.ini',encoding='utf-8')
assert ini['Format']['Version']=='3.9'
assert ini['Control']['Start']=='ThunderbirdPortable.exe'
assert ini['Details']['AppID']=='ThunderbirdPortable-vhick'
assert not list((root/'Data/profile').iterdir()),'Do not ship an existing Thunderbird user profile'
assert (root/'App/AppInfo/appicon.ico').is_file()
# All exported menu icons must be the exact files validated against Thunderbird's
# source icon. A file named appicon is not by itself proof of correct branding.
from pathlib import Path
from PIL import Image
icon_home=Path('work/icons')
icon_provenance=json.loads((icon_home/'THUNDERBIRD-ICON-PROVENANCE.json').read_text('utf-8'))
assert icon_provenance['source_path']=='mail/branding/thunderbird/messengerWindow.ico'
assert hashlib.sha256((icon_home/'appicon.ico').read_bytes()).hexdigest()==icon_provenance['sha256']
for sz in (16,32,75,128,256):
    name=f'appicon_{sz}.png'
    assert (root/'App/AppInfo'/name).read_bytes()==(icon_home/name).read_bytes()
    with Image.open(root/'App/AppInfo'/name) as img:
        assert img.size==(sz,sz) and img.getbbox(),f'Invalid PNG {name}'
assert (root/'App/AppInfo/appicon.ico').read_bytes()==(icon_home/'appicon.ico').read_bytes()
assert (root/'Other/Source/THUNDERBIRD-ICON-PROVENANCE.json').read_bytes()==(icon_home/'THUNDERBIRD-ICON-PROVENANCE.json').read_bytes()
assert json.loads((root/'App/Thunderbird/distribution/policies.json').read_text('utf-8'))['policies']['DisableAppUpdate'] is True
zipname=pathlib.Path('dist')/targets['zip']
with zipfile.ZipFile(zipname) as z:
    assert z.testzip() is None
    names=set(z.namelist())
    assert 'stage/ThunderbirdPortable/ThunderbirdPortable.exe' in names or 'ThunderbirdPortable/ThunderbirdPortable.exe' in names
    # ZIP must NOT carry stage/ prefix: this is also independently checked below.
    assert all(not n.startswith('stage/') for n in names),'ZIP has an unwanted stage/ parent folder'
    assert 'ThunderbirdPortable/App/AppInfo/appinfo.ini' in names
    assert 'ThunderbirdPortable/Data/profile/' in names
    assert 'ThunderbirdPortable/App/Thunderbird/thunderbird.exe' in names
if args.paf:
    paf=pathlib.Path('dist')/targets['paf_independent' if args.independent else 'paf'];pe(paf)
    seven='7z'
    t=subprocess.run([seven,'t',str(paf)],timeout=150,capture_output=True,text=True)
    if t.returncode:raise RuntimeError('PAF 7-Zip integrity failed: '+t.stdout[-1000:]+t.stderr[-1000:])
    l=subprocess.run([seven,'l','-slt',str(paf)],timeout=120,capture_output=True,text=True,check=True)
    listing=l.stdout.lower().replace('\\','/')
    for required in ['thunderbirdportable.exe','appinfo.ini','thunderbird.exe']:
        if required not in listing:raise RuntimeError('PAF payload missing '+required)
    # Extract the NSIS payload ONLY for archive verification. Never run installer UI.
    inspection=pathlib.Path('work/paf-inspection')
    if inspection.exists():shutil.rmtree(inspection)
    inspection.mkdir(parents=True)
    subprocess.run([seven,'x',str(paf),f'-o{inspection}','-y','-bd'],timeout=240,capture_output=True,text=True,check=True)
    for filename, original in [
        ('thunderbirdportable.exe',root/'ThunderbirdPortable.exe'),
        ('thunderbird.exe',root/'App/Thunderbird/thunderbird.exe'),
        ('appinfo.ini',root/'App/AppInfo/appinfo.ini'),
    ]:
        matches=[p for p in inspection.rglob('*') if p.is_file() and p.name.lower()==filename]
        if len(matches)!=1:raise RuntimeError('PAF extracted expected exactly one '+filename+', found '+str(matches[:5]))
        def digest(path):
            with pathlib.Path(path).open('rb') as f:
                h=hashlib.sha256()
                for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
                return h.digest()
        if digest(matches[0])!=digest(original):raise RuntimeError('Official PAF embedded file differs from the exact staged file: '+filename)
    print('Verified extracted PAF payload byte-for-byte matches staged launcher, Thunderbird binary and metadata')
    engine=pathlib.Path('dist/installer-engine.txt').read_text('utf-8').strip()
    assert engine==('independent NSIS (not official PortableApps.com Installer)' if args.independent else 'official PortableApps.com Installer 3.9.22'),engine
    print('PAF: valid PE and 7z archive integrity, exact staged payload, explicitly recorded engine; NOT GUI-install tested')
print('Static stage/ZIP validation passed, Windows PE headers verified; no GUI claim')
