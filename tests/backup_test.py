"""Integration checks for verified backups and the launcher's failure path."""
from pathlib import Path
import hashlib, json, shutil, subprocess, time, uuid

root=Path(__file__).resolve().parents[1]
fixture=root/'build'/('backup-test-'+uuid.uuid4().hex[:8])
(fixture/'MGS4').mkdir(parents=True)
(fixture/'mgs4_savedata_win'/'test-profile').mkdir(parents=True)
payload=bytes(range(256))*16
(fixture/'mgs4_savedata_win'/'test-profile'/'MGS4.SAV').write_bytes(payload)
for name in ['Launch-MGS4.cmd','Backup-MGS4Saves.ps1']:
    shutil.copy2(root/name,fixture/name)
subprocess.run([str(root/'tools/zig-windows-x86_64-0.13.0/zig.exe'),'cc','-O2',
                str(root/'tests/launch_marker.c'),'-o',str(fixture/'MGS4/mgs4.exe')],check=True)

def backup():
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass',
                    '-File',str(fixture/'Backup-MGS4Saves.ps1')],capture_output=True)
    assert result.returncode==0,(result.stdout,result.stderr)

# Force a real filesystem failure rather than mocking the script result.
(fixture/'MGS4-SaveBackups').write_bytes(b'not a directory')
failed=subprocess.run(['cmd.exe','/c',str(fixture/'Launch-MGS4.cmd')],cwd=fixture,
                      input=b'\r\n',capture_output=True,timeout=15)
assert failed.returncode==1 and not (fixture/'MGS4/game-started.marker').exists()
(fixture/'MGS4-SaveBackups').unlink()
backup();backup()
copies=list((fixture/'MGS4-SaveBackups').iterdir())
assert len(copies)==2
for directory in copies:
    manifest=json.loads((directory/'BACKUP-SHA256.json').read_text(encoding='utf-8-sig'))
    assert len(manifest)==1
    for name,digest in manifest.items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest==hashlib.sha256(payload).hexdigest()
assert (fixture/'mgs4_savedata_win/test-profile/MGS4.SAV').read_bytes()==payload
started=subprocess.run(['cmd.exe','/c',str(fixture/'Launch-MGS4.cmd')],cwd=fixture,capture_output=True,timeout=15)
assert started.returncode==0
for _ in range(30):
    if (fixture/'MGS4/game-started.marker').exists():break
    time.sleep(.1)
assert (fixture/'MGS4/game-started.marker').exists()
report={'backup_failure_blocks_game_launch':True,'success_starts_game_after_backup':True,
        'backups_preserve_exact_bytes':True,'previous_backups_not_overwritten':True,
        'source_saves_unchanged':True}
# Results go to ignored build/reports; docs/backup-tests.json is reviewed evidence.
out=root/'build'/'reports';out.mkdir(parents=True,exist_ok=True)
(out/'backup-tests.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Backup integration checks passed. Wrote',out/'backup-tests.json')
