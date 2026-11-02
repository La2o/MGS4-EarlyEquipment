"""Live-test results go to ignored build/reports, never over the tracked evidence in docs/.

The docs/ reports also hold results from one-off runs that no script reproduces,
so a new result is promoted by reviewing it and merging it in by hand. Each save
appends to <name>.runs.json which script wrote it, when, and the hash/version of
every project module loaded in the game, so results are never labeled by guess.
"""
import ctypes,datetime,functools,hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'external/mgs4trainer'))
from mgs4trainer.core.winproc import kernel32,MODULEENTRY32,TH32CS_SNAPMODULE,INVALID_HANDLE_VALUE
REPORTS=ROOT/'build/reports'
WATCHED=('mgs4.exe','MGS4EarlyEquipment.asi','MGS4EarlyEquipmentLive.asi','EEDev.asi','EEGameProbe.dll')

@functools.lru_cache
def modules(pid):
    """Watched modules loaded in the process: file path, SHA-256 and embedded mod version."""
    found={};watched={n.lower() for n in WATCHED}
    snapshot=kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,pid)
    if snapshot==INVALID_HANDLE_VALUE:return found
    try:
        entry=MODULEENTRY32();entry.dwSize=ctypes.sizeof(entry);ok=kernel32.Module32First(snapshot,ctypes.byref(entry))
        while ok:
            name=entry.szModule.decode('mbcs','ignore')
            if name.lower() in watched:
                path=pathlib.Path(entry.szExePath.decode('mbcs','ignore'));data=path.read_bytes()
                version=re.search(rb'MGS4 Early Equipment ([0-9.]+) starting',data)
                found[name]={'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'version':version and version[1].decode()}
            ok=kernel32.Module32Next(snapshot,ctypes.byref(entry))
    finally:kernel32.CloseHandle(snapshot)
    return found

def asi_version(pid,module='MGS4EarlyEquipment.asi'):
    """Version string compiled into the loaded module, or None if it is not loaded."""
    return next((m['version'] for n,m in modules(pid).items() if n.lower()==module.lower()),None)

def load(name,default):
    """This session's result so far, for scripts that extend another script's report."""
    path=REPORTS/name
    return json.loads(path.read_text()) if path.exists() else default

def save(name,data,pid):
    REPORTS.mkdir(parents=True,exist_ok=True)
    (REPORTS/name).write_text(json.dumps(data,indent=2)+'\n')
    log=pathlib.Path(name).stem+'.runs.json';runs=load(log,[])
    runs.append({'script':pathlib.Path(sys.argv[0]).name,'recorded':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'modules':modules(pid)})
    (REPORTS/log).write_text(json.dumps(runs,indent=2)+'\n')
    print(f'Wrote {REPORTS/name}; docs/ is unchanged. Review before promoting any result.')
