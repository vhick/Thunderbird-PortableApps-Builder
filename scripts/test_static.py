"""Offline sanity checks (no Windows tools or Mozilla download required)."""
from pathlib import Path
import re
root=Path(__file__).resolve().parent.parent
wf=(root/'.github/workflows/build-portableapps.yml').read_text('utf-8')
assert 'workflow_dispatch:' in wf
assert 'windows-2022' in wf
assert wf.count('uses: vhick/portable-release-publisher@v1.1.1')==2
assert 'dry-run: \'true\'' in wf and 'dry-run: \'false\'' in wf
assert 'actions/upload-artifact' not in wf
launcher=(root/'launcher/ThunderbirdPortable.cpp').read_text('utf-8')
assert 'CreateProcessW' in launcher and ' -profile ' in launcher and 'Data' in launcher
assert 'RegSetValue' not in launcher
assert 'traceguard::Session' in launcher
assert 'MOZ_CRASHREPORTER_DATA_DIRECTORY' in launcher
assert (root/'launcher/TraceGuard.h').is_file()
assert 'CAPTURED' in (root/'launcher/TraceGuard.h').read_text('utf-8')
assert (root/'tests/traceguard_fixture.cpp').is_file()
assert 'test_traceguard.ps1' in wf
assert 'DisableAppUpdate' in (root/'scripts/package.py').read_text('utf-8')
assert (root/'scripts/compile-launcher.cmd').is_file()
assert (root/'installer/ThunderbirdPortable.nsi').is_file()
assert (root/'scripts/build_independent_nsis.py').is_file()
assert 'work/icons' in (root/'scripts/package.py').read_text('utf-8')
assert r'work\\icons\\appicon.ico' in (root/'launcher/launcher.rc').read_text('utf-8')
assert 'Homepage={homepage}' in (root/'scripts/package.py').read_text('utf-8')
assert (root/'scripts/prepare_icons.py').is_file() and (root/'scripts/test_icons.py').is_file()
assert 'prepare_icons.py --verify-launcher' in wf
assert 'python scripts/prepare_icons.py' in wf
for name in ['resolve.py','download.py','extract_thunderbird.py','build_paf.py','validate.py','package.py','verify_publisher.py','confirm_release.py','check_existing.py']:
    assert (root/'scripts'/name).is_file()
print('PASS: static builder inventory, launcher behavior references, upstream Thunderbird icons and publisher integration')

# Canonical naming regression checks. Must pass before downloads/compilation.
from pathlib import Path
import ast
source=(root/'scripts/resolve.py').read_text('utf-8')
assert "ThunderbirdPortable_" in source and "-r6" in source
assert "ThunderbirdPortable" in (root/'scripts/package.py').read_text('utf-8')
assert "Start=ThunderbirdPortable.exe" in (root/'scripts/package.py').read_text('utf-8')
assert "AppID=ThunderbirdPortable-vhick" in (root/'scripts/package.py').read_text('utf-8')
for sourcefile in [root/'launcher/ThunderbirdPortable.cpp',root/'scripts/build_launcher.ps1',root/'scripts/compile-launcher.cmd',root/'scripts/smoke.ps1',root/'scripts/build_paf.py',root/'scripts/validate.py',root/'scripts/prepare_icons.py',root/'scripts/build_independent_nsis.py',root/'installer/ThunderbirdPortable.nsi']:
    assert sourcefile.exists(), sourcefile
    assert 'ThunderbirdCommunityPortable' not in sourcefile.read_text('utf-8'), sourcefile
nsis=(root/'installer/ThunderbirdPortable.nsi').read_text('utf-8')
assert 'ReadINIStr $R3' in nsis and 'AppID' in nsis and 'ThunderbirdPortable-vhick' in nsis
assert 'ThunderbirdPortable.exe' in nsis
assert 'mail/branding/thunderbird/messengerWindow.ico' in (root/'scripts/prepare_icons.py').read_text('utf-8')
assert 'appicon_256.png' in (root/'scripts/package.py').read_text('utf-8')
assert 'assets/appicon.ico' not in (root/'scripts/package.py').read_text('utf-8')
print('PASS: r6 canonical ThunderbirdPortable stage/EXE/AppID/installer names and official artwork')

# r6: Stormhen-derived prevention and safe LocalLow coexistence.
assert 'roots.localLow/L"Thunderbird"' in (root/'launcher/TraceGuard.h').read_text('utf-8')
assert 'MOZ_MAINTENANCE_SERVICE' in launcher and 'MOZ_UPDATER' in launcher
assert 'MOZ_PLUGIN_PATH' in launcher and 'MOZ_CRASHREPORTER_DISABLE' in launcher
assert 'mail.winsearch.enable' in (root/'scripts/package.py').read_text('utf-8')
assert 'mail.shell.checkDefaultClient' in (root/'scripts/package.py').read_text('utf-8')
assert 'Data/plugins' in (root/'scripts/package.py').read_text('utf-8')
print('PASS: r6 Stormhen prevention alongside TraceGuard, LocalLow coverage and policy safeguards')
