param([string]$Zig = "$PSScriptRoot\tools\zig-windows-x86_64-0.13.0\zig.exe")
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path "$PSScriptRoot\dist\MGS4\scripts","$PSScriptRoot\build" -Force | Out-Null
$sources=@('src/early_equipment.c','external/minhook/src/buffer.c','external/minhook/src/hook.c','external/minhook/src/trampoline.c','external/minhook/src/hde/hde64.c')
Push-Location $PSScriptRoot
try {
    & $Zig cc -target x86_64-windows-gnu -O2 -Wall -Wextra -shared -Iexternal/minhook/include @sources -ladvapi32 -o dist/MGS4/scripts/MGS4EarlyEquipment.asi
    if($LASTEXITCODE){throw 'Mod compilation failed.'}
    & $Zig cc -target x86_64-windows-gnu -O2 -UNDEBUG -Wall -Wextra tests/policy_test.c -o build/policy_test.exe
    if($LASTEXITCODE){throw 'Test compilation failed.'}
    & .\build\policy_test.exe
    if($LASTEXITCODE){throw 'Policy checks failed.'}
} finally {Pop-Location}
