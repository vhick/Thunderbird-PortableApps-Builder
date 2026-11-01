"""Headless official PortableApps Installer build. No NSIS fallback is mislabeled official."""
import configparser,hashlib,json,os,pathlib,re,shutil,subprocess,time,urllib.request,sys

VERSION='3.9.22'
# Reconfirmed from public, successful FreeCrawl r7 builder's SourceForge release verification.
# Reverify with the authentic SourceForge published checksum if this version is changed.
SHA256='689456f1fb1320c45e82a077afe6b87fb388fd3f75c41d9ee9ce8d45f3966b67'
NAME=f'PortableApps.comInstaller_{VERSION}.paf.exe'
TARGETS=json.loads(pathlib.Path('work/targets.json').read_text('utf-8'))
stage=pathlib.Path('stage/ThunderbirdCommunityPortable').resolve()
dist=pathlib.Path('dist').resolve()
toolhome=pathlib.Path(os.environ.get('RUNNER_TEMP','work'))/'tb-community-tool'
toolhome.mkdir(parents=True,exist_ok=True)
download=toolhome/NAME
seven=shutil.which('7z') or r'C:\Program Files\7-Zip\7z.exe'
if not pathlib.Path(seven).is_file() and not shutil.which('7z'):
    raise RuntimeError('Cannot locate 7z.exe on GitHub Windows runner')

def run(argv,timeout,cwd=None):
    print('RUN:',[str(v) for v in argv],flush=True)
    proc=subprocess.Popen([str(v) for v in argv],cwd=cwd,text=True,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        out,err=proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        # Kill only the specific tool's process tree, not unrelated Windows applications.
        # This prevents a stalled GUI packager/child compressor from consuming CI minutes.
        if os.name=='nt':
            try:
                subprocess.run(['taskkill.exe','/PID',str(proc.pid),'/T','/F'],
                               capture_output=True,text=True,timeout=20,check=False)
            except (OSError,subprocess.SubprocessError):pass
        if proc.poll() is None:proc.kill()
        try:proc.communicate(timeout=15)
        except subprocess.SubprocessError:pass
        raise subprocess.TimeoutExpired([str(v) for v in argv],timeout)
    result=subprocess.CompletedProcess([str(v) for v in argv],proc.returncode,out,err)
    if proc.returncode:
        print('FAILED TOOL STDOUT:',out[-2500:],flush=True)
        print('FAILED TOOL STDERR:',err[-2500:],flush=True)
        raise subprocess.CalledProcessError(proc.returncode,[str(v) for v in argv],out,err)
    return result

urls=[f'https://{mirror}/project/portableapps/PortableApps.com%20Installer/{NAME}' for mirror in ['netix.dl.sourceforge.net','cfhcable.dl.sourceforge.net','pilotfiber.dl.sourceforge.net','gigenet.dl.sourceforge.net','downloads.sourceforge.net']]
valid=False
for url in urls:
    print('Getting vendor tool from',url)
    try:
        h=hashlib.sha256();length=0
        req=urllib.request.Request(url,headers={'User-Agent':'ThunderbirdCommunityPortableBuilder/1.0'})
        with urllib.request.urlopen(req,timeout=45) as source,download.open('wb') as dest:
            while block:=source.read(1024*1024):
                length+=len(block)
                if length>30_000_000:raise RuntimeError('Unusually large tool distribution')
                h.update(block);dest.write(block)
        if 1_000_000<=length<=30_000_000 and h.hexdigest()==SHA256 and download.read_bytes()[:2]==b'MZ':
            valid=True;break
        print('Tool rejected: incorrect length or published SHA-256',length,h.hexdigest())
    except Exception as exc:print('Vendor mirror failed:',type(exc).__name__,str(exc)[:300])
if not valid:raise RuntimeError('No trusted SourceForge mirror supplied checksum-verified official PortableApps.com Installer '+VERSION)

extract=toolhome/'extracted'
if extract.exists():shutil.rmtree(extract)
extract.mkdir()
r=run([seven,'x',download,f'-o{extract}','-y','-bd'],120)
print(r.stdout[-1000:])
programs=list(extract.rglob('PortableApps.comInstaller.exe'))
if len(programs)!=1:raise RuntimeError('Expected one extracted official PortableApps.comInstaller.exe; found '+str([str(x) for x in programs]))
builder=programs[0]
if builder.stat().st_size<10_000 or builder.open('rb').read(2)!=b'MZ':raise RuntimeError('Invalid extracted vendor compiler')
# Fail immediately on metadata gaps that can cause an interactive vendor prompt.
config=configparser.ConfigParser(interpolation=None)
config.read(stage/'App/AppInfo/appinfo.ini',encoding='utf-8')
for section,keys in {'Details':['Name','AppID','Publisher','Homepage','Category','Description','Language'],
                     'Version':['PackageVersion','DisplayVersion'],'Control':['Start','Icons']}.items():
    for key in keys:
        if not config.has_option(section,key) or not config.get(section,key).strip():
            raise RuntimeError(f'Missing official-tool appinfo.ini metadata: [{section}] {key}')
started=time.time()-2
compiler_problem=None
try:
    result=run([builder,stage],210,cwd=builder.parent)
    print('Official compiler stdout:',result.stdout[-4000:])
    print('Official compiler stderr:',result.stderr[-3000:])
except (subprocess.SubprocessError,OSError) as exc:
    compiler_problem=repr(exc)
    print('Official compiler did not finish; checking for a genuinely completed archive:',compiler_problem,flush=True)
    for log in (stage/'App/AppInfo').glob('*installer*log*'):
        print('OFFICIAL LOG:',log.read_text(errors='replace')[-5000:])
# Search only scoped directories created or used by the packager.
# A successful, fully verified archive can exist even when a vendor GUI remains open.
roots=[stage.parent,dist,builder.parent,pathlib.Path.cwd(),pathlib.Path.cwd().parent]
found={}
for root in roots:
    for p in root.glob('*.paf.exe'):
        if p.resolve()!=download.resolve() and p.stat().st_mtime>=started:
            found[str(p.resolve())]=p.resolve()
valid=[]
for p in found.values():
    try:
        if p.stat().st_size<150_000:continue
        run([seven,'t',p],120)
        with p.open('rb') as f:
            if f.read(2)!=b'MZ':continue
        out=run([seven,'l','-slt',p],90).stdout.lower().replace('\\','/')
        for item in ('thunderbirdcommunityportable.exe','appinfo.ini','thunderbird.exe'):
            if item not in out:raise RuntimeError('Missing PAF component '+item)
        valid.append(p)
    except (subprocess.SubprocessError,RuntimeError) as ex:print('Rejected candidate:',p,str(ex)[:200])
if len(valid)!=1:
    print('Official PAF not produced/verified. Candidates:',list(map(str,found.values())),'Compiler:',compiler_problem,flush=True)
    sys.exit(2)
output=dist/TARGETS['paf']
if output.exists():output.unlink()
shutil.copy2(valid[0],output)
(dist/'installer-engine.txt').write_text(f'official PortableApps.com Installer {VERSION}',encoding='utf-8')
(dist/'installer-tool-provenance.txt').write_text(f'Vendor tool: official PortableApps.com Installer {VERSION}\nOfficial SourceForge SHA-256: {SHA256}\nCompiled from: {stage}\nVendor program: {builder}\nNot certified/endorsed by PortableApps.com.\n',encoding='utf-8')
print('Produced official-tool generated PAF:',output,output.stat().st_size)
