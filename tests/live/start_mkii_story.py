import sys,struct,json,pathlib
from game_rpc import GameRpc,ROOT
r=GameRpc();b=r.base;ptr=lambda off:struct.unpack('<Q',r.proc.read_bytes(b+off,8))[0]
s=ptr(0x1c28b28);v=ptr(0x1c28b38);checkpoint=ptr(0x1c28b30);vcheckpoint=ptr(0x1c28b40)
assert r.proc.read_bytes(s+0x34,7)==b's01a10l' and 17<=struct.unpack('<I',r.proc.read_bytes(s+0x54,4))[0]<=19
assert r.proc.read_bytes(b+0x1d84344+6*0x48,2)==b'\x01\x00'
for address,value in [(b+0x1d84344+0x48,2),(s+0x526+2,2),(b+0x1d81f30+18*0x18,13),(s+0x350+18*2,13)]:r.proc.write_bytes(address,struct.pack('<h',value))
scratch=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(scratch,bytes.fromhex('69 c9 2b 08 04 06 ef a0 6e 00 00'));r.proc.write_bytes(scratch+0x100,bytes(16))
r.call(b+0x3ed5f0,scratch,scratch+0x100,0)
assert r.proc.read_bytes(s+0x526+12,2)==b'\x01\x00','Native inventory synchronization failed'
r.call(b+0xd25800,checkpoint,s,0x5b40);r.call(b+0xd25800,vcheckpoint,v,0x2800)
r.proc.write_bytes(checkpoint+0x54,struct.pack('<I',18))
print('Starting real Mk. II stage flow with 2 rations and 13 M4 reserve rounds, completed runs',struct.unpack('<H',r.proc.read_bytes(s,2))[0])
(ROOT/'build/story-before.json').write_text(json.dumps({'ration':2,'M4_ammo':13,'clears':struct.unpack('<H',r.proc.read_bytes(s,2))[0]}))
print('Native reload:',r.call(b+0x5bcb0,0));r.close()

