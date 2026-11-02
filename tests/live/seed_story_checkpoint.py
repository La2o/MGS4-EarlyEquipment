import sys,pathlib,struct,time,json
from game_rpc import GameRpc,ROOT
r=GameRpc();b=r.base;ptr=lambda off:struct.unpack('<Q',r.proc.read_bytes(b+off,8))[0]
source=(ROOT/'research/save_decrypted.bin').read_bytes();assert source[0x34:0x3b]==b's01a10l'
remote=r.proc.alloc_near(b,0x9000);assert remote;r.proc.write_bytes(remote,source[:0x8340])
r.call(b+0xd25800,ptr(0x1c28b30),remote,0x5b40);r.call(b+0xd25800,ptr(0x1c28b40),remote+0x5b40,0x2800)
print('Requesting native reload of copied pre-Mk. II NG+ checkpoint',r.call(b+0x5bcb0,0));r.close()
