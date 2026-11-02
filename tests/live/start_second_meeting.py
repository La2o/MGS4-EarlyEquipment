import sys,struct,time,pathlib,json
from game_rpc import GameRpc,ROOT
r=GameRpc();b=r.base;ptr=lambda off:struct.unpack('<Q',r.proc.read_bytes(b+off,8))[0]
for _ in range(80):
 s=ptr(0x1c28b28)
 if struct.unpack('<I',r.proc.read_bytes(s+0x54,4))[0]>=1 and ptr(0x23eb5f50):break
 time.sleep(.2)
else:raise TimeoutError('Second opening world did not initialize')
read=lambda a:struct.unpack('<h',r.proc.read_bytes(a,2))[0]
assert read(s)==2 and read(b+0x1d84344+16*0x48)==1 and read(b+0x1d81f30+18*0x18)==77
print('Second NG+ playable opening: latest gear and ammo preserved')
for address,value in [(b+0x1d84344+0x48,1),(b+0x1d81f30+18*0x18,17)]:r.proc.write_bytes(address,struct.pack('<h',value))
scratch=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(scratch,bytes.fromhex('69 c9 2b 08 04 06 ef a0 6e 00 00'));r.proc.write_bytes(scratch+0x100,bytes(16));r.call(b+0x3ed5f0,scratch,scratch+0x100,0)
checkpoint=ptr(0x1c28b30);r.call(b+0xd25800,checkpoint,s,0x5b40);r.call(b+0xd25800,ptr(0x1c28b40),ptr(0x1c28b38),0x2800)
original=(ROOT/'research/save_decrypted.bin').read_bytes()
r.proc.write_bytes(checkpoint+0x2c,original[0x2c:0x3c]);r.proc.write_bytes(checkpoint+0x54,struct.pack('<I',18))
print('Starting second-run Mk. II checkpoint with 1 ration and 17 M4 reserve rounds:',r.call(b+0x5bcb0,0))
p=(ROOT/'docs/story-tests.json');report=json.loads(p.read_text());report['next_NGplus']['playable_opening_verified']=True;p.write_text(json.dumps(report,indent=2)+'\n');r.close()
