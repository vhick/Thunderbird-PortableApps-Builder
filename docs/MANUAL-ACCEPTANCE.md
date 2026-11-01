# Manual Windows / PortableApps acceptance procedure (NOT performed in CI)

Use an **empty test PortableApps directory** and test mail account, never your production Thunderbird profile. The name `ThunderbirdPortable` is also used by the official PortableApps.com Thunderbird Portable release: do not overwrite an existing app with that name.

1. Extract the ZIP into `T:\PortableApps\ThunderbirdPortable` (only if that folder is not already occupied) or test an installer through a separate PortableApps Platform menu; if named `IndependentNSIS`, it is NOT an official-tool PAF and Menu acceptance is not established.
2. Verify the root `ThunderbirdPortable.exe` has a real application icon and launches Thunderbird, not Command Prompt or a fake stub.
3. Open Thunderbird **Help → Troubleshooting Information → Profile Folder / Open Folder**. Confirm it points inside `ThunderbirdPortable\Data\profile` and NOT `%APPDATA%\Thunderbird\Profiles`.
4. Add a test account or local folders. Create messages, a calendar item and address book entry. Close Thunderbird normally; inspect `Data\profile` for actual profile files and email stores.
5. Reopen and verify all test data still exists. In a separate Explorer window inspect `%APPDATA%\Thunderbird`, `%LOCALAPPDATA%`, Windows temp and Registry with appropriate tools; record any newly created traces without deleting pre-existing installed Thunderbird data.
6. Close Thunderbird fully. Move the **entire** `ThunderbirdPortable` directory to a different directory or drive (different drive letter when available). Launch and verify that messages, calendar, contacts and extensions still work; inspect `prefs.js.before-portable-relocation.bak` if present.
7. Back up `Data` and record a test marker file with known contents under `Data\settings\test-marker.txt`. Use the generated official `.paf.exe` or independently labeled `.paf.exe` (if Platform accepts it) to install **over the same exact app folder**. Verify the marker and actual mail profile remain intact, and there is no duplicate nested folder.
8. Confirm Thunderbird can start again from PortableApps Menu. Do not overwrite an existing official `ThunderbirdPortable` installation. Use a separate test Platform root: this independent r6 builder intentionally uses the same folder name and a distinct AppID.
9. Disable/remove optional shell association or default-email integration through Windows Settings if you chose such integration within Thunderbird. The builder itself installs no integrations to remove.
10. Only after passing these checks consider using the package for real mail. Back up your profile before every upgrade. **Never test a downgrade** against important profiles; Thunderbird can change profile database formats between versions.

**Recording:** None of these interactive checks are claimed to have passed without performing them on real Windows.

## r6 TraceGuard manual acceptance (required in addition to the steps above)

1. Back up the test portable `Data` tree and your installed Thunderbird profile separately.
2. Note which paths already exist under `%APPDATA%/Thunderbird`, `%LOCALAPPDATA%/Thunderbird`, `%APPDATA%/Mozilla`, `%LOCALAPPDATA%/Mozilla`, `%PROGRAMDATA%/Mozilla`.
3. Run `ThunderbirdPortable.exe` and close normally. Confirm `Data/TraceGuard/logs/session-*.txt` exists.
4. Confirm a **pre-existing** Thunderbird profile or cache folder has not been renamed, deleted or moved by this wrapper.
5. In a separate Windows test user profile that has never run Thunderbird, test whether newly created dedicated Thunderbird AppData paths were captured under `Data/TraceGuard/captured`.
6. Check ProgramData; any new shared Mozilla updates folder must be left for manual review, not force-deleted.
7. Repeat with another Thunderbird process open; TraceGuard must log `KEEP` instead of capturing host paths.
8. Test on a different drive, restarting after relocation and verifying profile messages/accounts persist; captured host traces are *not* reintroduced into the main `Data/profile`.
9. If the launcher or Thunderbird crashes, verify host data is retained and do not attempt to use TraceGuard as a crash recovery mechanism.
10. Record actual GUI installation and existing-Data upgrade results separately from isolated CI fixture tests.

## r6 Stormhen-derived checks

1. In an isolated Windows test user, start portable Thunderbird; verify no new default-mail prompt or Windows Search integration is requested.
2. Check `App/Thunderbird/distribution/policies.json` for `DisableAppUpdate`, `mail.shell.checkDefaultClient`, and `mail.winsearch.enable` settings.
3. Create a test file under *pre-existing* LocalLow/Thunderbird before launch and ensure it survives unchanged.
4. In a clean test user with no LocalLow Thunderbird directory, create a file there while the portable child runs, close normally, and inspect `Data/TraceGuard/captured/LocalLow/Thunderbird/session-*`.
5. Confirm `Data/plugins` and `Data/TraceGuard/logs` exist and no ProgramData folders were modified by TraceGuard.
6. Run with Thunderbird already running elsewhere, then close the portable session; confirm all host folders are preserved.
