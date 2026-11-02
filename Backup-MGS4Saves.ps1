param([string]$GameRoot=$PSScriptRoot)
$ErrorActionPreference='Stop'
function SaveFileHash([string]$Path){
    $stream=[IO.File]::OpenRead($Path)
    $sha=[Security.Cryptography.SHA256]::Create()
    try {return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLowerInvariant()}
    finally {$sha.Dispose();$stream.Dispose()}
}
try {
    $root=[IO.Path]::GetFullPath($GameRoot)
    $exe=Join-Path $root 'MGS4/mgs4.exe'
    if(Get-Process -Name mgs4 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq $exe}){
        throw 'Close this copy of MGS4 before backing up its saves.'
    }
    $source=Join-Path $root 'mgs4_savedata_win'
    if(!(Test-Path -LiteralPath $source -PathType Container)){
        Write-Output 'No existing MGS4 saves to back up.'
        exit 0
    }
    # Never replace or prune an older backup. A manifest marks a complete copy.
    $stamp=(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+[guid]::NewGuid().ToString('N').Substring(0,8)
    $destination=Join-Path $root "MGS4-SaveBackups/$stamp"
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    $manifest=[ordered]@{}
    foreach($file in Get-ChildItem -LiteralPath $source -Recurse -File -Force){
        $relative=$file.FullName.Substring($source.Length).TrimStart('\','/')
        $copy=Join-Path $destination $relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $copy) -Force | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $copy
        $hash=SaveFileHash $file.FullName
        if((SaveFileHash $copy) -ne $hash){
            throw "Save backup verification failed: $relative"
        }
        $manifest[$relative]=$hash.ToLowerInvariant()
    }
    # Detect a cloud sync or another writer changing the source during copying.
    $current=@(Get-ChildItem -LiteralPath $source -Recurse -File -Force)
    if($current.Count -ne $manifest.Count){throw 'Save files changed during backup; retry before launching.'}
    foreach($file in $current){
        $relative=$file.FullName.Substring($source.Length).TrimStart('\','/')
        if(!$manifest.Contains($relative) -or (SaveFileHash $file.FullName) -ne $manifest[$relative]){
            throw 'Save files changed during backup; retry before launching.'
        }
    }
    $manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $destination 'BACKUP-SHA256.json') -Encoding utf8
    Write-Output "Verified save backup: $destination"
} catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
