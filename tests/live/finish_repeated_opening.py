import sys,struct,time,json,pathlib
from game_rpc import GameRpc,ROOT
r=GameRpc();b=r.base;empty=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(empty,bytes(16))
for _ in range(100):
 s=struct.unpack('<Q',r.proc.read_bytes(b+0x1c28b28,8))[0]
 script=r.call(b+0x3edd10)
 if struct.unpack('<I',r.proc.read_bytes(script+8,4))[0]==678 and struct.pack('<I',0x61fde8) in r.proc.read_bytes(r.call(b+0x3ecb50),0x400):break
 time.sleep(.2)
else:raise TimeoutError('Opening movie not ready')
print('Normal opening completion callback:',r.call(b+0x3ed630,616,empty),flush=True)
time.sleep(2)
read=lambda a:struct.unpack('<h',r.proc.read_bytes(a,2))[0]
assert struct.unpack('<I',r.proc.read_bytes(s+0x54,4))[0]==1
assert read(s)==2 and read(b+0x1d84344+0x48)==3 and read(b+0x1d81f30+18*0x18)==77
assert read(b+0x1d84344+16*0x48)==1 and read(b+0x1d84344+15*0x48)==-1
print('Same Clear Data: playable opening, 3 rations, 77 M4 rounds, earned Stealth, no Bandana; pause',r.call(b+0x73fdc0))
p=(ROOT/'docs/story-tests.json');report=json.loads(p.read_text());report['same_clear_data_restarted']['playable_opening_verified']=True;p.write_text(json.dumps(report,indent=2)+'\n');r.close()
