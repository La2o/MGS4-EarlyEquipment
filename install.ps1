param([string]$GameRoot='C:\Program Files (x86)\Steam\steamapps\common\METAL GEAR SOLID 4')
$ErrorActionPreference='Stop'
$game=Join-Path $GameRoot 'MGS4'
$exe=Join-Path $game 'mgs4.exe'
if(!(Test-Path -LiteralPath $exe)){throw "mgs4.exe not found: $exe"}
if((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -ne '656EDE900B03467E4ED05A00ECA35F0AC306CE57A8F29A76A20E5A5410D02900'){
    throw 'This mod supports the installed Steam 1.4.1 executable only. No files copied.'
}
$scripts=Join-Path $game 'scripts'
New-Item -ItemType Directory -Path $scripts -Force | Out-Null
$target=Join-Path $scripts 'MGS4EarlyEquipment.asi'
$copyMod=$true
if(Test-Path -LiteralPath $target){
    $oldHash=(Get-FileHash -LiteralPath $target).Hash
    $newHash=(Get-FileHash -LiteralPath "$PSScriptRoot\dist\MGS4\scripts\MGS4EarlyEquipment.asi").Hash
    if($oldHash -ne $newHash){
        if(Get-Process -Name mgs4 -ErrorAction SilentlyContinue){throw 'Close MGS4 before updating the installed ASI.'}
        Copy-Item -LiteralPath $target -Destination "$target.bak" -Force
    } else {$copyMod=$false}
}
if($copyMod){Copy-Item -LiteralPath "$PSScriptRoot\dist\MGS4\scripts\MGS4EarlyEquipment.asi" -Destination $target -Force}
# Preserve existing ASI loaders supplied by other mods.
if(!(Test-Path -LiteralPath (Join-Path $game 'winmm.dll')) -and !(Test-Path -LiteralPath (Join-Path $game 'dinput8.dll'))){
    Copy-Item -LiteralPath "$PSScriptRoot\dist\MGS4\winmm.dll" -Destination (Join-Path $game 'winmm.dll')
}
Copy-Item -LiteralPath "$PSScriptRoot\Launch-MGS4.cmd","$PSScriptRoot\Backup-MGS4Saves.ps1" -Destination $GameRoot -Force
Write-Output "Installed: $target"
Write-Output 'Run Launch-MGS4.cmd to skip the Master Collection launcher.'
