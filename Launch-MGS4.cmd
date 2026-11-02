@echo off
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0Backup-MGS4Saves.ps1"
if errorlevel 1 (
  echo Save backup failed. MGS4 was not started.
  pause
  exit /b 1
)
set "SteamAppId=2492670"
set "SteamGameId=2492670"
cd /d "%~dp0MGS4"
start "" "mgs4.exe" -region eu -lan en -selfregion EU -resolution 0 -ctrltype AUTO
