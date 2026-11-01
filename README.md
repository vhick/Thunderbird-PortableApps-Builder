# Thunderbird Community PortableApps Builder r3 — Original Thunderbird Icon Fix

An **independent, no-fork** GitHub Actions builder for the latest stable 64-bit Thunderbird Windows release. It downloads and checks Mozilla's original Windows installer, extracts the official app without running a setup wizard, compiles a genuine C++ portable launcher and publishes verified release packages through `vhick/portable-release-publisher@v1.1.1`.

**This is not an official Thunderbird, PortableApps.com, or Mozilla release.** For fully supported PortableApps.com distribution, use [Thunderbird, Portable Edition](https://portableapps.com/apps/internet/thunderbird_portable). The project-specific source audit and licensing discussion are in `docs/AUDIT.md`.

## r3: original Thunderbird icon now replaces generic artwork

r2 embedded a generic, programmatically generated icon in both the C++ launcher and `App/AppInfo` menu files. r3 changes the **build pipeline**, not just the README or pre-made PNGs:

1. `scripts/prepare_icons.py` downloads Thunderbird's **real release branding icon** from `thunderbird/thunderbird-desktop`, path `mail/branding/thunderbird/messengerWindow.ico`. A resolved official release source commit is preferred. If that tag is not available, the script pins the exact upstream `main` commit at build time and marks this fallback in the included provenance record.
2. The downloaded original ICO must have a valid multi-size icon header, at least one 128px or larger frame, and a verified Git blob checksum (compared against GitHub's reported file blob SHA-1). The script also records SHA-256 and upstream source commit in `Other/Source/THUNDERBIRD-ICON-PROVENANCE.json`.
3. A pinned `Pillow==11.3.0` package creates exact-size `appicon_16.png`, `appicon_32.png`, `appicon_75.png`, `appicon_128.png` and `appicon_256.png` from original icon frames. The original `appicon.ico` is copied **unchanged** from official source. Old `assets/` placeholder graphics have been removed from the builder entirely.
4. `launcher/launcher.rc` embeds the same verified original Thunderbird ICO in the genuine compiled `ThunderbirdCommunityPortable.exe`. CI checks the native EXE contains an actual icon resource from that file and blocks publishing if it does not.
5. `scripts/package.py` copies those exact checked icon files into `App/AppInfo`. ZIP/PAF packaging includes the same source artwork; stage validation compares every icon against the downloaded original, and confirms the icon provenance is packaged.
6. New r3 release tags and filenames prevent overwriting existing r2 releases. The launcher runtime, profile handling, official PAF path and independent installer fallback retain their r2 behavior.

**Trademark notice:** The Thunderbird icon is Thunderbird's own artwork and may be subject to Thunderbird/Mozilla trademark restrictions. This community builder is not endorsed by Thunderbird, Mozilla or PortableApps.com. Keep the project private for personal use unless you have reviewed the applicable redistribution and branding conditions. The existing public-distribution acknowledgement requirement remains.

This icon update requires a new Actions build; it cannot retroactively change an existing r2 ZIP or PAF. Windows can cache icons: refresh/restart the PortableApps menu after upgrading.

## r2: earlier PAF stall and fallback changes (retained in r3)

The November 1, 2026 logs show the Thunderbird download, checksum verification, application extraction, C++ launcher compilation, headless startup check, ZIP packaging and ZIP validation succeeding. The official `PortableApps.comInstaller.exe` was extracted from the SHA-256-verified PortableApps.com Installer 3.9.22 distribution but failed to finish when called with the prepared app directory. The subprocess timed out after **480 seconds**. That is consistent with a prompt or stalled vendor packager; the log does not prove which. The r1 PowerShell fallback branch also inherited the nonzero exit code and failed before the shared release publisher could run.

The retained r2 corrections are:

1. Supplies a proper `Homepage` in `App/AppInfo/appinfo.ini` and checks required metadata before invoking the official packager. A missing homepage was an actual metadata gap, but cannot conclusively be called the source of the timeout.
2. Keeps the verified official headless tool acquisition and SHA-256 pin. Shortens official compiler wait to a **bounded 210 seconds**; after a timeout/failure it also checks controlled output locations for a newly created, genuinely intact vendor-built PAF.
3. The optional vendor-packaging step now **always exits successfully after selecting a verified fallback**, rather than accidentally terminating the overall workflow. A failed application download, checksum, launcher compilation, runtime smoke check or ZIP validation still fails the build.
4. Adds an **explicit, readable independent NSIS fallback** with its own source in `installer/ThunderbirdCommunityPortable.nsi`, distinct release name and engine provenance. It creates a genuine interactive Windows installer with a `.paf.exe` suffix and a PortableApps-style file layout, but it is **NOT the unmodified PortableApps.com Installer nor certified for PortableApps Platform**. Its actual installation/upgrade and Platform UI behavior remain subject to real Windows manual testing.
5. If both installer routes fail (or the independent fallback is disabled), publishes the independently verified EXE-based PortableApps ZIP under a clearly named `-ziponly` release tag. A failed optional installer must never stop valid ZIP publishing.
6. Uses a separate builder revision for release tags so prior releases cannot be overwritten or misidentified.

## Release outputs

| Engine used | GitHub release tag | Packages |
| --- | --- | --- |
| Verified original official PortableApps.com Installer 3.9.22 | `portable-v<VERSION>-r3` | `ThunderbirdCommunityPortable_<VERSION>_r3_win64.zip` and `ThunderbirdCommunityPortable_<VERSION>_r3_win64.paf.exe` |
| Independent, explicitly labeled NSIS fallback | `portable-v<VERSION>-r3-independent-nsis` | same ZIP plus `ThunderbirdCommunityPortable_<VERSION>_r3_win64_IndependentNSIS.paf.exe` |
| ZIP-only | `portable-v<VERSION>-r3-ziponly` | the verified ZIP only |

The GitHub Actions run summary declares which engine was selected. Independent `.paf.exe` is *not* official-tool-generated, even though it is a real NSIS installer executable. Do not claim PortableApps.com certification or confirmed Menu installation without manually testing it.

## Replace your existing builder using GitHub Desktop

1. Download and extract the **r3 builder kit ZIP** outside your existing GitHub Desktop repository.
2. Exit any prior builder scripts. In **GitHub Desktop**, select your existing `Thunderbird-PortableApps-Builder` repository.
3. Choose **Repository → Show in Explorer**. Copy the *contents* of the extracted r3 kit into this existing repository folder, allowing replacement of r2 files. Include the `.github` folder. The old r2 `assets` folder contains only unused generic icons and can be deleted from the builder repository. **Do not copy or replace `.git`, and do not create a new repository or fork Thunderbird.**
4. Check GitHub Desktop's Changes tab. Confirm that files such as `.github/workflows/build-portableapps.yml`, `scripts/build_paf.py`, `scripts/build_independent_nsis.py`, `scripts/package.py`, `installer/ThunderbirdCommunityPortable.nsi` and `README.md` have changed or been added.
5. Enter the commit summary `Use original Thunderbird artwork in PortableApps - r3`, click **Commit to main**, then **Push origin**.
6. Open your repository on GitHub, go to **Actions → Build Thunderbird Community Portable (official PAF, independent fallback, ZIP) → Run workflow**.
7. Keep **version** as `latest`. Leave **allow_independent_nsis_fallback** enabled if you are willing to test an independently built NSIS installer when the official compiler stalls. Disable it if you want only an official-tool PAF or the verified ZIP. The separate **public redistribution acknowledgement** is required for public repositories; private repositories normally leave it off.
8. Select **Run workflow**. Open the run summary and check `Final packaging engine: official`, `independent`, or `ziponly`.
9. Open your repository's **Releases** and download the ZIP or installer matching that exact engine/tag. The publisher runs once as a dry-run and then once for actual release publishing; it does not use completed-package Actions artifacts.

## Installing and upgrading

**ZIP:** Extract to the *existing* PortableApps directory, such that `X:\PortableApps\ThunderbirdCommunityPortable\ThunderbirdCommunityPortable.exe` is the actual executable path. Refresh the PortableApps Platform Menu. To upgrade, keep existing `ThunderbirdCommunityPortable\Data` unchanged: replace only the root launcher, `App`, and `Other` contents. Do not delete the whole existing app directory.

**Official-tool PAF:** When produced, use PortableApps Platform **Apps → Install a New App**. It should install a sibling `ThunderbirdCommunityPortable` folder. Install first to a disposable test PortableApps directory, not over real mail data.

**Independent NSIS `.paf.exe`:** This is a normal visible installer wizard and not official-tool-generated. If the Platform does not recognize it, run the installer directly, choose the **parent PortableApps directory** in its folder-selection page, and test the resulting Menu entry. The NSIS installer never intentionally deletes or replaces `Data`; its actual installation and upgrade behavior still needs interactive verification.

**Important:** Neither package imports an installed profile automatically. Thunderbird's profile should be inside `ThunderbirdCommunityPortable\Data\profile`. Do not replace the separately maintained official `ThunderbirdPortable` directory. Before each update, close Thunderbird fully and back up the entire `Data` folder. See `docs/MANUAL-ACCEPTANCE.md`.

## Implementation details

- Official Thunderbird input: Mozilla `LATEST_THUNDERBIRD_VERSION` and exact Mozilla `SHA256SUMS` for the Windows 64-bit English release installer. No fork or upstream repository modification. The source release tag/commit is recorded when resolvable.
- Native `ThunderbirdCommunityPortable.exe` is built in Windows CI via MSVC, not a CMD-to-EXE wrapper. Runs `App\Thunderbird\thunderbird.exe -no-remote -profile Data\profile`, with data and temporary files inside the portable directory where supported.
- App updates are controlled with Thunderbird's documented `DisableAppUpdate` enterprise policy; verified releases replace `App`, not `Data`.
- The original official PortableApps.com Installer 3.9.22 is obtained from a pinned SHA-256 verified SourceForge distribution, unpacked using 7-Zip without running its graphical installer, then invoked with the documented app directory argument. No mandatory headless installation UI test is run.
- Independent NSIS fallback compiles from readable `.nsi` code using `makensis`. When NSIS isn't on the runner, the script uses Chocolatey to acquire it with an explicit timeout. It never passes off that compiler as the official PortableApps.com Installer.
- The same staged application feeds all formats, with no duplicate Thunderbird compilation. Signed official Thunderbird binaries are reused unchanged; the new independent launcher/installer may be unsigned.
- ZIP and PAF validation checks the PE headers, package structure and archive integrity. Extracted PAF binaries and `appinfo.ini` are compared byte-for-byte to the validated stage. This **does not** prove installation or Menu compatibility.
- Release tags are immutable and checked for existing/conflicting assets, retaining the last three only if an operator separately opts into pruning. Default is `prune: false`. Public/private release visibility follows the builder repository. `GITHUB_TOKEN` has `contents: write`, without a PAT.

## Reference links

- https://github.com/thunderbird/thunderbird-desktop
- https://portableapps.com/development/portableapps.com_format
- https://portableapps.com/apps/development/portableapps.com_installer
- https://github.com/vhick/FreeCrawl-PortableApps-Builder
- https://github.com/vhick/portable-release-publisher/blob/v1.1.1/action.yml

## Validation boundaries

The r3 ZIP builder source and icon conversion logic were checked offline on Linux with synthetic test artwork; real Thunderbird and Windows installer compilation, actual PAF installation, a second-location launch, data preservation and live GitHub Releases publishing must be verified in your next GitHub Actions/Windows tests. An error on the mandatory ZIP path continues to block publishing rather than being treated as a fallback.
