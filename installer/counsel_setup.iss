#define MyAppName "counselog"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "전문상담교사 박재현"
#define MyAppExeName "counselog.exe"
#define MyAppIconPath "..\assets\counselog.ico"

[Setup]
AppId={{9DEB1AB8-7B73-4E0F-9B3C-EF65E0E5B401}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=counselog_setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
#ifexist MyAppIconPath
SetupIconFile={#MyAppIconPath}
UninstallDisplayIcon={app}\{#MyAppExeName}
#endif

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면 바로가기 생성"; GroupDescription: "추가 작업:"; Flags: unchecked

[Files]
Source: "..\dist\counselog\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
#ifexist MyAppIconPath
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"
#else
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
#endif

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} 실행"; Flags: nowait postinstall skipifsilent
