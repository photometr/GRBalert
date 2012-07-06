;Change this file to customize zip2exe generated installers with a modern interface

!include "MUI.nsh"

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Auto Launch icon" SecQuick
    SetOutPath $INSTDIR
    CreateShortCut "$SMPROGRAMS\Startup\GA.lnk" "$INSTDIR\GA.exe" \
    "some command line parameters" "$INSTDIR\GA.exe" 2 SW_SHOWNORMAL \
    ALT|CTRL|SHIFT|F5 "GRB Alert"
SectionEnd