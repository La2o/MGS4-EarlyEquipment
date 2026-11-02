import sys,struct,time,pathlib,json
from game_rpc import GameRpc,ROOT
import reports
r=GameRpc();s=struct.unpack('<Q',r.proc.read_bytes(r.base+0x1c28b28,8))[0];carry=(ROOT/'research/save_decrypted.bin').read_bytes()[0x5b40:0x8340];w=struct.unpack_from('<95H',carry,0x129a)
rows=[]
for n in range(12):
 snap=r.proc.read_bytes(s,0x5b40);eye=struct.unpack('<h',r.proc.read_bytes(r.base+0x1d84344+6*0x48,2))[0]
 live=[struct.unpack('<H',r.proc.read_bytes(r.base+0x1d825aa+i*0x50,2))[0] for i in range(95)]
 row={'stage':snap[0x34:0x3b].decode(),'progress':struct.unpack_from('<I',snap,0x54)[0],'clear_count':struct.unpack_from('<H',snap)[0],'solid_eye':eye,'all_carried_weapons_match':all(live[i]>=x for i,x in enumerate(w) if x)}
 rows.append(row)
 if n in (0,11):print(row)
 time.sleep(1)
assert all(x['stage']=='s01a00l' and x['solid_eye']==1 and x['all_carried_weapons_match'] for x in rows)
reports.save('opening-world-tests.json',{'version':reports.asi_version(r.pid),'scope':'Cold-start release ASI in real s01a00l world; carry tables seeded in disposable memory; no save files edited','samples':rows},r.pid);r.close()
