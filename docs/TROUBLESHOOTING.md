# Troubleshooting and safeguards

| Symptom | What to check | Safe action |
|---|---|---|
| No GitHub Actions workflow | `.github/workflows/build-portableapps.yml` must be directly at repository root after copying all hidden files | Reopen GitHub Desktop and commit the workflow file |
| Public-repo safety gate failed | Public release requires legal/trademark review | Make repository Private or review terms then tick the workflow acknowledgement |
| SHA-256 mismatch | Official Mozilla `SHA256SUMS` or installer did not match | Stop; do not bypass checksum. Retry a newer workflow run or select another stable version |
| 7-Zip cannot extract Thunderbird installer | Mozilla altered the installer archive or runner lacks 7z | Inspect log; do not install software on runner to obtain binaries; adjust extractor in a new builder revision |
| MSVC compiler fails | Windows hosted image changed, VS C++ tooling unavailable, or C++ source needs a fix | Inspect `build_launcher.ps1` log. Do not replace launcher with CMD |
| `-headless -version` fails | Thunderbird changed headless CLI behavior or executable is incomplete | Look for child process error. Test on Windows before changing smoke command |
| PAF download/sourceforge errors | Authenticated official-tool SHA mismatch or mirror outage | Workflow selects independently labeled NSIS if explicitly enabled, otherwise ZIP-only. Never misrepresent independent output as official |
| PAF generated but invalid | ZIP/PE/7z payload checks failed | A PAF failing verification is discarded. An independently checked ZIP may still publish as documented fallback; investigate the installer separately |
| Publisher action contract changed | `verify_publisher.py` checks v1.1.1 tag and actual inputs | Fix after reading real `action.yml`; never guess unsupported arguments |
| Release tag already exists incomplete | Shared publisher refuses mutation | Increase builder revision after analyzing cause, do not overwrite assets |
| Thunderbird launches with installed profile | Direct `thunderbird.exe` invocation bypassed launcher | Always launch root `ThunderbirdCommunityPortable.exe` or PortableApps Menu |
| Mail store broken on relocation | User-specified external paths or an extension retained old absolute drive | Use the prefs backup; relocate known data; manually fix external paths through Thunderbird account settings |
| PortableApps Menu icon missing | Wrong extraction directory or Platform not refreshed | Verify `X:\PortableApps\ThunderbirdCommunityPortable\App\AppInfo\appinfo.ini` and root EXE; refresh/restart menu |
| Antivirus alert | Unsigned community wrapper may have low reputation | Inspect source/signatures and published SHA-256. Do **not** disable protection or add exclusions |

## Limits and distinctions

The Mozilla-installer checksum is fetched live from Mozilla and validates the downloaded installer content. The PortableApps **tool** checksum is separately pinned to the successful public r7 reference for version 3.9.22 and checked on each CI run; update it only after checking the authentic vendor publication. The independent wrapper remains unsigned by default.

The GitHub Actions job limit is 55 minutes, but the normal objective is much shorter. A timeout/failure is reported as such; it is not evidence the application worked. GitHub Free minutes for Private projects and release asset storage are subject to GitHub's current limits and usage accounting.

## r2 official PAF stalls or returns exit 2

The official vendor packager might open an unattended prompt or otherwise fail to finish. r2 checks required metadata and limits the build to 210 seconds. If a completed official PAF cannot be validated, it selects the explicitly enabled independent NSIS fallback, or the verified ZIP if that fallback is disabled/unavailable. The result is labeled in the workflow summary and release tag. This is **not** evidence of official packaging success.

## r2 independently built NSIS compiler is unavailable

On the standard Windows runner the fallback looks for `makensis.exe`, then attempts a bounded Chocolatey installation. If that acquisition fails, it publishes the verified ZIP under `-ziponly`; it does not fabricate a PAF. Inspect `scripts/build_independent_nsis.py` and the step log. There is no antivirus-disabling workaround.

## r2 independent installer creates an unexpected folder

The destination directory is the existing **PortableApps parent folder**, not `ThunderbirdCommunityPortable` itself. When invoked through the Platform the installer tries to honor `/DESTINATION=`; when run directly, select the parent directory on its visible folder-selection page. Confirm the resulting `PortableApps\\ThunderbirdCommunityPortable\\ThunderbirdCommunityPortable.exe` path before adding a real mail account.
