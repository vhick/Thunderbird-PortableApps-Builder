"""Bounded, non-GUI archive verification and extraction of a SHA-256-checked Mozilla installer."""
import pathlib,shutil,subprocess

exe=pathlib.Path('work/thunderbird-installer.exe')
if not exe.is_file():raise RuntimeError('Verified Mozilla Windows installer has not been downloaded')
seven=shutil.which('7z') or r'C:\Program Files\7-Zip\7z.exe'
if not pathlib.Path(seven).is_file() and not shutil.which('7z'):
    raise RuntimeError('7z.exe not found on the Windows runner')

def run(*argv,timeout):
    print('Archive operation:',argv[0], 'timeout:',timeout,flush=True)
    try:
        p=subprocess.run([str(x) for x in argv],capture_output=True,text=True,timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f'Thunderbird installer archive command timed out after {timeout}s') from exc
    if p.returncode:
        raise RuntimeError('Mozilla installer archive failed: '+p.stdout[-1500:]+p.stderr[-1500:])
    print(p.stdout[-400:],flush=True)

run(seven,'t',exe,timeout=180)
out=pathlib.Path('work/extracted')
if out.exists():shutil.rmtree(out)
out.mkdir(parents=True)
run(seven,'x',exe,f'-o{out}','-y','-bd',timeout=240)
cores=[p for p in out.rglob('thunderbird.exe') if p.parent.name.lower()=='core']
if len(cores)!=1 or not (cores[0].parent/'application.ini').is_file():
    raise RuntimeError('Mozilla installer payload layout changed; no single core/thunderbird.exe + application.ini found')
print('PASS: Thunderbird program extracted without ever running its setup GUI')
