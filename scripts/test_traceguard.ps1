# Build and execute isolated TraceGuard behavior tests on a Windows GitHub runner.
$ErrorActionPreference='Stop'
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere)) { throw 'Missing Visual Studio C++ toolchain' }
$vs=(& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath | Select-Object -First 1)
if (-not $vs) { throw 'Missing MSVC compiler' }
$env:PORTABLE_VCVARS=Join-Path $vs 'VC\Auxiliary\Build\vcvars64.bat'
$proc=[Diagnostics.ProcessStartInfo]::new('cmd.exe')
$proc.UseShellExecute=$false
$proc.WorkingDirectory=(Get-Location).Path
foreach($a in @('/d','/c','scripts\compile-traceguard-test.cmd')) { [void]$proc.ArgumentList.Add($a) }
$p=[Diagnostics.Process]::Start($proc)
if (-not $p) { throw 'TraceGuard test compiler failed to start' }
try {
  if (-not $p.WaitForExit(180000)) { $p.Kill($true); throw 'TraceGuard test compiler timed out' }
  if ($p.ExitCode -ne 0) { throw "TraceGuard test compiler failed: $($p.ExitCode)" }
} finally { $p.Dispose() }
$testRoot=Join-Path $env:RUNNER_TEMP 'ThunderbirdTraceGuard-IsolatedTest'
if (Test-Path $testRoot) { Remove-Item $testRoot -Recurse -Force }
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
$test=(Resolve-Path 'work/traceguard-fixture.exe').Path
$p=[Diagnostics.ProcessStartInfo]::new($test)
$p.UseShellExecute=$false
[void]$p.ArgumentList.Add($testRoot)
$child=[Diagnostics.Process]::Start($p)
try {
  if (-not $child.WaitForExit(60000)) { $child.Kill($true);throw 'TraceGuard fixture timeout' }
  if ($child.ExitCode -ne 0) { throw "TraceGuard fixture failed: $($child.ExitCode)" }
} finally { $child.Dispose() }
Write-Host 'PASS isolated TraceGuard safety tests.'
