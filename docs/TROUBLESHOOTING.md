# Troubleshooting and safeguards

| Symptom | What to check | Safe action |
|---|---|---|
| No GitHub Actions workflow | `.github/workflows/build-portableapps.yml` must be directly at repository root after copying all hidden files | Reopen GitHub Desktop and commit the workflow file |
| Public-repo safety gate failed | Public release requires legal/trademark review | Make repository Private or review terms then tick the workflow acknowledgement |
| SHA-256 mismatch | Official Mozilla `SHA256SUMS` or installer did not match | Stop; do not bypass checksum. Retry a newer workflow run or select another stable version |
| 7-Zip cannot extract Thunderbird installer | Mozilla altered the installer archive or runner lacks 7z | Inspect log; do not install software on runner to obtain binaries; adjust extractor in a new builder revision |
| MSVC compiler fails | Windows hosted image changed, VS C++ tooling unavailable, or C++ source needs a fix | Inspect `build_launcher.ps1` log. Do not replace launcher with CMD |
| `-headless -version` fails | Thunderbird changed headless CLI behavior or executable is incomplete | Look for child process error. Test on Windows before changing smoke command |
| PAF download/sourceforge errors | Authenticated official-tool SHA mismatch or mirror outage | Workflow publishes explicitly labeled ZIP-only fallback. Do not rename a generic installer to PAF |
| PAF generated but invalid | ZIP/PE/7z payload checks failed | Workflow fails and must not publish any package. Investigate before bumping revision |
| Publisher action contract changed | `verify_publisher.py` checks v1.1.1 tag and actual inputs | Fix after reading real `action.yml`; never guess unsupported arguments |
| Release tag already exists incomplete | Shared publisher refuses mutation | Increase builder revision after analyzing cause, do not overwrite assets |
| Thunderbird launches with installed profile | Direct `thunderbird.exe` invocation bypassed launcher | Always launch root `ThunderbirdCommunityPortable.exe` or PortableApps Menu |
| Mail store broken on relocation | User-specified external paths or an extension retained old absolute drive | Use the prefs backup; relocate known data; manually fix external paths through Thunderbird account settings |
| PortableApps Menu icon missing | Wrong extraction directory or Platform not refreshed | Verify `X:\PortableApps\ThunderbirdCommunityPortable\App\AppInfo\appinfo.ini` and root EXE; refresh/restart menu |
| Antivirus alert | Unsigned community wrapper may have low reputation | Inspect source/signatures and published SHA-256. Do **not** disable protection or add exclusions |

## Limits and distinctions

The Mozilla-installer checksum is fetched live from Mozilla and validates the downloaded installer content. The PortableApps **tool** checksum is separately pinned to the successful public r7 reference for version 3.9.22 and checked on each CI run; update it only after checking the authentic vendor publication. The independent wrapper remains unsigned by default.

The GitHub Actions job limit is 55 minutes, but the normal objective is much shorter. A timeout/failure is reported as such; it is not evidence the application worked. GitHub Free minutes for Private projects and release asset storage are subject to GitHub's current limits and usage accounting.
