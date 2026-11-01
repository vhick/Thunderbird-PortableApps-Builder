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
launcher=(root/'launcher/ThunderbirdCommunityPortable.cpp').read_text('utf-8')
assert 'CreateProcessW' in launcher and ' -profile ' in launcher and 'Data' in launcher
assert 'AppData' not in launcher and 'RegSetValue' not in launcher
assert 'DisableAppUpdate' in (root/'scripts/package.py').read_text('utf-8')
assert (root/'scripts/compile-launcher.cmd').is_file()
assert (root/'installer/ThunderbirdCommunityPortable.nsi').is_file()
assert (root/'scripts/build_independent_nsis.py').is_file()
assert 'Homepage={homepage}' in (root/'scripts/package.py').read_text('utf-8')
for name in ['appicon.ico','appicon_16.png','appicon_32.png','appicon_75.png','appicon_128.png','appicon_256.png']:
    assert (root/'assets'/name).is_file()
for name in ['resolve.py','download.py','extract_thunderbird.py','build_paf.py','validate.py','package.py','verify_publisher.py','confirm_release.py','check_existing.py']:
    assert (root/'scripts'/name).is_file()
print('PASS: static builder inventory, launcher behavior references, icons and publisher integration')
