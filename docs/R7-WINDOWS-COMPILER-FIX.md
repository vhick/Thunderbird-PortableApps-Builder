# r7 - Fix failing Windows MSVC TraceGuard fixture (Step 12)

## Evidence

In `logs_112026389485.zip`, `12_Compile and run isolated TraceGuard safety fixture` exited 1. MSVC 14.44 diagnosed C2668 for unqualified `exists` / `is_directory` helpers in `TraceGuard.h`: both the local helper and the standard library name are found for `std::filesystem::path` through argument-dependent lookup. MSVC also rejected `L"Roaming" / L"Thunderbird"` and two equivalent Local/LocalLow expressions, reporting C2296 and C2297, followed by cascading C2660 errors.

## Code repair

- Distinct `trace_exists` and `trace_is_directory` helpers; all old unqualified calls are replaced.
- `fs::path(L"Roaming") / L"Thunderbird"`, and the equivalent Local / LocalLow paths.
- Static regression guard in `scripts/test_static.py`; Windows `tests/traceguard_fixture.cpp` stays a mandatory MSVC compile-and-execute gate before the main launcher is built.
- New revision r7, release tag and filenames to avoid mixing r6 failures with r7 artifacts.

## Preserved behavior

- Official Thunderbird icon and `ThunderbirdPortable/ThunderbirdPortable.exe`.
- Only newly created dedicated Thunderbird roots are eligible for TraceGuard capture; pre-existing host data and shared ProgramData remain protected.
- Profile under Data; same publisher v1.1.1, ZIP and honest official-tool/independent/ZIP-only installer selection.
- No broad removal, administrator requirement, junction creation, or registry modifications.

## Test boundaries

The first r7 GitHub Actions Windows run must compile and execute the isolated safety fixture, compile the real C++ launcher, validate icon embedding, run its smoke test, and validate packaging before releasing anything. Local static and mocked header C++ syntax checks are not a replacement for a real MSVC compile or running Thunderbird on Windows. A manual PAF upgrade and Platform Menu discovery test remain separate.
