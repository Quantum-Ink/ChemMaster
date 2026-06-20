; ChemMaster Inno Setup Script
; Requires Inno Setup 6+ (https://jrsoftware.org/isinfo.php)

#define MyAppName "ChemMaster"
#define MyAppVersion "1.0.7"
#define MyAppPublisher "ChemMaster"
#define MyAppURL "https://github.com/Quantum-Ink/ChemMaster"
#define MyAppExeName "ChemMaster.exe"

[Setup]
AppId={{B9E3A970-6F1A-4C5D-8E2B-1A3B5C7D9E0F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=..\LICENSE
OutputDir=..\build\installer
OutputBaseFilename=ChemMaster-Setup-{#MyAppVersion}
SetupIconFile=..\build\windows\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\build\bin\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Register file associations for .mol and .sdf files
Root: HKA; Subkey: "Software\Classes\.mol\OpenWithProgids"; ValueType: string; ValueName: "ChemMaster.mol"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.sdf\OpenWithProgids"; ValueType: string; ValueName: "ChemMaster.sdf"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\ChemMaster.mol"; ValueType: string; ValueName: ""; ValueData: "ChemMaster MOL File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\ChemMaster.mol\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\ChemMaster.mol\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\ChemMaster.sdf"; ValueType: string; ValueName: ""; ValueData: "ChemMaster SDF File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\ChemMaster.sdf\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\ChemMaster.sdf\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[UninstallDelete]
Type: filesandordirs; Name: "{app}\.chemmaster"
Type: filesandordirs; Name: "{app}\tmp"
