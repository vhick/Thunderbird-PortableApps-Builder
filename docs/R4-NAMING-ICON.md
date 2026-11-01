# Thunderbird r4 — canonical names and original artwork

Directory: `ThunderbirdPortable/`
EXE: `ThunderbirdPortable.exe`
Menu display name: `Thunderbird Portable (Independent Build)`
Unique AppID: `ThunderbirdPortable-vhick`
ZIP: `ThunderbirdPortable_<VERSION>_r4_win64.zip`
Official-tool PAF: `ThunderbirdPortable_<VERSION>_r4_win64.paf.exe`
Independent NSIS: `ThunderbirdPortable_<VERSION>_r4_win64_IndependentNSIS.paf.exe`
Release tag: `portable-v<VERSION>-r4` (with separate fallback suffix).

All icon formats are generated from upstream Thunderbird's original `mail/branding/thunderbird/messengerWindow.ico`, pinned to a verified source commit, with a SHA-256 provenance record. A launcher EXE missing the embedded authentic ICO fails the workflow. The launcher and both installer engines use the staged `App/AppInfo/appicon.ico`. This does not confer trademark authorization for public redistribution.

## Existing official Thunderbird Portable COLLISION

This requested canonical `ThunderbirdPortable` root is also used by PortableApps.com's existing official Thunderbird release. The third-party package is not an update for that official release and can have different profile formats. Never overwrite it. Test on an empty, separate PortableApps root. NSIS fallback installer rejects unknown/existing official metadata. The official-tool packaging engine has not been proven to reject replacing a different existing package, so keep the test root separate.

## Migrating r3 without losing mail data

1. Quit Thunderbird fully. Backup your entire r3 `ThunderbirdCommunityPortable` directory.
2. Install r4 to a **new** separate PortableApps directory that does not contain `ThunderbirdPortable`.
3. Confirm new launcher starts and profile location is `Data/profile`. Exit.
4. With Thunderbird closed, copy the backed-up r3 `Data` directory into the empty r4 app directory, with a second independent copy retained. Don't merge over an existing filled profile.
5. Start r4; verify messages, accounts, address book, calendars and extensions. Check any old absolute paths. If this fails, use the untouched r3 backup instead.
6. Test move/upgrade before using important data; never downgrade a live profile.

**Testing:** Static code and synthetic icon validation are available locally. Real Windows Menu detection, PAF install/upgrade and actual original icon resource embedding are checked by Actions and manual acceptance, not guaranteed by this source revision.
