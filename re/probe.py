import sys, struct, json, pathlib, hashlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'external/mgs4trainer'))
from mgs4trainer.core.winproc import find_pid, find_module_base, ProcessHandle
pid = find_pid('mgs4.exe')
base = find_module_base(pid, 'mgs4.exe')
p = ProcessHandle(pid)
print('pid', pid, 'base', hex(base))
for rva in [0x1c28b28, 0x1c28b30, 0x1c28b38, 0x1c28b40]:
    ptr = struct.unpack('<Q', p.read_bytes(base+rva,8))[0]
    print(hex(rva),hex(ptr))
    if ptr:
        data=p.read_bytes(ptr,0x1000)
        (ROOT / f'research/buffer_{rva:x}.bin').write_bytes(data)
        print('clear/diff/stage/scenario', struct.unpack_from('<IHH',data),data[0x34:0x3c],struct.unpack_from('<I',data,0x54))
print('weapons', [struct.unpack('<H',p.read_bytes(base+0x1d825aa+i*0x50,2))[0] for i in range(95)])
print('items', [struct.unpack('<H',p.read_bytes(base+0x1d84344+i*0x48,2))[0] for i in range(99)])
(ROOT / 'research/runtime_text.bin').write_bytes(p.read_bytes(base+0x1000,0x165cf80))
print('dumped text')
p.close()
