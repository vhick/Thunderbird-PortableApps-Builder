@echo off
setlocal
REM This script runs ONLY on GitHub Actions to compile a native C++ EXE.
REM It is not the portable launcher, and is not shipped as the app entry point.
if not defined PORTABLE_VCVARS (
  echo ERROR: C++ toolchain environment was not selected.
  exit /b 1
)
call "%PORTABLE_VCVARS%"
if errorlevel 1 exit /b 1
rc.exe /nologo /fo"work\launcher.res" launcher\launcher.rc
if errorlevel 1 exit /b 1
cl.exe /nologo /std:c++17 /EHsc /MT /O2 /W4 /DUNICODE /D_UNICODE launcher\ThunderbirdPortable.cpp work\launcher.res /link /SUBSYSTEM:WINDOWS /OUT:work\ThunderbirdPortable.exe shell32.lib user32.lib
if errorlevel 1 exit /b 1
exit /b 0
