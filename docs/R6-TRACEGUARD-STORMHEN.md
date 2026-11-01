# r6 — TraceGuard: safe Windows remnant handling

## What TraceGuard does

TraceGuard is compiled into the genuine `ThunderbirdPortable.exe` Windows launcher. It does **not** run as a background service, require administrator rights, install a system watcher, create junctions, or use opaque PowerShell.

1. Before launching Thunderbird, save a presence-only snapshot of known Thunderbird-related top-level directories under AppData, LocalAppData and ProgramData.
2. Launch `App/Thunderbird/thunderbird.exe -no-remote -profile Data/profile`, as in r4.
3. Use portable `Data/temp` for `TEMP` and `TMP` and Mozilla's documented crash-report directory environment variables for `Data/CrashReports`.
4. Wait for the Thunderbird process that was started by the portable launcher.
5. When it exits successfully and there were no other running `thunderbird.exe` processes before launch or after exit, capture newly created *dedicated* `%APPDATA%/Thunderbird` and `%LOCALAPPDATA%/Thunderbird` trees under `Data/TraceGuard/captured` (if safe), and remove newly created **empty** `%APPDATA%/Mozilla` and `%LOCALAPPDATA%/Mozilla` parent directories.
6. Never automatically move an existing directory, and never modify ProgramData, GnuPG or nonempty shared Mozilla directories. Save a plain text decision log for every session.

## Watched locations and safety policy

| Host path | Action when absent before launch, created during session | If it existed before launch |
|---|---|---|
| `%APPDATA%/Thunderbird` | Move entire dedicated root to `Data/TraceGuard/captured/Roaming/Thunderbird/session-*` only after safe shutdown | Leave untouched |
| `%LOCALAPPDATA%/Thunderbird` | Move entire dedicated root to `Data/TraceGuard/captured/Local/Thunderbird/session-*` only after safe shutdown | Leave untouched |
| `%APPDATA%/Mozilla` | Remove only if newly created and entirely empty | Leave untouched |
| `%LOCALAPPDATA%/Mozilla` | Remove only if newly created and entirely empty | Leave untouched |
| `%LOCALAPPDATA%/gnupg` | Report only — may contain external PGP keys | Leave untouched |
| `%PROGRAMDATA%/Mozilla` | Report only — may be shared with Firefox/other apps | Leave untouched |
| `%PROGRAMDATA%/Mozilla-1de4eec8-1241-4177-a864-e594e8d1fb38` | Report only — machine-wide updates | Leave untouched |
| `%PROGRAMDATA%/Thunderbird` | Report only — machine-wide storage not proven exclusive | Leave untouched |
| `%LOCALAPPDATA%/GitHubDesktop`, `%APPDATA%/GitHub Desktop` | Not watched and never touched — different application | Not applicable |

## Data tree

```text
ThunderbirdPortable/
  ThunderbirdPortable.exe
  Data/
    profile/                 # Thunderbird mail and account settings
    temp/                    # Child process temp files
    CrashReports/            # Mozilla documented crash-reporter redirects
    TraceGuard/
      captured/
        Roaming/Thunderbird/session-<timestamp-PID>/
        Local/Thunderbird/session-<timestamp-PID>/
      logs/session-<timestamp-PID>.txt
```

`captured` contains host traces, NOT imported mail profiles. Thunderbird's active profile remains `Data/profile`; do not merge captured data into that directory automatically.

## Safety rules

- The entry point is a transparent compiled C++ EXE. No hidden processes, administrator elevation, registry edits, scheduled tasks, services, or forced process termination.
- Windows reparse points and junctions are never followed as capture sources. Every tree is prechecked; capture is limited to 20,000 entries / 512 MiB per directory. Files on different drives are copied and verified byte-for-byte before the source can be removed.
- Any interrupted launcher, nonzero application exit, concurrently running Thunderbird, unexpected files, permissions error or failed verification leaves data in place (and logs the decision). In exceptional cross-volume failures, a `*.pending` copy can remain under `Data/TraceGuard/captured`; review the log before manual cleanup.
- No existing `%APPDATA%/Thunderbird` or `%LOCALAPPDATA%/Thunderbird` folder is removed or moved, even if the portable session adds data inside it. r4 or installed Thunderbird leftovers that predate r6 need a separate **manual ownership review**.
- **TraceGuard is not a full process-level filesystem tracer.** Windows can retain application-specific registry entries, OS caches, thumbnails, certificate/network state and logs. ProgramData traces are report-only. A computer with installed Thunderbird or Firefox may legitimately have shared folders that must not be removed.
- On USB/external drives, cross-volume verified capture is slower. The launcher waits for cleanup to finish; do not unplug the drive during the process.

