import sys,struct,pathlib,time,json
from game_rpc import GameRpc,ROOT
r=GameRpc();b=r.base;empty=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(empty,bytes(16))
for _ in range(80):
 script=r.call(b+0x3edd10);count=struct.unpack('<I',r.proc.read_bytes(script+8,4))[0]
 if count==199:break
 time.sleep(.2)
else:raise TimeoutError('Title script did not load')
print('Actual title context loaded:',count,'procedures')
source=(ROOT/'build/next-clear-fixture.bin').read_bytes();assert len(source)==0x8340
for off,data in [(0x1c28b28,source[:0x5b40]),(0x1c28b30,source[:0x5b40]),(0x1c28b38,source[0x5b40:]),(0x1c28b40,source[0x5b40:])]:
 dest=struct.unpack('<Q',r.proc.read_bytes(b+off,8))[0];r.proc.write_bytes(dest,data)
print('Starting native Clear Data NG+ reset (title procedure 198):',r.call(b+0x3ed630,198,empty))
(ROOT/'build/ngplus-started.txt').write_text('Actual title procedure 198 with simulated second Clear Data: rations=3, M4 ammo=77, Stealth earned, completed runs=2.\n')
r.close()
