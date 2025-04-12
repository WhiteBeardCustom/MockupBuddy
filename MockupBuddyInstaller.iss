; Script generated manually for MockupBuddy

[Setup]
AppName=MockupBuddy
AppVersion=0.8.0
AppPublisher=White Beard Custom, LLC
AppPublisherURL=https://mockupbuddypro.com
AppSupportURL=https://mockupbuddypro.com/support
AppUpdatesURL=https://mockupbuddypro.com/downloads
AppID=MockupBuddy
DefaultDirName={pf}\MockupBuddy
DefaultGroupName=MockupBuddy
UninstallDisplayIcon={app}\MockupBuddy_PySide6_v0.8.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=MockupBuddy_Installer_v0.8.0
DisableProgramGroupPage=yes
SetupIconFile=.\src\assets\MockupBuddyDesktop.ico
LicenseFile=license.txt
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

[Files]
Source: "dist\MockupBuddy_PySide6_v0.8\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\MockupBuddy"; Filename: "{app}\MockupBuddy_PySide6_v0.8.exe"
Name: "{userdesktop}\MockupBuddy"; Filename: "{app}\MockupBuddy_PySide6_v0.8.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"