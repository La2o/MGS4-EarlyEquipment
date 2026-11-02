import pathlib, sys, struct
from capstone import *
ROOT=pathlib.Path(__file__).resolve().parents[1]
data=(ROOT/'research/runtime_text.bin').read_bytes()
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
def dis(start,size):
    for i in md.disasm(data[start-0x1000:start-0x1000+size],start):
        print(f'{i.address:08x} {i.bytes.hex():28} {i.mnemonic:8} {i.op_str}')
if sys.argv[1]=='func':
    import pefile
    pe=pefile.PE(r'C:\Program Files (x86)\Steam\steamapps\common\METAL GEAR SOLID 4\MGS4\mgs4.exe')
    addr=int(sys.argv[2],16)
    for e in pe.DIRECTORY_ENTRY_EXCEPTION:
        if e.struct.BeginAddress<=addr<e.struct.EndAddress:
            print('FUNCTION',hex(e.struct.BeginAddress),hex(e.struct.EndAddress))
            dis(e.struct.BeginAddress,min(e.struct.EndAddress-e.struct.BeginAddress, int(sys.argv[3],16) if len(sys.argv)>3 else 0x120))
elif sys.argv[1]=='dis':
    dis(int(sys.argv[2],16), int(sys.argv[3],16) if len(sys.argv)>3 else 0x100)
elif sys.argv[1]=='refs':
    target=int(sys.argv[2],16)
    # Brute RIP-relative displacement matches, then decode neighboring opcodes.
    hits=[]
    for n in range(len(data)-4):
        if n+0x1000+4+struct.unpack_from('<i',data,n)[0]==target:
            hits.append(n+0x1000)
    for hit in hits:
        print('REF',hex(hit));dis(hit-3,0x30)
