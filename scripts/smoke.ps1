# Real Windows executable and child process check in an isolated COPY of the stage.
# No test profile or location marker ever leaks into the distributed ZIP/PAF stage.
$ErrorActionPreference='Stop'
$source=(Resolve-Path 'stage/ThunderbirdPortable').Path
$target=Join-Path $env:RUNNER_TEMP 'ThunderbirdPortable-LaunchSmoke'
if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
$exe=Join-Path $target 'ThunderbirdPortable.exe'
function Test-Launch([string[]]$ProgramArgs,[int]$TimeoutSeconds) {
  $info=[Diagnostics.ProcessStartInfo]::new($exe)
  $info.UseShellExecute=$false
  foreach($arg in $ProgramArgs) { [void]$info.ArgumentList.Add($arg) }
  $p=[Diagnostics.Process]::Start($info)
  if (-not $p) { throw 'Native launcher did not start.' }
  try {
    if (-not $p.WaitForExit($TimeoutSeconds*1000)) { try{$p.Kill($true)}catch{$p.Kill()};throw 'Thunderbird smoke test timed out' }
    if ($p.ExitCode -ne 0) { throw "Thunderbird smoke process failed with exit code $($p.ExitCode)" }
  } finally { $p.Dispose() }
}
Test-Launch @('--portable-diagnostics') 30
# This is a REAL launcher->Thunderbird.exe Windows CreateProcess test; no installer UI.
# -headless -version is an application-supported diagnostic rather than a GUI session.
Test-Launch @('-headless','-version') 120
if (-not (Test-Path -LiteralPath (Join-Path $target 'Data/profile') -PathType Container)) { throw 'Portable Data/profile not created' }
$old=$target
$new=$target+'-moved'
if (Test-Path $new) {Remove-Item -LiteralPath $new -Recurse -Force}
Move-Item -LiteralPath $old -Destination $new
$exe=Join-Path $new 'ThunderbirdPortable.exe'
Test-Launch @('--portable-diagnostics') 30
Test-Launch @('-headless','-version') 120
Write-Host 'PASS: compiled launcher runs real Thunderbird headless and survives directory relocation. Profile write operation is tested separately in manual GUI acceptance.'
