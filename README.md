# Thunderbird Community Portable Builder r1

An independent **no-fork** GitHub Actions builder for an EXE-based PortableApps-style package of official Windows x64 Thunderbird Release binaries.

**Important:** There is already an officially maintained [Thunderbird, Portable Edition](https://portableapps.com/apps/internet/thunderbird_portable). Use that for fully supported PortableApps Platform updates and authorized branding. This independent project is useful for personal experiments and independent release automation; **it is not an official Thunderbird or PortableApps.com product, certified installer, or approved trademark use.**

## What the builder does

1. Reads the official Mozilla Thunderbird stable version from the [Mozilla product-details feed](https://product-details.mozilla.org/1.0/thunderbird_versions.json), and the corresponding official release checksum list. Records the upstream Git repository and matching source tag/commit when available; never treats GitHub's `main` as the release commit.
2. Downloads **only** the Mozilla-hosted official Windows installer for that stable version, checks its exact SHA-256 against `SHA256SUMS`, and **extracts** its application binaries with 7-Zip. It never launches the Mozilla Windows setup wizard.
3. Uses MSVC on `windows-2022` to compile the real `ThunderbirdCommunityPortable.exe` from original, readable C++ code, embedding an original generic envelope icon. The executable starts the official Thunderbird program with `-no-remote -profile <portable>\Data\profile`.
4. Packages `ThunderbirdCommunityPortable` with `App`, `Data`, `Other`, PortableApps Format 3.9 `appinfo.ini`, original app binaries, attribution and source. Builds ready-to-extract ZIP.
5. Obtains PortableApps.com Installer **3.9.22**, verifies its pinned SHA-256, extracts the original vendor packager headlessly and invokes its own `PortableApps.comInstaller.exe` on the completed stage. The generated `.paf.exe` is checked as an archive/PE and explicitly attributed to the official tool. If the tool fails, only ZIP is published under a `-ziponly` release tag; **there is no generic NSIS fallback falsely labeled official**.
6. Uses the verified `vhick/portable-release-publisher@v1.1.1` twice: dry-run and real publish. No `actions/upload-artifact`, Git LFS or additional uploader.

**Build method disclosure:** Thunderbird itself is **not compiled from source** in this GitHub Actions workflow. The Mozilla-signed, checksum-verified Windows binaries are redistributed unchanged, and the portability launcher **is compiled** from the C++ in this kit. A full Thunderbird source compilation requires the Mozilla Firefox platform source, MozillaBuild and substantial build resources, making it unsuitable as the default GitHub Free approach.

## Release outputs

- `ThunderbirdCommunityPortable_<ThunderbirdVersion>_r1_win64.zip` — ready-to-extract `ThunderbirdCommunityPortable` folder with real root EXE launcher.
- `ThunderbirdCommunityPortable_<ThunderbirdVersion>_r1_win64.paf.exe` — only if compiled from **unmodified official PortableApps.com Installer 3.9.22** and archive checked. If the official packaging engine cannot be obtained/compiled/validated, a ZIP-only release is labeled `...-ziponly` and the workflow summary explains why.

**Data safety:** keep `ThunderbirdCommunityPortable\Data` when upgrading. Do not replace your existing official `ThunderbirdPortable` folder with this independent `ThunderbirdCommunityPortable` package. Thunderbird stores messages, accounts, calendars, contacts, extension data, and profile databases in `Data\profile`. The launcher does **not** import any installed profile automatically.

## Fast setup with GitHub Desktop

1. Open **GitHub Desktop → File → New repository**. Name it `Thunderbird-PortableApps-Builder`; select a local location, and choose **Create repository**. Do not fork Thunderbird or the FreeCrawl reference.
2. Extract this builder ZIP. Copy **everything inside** the extracted folder (including hidden `.github`) into the repository folder that GitHub Desktop created. Do not nest an extra builder directory.
3. In GitHub Desktop, use the **Changes** tab. Enter a message like `Add Thunderbird PortableApps builder r1`; click **Commit to main**.
4. Click **Publish repository**. Leave **Keep this code private** checked for a personal build. Public releases distribute Thunderbird binaries to everyone and need separate trademark/redistribution review and explicit acknowledgement on the workflow form.
5. Open your new builder repository on GitHub in a browser. Click **Actions**. Allow workflows if GitHub prompts you.
6. Select **Build Thunderbird Community Portable (ZIP + official PAF)** → **Run workflow** → version `latest`. For a private repository, leave `public_redistribution_ack` unchecked. Click **Run workflow**.
7. Open the run and watch for green checks. If a step fails, open it and save its log; never manually rename an installer or remove a failed checksum test.
8. After success, open your builder repository's **Releases** area, select the latest `portable-v<version>-r1` release (or `-ziponly` if no official-tool PAF). Download one of the intended packages.
9. **PAF:** Start PortableApps.com Platform, use its **Apps → Install a New App (.paf.exe)** option, select this package, and choose your existing Platform's `PortableApps` directory. The new `ThunderbirdCommunityPortable` folder should appear alongside, not inside, `ThunderbirdPortable`.
10. **ZIP:** Extract the ZIP **directly into** `X:\PortableApps\`, so the resulting path is `X:\PortableApps\ThunderbirdCommunityPortable\ThunderbirdCommunityPortable.exe`. Do **not** create nested `ThunderbirdCommunityPortable\ThunderbirdCommunityPortable` folders.
11. In PortableApps Menu, refresh the app icons (or restart the Platform). Launch **Thunderbird Community Portable**; set up a new email account only after confirming the portable profile path in Thunderbird's Troubleshooting Information.
12. **Upgrade:** close every window of this portable Thunderbird and back up its `Data` folder. For PAF install over the *same* `ThunderbirdCommunityPortable` folder; for ZIP extract only `App`, `Other`, and root launcher, keeping the old `Data` **untouched**. Never extract the ZIP with a full-folder delete/sync over `Data`.

## Important behavior and limitations

- This launcher blocks arguments that would select a different profile. This prevents accidental use of installed Thunderbird profiles. The portable profile is at `Data\profile`, and temporary files inherit `Data\temp`.
- On folder relocation, only recognized Thunderbird absolute mail root/server directory paths within `prefs.js` are rewritten, with a backup. For externally stored mail, helper programs, user-customized paths and some extensions, manual path repair may still be required.
- The builder adds `App\Thunderbird\distribution\policies.json` containing Thunderbird's officially documented `DisableAppUpdate=true` policy, so Thunderbird does not update its own extracted program files and bypass GitHub release/version checks. The portable program is updated by replacing `App` from the next verified release, while preserving `Data`. No registry changes, services, scheduled tasks, firewall rules, startup installation, system-wide default email client changes, or administrator elevation are performed by the wrapper. The Windows shell, Thunderbird OS integrations, crash reporting, security products and network services can nevertheless leave host-specific traces.
- PAF archive inspection is **not** an installation or upgrade GUI test. Windows launcher diagnostics and Thunderbird headless launch are automated, but a separate **manual interactive acceptance test** (see `docs/MANUAL-ACCEPTANCE.md`) must verify Menu behavior, real mail-profile writes and upgrade preservation.
- The bundled binaries keep Thunderbird trademarks and code signatures supplied by Mozilla. The original wrapper uses a generic icon and distinct community name/AppID. Rebuilding Mozilla binaries or distributing this package publicly may require additional trademark permissions. Review `docs/AUDIT.md`.
- Windows executables built by GitHub Actions are normally **unsigned**, even though underlying official Thunderbird executable files retain their original signatures. Clean code reduces false positives but does not guarantee antivirus acceptance.
- No GitHub Personal Access Token is required: the shared release publisher uses the standard Actions `GITHUB_TOKEN` with `contents: write`. GitHub Release visibility follows the builder repository's existing visibility. Automatic pruning is OFF; latest three managed releases are retained only as a future opt-in policy.

## Key files

- `.github/workflows/build-portableapps.yml` — manual, single Windows job, duplicate guard, validation, publication.
- `launcher/ThunderbirdCommunityPortable.cpp`, `launcher/launcher.rc`, `assets/` — native EXE source/icon.
- `scripts/resolve.py`, `download.py`, `extract_thunderbird.py`, `package.py` — stable version, verified download, bounded extraction, and staging.
- `scripts/build_launcher.ps1`, `scripts/compile-launcher.cmd`, `smoke.ps1` — transparent MSVC build helper and non-GUI Windows runtime checks; CMD is compiler-only, never the application launcher.
- `scripts/build_paf.py`, `validate.py` — unmodified official packager, archive integrity, PE checks.
- `scripts/verify_publisher.py`, `check_existing.py`, `confirm_release.py` — shared publisher contract and safe release tags.
- `docs/AUDIT.md`, `docs/MANUAL-ACCEPTANCE.md`, `docs/TROUBLESHOOTING.md` — evidence, limits and manual checks.

## Official reference links

- [Thunderbird desktop source](https://github.com/thunderbird/thunderbird-desktop)
- [Mozilla releases & checksums](https://releases.mozilla.org/pub/thunderbird/releases/)
- [PortableApps Format 3.9](https://portableapps.com/development/portableapps.com_format)
- [PortableApps Installer](https://portableapps.com/apps/development/portableapps.com_installer)
- [Publisher v1.1.1 action](https://github.com/vhick/portable-release-publisher/blob/v1.1.1/action.yml)
- [User-tested FreeCrawl r7 reference](https://github.com/vhick/FreeCrawl-PortableApps-Builder)

## Build acceptance statement

This kit was statically created and syntax-tested, not live-executed on a Windows GitHub runner during authoring. If a specific upstream version changes archive layout or headless smoke behavior, the builder is configured to fail or use its explicitly labeled ZIP-only fallback rather than claim a nonexistent PAF. No installer or Platform GUI tests are claimed here.
