import sys,struct,time,pathlib,json
from game_rpc import GameRpc,ROOT
r=GameRpc();s=struct.unpack('<Q',r.proc.read_bytes(r.base+0x1c28b28,8))[0];v=struct.unpack('<Q',r.proc.read_bytes(r.base+0x1c28b38,8))[0]
state=r.proc.read_bytes(s,0x5b40)
print('Before:',state[0x34:0x3b],struct.unpack_from('<HI',state,0)[0],struct.unpack_from('<I',state,0x54)[0])
assert struct.unpack_from('<H',state)[0]==0 and state[0x34:0x3b]==b's01a10l' and struct.unpack_from('<I',state,0x54)[0]<18
# Seed NG+ carry data in this disposable test session; no save file is written.
carry=(ROOT/'research/save_decrypted.bin').read_bytes()[0x5b40:0x8340]
r.proc.write_bytes(v,carry);r.proc.write_bytes(s,struct.pack('<H',1));time.sleep(.5)
live=[struct.unpack('<H',r.proc.read_bytes(r.base+0x1d825aa+i*0x50,2))[0] for i in range(95)]
w=struct.unpack_from('<95H',carry,0x129a)
items=[struct.unpack('<h',r.proc.read_bytes(r.base+0x1d84344+i*0x48,2))[0] for i in range(99)]
snap=r.proc.read_bytes(s,0x5b40)
checks={'all_67_carried_weapons_match':all(live[i]==x for i,x in enumerate(w) if x),'solid_eye':items[6]==1,'mk_ii':items[7]==1,'unearned_bandana_locked':items[15]==-1,'unearned_stealth_locked':items[16]==-1,'camo_matches':all(snap[a:a+n]==carry[b:b+n] for a,b,n in [(0x4bb8,0x14a8,256),*[(0x4cb8+i*128,0x15a8+i*128,128) for i in range(6)]])}
print(checks);assert all(checks.values())
fn=r.export('test_handover_guard')
for mode,expected,name in [(0,1,'Mk. II does not refill spent supplies'),(1,0,'Unmodified save reload still receives native handover')]:
 result=r.call(fn,mode);print(name,result);checks[name]=result==expected;assert result==expected
(ROOT/'docs/runtime-tests.json').write_text(json.dumps({'version':'0.3.0','scope':'Real s01a10l world, disposable NG+ carry fixture, native game-thread RPC','checks':checks},indent=2)+'\n')
r.close()
