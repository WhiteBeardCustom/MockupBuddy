[Setup]
AppName=MockupBuddy
AppVersion=0.8.1
DefaultDirName={pf}\MockupBuddy
DefaultGroupName=MockupBuddy
OutputDir=Output
OutputBaseFilename=MockupBuddyInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE
SetupIconFile=src\assets\MockupBuddyDesktop.ico
DisableProgramGroupPage=yes
AllowNoIcons=yes

[Files]
Source: "dist\MockupBuddy_PySide6_v0.8.1\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "src\assets\*.png"; DestDir: "{app}\images"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\MockupBuddy"; Filename: "{app}\MockupBuddy_PySide6_v0.8.1.exe"
Name: "{userdesktop}\MockupBuddy"; Filename: "{app}\MockupBuddy_PySide6_v0.8.1.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\MockupBuddy_PySide6_v0.8.1.exe"; Description: "Launch MockupBuddy"; Flags: nowait postinstall skipifsilent unchecked

[UninstallRun]