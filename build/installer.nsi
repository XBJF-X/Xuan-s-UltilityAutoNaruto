; =========================================================
; Xuan NSIS installer script (ASCII only)
; - Installs build/release/* -> $INSTDIR
; - Upgrade: cleans old-version leftovers, keeps user data (config/log/setting.ini)
; - Uninstall: asks whether to keep user data (log/config/setting.ini)
;   src (incl. database.db) is always removed (developer-maintained data)
; - Version & output file passed by build_release.py via /DVERSION /DOUT_FILE
; =========================================================
Unicode true

!define PRODUCT_NAME "Xuan"
!define PRODUCT_VERSION "0.17.1"
!define PRODUCT_PUBLISHER "Xuan"
!define PRODUCT_WEB_SITE "https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Xuan.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKCU"
!define INSTALL_REG_KEY "Software\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}"

SetCompressor /SOLID lzma

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"
!include "FileFunc.nsh"

!insertmacro GetParameters
!insertmacro GetOptions

!define MUI_ABORTWARNING
!define MUI_ICON "${ICON}"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!insertmacro MUI_PAGE_WELCOME
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE "directory_leave"
!insertmacro MUI_PAGE_DIRECTORY

; Directory page leave callback: force $INSTDIR to end with Xuan.
; NSIS InstallDir's last path component (Xuan) is "may be appended back on to the
; string at install time" after the user browses a folder (per official docs), but
; that behavior is NOT guaranteed - if it does not trigger, the cleanup logic would
; run directly on the user-selected (parent) directory and delete its data.
; Here we deterministically ensure the install dir is always <selected>\Xuan.
Function directory_leave
  ${GetFileName} "$INSTDIR" $0
  StrCmp $0 "${PRODUCT_NAME}" dir_ok
    StrCpy $INSTDIR "$INSTDIR\${PRODUCT_NAME}"
  dir_ok:
FunctionEnd
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\Xuan.exe"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
UninstPage custom un.ShowKeepDataPage un.LeaveKeepDataPage
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${OUT_FILE}"
InstallDir "$LOCALAPPDATA\Xuan"
InstallDirRegKey ${PRODUCT_UNINST_ROOT_KEY} "${INSTALL_REG_KEY}" "InstallLocation"
ShowInstDetails show
ShowUnInstDetails show

; WebView2 Runtime GUID (evergreen install)
!define WEBVIEW2_KEY "SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
!define WEBVIEW2_KEY2 "SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"

; ============ Install ============
Section "Xuan" SEC_MAIN
  ; 1. Kill running instance (launcher + its backend python child processes)
  ;    /T kills the whole process tree; otherwise the backend python.exe (which holds
  ;    _internal\venv\Lib\site-packages\*.pyd/*.dll) survives and blocks file overwrite,
  ;    causing the NSIS "cannot write file" retry dialog during upgrade install.
  nsExec::ExecToLog 'taskkill /f /t /im Xuan.exe'
  Sleep 1000

  ; 2. WebView2 Runtime check (missing -> warn, allow continue)
  ReadRegStr $R0 HKLM "${WEBVIEW2_KEY}" "pv"
  StrCmp $R0 "" 0 wv2_ok
    ReadRegStr $R0 HKLM "${WEBVIEW2_KEY2}" "pv"
  StrCmp $R0 "" 0 wv2_ok
    MessageBox MB_YESNO|MB_ICONEXCLAMATION \
      "WebView2 Runtime was not detected. The app UI may not display correctly.$\r$\nContinue installation anyway?" IDYES wv2_ok
    Abort
  wv2_ok:

  ; 3. Clean old-version leftovers, keep user data (config/log/setting.ini)
  ;    Safety: only clean when $INSTDIR is really the Xuan app dir (Xuan.exe exists,
  ;    i.e. upgrade install). Fresh install to a new dir / a dir with other data
  ;    always skips cleanup, so user data can never be deleted by mistake.
  IfFileExists "$INSTDIR\Xuan.exe" 0 skip_clean
  IfFileExists "$INSTDIR\*.*" 0 skip_clean
    FindFirst $0 $1 "$INSTDIR\*"
    clean_loop:
      StrCmp $1 "" clean_done
      StrCmp $1 "." clean_next
      StrCmp $1 ".." clean_next
      StrCmp $1 "config" clean_next
      StrCmp $1 "log" clean_next
      StrCmp $1 "setting.ini" clean_next
      IfFileExists "$INSTDIR\$1\*.*" 0 clean_del_file
        RMDir /r "$INSTDIR\$1"
        Goto clean_next
      clean_del_file:
        Delete "$INSTDIR\$1"
      clean_next:
        FindNext $0 $1
        Goto clean_loop
    clean_done:
      FindClose $0
  skip_clean:

  ; 4. Copy whole release dir (Xuan.exe + _internal(portable venv) + backend + frontend/dist + src + bin/ppocrv5)
  SetOutPath "$INSTDIR"
  File /r "${RELEASE}\*"

  ; 5. Ensure user data dirs
  CreateDirectory "$INSTDIR\config"
  CreateDirectory "$INSTDIR\log"

  ; 6. Uninstaller + shortcuts (program + uninstall)
  WriteUninstaller "$INSTDIR\uninst.exe"
  CreateDirectory "$SMPROGRAMS\Xuan"
  CreateShortCut "$SMPROGRAMS\Xuan\Xuan.lnk" "$INSTDIR\Xuan.exe"
  CreateShortCut "$SMPROGRAMS\Xuan\Uninstall Xuan.lnk" "$INSTDIR\uninst.exe"
  CreateShortCut "$DESKTOP\Xuan.lnk" "$INSTDIR\Xuan.exe"

  ; 7. Registry
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${INSTALL_REG_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"

  ; 8. Silent upgrade auto-restart: launcher passes /AUTOSTART after downloading the installer
  ${If} ${Silent}
    ${GetParameters} $R1
    ClearErrors
    ${GetOptions} $R1 "/AUTOSTART" $R2
    ${IfNot} ${Errors}
      Exec '"$INSTDIR\Xuan.exe"'
    ${EndIf}
  ${EndIf}
SectionEnd

; ============ Uninstall ============
Var KeepDataCheckbox
Var KeepDataState

Function un.ShowKeepDataPage
  nsDialogs::Create 1018
  Pop $0
  ${If} $0 == error
    Abort
  ${EndIf}
  ${NSD_CreateLabel} 0 0 100% 24u "Keep user data (log/config/setting.ini)?"
  Pop $0
  ${NSD_CreateCheckBox} 10u 30u 90% 12u "Keep user data (recommended)"
  Pop $KeepDataCheckbox
  ${NSD_SetState} $KeepDataCheckbox ${BST_CHECKED}
  ${NSD_CreateLabel} 10u 50u 90% 24u "Uncheck to also delete log, config and setting.ini"
  Pop $0
  nsDialogs::Show
FunctionEnd

Function un.LeaveKeepDataPage
  ${NSD_GetState} $KeepDataCheckbox $KeepDataState
FunctionEnd

Section "Uninstall"
  nsExec::ExecToLog 'taskkill /f /t /im Xuan.exe'
  Sleep 1000

  ; Safety: $INSTDIR is inferred from uninst.exe location, normally the Xuan app dir.
  ; If abnormal (uninst.exe moved elsewhere), abort deletion to protect user data.
  IfFileExists "$INSTDIR\Xuan.exe" 0 uninst_abort

  ; Shortcuts
  Delete "$SMPROGRAMS\Xuan\Xuan.lnk"
  Delete "$SMPROGRAMS\Xuan\Uninstall Xuan.lnk"
  Delete "$DESKTOP\Xuan.lnk"
  RMDir "$SMPROGRAMS\Xuan"

  ; Program files (src incl. database.db always removed)
  RMDir /r "$INSTDIR\_internal"
  RMDir /r "$INSTDIR\venv"
  RMDir /r "$INSTDIR\backend"
  RMDir /r "$INSTDIR\frontend"
  RMDir /r "$INSTDIR\bin"
  RMDir /r "$INSTDIR\src"
  Delete "$INSTDIR\Xuan.exe"

  ; User data per choice (default keep)
  ${If} $KeepDataState == ${BST_UNCHECKED}
    RMDir /r "$INSTDIR\log"
    RMDir /r "$INSTDIR\config"
    Delete "$INSTDIR\setting.ini"
  ${EndIf}

  Delete "$INSTDIR\uninst.exe"

  ; Registry
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${INSTALL_REG_KEY}"
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_DIR_REGKEY}"

  RMDir "$INSTDIR"
  uninst_abort:
SectionEnd

