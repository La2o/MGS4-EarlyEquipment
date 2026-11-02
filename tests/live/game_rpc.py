"""Development-only client for tests/game_probe.c."""
import ctypes,struct,time,sys,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'external/mgs4trainer'))
from mgs4trainer.core.winproc import find_pid,find_module_base,ProcessHandle
from ctypes import wintypes as w
class GameRpc:
    def __init__(self, executable='mgs4.exe'):
        k=self.k=ctypes.WinDLL('kernel32',use_last_error=True)
        k.OpenFileMappingW.argtypes=[w.DWORD,w.BOOL,w.LPCWSTR];k.OpenFileMappingW.restype=w.HANDLE
        k.MapViewOfFile.argtypes=[w.HANDLE,w.DWORD,w.DWORD,w.DWORD,ctypes.c_size_t];k.MapViewOfFile.restype=w.LPVOID
        k.UnmapViewOfFile.argtypes=[w.LPCVOID];k.CloseHandle.argtypes=[w.HANDLE]
        self.mapping=k.OpenFileMappingW(0xf001f,False,'Local\\MGS4EarlyEquipmentTests')
        if not self.mapping:raise OSError('Test helper is not loaded')
        self.memory=k.MapViewOfFile(self.mapping,0xf001f,0,0,4096)
        self.pid=find_pid(executable);self.base=find_module_base(self.pid,executable);self.proc=ProcessHandle(self.pid)
    def call(self,fn,*args,timeout=10):
        data=struct.pack('<IIQ4QQ',0,0,fn,*(list(args)+[0]*4)[:4],0)
        ctypes.memmove(self.memory,data,len(data));ctypes.c_int32.from_address(self.memory).value=1
        deadline=time.monotonic()+timeout
        while not ctypes.c_int32.from_address(self.memory+4).value:
            if time.monotonic()>deadline:raise TimeoutError('Game-thread test call did not finish')
            time.sleep(.01)
        return ctypes.c_uint64.from_address(self.memory+48).value
    def export(self,name,module_name='EEGameProbe.dll',path=ROOT/'build/EEGameProbe.dll'):
        import pefile
        module=find_module_base(self.pid,module_name);assert module
        pe=pefile.PE(str(path))
        return module+next(s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==name.encode())
    def close(self):
        self.proc.close();self.k.UnmapViewOfFile(self.memory);self.k.CloseHandle(self.mapping)
if __name__=='__main__':
    r=GameRpc();print('RPC test',r.call(r.base+0x3ed970));r.close()
