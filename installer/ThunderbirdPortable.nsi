; Independent NSIS PortableApps-style installer, NOT the PortableApps.com Installer.
; Created only when the workflow explicitly allows an independently labeled fallback.
; Never removes/overwrites existing Data.
Unicode true
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!ifndef STAGE_DIR
  !error "STAGE_DIR required"
!endif
!ifndef OUTPUT_FILE
  !error "OUTPUT_FILE required"
!endif
Name "Thunderbird Portable - Independent NSIS"
OutFile "${OUTPUT_FILE}"
RequestExecutionLevel user
InstallDir "$EXEDIR"
Icon "${STAGE_DIR}\App\AppInfo\appicon.ico"
SetCompressor /SOLID lzma
ShowInstDetails show
BrandingText "Independent community installer; not the official PortableApps.com Installer"
Page directory
Page instfiles

Function .onInit
  ; PortableApps Platform normally supplies /DESTINATION=path when launching an installer.
  ${GetParameters} $R0
  ClearErrors
  ${GetOptions} $R0 "/DESTINATION=" $R1
  ${IfNot} ${Errors}
    StrCpy $INSTDIR $R1
  ${EndIf}
  ; Accept a Platform /DESTINATION= that points either to the PortableApps
  ; parent or directly to the named application directory.
  ${GetFileName} "$INSTDIR" $R2
  ${If} $R2 == "ThunderbirdPortable"
    ${GetParent} "$INSTDIR" $R2
    StrCpy $INSTDIR $R2
  ${EndIf}
FunctionEnd

Section "Thunderbird Portable (Independent Build)" SEC01
  ; The target is the PortableApps PARENT folder; app directory added exactly once.
  ; Protect an existing *official* ThunderbirdPortable or unknown installation.
  ; Its AppID is different even though the requested folder name is identical.
  ${If} ${FileExists} "$INSTDIR\ThunderbirdPortable\*.*"
    ${IfNot} ${FileExists} "$INSTDIR\ThunderbirdPortable\App\AppInfo\appinfo.ini"
      MessageBox MB_OK|MB_ICONSTOP "An existing ThunderbirdPortable folder without recognizable builder metadata was found. Backup and choose a different PortableApps root; no files were changed."
      Abort
    ${EndIf}
    ReadINIStr $R3 "$INSTDIR\ThunderbirdPortable\App\AppInfo\appinfo.ini" "Details" "AppID"
    ${If} $R3 != "ThunderbirdPortable-vhick"
      MessageBox MB_OK|MB_ICONSTOP "ThunderbirdPortable is already used by a different release (AppID=$R3). To protect mail data, installation was refused. Choose a separate PortableApps root."
      Abort
    ${EndIf}
  ${EndIf}
  ${If} ${FileExists} "$INSTDIR\ThunderbirdPortable\Data\*.*"
    ${IfNot} ${FileExists} "$INSTDIR\ThunderbirdPortable\App\AppInfo\appinfo.ini"
      MessageBox MB_OK|MB_ICONSTOP "Unknown existing ThunderbirdPortable Data was found. Installation blocked to protect user profiles."
      Abort
    ${EndIf}
  ${EndIf}
  CreateDirectory "$INSTDIR\ThunderbirdPortable"
  RMDir /r "$INSTDIR\ThunderbirdPortable\App"
  ${If} ${FileExists} "$INSTDIR\ThunderbirdPortable\App"
    MessageBox MB_OK|MB_ICONSTOP "Unable to replace App. Close portable Thunderbird and retry. Data is preserved."
    Abort
  ${EndIf}
  RMDir /r "$INSTDIR\ThunderbirdPortable\Other"
  ${If} ${FileExists} "$INSTDIR\ThunderbirdPortable\Other"
    MessageBox MB_OK|MB_ICONSTOP "Unable to replace Other. Close portable Thunderbird and retry."
    Abort
  ${EndIf}
  SetOutPath "$INSTDIR\ThunderbirdPortable"
  File "${STAGE_DIR}\ThunderbirdPortable.exe"
  SetOutPath "$INSTDIR\ThunderbirdPortable\App"
  File /r "${STAGE_DIR}\App\*.*"
  SetOutPath "$INSTDIR\ThunderbirdPortable\Other"
  File /r "${STAGE_DIR}\Other\*.*"
  ; Only creates missing directories. Existing Data files are never packaged/deleted.
  CreateDirectory "$INSTDIR\ThunderbirdPortable\Data"
  CreateDirectory "$INSTDIR\ThunderbirdPortable\Data\profile"
  CreateDirectory "$INSTDIR\ThunderbirdPortable\Data\temp"
  CreateDirectory "$INSTDIR\ThunderbirdPortable\Data\settings"
SectionEnd
