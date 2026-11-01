# r3 original Thunderbird icon repair

## Root cause
r2 shipped generic artwork in `assets/appicon.ico` and `assets/appicon_*.png`, embedded into the launcher by `launcher/launcher.rc` and copied into the PortableApps Platform icon directory by `scripts/package.py`.

## Original upstream icon
The Thunderbird source repository has its actual Windows release icon at `mail/branding/thunderbird/messengerWindow.ico`.
- Repository: https://github.com/thunderbird/thunderbird-desktop
- Source file: https://github.com/thunderbird/thunderbird-desktop/blob/main/mail/branding/thunderbird/messengerWindow.ico
- Brand details: https://source-docs.thunderbird.net/en/latest/build/index.html
- Format 3.9 icons: https://portableapps.com/development/portableapps.com_format

The Actions job retrieves this file from an exact commit using GitHub's Contents API, verifies Git object integrity and records its SHA-256. If the stable release tag is unavailable, it pins the exact main commit instead of silently using an unversioned URL. Download or verification failure is fatal; generic icon files can no longer leak into release outputs.

## Icon paths in delivered application
- `ThunderbirdPortable/ThunderbirdPortable.exe`: official icon embedded in compiled launcher resource.
- `ThunderbirdPortable/App/AppInfo/appicon.ico`: original upstream ICO bytes.
- `ThunderbirdPortable/App/AppInfo/appicon_16.png`, `_32.png`, `_75.png`, `_128.png`, `_256.png`: converted from original ICO.
- `ThunderbirdPortable/Other/Source/THUNDERBIRD-ICON-PROVENANCE.json`: source commit and checksum audit trail.
- PAF EXE installer: installer branding uses `App/AppInfo/appicon.ico`, both official and independent fallback paths.

## Tests and limitations
- A local offline test checks conversion from a synthetic ICO, the image sizes, parsing and checksum algorithms. It is *not* the real Thunderbird downloaded icon.
- The Windows Actions run retrieves the real artwork, recompiles the launcher and verifies an image resource matches before shipping.
- A static launcher resource test does not prove the Windows shell immediately refreshes previously cached menu icons. After updating to r3, refresh/restart the Platform Menu or Windows Explorer if the old icon remains displayed.
- Trademark/redistribution restrictions still apply. Public distribution requires independently checking current permissions.
