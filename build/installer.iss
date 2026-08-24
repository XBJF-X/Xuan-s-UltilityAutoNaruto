; =========================================================
; Xuan Inno Setup installer script (UTF-8, 需带 BOM 编译)
; - Installs build/release/* -> {app} (default %LOCALAPPDATA%\Xuan)
; - Upgrade: enumerates the old-version leftovers that will be deleted and
;   explicitly lists them on a confirmation page (user data config/log/setting.ini kept)
; - Uninstall: asks whether to keep user data (log/config/setting.ini);
;   src (incl. database.db) is always removed (developer-maintained data)
; - Install path registry key HKCU\Software\Xuan\Xuan\InstallLocation is inherited
;   (same key as the previous NSIS installer)
; - Version & release dir passed by build_release.py via /DMyAppVersion /DReleaseDir
; =========================================================
#define MyAppName "Xuan"
#define MyAppVersion "0.17.17"
#define MyAppPublisher "Xuan"
#define MyAppURL "https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto"
#define MyAppExeName "Xuan.exe"

#ifndef MyAppIcon
  #define MyAppIcon "{#SourcePath}..\src\ASDS.ico"
#endif

; 安装内容目录（build_release.py 通过 /DReleaseDir 传入绝对路径）
#ifndef ReleaseDir
  #define ReleaseDir "release"
#endif

[Setup]
; 应用标识：卸载注册表键名为 <AppId>_is1（HKCU，因 PrivilegesRequired=lowest）
AppId=Xuan
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
; 默认安装目录：%LOCALAPPDATA%\Xuan；旧路径从注册表继承（见 [Code] InitializeWizard）
DefaultDirName={localappdata}\Xuan
DefaultGroupName={#MyAppName}
; 不显示程序组选择页，开始菜单固定为 Xuan
DisableProgramGroupPage=yes
; 无论是否已安装过，始终显示目录选择页（已安装时自动预填上次路径，用户仍可修改）
DisableDirPage=no
; per-user 安装（注册表写 HKCU，与 NSIS 的 PRODUCT_UNINST_ROOT_KEY=HKCU 一致）
PrivilegesRequired=lowest
OutputDir=out
OutputBaseFilename=XuanInstaller_V{#MyAppVersion}
SetupIconFile={#MyAppIcon}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
; 简体中文语言文件随仓库分发（build/languages/），不依赖编译机 Inno Setup 安装目录
Name: "chinesesimplified"; MessagesFile: "languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; 整个 release 目录（Xuan.exe + _internal(portable venv) + backend + frontend/dist + src + bin/ppocrv5）
Source: "{#ReleaseDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 开始菜单 Xuan\Xuan.lnk、Xuan\Uninstall Xuan.lnk、桌面 Xuan.lnk（与 NSIS 一致）
Name: "{autoprograms}\{#MyAppName}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autoprograms}\{#MyAppName}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

[Registry]
; 安装路径注册表键（NSIS 同款继承）：HKCU\Software\Xuan\Xuan\InstallLocation = {app}
; 下次安装时 [Code] InitializeWizard 读取该键恢复上次安装目录
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"; Flags: uninsdeletekey

[Run]
; 安装完成运行 Xuan（静默升级不运行，由 /AUTOSTART 逻辑接管）
Filename: "{app}\{#MyAppExeName}"; Description: "运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 程序文件兜底删除（含热更新新增内容），卸载器会先删自身安装的文件
; 用户数据 config/log/setting.ini 按卸载时选择处理（见 [Code] usPostUninstall）
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\backend"
Type: filesandordirs; Name: "{app}\frontend"
Type: filesandordirs; Name: "{app}\bin"
Type: filesandordirs; Name: "{app}\src"
Type: files; Name: "{app}\{#MyAppExeName}"

; 取消/中止安装的中文确认消息（安装过程中 Cancel 按钮始终可用，允许用户中断）
[Messages]
ExitSetupTitle=退出安装
ExitSetupMessage=安装尚未完成。如果现在退出，程序将不会被安装。%n%n您可以在之后随时重新运行安装程序以完成安装。%n%n是否退出安装？
SetupAborted=安装未完成。%n%n请解决该问题后重新运行安装程序。

[Code]
type
  // Win32 MSG 结构（供 PeekMessage 使用；pt 用两个 LongWord 表示 POINT 布局）
  TMsg = record
    hwnd: LongWord;
    message: Cardinal;
    wParam: LongWord;
    lParam: LongWord;
    time: LongWord;
    ptX: LongWord;
    ptY: LongWord;
  end;

  // SHFILEOPSTRUCT（移入回收站用；pFrom/pTo 为双 null 结尾的路径列表）
  TSHFileOpStruct = record
    hwnd: LongWord;
    wFunc: LongWord;
    pFrom: String;
    pTo: String;
    fFlags: LongWord;
    fAnyOperationsAborted: Integer; // BOOL 为 4 字节，保持结构布局
    hNameMappings: LongWord;
    lpszProgressTitle: String;
  end;

function PeekMessage(var lpMsg: TMsg; hWnd, wMsgFilterMin, wMsgFilterMax, wRemoveMsg: LongWord): Integer;
  external 'PeekMessageW@user32.dll stdcall';
function TranslateMessage(const lpMsg: TMsg): Integer;
  external 'TranslateMessage@user32.dll stdcall';
function DispatchMessage(const lpMsg: TMsg): Integer;
  external 'DispatchMessageW@user32.dll stdcall';
function SHFileOperation(const lpFileOp: TSHFileOpStruct): Integer;
  external 'SHFileOperationW@shell32.dll stdcall';

// 处理待处理窗口消息（让 Cancel 按钮点击能被响应，从而支持中断清理/安装）
procedure PumpMessages;
var
  Msg: TMsg;
begin
  while PeekMessage(Msg, 0, 0, 0, 1) > 0 do // PM_REMOVE = 1
  begin
    TranslateMessage(Msg);
    DispatchMessage(Msg);
  end;
end;

// 将单个文件/目录移入回收站（FO_DELETE + FOF_ALLOWUNDO）；成功返回 True，失败返回 False
function RecyclePath(const Path: String): Boolean;
var
  FileOp: TSHFileOpStruct;
begin
  Result := False;
  try
    FileOp.hwnd := WizardForm.Handle;
    FileOp.wFunc := 3;                        // FO_DELETE
    FileOp.pFrom := Path + #0 + #0;           // 双 null 结尾
    FileOp.pTo := '';
    // FOF_ALLOWUNDO(回收站) | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI
    FileOp.fFlags := $40 or $10 or $4 or $400;
    FileOp.fAnyOperationsAborted := 0;
    FileOp.hNameMappings := 0;
    FileOp.lpszProgressTitle := '';
    Result := (SHFileOperation(FileOp) = 0);
  except
    Result := False;
  end;
end;

const
  InstallRegKey = 'Software\Xuan\Xuan';
  InstallValueName = 'InstallLocation';
  WebView2Key1 = 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  WebView2Key2 = 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';

var
  CleanupPage: TWizardPage;
  CleanupMemo: TNewMemo;
  KeepUserData: Boolean;

// ============ 工具函数 ============

function CmdLineParamExists(const Param: String): Boolean;
var
  CmdLine: String;
begin
  CmdLine := ' ' + GetCmdTail() + ' ';
  Result := (Pos(' ' + Param + ' ', CmdLine) > 0);
end;

function WebView2Present(): Boolean;
var
  Pv: String;
begin
  Result := True;
  if RegQueryStringValue(HKLM, WebView2Key1, 'pv', Pv) then Exit;
  if RegQueryStringValue(HKLM, WebView2Key2, 'pv', Pv) then Exit;
  Result := False;
end;

// 枚举目标目录顶层（排除用户数据 config/log/setting.ini），返回将被删除的文件/目录清单
function BuildCleanupList(const Dir: String): String;
var
  FindRec: TFindRec;
begin
  Result := '';
  if not FindFirst(AddBackslash(Dir) + '*', FindRec) then Exit;
  try
    repeat
      if (FindRec.Name = '.') or (FindRec.Name = '..') or
         (FindRec.Name = 'config') or (FindRec.Name = 'log') or
         (FindRec.Name = 'setting.ini') then
        Continue;
      if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
        Result := Result + '[目录] ' + FindRec.Name + #13#10
      else
        Result := Result + '[文件] ' + FindRec.Name + #13#10;
    until not FindNext(FindRec);
  finally
    FindClose(FindRec);
  end;
  if Result <> '' then
    Result := '目标目录: ' + Dir + #13#10 + '------------------------------' + #13#10 + Result;
end;

// 删除目标目录顶层（排除用户数据），与确认清单保持一致
procedure DeleteCleanup(const Dir: String);
var
  FindRec: TFindRec;
  ItemPath: String;
begin
  if not FindFirst(AddBackslash(Dir) + '*', FindRec) then Exit;
  try
    repeat
      // 处理取消消息，允许用户在清理旧残留期间中断安装
      PumpMessages;
      // Inno 在用户确认取消后禁用 Cancel 按钮；据此中断清理循环
      if not WizardForm.CancelButton.Enabled then
        Break;
      if (FindRec.Name = '.') or (FindRec.Name = '..') or
         (FindRec.Name = 'config') or (FindRec.Name = 'log') or
         (FindRec.Name = 'setting.ini') then
        Continue;
      ItemPath := AddBackslash(Dir) + FindRec.Name;
      if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
      begin
        // 优先移入回收站（可恢复），失败则回退永久删除
        if not RecyclePath(ItemPath) then
          DelTree(ItemPath, True, True, True);
      end
      else
      begin
        if not RecyclePath(ItemPath) then
          DeleteFile(ItemPath);
      end;
    until not FindNext(FindRec);
  finally
    FindClose(FindRec);
  end;
end;

// ============ 安装事件 ============

// 1. 从注册表读取上次安装路径（继承）；2. 创建升级清理确认页
procedure InitializeWizard();
var
  PrevDir: String;
begin
  // 安装路径继承：读取 HKCU\Software\Xuan\Xuan\InstallLocation（NSIS 同款注册表键）
  if RegQueryStringValue(HKCU, InstallRegKey, InstallValueName, PrevDir) then
  begin
    if DirExists(PrevDir) then
      WizardForm.DirEdit.Text := PrevDir;
  end;

  // 升级清理确认页（插在 wpReady 之后，仅升级安装时进入）
  CleanupPage := CreateCustomPage(wpReady, '升级清理确认',
    '检测到旧版本文件，请核对将清理的内容。除用户数据（config、log、setting.ini）外，旧版本文件将被移入回收站（可从回收站恢复），确认后点击"下一步"继续。');
  CleanupMemo := TNewMemo.Create(WizardForm);
  with CleanupMemo do
  begin
    Parent := CleanupPage.Surface;
    Left := ScaleX(8);
    Top := ScaleY(8);
    Width := CleanupPage.SurfaceWidth - ScaleX(16);
    Height := CleanupPage.SurfaceHeight - ScaleY(16);
    ReadOnly := True;
    ScrollBars := ssVertical;
    WordWrap := True;
  end;
end;

// wpReady 下一步：WebView2 检查 + 升级清理文件列表确认
function NextButtonClick(CurPageID: Integer): Boolean;
var
  AppDir: String;
  FilesList: String;
begin
  Result := True;

  // 目录页下一步：用户选定路径末段不是 Xuan 时，追加 \Xuan 作为应用目录（确定性行为）
  if CurPageID = wpSelectDir then
  begin
    if CompareText(ExtractFileName(WizardForm.DirEdit.Text), 'Xuan') <> 0 then
      WizardForm.DirEdit.Text := AddBackslash(WizardForm.DirEdit.Text) + 'Xuan';
  end;

  if CurPageID = wpReady then
  begin
    // WebView2 Runtime 检查（缺失仅警告，允许继续）
    if not WebView2Present() then
    begin
      if MsgBox('未检测到 WebView2 Runtime，应用界面可能无法正常显示。' + #13#10 + #13#10 +
                '是否仍要继续安装？',
                mbConfirmation, MB_YESNO) = IDNO then
      begin
        Result := False;
        Exit;
      end;
    end;

    // 升级安装：目标目录存在旧版本（Xuan.exe）时，列出将被删除的文件并让用户确认
    AppDir := ExpandConstant('{app}');
    if FileExists(AppDir + '\Xuan.exe') then
    begin
      FilesList := BuildCleanupList(AppDir);
      if FilesList <> '' then
      begin
        CleanupMemo.Text := FilesList;
        Result := True; // 进入清理确认页
        Exit;
      end;
    end;
  end;
end;

// 安装开始前杀掉运行中的 Xuan 进程树（避免 pyd/dll 被占用）
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  Exec('taskkill.exe', '/f /t /im Xuan.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(1000);
end;

// 文件复制前执行旧版本残留清理（与确认清单一致）
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssInstall then
  begin
    if FileExists(ExpandConstant('{app}\Xuan.exe')) then
      DeleteCleanup(ExpandConstant('{app}'));
  end;

  if CurStep = ssPostInstall then
  begin
    // 静默升级（launcher 大更新）：/VERYSILENT ... /AUTOSTART 安装完成后自启动
    if (CmdLineParamExists('/SILENT') or CmdLineParamExists('/VERYSILENT'))
       and CmdLineParamExists('/AUTOSTART') then
    begin
      Exec(ExpandConstant('{app}\Xuan.exe'), '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
    end;
  end;
end;

// ============ 卸载事件 ============

// 卸载开始：安全校验（Xuan.exe 存在性）+ 询问是否保留用户数据
function InitializeUninstall(): Boolean;
begin
  Result := True;

  // 安全校验：$INSTDIR 由卸载器位置推断，正常情况下为 Xuan 应用目录；
  // 若 Xuan.exe 不存在（卸载器被移动等异常情况），提示用户避免误删数据
  if not FileExists(ExpandConstant('{app}\Xuan.exe')) then
  begin
    if MsgBox('未找到 ' + ExpandConstant('{app}\Xuan.exe') + '。' + #13#10 +
              '为避免误删数据，建议中止卸载。' + #13#10 + #13#10 +
              '是否仍要继续卸载？',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;

  // 询问是否保留用户数据（config/log/setting.ini），默认保留
  KeepUserData := True;
  if MsgBox('是否保留用户数据（config、log、setting.ini）？' + #13#10 + #13#10 +
            '选择"是"保留（推荐），下次安装可继续使用；' + #13#10 +
            '选择"否"将同时删除用户数据。',
            mbConfirmation, MB_YESNO) = IDNO then
    KeepUserData := False;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
  AppDir: String;
begin
  // 卸载最开始时杀掉运行中的 Xuan 进程树
  if CurUninstallStep = usAppMutexCheck then
  begin
    Exec('taskkill.exe', '/f /t /im Xuan.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Sleep(1000);
  end;

  // 卸载完成：按选择处理用户数据；清理旧版 NSIS 安装遗留的注册表键
  if CurUninstallStep = usPostUninstall then
  begin
    if not KeepUserData then
    begin
      AppDir := ExpandConstant('{app}');
      DelTree(AppDir + '\config', True, True, True);
      DelTree(AppDir + '\log', True, True, True);
      DeleteFile(AppDir + '\setting.ini');
    end;
    // 兼容旧 NSIS 安装器：删除其写入/使用的注册表键（本安装器的键由 [Registry] uninsdeletekey 自动清理）
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\Xuan');
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Microsoft\Windows\CurrentVersion\App Paths\Xuan.exe');
  end;
end;

