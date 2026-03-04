[Setup]
AppName=QE Defect AI
AppVersion=1.0
DefaultDirName={autopf}\QE Defect AI
DefaultGroupName=QE Defect AI
UninstallDisplayIcon={app}\DefectRecurrenceDetector.exe
ArchitecturesInstallIn64BitMode=x64
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename=QE_Defect_AI_Setup
CloseApplications=yes
CloseApplicationsFilter=DefectRecurrenceDetector.exe
PrivilegesRequired=admin 
[Files]
Source: "dist\DefectRecurrenceDetector.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Icon_1.ico"; DestDir: "{app}"; DestName: "app.ico"; Flags: ignoreversion

[Icons]
Name: "{group}\QE Defect AI"; Filename: "{app}\DefectRecurrenceDetector.exe"; IconFilename: "{app}\app.ico"
Name: "{group}\Uninstall QE Defect AI"; Filename: "{uninstallexe}"
Name: "{autodesktop}\QE Defect AI"; Filename: "{app}\DefectRecurrenceDetector.exe"; IconFilename: "{app}\app.ico"

[Run]
Filename: "{app}\DefectRecurrenceDetector.exe"; Description: "Launch QE Defect AI"; Flags: postinstall nowait skipifsilent

[Code]
procedure CreateCacheDir;
var
  CachePath: string;
begin
  CachePath := ExpandConstant('{localappdata}\QE Defect AI\cache');
  if not DirExists(CachePath) then
    ForceDirectories(CachePath);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    CreateCacheDir;
end;