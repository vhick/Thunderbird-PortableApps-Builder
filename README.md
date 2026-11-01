# r7 — Windows TraceGuard compilation repair

**r7 fixes the observed GitHub Actions r6 failure at Step 12 (C2668, C2296, C2297, C2660).**
The C++17 helper functions were renamed to `trace_exists` and `trace_is_directory` to avoid conflicting with `std::filesystem` through argument-dependent lookup. The three `Roaming`, `Local`, and `LocalLow` capture subpaths now start with explicit `std::filesystem::path` objects. No TraceGuard data-removal policy was relaxed.

The entire r6 workflow and official icon pipeline remain in place. r7 uses separate filenames and `portable-v<version>-r7` release tags. No successful Windows build or real Thunderbird runtime test is claimed until it has run.

# Thunderbird PortableApps Builder r7 — Stormhen Prevention + Safe TraceGuard (Standard Naming and Official Icons)

**Standard folder and launcher:** `ThunderbirdPortable/ThunderbirdPortable.exe`

**Original Thunderbird icon:** The builder fetches the authentic upstream `messengerWindow.ico` and embeds it in the EXE, PortableApps menu icons and installer (no generic icon fallback).

**r7 release tag:** `portable-v<VERSION>-r7` with distinct fallback suffixes. `vhick/portable-release-publisher@v1.1.1` is unchanged.

## Preserved from r6: Stormhen prevention coexisting with TraceGuard

The genuine compiled C++ portable launcher now performs a conservative before/after snapshot of known Thunderbird-related host folders. Only newly created, dedicated Thunderbird directories under `%APPDATA%`, `%LOCALAPPDATA%`, and `%USERPROFILE%/AppData/LocalLow` can be safely captured into `Data/TraceGuard/captured` when no other Thunderbird is running and Thunderbird exits normally. New, empty `%APPDATA%/Mozilla` and `%LOCALAPPDATA%/Mozilla` parent directories may be removed. Pre-existing folders, ProgramData, shared Mozilla and GnuPG directories remain protected and are reported rather than forcibly moved or deleted.

Thunderbird-local enterprise policies disable Windows Search integration and default-client prompts without editing the Windows registry. The launcher also sets `MOZ_MAINTENANCE_SERVICE=0`, `MOZ_UPDATER=0`, `MOZ_PLUGIN_PATH=Data/plugins`, and `MOZ_CRASHREPORTER_DISABLE=1` in its child environment. `TEMP` and `TMP` remain under `Data/temp`. Mozilla's supported crash reporter environment variables now point under `Data/CrashReports`. Every real launch generates an audit file under `Data/TraceGuard/logs/session-*.txt`, indicating `CAPTURED`, `KEEP`, `REMOVED`, or `NO TRACE` for each path.

**This is not a guarantee of zero Windows traces.** It does not intercept all filesystem or registry writes, and it never assumes existing host Thunderbird data belongs to your portable application. Review `docs/R6-TRACEGUARD-STORMHEN.md` for the full paths, restrictions, safety controls and user acceptance checklist.

## What the workflow produces

- `ThunderbirdPortable_<version>_r7_win64.zip`: ready-to-extract PortableApps package with the compiled `ThunderbirdPortable.exe` and authentic Thunderbird icons.
- `ThunderbirdPortable_<version>_r7_win64.paf.exe`: attempted with the real official PortableApps.com Installer, not a repackaged ZIP.
- If the official tool fails and the manual workflow option permits it: `ThunderbirdPortable_<version>_r7_win64_IndependentNSIS.paf.exe`, clearly identified as an **independent** NSIS package, not an official PortableApps.com Installer build/certification.
- If PAF generation cannot be validated, the checked ZIP can be published on a distinct `-ziponly` release tag.

The builder downloads Mozilla's stable, checksum-verified official Windows 64-bit Thunderbird binaries, extracts the application without running an installer, compiles the portable launcher using MSVC on a Windows GitHub runner, and builds both packages from the same staged application. No developer repository fork is needed. Source-level full Mozilla/Thunderbird application compilation is not done.

## Protect existing ThunderbirdPortable installations

The official PortableApps.com Thunderbird Portable **already uses** the `ThunderbirdPortable` folder name. This independent package has AppID `ThunderbirdPortable-vhick` and must NOT be installed over the existing official release. Use a **separate empty test PortableApps root**. Do not merge r1–r3 `ThunderbirdCommunityPortable` folders into this installation without a complete backup. Do not remove existing `Data` during updates. The independent NSIS package refuses unknown AppIDs; the official tool's collision behavior must be manually checked.

