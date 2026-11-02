import sys, pathlib,struct,re
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'external/mgs4trainer'))
from mgs4trainer.core.winproc import *
p=ProcessHandle(find_pid('mgs4.exe'));base=find_module_base(find_pid('mgs4.exe'),'mgs4.exe')
d=p.read_bytes(base+0x165e000,0x4a1002)
(ROOT/'research/rdata.bin').write_bytes(d)
for m in re.finditer(rb'[ -~]{5,}',d):
    s=m.group().decode()
    if re.search(r'newgame|new_game|carry|restore|backup|weapon|item|invent',s,re.I) and len(s)<130:
        print(hex(m.start()+0x165e000), s)
# Dispatch table references to inventory backup/restore functions.
for start,size in [(0x165e000,0x4a1002),(0x1b00000,0x280000)]:
    d=p.read_bytes(base+start,size)
    for target in [0x67b10,0x68b20]:
        for m in re.finditer(re.escape(struct.pack('<Q',base+target)),d):
            print('PTR_REF',hex(target),hex(start+m.start()),d[max(0,m.start()-16):m.start()+32].hex())
p.close()
