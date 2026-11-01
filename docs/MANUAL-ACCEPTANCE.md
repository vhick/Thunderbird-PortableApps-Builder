# Manual Windows / PortableApps acceptance procedure (NOT performed in CI)

Use an **empty test PortableApps directory** and test mail account, never your production Thunderbird profile.

1. Extract the ZIP into `T:\PortableApps\ThunderbirdCommunityPortable` or install the true official-tool PAF through the PortableApps Platform menu.
2. Verify the root `ThunderbirdCommunityPortable.exe` has a real application icon and launches Thunderbird, not Command Prompt or a fake stub.
3. Open Thunderbird **Help → Troubleshooting Information → Profile Folder / Open Folder**. Confirm it points inside `ThunderbirdCommunityPortable\Data\profile` and NOT `%APPDATA%\Thunderbird\Profiles`.
4. Add a test account or local folders. Create messages, a calendar item and address book entry. Close Thunderbird normally; inspect `Data\profile` for actual profile files and email stores.
5. Reopen and verify all test data still exists. In a separate Explorer window inspect `%APPDATA%\Thunderbird`, `%LOCALAPPDATA%`, Windows temp and Registry with appropriate tools; record any newly created traces without deleting pre-existing installed Thunderbird data.
6. Close Thunderbird fully. Move the **entire** `ThunderbirdCommunityPortable` directory to a different directory or drive (different drive letter when available). Launch and verify that messages, calendar, contacts and extensions still work; inspect `prefs.js.before-portable-relocation.bak` if present.
7. Back up `Data` and record a test marker file with known contents under `Data\settings\test-marker.txt`. Use the generated `.paf.exe` to install **over the same exact app folder**. Verify the marker and actual mail profile remain intact, and there is no duplicate nested folder.
8. Confirm Thunderbird can start again from PortableApps Menu. Do not overwrite the official `ThunderbirdPortable` installation; this independent build uses `ThunderbirdCommunityPortable`.
9. Disable/remove optional shell association or default-email integration through Windows Settings if you chose such integration within Thunderbird. The builder itself installs no integrations to remove.
10. Only after passing these checks consider using the package for real mail. Back up your profile before every upgrade. **Never test a downgrade** against important profiles; Thunderbird can change profile database formats between versions.

**Recording:** None of these interactive checks are claimed to have passed without performing them on real Windows.
