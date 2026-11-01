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
Name "Thunderbird Community Portable (Independent NSIS)"
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
FunctionEnd

Section "Thunderbird Community Portable" SEC01
  ; The target is the PortableApps PARENT folder; app directory added exactly once.
  CreateDirectory "$INSTDIR\ThunderbirdCommunityPortable"
  RMDir /r "$INSTDIR\ThunderbirdCommunityPortable\App"
  ${If} ${FileExists} "$INSTDIR\ThunderbirdCommunityPortable\App"
    MessageBox MB_OK|MB_ICONSTOP "Unable to replace App. Close portable Thunderbird and retry. Data is preserved."
    Abort
  ${EndIf}
  RMDir /r "$INSTDIR\ThunderbirdCommunityPortable\Other"
  ${If} ${FileExists} "$INSTDIR\ThunderbirdCommunityPortable\Other"
    MessageBox MB_OK|MB_ICONSTOP "Unable to replace Other. Close portable Thunderbird and retry."
    Abort
  ${EndIf}
  SetOutPath "$INSTDIR\ThunderbirdCommunityPortable"
  File "${STAGE_DIR}\ThunderbirdCommunityPortable.exe"
  SetOutPath "$INSTDIR\ThunderbirdCommunityPortable\App"
  File /r "${STAGE_DIR}\App\*.*"
  SetOutPath "$INSTDIR\ThunderbirdCommunityPortable\Other"
  File /r "${STAGE_DIR}\Other\*.*"
  ; Only creates missing directories. Existing Data files are never packaged/deleted.
  CreateDirectory "$INSTDIR\ThunderbirdCommunityPortable\Data"
  CreateDirectory "$INSTDIR\ThunderbirdCommunityPortable\Data\profile"
  CreateDirectory "$INSTDIR\ThunderbirdCommunityPortable\Data\temp"
  CreateDirectory "$INSTDIR\ThunderbirdCommunityPortable\Data\settings"
SectionEnd
