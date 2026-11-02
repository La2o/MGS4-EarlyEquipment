@echo off
rem Game language. Use one pair: English eu en, French eu fr, Italian eu it,
rem German eu gr, Spanish eu sp, Portuguese eu pt, Japanese jp jp.
set "MGS4_REGION=eu"
set "MGS4_LANGUAGE=en"

powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0Backup-MGS4Saves.ps1"
if errorlevel 1 (
  echo Save backup failed. MGS4 was not started.
  pause
  exit /b 1
)
set "SteamAppId=2492670"
set "SteamGameId=2492670"
cd /d "%~dp0MGS4"
start "" "mgs4.exe" -region %MGS4_REGION% -lan %MGS4_LANGUAGE% -selfregion EU -resolution 0 -ctrltype AUTO
