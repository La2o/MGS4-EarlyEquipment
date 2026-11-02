"""Development-only: load our compiled ASI into the already running game."""
import ctypes,sys,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'external/mgs4trainer'))
from mgs4trainer.core.winproc import find_pid,find_module_base
from ctypes import wintypes as w
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
k.VirtualAllocEx.argtypes=[w.HANDLE,w.LPVOID,ctypes.c_size_t,w.DWORD,w.DWORD];k.VirtualAllocEx.restype=w.LPVOID
k.WriteProcessMemory.argtypes=[w.HANDLE,w.LPVOID,w.LPCVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)];k.WriteProcessMemory.restype=w.BOOL
k.GetModuleHandleW.argtypes=[w.LPCWSTR];k.GetModuleHandleW.restype=w.HMODULE
k.GetProcAddress.argtypes=[w.HMODULE,ctypes.c_char_p];k.GetProcAddress.restype=w.LPVOID
k.CreateRemoteThread.argtypes=[w.HANDLE,w.LPVOID,ctypes.c_size_t,w.LPVOID,w.LPVOID,w.DWORD,ctypes.POINTER(w.DWORD)];k.CreateRemoteThread.restype=w.HANDLE
k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];k.WaitForSingleObject.restype=w.DWORD
k.VirtualFreeEx.argtypes=[w.HANDLE,w.LPVOID,ctypes.c_size_t,w.DWORD];k.VirtualFreeEx.restype=w.BOOL
k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle.restype=w.BOOL
pid=find_pid(sys.argv[2] if len(sys.argv)>2 else 'mgs4.exe');assert pid
path=pathlib.Path(sys.argv[1]).resolve();assert path.name in ('MGS4EarlyEquipment.asi','MGS4EarlyEquipmentLive.asi','EEGameProbe.dll','EEDev.asi') and path.is_file()
assert find_module_base(pid,path.name) is None,'ASI is already loaded; restart before replacing it'
h=k.OpenProcess(0x43a,False,pid);assert h,ctypes.get_last_error()
payload=(str(path)+'\0').encode('utf-16-le');remote=k.VirtualAllocEx(h,None,len(payload),0x3000,4);assert remote
count=ctypes.c_size_t();assert k.WriteProcessMemory(h,remote,payload,len(payload),ctypes.byref(count))
local=k.GetModuleHandleW('kernel32.dll');proc=k.GetProcAddress(local,b'LoadLibraryW')
# LoadLibraryW may be forwarded to KernelBase, so identify its actual owner.
class MBI(ctypes.Structure):
    _fields_=[('BaseAddress',w.LPVOID),('AllocationBase',w.LPVOID),('AllocationProtect',w.DWORD),('RegionSize',ctypes.c_size_t),('State',w.DWORD),('Protect',w.DWORD),('Type',w.DWORD)]
k.VirtualQuery.argtypes=[w.LPCVOID,ctypes.POINTER(MBI),ctypes.c_size_t];k.VirtualQuery.restype=ctypes.c_size_t
k.GetModuleFileNameW.argtypes=[w.HMODULE,w.LPWSTR,w.DWORD];k.GetModuleFileNameW.restype=w.DWORD
m=MBI();assert k.VirtualQuery(proc,ctypes.byref(m),ctypes.sizeof(m));name=ctypes.create_unicode_buffer(260);assert k.GetModuleFileNameW(m.AllocationBase,name,260)
owner=pathlib.Path(name.value).name;remote_module=find_module_base(pid,owner);assert remote_module
t=k.CreateRemoteThread(h,None,0,remote_module+proc-m.AllocationBase,remote,0,None);assert t,ctypes.get_last_error()
assert k.WaitForSingleObject(t,10000)==0,'LoadLibrary did not finish'
k.VirtualFreeEx(h,remote,0,0x8000);k.CloseHandle(t);k.CloseHandle(h)
assert find_module_base(pid,path.name),'LoadLibrary failed'
print('Loaded ASI into mgs4.exe. No inventory changes until the next stage initialization.')
