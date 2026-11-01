# Exact r1 failure analysis (user-provided GitHub Actions logs, November 1, 2026)

## Verified successful stages

- Thunderbird stable version and Mozilla release checksum lookup
- Shared publisher v1.1.1 input checks
- Official Thunderbird installer download, SHA-256 check, extraction of app payload
- Genuine MSVC C++ portable launcher compilation
- Thunderbird headless smoke checks, staged ZIP packaging and ZIP validation
- Official PortableApps.com Installer 3.9.22 download SHA check and 7-Zip archive extraction

## Failure

The first error is under step 15, `Generate and independently verify official-tool PAF (no GUI)`:

```
Official compiler failed; no mislabeled NSIS fallback:
TimeoutExpired(['...\\PortableApps.comInstaller.exe', '...\\stage\\ThunderbirdPortable'], 480)
...
Process completed with exit code 1.
```

**Observed**: the vendor compiler stayed running for 480 seconds. This is consistent with a blocked GUI prompt or process but no vendor window screenshot or log was captured; do not assert a unique exact cause.

**Separate bug**: the PowerShell fallback code recorded `ok=false` and emitted a warning but did not execute an explicit `exit 0`. The earlier Python command's nonzero exit was therefore inherited, killing the entire step and preventing both publisher steps. That was contrary to the intended ZIP-only fallback policy.

## r2 mitigation

- Precheck required appinfo.ini entries, include the previously missing Homepage field.
- Bound the official compiler to 210 seconds and search for a fresh archive even after the vendor process exits abnormally or times out. All selected files still undergo independent integrity and staged-byte comparison.
- Select `official`, `independent`, or `ziponly` and explicitly `exit 0` after an optional installer failure. This only applies after mandatory ZIP validation passed.
- Offer a separately labeled, independently compiled NSIS PAF-style installer when fallback is enabled. It never claims vendor engine provenance. If its creation or verification fails, publish ZIP only.
- Release tags r2 are distinct to protect prior releases.

## Remaining uncertainty

A live Windows GitHub Actions run is needed to determine if the official compiler now finishes, if the independent NSIS script compiles on a hosted Windows image, and if the generated installer actually installs/upgrades correctly through PortableApps Platform. None of those are proven from the r1 logs or static validation.
