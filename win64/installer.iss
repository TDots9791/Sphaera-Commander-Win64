; Установщик Sphaera Commander Windows (ТЗ §5, Ф4).
; Сборка (версию подставляет CI из CORE_VERSION.txt):
;   ISCC win64\installer.iss /DAPP_VERSION=0.22.2
; Конфиг пользователя (%APPDATA%\SphaeraCommander) установщик и
; деинсталлятор НЕ трогают — конфиг переживает обновление (ТЗ §5 Ф4);
; удаление настроек — осознанное действие пользователя.

#define AppName "Sphaera Commander"
#ifndef APP_VERSION
#define APP_VERSION "0.0.0"
#endif

[Setup]
AppId={{B8CE0EF6-B7C3-4EBF-9C89-7489BB311EA5}
AppName={#AppName}
AppVersion={#APP_VERSION}
AppPublisher=Sphaera
DefaultDirName={autopf}\SphaeraCommander
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
SourceDir=..
OutputDir=dist-installer
OutputBaseFilename=SphaeraCommander-{#APP_VERSION}-setup
SetupIconFile=win64\sphaera-commander.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\SphaeraCommander.exe
; 64-битный режим установки: иначе Inno кладёт {autopf} в Program Files (x86)
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktop"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\SphaeraCommander\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\SphaeraCommander.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\SphaeraCommander.exe"; Tasks: desktop

[Registry]
Root: HKCR; Subkey: "Directory\shell\SphaeraCommander"; ValueType: string; ValueData: "Открыть в Sphaera Commander"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\SphaeraCommander"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\SphaeraCommander.exe"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\SphaeraCommander\command"; ValueType: string; ValueData: """{app}\SphaeraCommander.exe"" ""%1"""; Flags: uninsdeletekey

[Run]
Filename: "{app}\SphaeraCommander.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
