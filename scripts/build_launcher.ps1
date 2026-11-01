$ErrorActionPreference = 'Stop'
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere)) { throw 'Visual Studio C++ Build Tools (vswhere.exe) unavailable.' }
$vs = (& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath | Select-Object -First 1)
if (-not $vs) { throw 'Windows runner is missing VS C++ x64 compiler.' }
$vcvars = Join-Path $vs 'VC\Auxiliary\Build\vcvars64.bat'
if (-not (Test-Path -LiteralPath $vcvars)) { throw 'Missing vcvars64.bat' }
New-Item -ItemType Directory -Path 'work' -Force | Out-Null
# Compile directly into a genuine PE executable with an embedded original, non-trademarked icon.
$env:PORTABLE_VCVARS = $vcvars
$proc = [Diagnostics.ProcessStartInfo]::new('cmd.exe')
$proc.UseShellExecute = $false
$proc.WorkingDirectory = (Get-Location).Path
[void]$proc.ArgumentList.Add('/d')
[void]$proc.ArgumentList.Add('/c')
[void]$proc.ArgumentList.Add('scripts\compile-launcher.cmd')
$p = [Diagnostics.Process]::Start($proc)
if (-not $p) { throw 'Compiler did not start' }
try {
  if (-not $p.WaitForExit(180000)) {
    try { $p.Kill($true) } catch { $p.Kill() }
    throw 'Launcher compiler exceeded 180 seconds'
  }
  if ($p.ExitCode -ne 0) { throw "C++ launcher build failed with exit code $($p.ExitCode)" }
} finally { $p.Dispose() }
if (-not (Test-Path 'work/ThunderbirdCommunityPortable.exe')) { throw 'Compiled launcher missing after successful compiler exit' }
Write-Host 'Native C++ launcher compiled successfully.'
