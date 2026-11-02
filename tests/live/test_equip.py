import sys,struct,time,pathlib,json
from game_rpc import GameRpc,ROOT
r=GameRpc();s=struct.unpack('<Q',r.proc.read_bytes(r.base+0x1c28b28,8))[0]
assert struct.unpack('<H',r.proc.read_bytes(r.base+0x1d825aa+24*0x50,2))[0]==2
quick=list(struct.unpack('<5h',r.proc.read_bytes(s+0xaa4,10)));slot=quick.index(0)
assert r.call(r.base+0x73fdc0)==0
r.call(r.base+0x73fe60,2)
r.proc.write_bytes(s+0xaa4+slot*2,struct.pack('<h',24))
r.call(r.base+0x6d490,timeout=20);time.sleep(.15)
r.call(r.base+0x6d2d0,r.base+0x1d82580+24*0x50);time.sleep(.15)
r.call(r.base+0x73fdd0,2);time.sleep(.5)
current=struct.unpack('<H',r.proc.read_bytes(s+0xac4,2))[0];print('Equipped weapon',current);assert current==24
# Ensure the frame hook does not replenish stock on subsequent frames.
ration=r.base+0x1d84344+0x48;before=r.proc.read_bytes(ration,2);r.proc.write_bytes(ration,struct.pack('<h',2));time.sleep(2)
assert r.proc.read_bytes(ration,2)==struct.pack('<h',2)
r.proc.write_bytes(ration,before)
report=json.loads((ROOT/'docs/runtime-tests.json').read_text());report['checks']['M4 model preloaded and equipped in playable world']=True;report['checks']['spent ration stays spent across frames']=True;(ROOT/'docs/runtime-tests.json').write_text(json.dumps(report,indent=2)+'\n')
r.close()
