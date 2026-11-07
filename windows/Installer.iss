#ifndef AppVersion
  #define AppVersion "0.2.0"
#endif
[Setup]
AppId={{E48CF7E3-EABA-48CF-94FC-0C7412C3CF5E}
AppName=Egress Workbench
AppVersion={#AppVersion}
AppPublisher=Egress Workbench
AppPublisherURL=https://github.com/engeeeee/egress-workbench-app
AppSupportURL=https://github.com/engeeeee/egress-workbench-app/releases
DefaultDirName={localappdata}\Programs\EgressWorkbench
DefaultGroupName=Egress Workbench
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=dist
OutputBaseFilename=Egress-Workbench-Windows-x64-{#AppVersion}-Setup
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\EgressWorkbench.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no
VersionInfoDescription=Egress Workbench Windows installer
VersionInfoVersion={#AppVersion}

[Languages]
Name: "chinesesimp"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："

[Files]
Source: "dist\EgressWorkbench\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Egress Workbench"; Filename: "{app}\EgressWorkbench.exe"; AppUserModelID: "EgressWorkbench.Windows"
Name: "{autodesktop}\Egress Workbench"; Filename: "{app}\EgressWorkbench.exe"; Tasks: desktopicon; AppUserModelID: "EgressWorkbench.Windows"

[Run]
Filename: "{app}\EgressWorkbench.exe"; Description: "启动 Egress Workbench"; Flags: nowait postinstall skipifsilent
