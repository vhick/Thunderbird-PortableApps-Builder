@echo off
setlocal
if not defined PORTABLE_VCVARS exit /b 1
call "%PORTABLE_VCVARS%"
if errorlevel 1 exit /b 1
cl.exe /nologo /std:c++17 /EHsc /MT /O2 /W4 /DUNICODE /D_UNICODE tests\traceguard_fixture.cpp /link /SUBSYSTEM:CONSOLE /OUT:work\traceguard-fixture.exe
if errorlevel 1 exit /b 1
exit /b 0
