# Thunderbird PortableApps Builder r4 — standard naming + authentic Thunderbird icons

**Application stage folder and ZIP root:** `ThunderbirdPortable/`  
**Compiled, genuine Windows launcher:** `ThunderbirdPortable.exe`  
**PortableApps metadata:** `App/AppInfo/appinfo.ini`, `[Control] Start=ThunderbirdPortable.exe`  
**Display name:** `Thunderbird Portable (Independent Build)` (distinguishes this from the separately maintained official PortableApps.com build)  
**Independent AppID:** `ThunderbirdPortable-vhick` (not the existing official ThunderbirdPortable AppID).  
**Package revision:** r4; `portable-v<VERSION>-r4` release tag.

## Important collision warning: official Thunderbird Portable is already called ThunderbirdPortable

The official PortableApps.com Thunderbird Portable package uses the exact same `ThunderbirdPortable` folder name requested here. **Never extract this community ZIP over an existing official Thunderbird Portable installation** or install its PAF over an existing official `ThunderbirdPortable` folder. Both editions may use different profile conventions. The independent NSIS fallback checks the existing AppID and refuses to overwrite an unrelated existing package. This source-level check does not guarantee the official PortableApps.com Installer can detect a separate unofficial package.

**Safe first installation:** use an empty, separate PortableApps Platform root (e.g. `T:\TestPortableApps\PortableApps\ThunderbirdPortable`) or ensure there is no `ThunderbirdPortable` directory in your intended PortableApps root. To migrate from previous r1–r3 builds using `ThunderbirdCommunityPortable`, keep that installation as an intact backup until r4 has passed first-launch, mail/profile, location-move, and upgrade acceptance checks. Don't simply rename or merge old packages; copy only a backed-up `Data` folder to an *empty, separate* r4 installation after closing Thunderbird completely, and then test with unimportant data first. Thunderbird profile database downgrades are not supported.

## Authentic icon policy

The build retrieves the original Thunderbird source-owned `mail/branding/thunderbird/messengerWindow.ico` from a pinned official upstream commit, verifies Git blob integrity, and records SHA-256 in `Other/Source/THUNDERBIRD-ICON-PROVENANCE.json`. The original icon (not generated placeholder artwork) becomes `App/AppInfo/appicon.ico` and the native EXE's compiled Windows icon resource. PortableApps-compliant PNGs are created at 16, 32, 75, 128, and 256 px, directly from the same verified Thunderbird artwork. Any icon download/verification/conversion or EXE embedding failure **stops** the build; there is no generic-icon fallback. Source: https://github.com/thunderbird/thunderbird-desktop/blob/main/mail/branding/thunderbird/messengerWindow.ico . The icon is Thunderbird's trademarked artwork; redistribution/branding permission must be checked separately.

## What the builder does

- Downloads Mozilla's official stable Windows 64-bit Thunderbird installer, verifies the SHA-256 listed by Mozilla, and extracts the contained application (does not run its setup wizard).
- Builds a native, inspectable C++ `ThunderbirdPortable.exe` that selects a portable profile under `Data/profile`, preserves persistent `Data` on updates, and redirects supported temporary paths.
- Produces one ready-to-extract PortableApps ZIP and tries to produce a PAF using the actual checksum-verified official PortableApps.com Installer 3.9.22, with bounded headless execution. If it fails and the user explicitly enables the option, it may produce a separately labeled **independent NSIS** `.paf.exe`-style installer. That is **not** an official PortableApps.com Installer output or certification. Otherwise the build can release just the verified ZIP.
- Checks all main filename/path references (stage, EXE, AppID, metadata, official and independent installers, ZIP and test paths) for consistent `ThunderbirdPortable` naming.
- Publishes via `vhick/portable-release-publisher@v1.1.1` once in dry-run, once to release; no generated binaries committed and no `upload-artifact` storage.
- No auto-created system startup, shell associations, services, hidden execution, registry clearing, or AV exclusions.

## GitHub Desktop update instructions (r3 → r4)

1. Download and extract `Thunderbird_PortableApps_Builder_Kit_r4_Standard_Naming.zip`.
2. Open the existing **builder repository** (not your installed Thunderbird data folder) in GitHub Desktop; choose **Repository → Show in Explorer**.
3. Copy the *contents* of this r4 kit (including hidden `.github`) into your builder repository. Replace matching source files. **Delete only the obsolete builder files** `launcher/ThunderbirdCommunityPortable.cpp` and `installer/ThunderbirdCommunityPortable.nsi` if they remain; these are source files, not user mail data. Do **not** delete `.git` or installed `Data` folders.
4. Return to GitHub Desktop, commit `Thunderbird r4 standard naming and original icon enforcement`, then **Push origin**.
5. In GitHub → Actions, run **Build Thunderbird Portable (Independent Build)**, using `version=latest`. A public builder requires `public_redistribution_ack=true` and an independent legal/branding review. A **private builder** is recommended for personal use.
6. Open **Releases** and get the r4 ZIP and, if available, the r4 PAF. Check the r4 Actions summary for the actual installer engine (official, independent, or ZIP only).
7. On a *separate test PortableApps root with no existing ThunderbirdPortable folder*, install the package via the Platform's **Apps → Install a New App** option for a PAF, or extract the ZIP directly into its `PortableApps` parent folder. Confirm `PortableApps\ThunderbirdPortable\ThunderbirdPortable.exe` exists (no double nesting).
8. Refresh/restart the PortableApps Menu. Launch and verify **Help → Troubleshooting Information → Profile Folder** points to `ThunderbirdPortable\Data\profile`. Follow `docs/MANUAL-ACCEPTANCE.md` before trusting the build with real mail.

**Existing r1–r3 packages do not become r4 automatically.** Keep original `ThunderbirdCommunityPortable\Data` backed up. Renaming existing installation folders without care can break stored absolute references.

## Tested vs untested

The source archive undergoes Python syntax, workflow YAML, static naming/publisher/icon checks and offline simulated stage/ZIP checks. No Windows/GitHub runner or real PortableApps Menu is available in the local packager environment. The full CI Windows launcher, original icon download, official PAF engine, Platform installation and upgrade tests must be verified in a real Actions/Windows run; no such success is implied here.

## Reference and support

- [PortableApps.com Format 3.9](https://portableapps.com/development/portableapps.com_format)
- [Official PortableApps.com Installer](https://portableapps.com/apps/development/portableapps.com_installer)
- [Thunderbird upstream](https://github.com/thunderbird/thunderbird-desktop)
- [Thunderbird official portable distribution](https://portableapps.com/apps/internet/thunderbird_portable)
- [Shared release publisher v1.1.1](https://github.com/vhick/portable-release-publisher/blob/v1.1.1/action.yml)
- [r7 reference builder](https://github.com/vhick/FreeCrawl-PortableApps-Builder)
- `docs/AUDIT.md` — codebase, profile, registry, upgrade and licensing notes
- `docs/MANUAL-ACCEPTANCE.md` — Windows install, Data-preserving upgrade, relocation and Menu checks
- `docs/R4-NAMING-ICON.md` — this revision's exact changes and acceptance requirements
- `docs/TROUBLESHOOTING.md` — build failure diagnosis
