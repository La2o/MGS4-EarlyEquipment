param([string]$Version='0.4.1')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$dist=Join-Path $PSScriptRoot 'dist'
Copy-Item -LiteralPath "$PSScriptRoot/README.md","$PSScriptRoot/Launch-MGS4.cmd","$PSScriptRoot/Backup-MGS4Saves.ps1" -Destination $dist -Force
# An explicit allowlist keeps saves, game assets, PDBs and test helpers out.
$files=@('README.md','Launch-MGS4.cmd','Backup-MGS4Saves.ps1','MGS4/winmm.dll','MGS4/scripts/MGS4EarlyEquipment.asi','licenses/MinHook.txt','licenses/Ultimate-ASI-Loader.txt')
$manifest=[ordered]@{}
foreach($file in $files){$manifest[$file]=(Get-FileHash -LiteralPath (Join-Path $dist $file) -Algorithm SHA256).Hash.ToLowerInvariant()}
$manifest | ConvertTo-Json | Set-Content -LiteralPath "$dist/SHA256.json" -Encoding utf8
$files+='SHA256.json'
$archive=Join-Path $dist "MGS4-EarlyEquipment-$Version.zip"
if(Test-Path -LiteralPath $archive){Remove-Item -LiteralPath $archive -Force}
$zip=[IO.Compression.ZipFile]::Open($archive,[IO.Compression.ZipArchiveMode]::Create)
try {
    foreach($file in $files){[IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $dist $file),$file,[IO.Compression.CompressionLevel]::Optimal) | Out-Null}
} finally {$zip.Dispose()}
Write-Output "Packaged: $archive"
Write-Output "SHA-256: $((Get-FileHash -LiteralPath $archive).Hash)"
