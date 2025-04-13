[Setup]
AppName=MockupBuddy
AppVersion=0.8.1
DefaultDirName={pf}\MockupBuddy
DefaultGroupName=MockupBuddy
OutputDir=Output
OutputBaseFilename=MockupBuddyInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\MockupBuddy.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\MockupBuddy.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*.png"; DestDir: "{app}\images"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{cm:LaunchApplication,MockupBuddy}"; Filename: "{app}\MockupBuddy.exe"

[Run]
Filename: "{app}\MockupBuddy.exe"; Description: "{cm:LaunchApplication,MockupBuddy}"; Flags: nowait postinstall skipifsilent

[UninstallRun]