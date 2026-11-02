import sys,struct,time,json,pathlib
from game_rpc import GameRpc
import reports
r=GameRpc();b=r.base;empty=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(empty,bytes(16));script=r.call(b+0x3edd10);assert struct.unpack('<I',r.proc.read_bytes(script+8,4))[0]==8
print('Skipping title movie through normal completion callback 8:',r.call(b+0x3ed630,8,empty))
for _ in range(100):
 s=struct.unpack('<Q',r.proc.read_bytes(b+0x1c28b28,8))[0];v=struct.unpack('<Q',r.proc.read_bytes(b+0x1c28b38,8))[0]
 if r.proc.read_bytes(s+0x34,7)==b's01a00l' and r.proc.read_bytes(b+0x1d84344+6*0x48,2)==b'\x01\x00':break
 time.sleep(.2)
else:raise TimeoutError('Next NG+ did not restore equipment in first area')
time.sleep(1)
read=lambda a:struct.unpack('<h',r.proc.read_bytes(a,2))[0]
checks={'clears':read(s),'progress':struct.unpack('<I',r.proc.read_bytes(s+0x54,4))[0],'ration':read(b+0x1d84344+0x48),'M4_ammo':read(b+0x1d81f30+18*0x18),'Stealth':read(b+0x1d84344+16*0x48),'Bandana':read(b+0x1d84344+15*0x48),'SolidEye':read(b+0x1d84344+6*0x48),'MkII':read(b+0x1d84344+7*0x48)}
print(checks);assert checks['clears']==2 and checks['ration']==3 and checks['M4_ammo']==77 and checks['Stealth']==1 and checks['Bandana']==-1
report=reports.load('story-tests.json',{});report.setdefault('next_NGplus',{}).update({'method':'Actual title procedure 198 with a simulated second Clear Data fixture, followed by real title_movie -> s01a00l flow; movie skipped by normal completion callback.','latest_carry_values_restored':True,'observed':checks});reports.save('story-tests.json',report,r.pid);r.close()
