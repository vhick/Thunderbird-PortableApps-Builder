"""Explicit independent NSIS fallback: NOT the official PortableApps.com Installer."""
import hashlib,json,os,pathlib,shutil,subprocess,sys

ROOT=pathlib.Path.cwd().resolve()
stage=(ROOT/'stage/ThunderbirdCommunityPortable').resolve()
targets=json.loads((ROOT/'work/targets.json').read_text(encoding='utf-8'))
output=(ROOT/'dist'/targets['paf_independent']).resolve()
output.parent.mkdir(parents=True,exist_ok=True)
if not (stage/'ThunderbirdCommunityPortable.exe').is_file():
    raise RuntimeError('Verified staged EXE missing; no independent installer generated')

candidates=[pathlib.Path(x) for x in (
    r'C:\Program Files (x86)\NSIS\makensis.exe',r'C:\Program Files\NSIS\makensis.exe',
)]
which=shutil.which('makensis.exe') or shutil.which('makensis')
if which:candidates.insert(0,pathlib.Path(which))
makensis=next((p for p in candidates if p.is_file()),None)
if makensis is None:
    choco=shutil.which('choco.exe')
    if not choco:raise RuntimeError('NSIS compiler missing and Chocolatey unavailable')
    print('Installing the regular NSIS compiler through the Windows runner Chocolatey package',flush=True)
    subprocess.run([choco,'install','nsis','--yes','--no-progress','--limit-output'],check=True,timeout=240)
    makensis=next((p for p in candidates if p.is_file()),None)
if not makensis:raise RuntimeError('makensis.exe absent after dependency acquisition')
with makensis.open('rb') as f:
    if f.read(2)!=b'MZ':raise RuntimeError('Invalid NSIS compiler executable')
if output.exists():output.unlink()
argv=[str(makensis),'/V3',f'/DSTAGE_DIR={stage}',f'/DOUTPUT_FILE={output}',
      str(ROOT/'installer/ThunderbirdCommunityPortable.nsi')]
print('Independent NSIS compilation:',argv[0],flush=True)
try:
    result=subprocess.run(argv,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=480)
except subprocess.TimeoutExpired as exc:
    raise RuntimeError('Independent NSIS compilation exceeded 480 seconds') from exc
print(result.stdout[-6000:],flush=True)
if result.returncode!=0:raise RuntimeError('Independent NSIS compiler failed: '+str(result.returncode))
if not output.is_file() or output.stat().st_size<200_000:
    raise RuntimeError('Independent NSIS did not create an installer')
with output.open('rb') as f:
    if f.read(2)!=b'MZ':raise RuntimeError('Independent installer is not a Windows executable')
(ROOT/'dist/installer-engine.txt').write_text('independent NSIS (not official PortableApps.com Installer)',encoding='utf-8')
(ROOT/'dist/installer-tool-provenance.txt').write_text(
    f'Engine: independently built NSIS; NOT PortableApps.com Installer.\nCompiler: {makensis}\n'
    'This is a PortableApps-style .paf.exe package with appinfo.ini; not certified or endorsed.\n'
    'No GUI installation, upgrade or Menu discovery has been tested by this script.\n',encoding='utf-8')
print('Created independently labeled PAF-style installer:',output,output.stat().st_size,flush=True)