## How to inspect on your own PC

1. Back up the entire existing `ThunderbirdPortable/Data` folder. Do not run an installed Thunderbird simultaneously with the portable version.
2. Launch `ThunderbirdPortable.exe` normally, not `App/Thunderbird/thunderbird.exe`.
3. Close Thunderbird completely and allow the launcher to finish.
4. Open `ThunderbirdPortable/Data/TraceGuard/logs/` and read the newest `session-*.txt`.
5. Lines beginning `CAPTURED` identify host folders moved into `Data/TraceGuard/captured`. `KEEP` means the folder was deliberately retained. `REMOVED` applies ONLY to a newly created empty Mozilla folder. `NO TRACE` means that path did not appear.
6. Check `%APPDATA%`, `%LOCALAPPDATA%` and `%PROGRAMDATA%` manually. Do not interpret the mere presence of a Mozilla directory as proof of a portable-app leak.
7. Repeat with a real mail account and with a separate installed Thunderbird instance (or fake external profile under test) to ensure data protection. Test an application-folder move and a reinstall over existing Data.

## GitHub Actions coverage

`tests/traceguard_fixture.cpp` is compiled by `scripts/test_traceguard.ps1` during the Windows workflow **before** the real launcher build. The fixture uses dedicated test roots under `RUNNER_TEMP`; it simulates newly created cache folders and pre-existing host profiles without ever touching real user AppData. A failure blocks publication.

No live desktop test, true third-party process attribution, interactive PAF installation, or installed Thunderbird coexistence test has been completed merely by passing static and fixture tests. Verify these on a Windows machine before relying on r6 for your real mail profile.

## Evidence

- https://support.mozilla.org/en-US/kb/profiles-where-thunderbird-stores-user-data
- https://github.com/PortableApps/AppConfigs/blob/master/T/Thunderbird/ThunderbirdPortableU.nsi
- https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html
- https://github.com/desktop/desktop/blob/development/docs/installation.md (GitHub Desktop paths are explicitly excluded)


## Additional r6 source-based changes (Stormhen-derived)

Source: https://github.com/portapps/stormhen-portable/blob/master/main.go

- Stormhen monitors `%APPDATA%/Thunderbird`, `%LOCALAPPDATA%/Thunderbird`, and `%USERPROFILE%/AppData/LocalLow/Thunderbird`. TraceGuard r6 adds LocalLow to existing before/after checks, with the *same* exclusive/newly-created-only capture rule. The LocalLow folder can contain installed app data, and pre-existing content is protected.
- Stormhen sets `MOZ_MAINTENANCE_SERVICE=0`, `MOZ_UPDATER=0`, and `MOZ_PLUGIN_PATH` to a portable path; r6 sets the same child-only variables and uses `Data/plugins`.
- Stormhen uses `MOZ_CRASHREPORTER_DISABLE=1` when disabled by config. r6 explicitly disables its Mozilla crash reporter by default, with supported crash storage still pointed at `Data/CrashReports` for any components that honor those paths. This can limit crash-dump generation and debugging.
- Stormhen's managed `mail.winsearch.enable` and `mail.shell.checkDefaultClient` preferences are applied via Thunderbird's documented `Preferences` policy in the **extracted portable app's** `distribution/policies.json`. No host registry policy is written. The build fails on conflicting upstream values instead of silently changing them.
- Stormhen's *optional* broad `files.Cleanup()` is deliberately **not copied**. TraceGuard never deletes existing Thunderbird folders.

## Expected limitations

1. `ProgramData` Mozilla or Thunderbird entries are reported only; they are not automatically removed.
2. Pre-existing host `AppData` paths are never captured; this protects installed Thunderbird and other applications.
3. Stormhen's updater and maintenance flags are supplemental; the official Thunderbird `DisableAppUpdate` policy remains the primary application-update control.
4. New LocalLow Thunderbird traces are only captured on clean shutdown and if no competing Thunderbird process is detected.
5. Windows prefetch, shell caches, security logs, app notifications and external integration traces are not completely preventable with a normal user launcher.
6. Existing r5 runtime `Data` can be retained; do not remove it on upgrades. Old session traces are not retroactively deleted.
