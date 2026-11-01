# Thunderbird Portable — source-based Windows portability audit

This is a targeted audit based on developer documentation, the actual upstream repository layout, Thunderbird profile/help documentation, the Mozilla official release distribution, and PortableApps.com Format 3.9. It is NOT a comprehensive runtime filesystem/registry trace of every Thunderbird feature.

| Area | Verified basis / behavior | Portable adaptation | Remaining limitation |
|---|---|---|---|
| Source/build | Thunderbird source in `thunderbird/thunderbird-desktop` is added as `comm/` inside the Mozilla Firefox platform tree; Windows builds use `mach`, MozillaBuild, MSVC, Rust | Instead of recompiling a large source tree, download official release stable Windows installer from Mozilla, verify SHA256SUMS and extract the signed application | Full Thunderbird source compilation not performed in builder; upstream binary used. Git source tag is resolved when available, otherwise not falsely asserted |
| User profile | Thunderbird Help: Windows normal user profile `%APPDATA%\Thunderbird\Profiles\` | Native launcher passes `-profile <portable>\Data\profile` and `-no-remote` before application startup | Thunderbird/Windows may leave non-profile traces. Never use its normal installed-profile shortcut |
| Mail storage, accounts, passwords, contacts, calendar and extensions | Mozilla profile files include `prefs.js`, local account mail files, profile stores, extensions and databases | All standard profile data remains in `Data\profile`; no host import or profile merging | User-configured external folders, custom helper apps, external PGP/GPG or account-specific paths may point outside Data |
| Relocation | Some profile mail prefs use absolute Windows paths (`mail.root.*`, `mail.server.server*.directory`) | Launcher backs up prefs and updates only known portable-root references on move; location marker in `Data\settings` | External absolute paths, extensions and data stores might require manual repair; only migrate after Thunderbird is fully closed |
| Temporary files | Thunderbird and child processes use Windows `TEMP` and `TMP` | Launcher passes `Data\temp` to Thunderbird process; additionally overrides documented crash reporter directories | Third-party extensions, Windows caches and some host integrations may still persist outside Data |
| Registry | This wrapper does not create HKCU/HKLM keys | No installer execution, no shell association, no startup task, no service, no elevation | Thunderbird OS integration/Windows shell interactions may use Windows registry or host caches, depending on user actions. Exact keys are not proven by a runtime trace |
| Processes | Thunderbird launches subprocesses and may spawn helpers | Native launcher waits for its launched parent; mutex blocks conflicting starts of same portable folder | Existing installed Thunderbird can run separately; do not override profile or bypass process checks |
| App updates | Mozilla application runtime includes updater logic | Builder controls GitHub package revision | Builder ships Thunderbird-documented `App/Thunderbird/distribution/policies.json` with `DisableAppUpdate=true` to prevent self-updating extracted binaries. Update by replacing `App` while preserving `Data`. Group Policy on host can override installation-local policy |
| Install/upgrade | Format 3.9 standard installer replaces `App` and `Other` but preserves `Data` | Explicit `RemoveDataDirectory=false`; distinct AppID avoids metadata identity collision, but requested ThunderbirdPortable root COLLIDES with the official PortableApps package; install to a separate empty PortableApps root | Actual interactive PAF upgrade and Menu discovery must be manually validated |
| Driver/service/task | No application-owned driver, Windows service or scheduled task is required for launching the standard email UI | None installed | Protocol/file associations, default-client selection and optional integrations are host changes and are NOT automatically installed/removed here |

## r6 dynamic TraceGuard — deliberately limited host cleanup

- At start, the native Windows launcher takes presence snapshots of the dedicated `%APPDATA%\Thunderbird` and `%LOCALAPPDATA%\Thunderbird` directories plus shared `%APPDATA%\Mozilla`, `%LOCALAPPDATA%\Mozilla`, `%LOCALAPPDATA%\gnupg`, `%PROGRAMDATA%\Mozilla`, `%PROGRAMDATA%\Mozilla-1de4eec8-1241-4177-a864-e594e8d1fb38`, and `%PROGRAMDATA%\Thunderbird`.
- Upon a successful Thunderbird exit, if **zero** `thunderbird.exe` processes existed before launching or remain afterwards, exclusively newly created dedicated Thunderbird directory roots can be moved to `Data\TraceGuard\captured`. This saves data rather than silently destroying it.
- A pre-existing folder is **never** relocated, even if the portable session added content there. A newly created, empty `%APPDATA%\Mozilla` or `%LOCALAPPDATA%\Mozilla` parent may be removed after a clean exit. Nonempty or pre-existing Mozilla roots, GnuPG and ProgramData are audit-only.
- Windows reparse points (junctions/symlinks) are excluded. Cross-volume capture performs byte-for-byte verification; failures leave sources for manual recovery. Captures are bounded to 20,000 entries and 512 MiB per tree.
- Before-shutdown crashes, interrupted launchers, nonzero child exit, lingering Thunderbird processes, insufficient permissions, and unrelated OS integrations are recorded or left alone, not assumed clean. The `Data\TraceGuard\logs` audit is created on each real launch.
- This is a **pre/post snapshot, not continuous process-level filesystem tracing**. No universal guarantee of zero host traces or automatic safe cleanup of installed application data is made.

## Evidence / primary references

- https://github.com/PortableApps/AppConfigs/blob/master/T/Thunderbird/ThunderbirdPortableU.nsi
- https://github.com/desktop/desktop/blob/development/docs/installation.md (separate Electron/GitHub Desktop paths; NOT Thunderbird cleanup targets)
- https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html
- https://github.com/thunderbird/thunderbird-desktop
- https://github.com/thunderbird/developer-docs/blob/master/thunderbird-development/setting-up-a-build-environment.md
- https://source-docs.thunderbird.net/en/latest/build/index.html
- https://support.mozilla.org/en-US/kb/profiles-where-thunderbird-stores-user-data
- https://releases.mozilla.org/pub/thunderbird/releases/
- https://product-details.mozilla.org/1.0/thunderbird_versions.json
- https://portableapps.com/development/portableapps.com_format
- https://updates.thunderbird.net/en-US/thunderbird/about/rights/

## Trademark / redistribution

Thunderbird MPL source-code permissions do not automatically grant Thunderbird trademark and logo rights. This independent wrapper uses Thunderbird's authentic trademarked icon, the requested canonical folder name (which collides with the official PortableApps build), and a distinct AppID; it makes no PortableApps.com certification claim. Review trademark rights before PUBLIC distribution. The official Thunderbird Portable is already available at https://portableapps.com/apps/internet/thunderbird_portable .