## Update the builder with GitHub Desktop

1. Download and extract `Thunderbird_PortableApps_Builder_Kit_r7_TraceGuard_Compile_Fix.zip`.
2. In **GitHub Desktop**, open your independent `Thunderbird-PortableApps-Builder` repository and select **Repository → Show in Explorer**.
3. Copy ALL r7 kit contents into the builder repository, including the hidden `.github` folder. Replace existing source files. Do not delete `.git` or any **installed** `ThunderbirdPortable/Data` directory.
4. In GitHub Desktop, commit `Thunderbird r7 TraceGuard MSVC compile fix` and **Push origin**.
5. In the GitHub repository, open **Actions → Build Thunderbird Portable (Independent Build)**. Choose **Run workflow**, leave `latest` unless a specific stable version is required, and run it. Use a private repository for personal testing; public redistribution requires a legal/trademark review and explicit workflow acknowledgement.
6. The workflow compiles and tests the TraceGuard fixture on Windows, compiles the real launcher, generates a ZIP and attempts an official-tool PAF, then validates before calling the Universal Release Publisher dry-run/publish actions.
7. Get the completed ZIP and, if available, the installer from the repository's **Releases** page. The action does not use `actions/upload-artifact` for finished packages.
8. In a separate PortableApps Platform test installation without another `ThunderbirdPortable` folder, use **Apps → Install a New App** to install a verified PAF. Or extract the ZIP into that test Platform's `PortableApps` folder. Refresh the menu.
9. Launch `ThunderbirdPortable.exe`, close Thunderbird normally, and read `Data/TraceGuard/logs/session-*.txt`. Confirm the profile is in `Data/profile`; verify that no existing host Thunderbird data moved.
10. Close Thunderbird and back up `Data`. Test updating to a newer r7 release without replacing the existing `Data` directory; confirm mail, calendar and account data remain present.

## Integrity tests

Local/offline: Python syntax checks, static source/metadata checks, original icon generator checks, GitHub Actions YAML parsing, and an isolated simulated ZIP packaging test. On Windows CI: `tests/traceguard_fixture.cpp` tests safe capture, installed-profile preservation, machine-wide ProgramData exclusions, and empty shared-parent cleanup; the launcher is compiled and Thunderbird is started in headless mode. **These Windows tests have not been executed here**, and no interactive PAF upgrade/PortableApps Menu test should be claimed successful until manually verified.

## Documentation

- `docs/R6-TRACEGUARD-STORMHEN.md` — exact paths and data-safety model.
- `docs/AUDIT.md` — application profile/runtime and Windows host limitations.
- `docs/MANUAL-ACCEPTANCE.md` — install, relocation and data-preserving upgrade acceptance.
- `docs/R1-FAILURE-ANALYSIS.md`, `docs/R3-ICON-FIX.md`, `docs/R4-NAMING-ICON.md` — historical fixes.
- `docs/TROUBLESHOOTING.md` — build and packaging errors.
- https://github.com/thunderbird/thunderbird-desktop — upstream source.
- https://github.com/desktop/desktop — unrelated GitHub Desktop reference; its folders are never Thunderbird cleanup targets.

**Legal:** Thunderbird and its icon are trademarked upstream artwork. A modified independently built portable distribution is not officially endorsed or certified by Mozilla/MZLA or PortableApps.com. Review rights before public publishing.

## r6 provenance and risk notes

The new reference is https://github.com/portapps/stormhen-portable (`main.go` on the master branch). The r6 launcher incorporates the *technique* of early environment setup and per-user `LocalLow` observation, not Stormhen binaries or its cleanup implementation. In Stormhen, `cleanup` is off by default; when enabled it calls `files.Cleanup` on entire `Thunderbird` directory trees. That approach is **not suitable** here because an installed Thunderbird profile could be present. Our TraceGuard continues to protect pre-existing paths, ProgramData, Mozilla shared data, symlinks, and uncertain shutdowns. Only empty shared-parent folders newly created in the session are eligible for removal.

Stormhen was renamed from a Thunderbird-branded package after a Mozilla trademark complaint. This independent builder's use of Thunderbird's original brand and icon is **not** a grant of trademark permission. Keep personal builds private unless you have independently reviewed the applicable branding terms.

Because the official PortableApps Thunderbird already owns the `ThunderbirdPortable` folder name, test the r7 build in a *separate Platform root*. Never overwrite an existing official `ThunderbirdPortable/Data`. New sessions cannot automatically identify and delete old r5 traces.
