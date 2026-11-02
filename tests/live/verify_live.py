import sys,struct,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'external/mgs4trainer'))
from mgs4trainer.core.winproc import find_pid,find_module_base,ProcessHandle
pid=find_pid('mgs4.exe');base=find_module_base(pid,'mgs4.exe');p=ProcessHandle(pid)
s=struct.unpack('<Q',p.read_bytes(base+0x1c28b28,8))[0]
v=struct.unpack('<Q',p.read_bytes(base+0x1c28b38,8))[0]
snapshot=p.read_bytes(s,0x5b40);carry=p.read_bytes(v,0x2800)
saved=struct.unpack_from('<95H',carry,0x129a)
live=[struct.unpack('<H',p.read_bytes(base+0x1d825aa+i*0x50,2))[0] for i in range(95)]
items=[struct.unpack('<h',p.read_bytes(base+0x1d84344+i*0x48,2))[0] for i in range(99)]
report={
 'version':'0.2.0',
 'stage':snapshot[0x34:0x3b].decode(),
 'scenario_progress':struct.unpack_from('<I',snapshot,0x54)[0],
 'completed_playthroughs':struct.unpack_from('<H',snapshot,0)[0],
 'difficulty':struct.unpack_from('<H',snapshot,6)[0],
 'carried_weapon_and_attachment_entries':sum(bool(x) for x in saved),
 'all_carried_weapon_states_match':all(live[i]==x for i,x in enumerate(saved) if x),
 'solid_eye_available':items[6]==1,
 'mk_ii_available':items[7]==1,
 'unearned_bandana_stays_locked':items[15]==-1 and struct.unpack_from('<h',carry,0x13e0+15*2)[0]==-1,
 'unearned_stealth_stays_locked':items[16]==-1 and struct.unpack_from('<h',carry,0x13e0+16*2)[0]==-1,
 'camo_tables_match':all(snapshot[a:a+n]==carry[b:b+n] for a,b,n in [(0x4bb8,0x14a8,256),*[(0x4cb8+i*128,0x15a8+i*128,128) for i in range(6)]]),
 'handover_log_entries':(ROOT/'build/live/MGS4EarlyEquipmentLive.log').read_text().count('Restored earned inventory'),
 'not_yet_verified':['first playable opening from Clear Data','later Mk. II duplicate handover guard','cold-start ASI loading after restart'],
}
p.close()
assert report['scenario_progress']==17
assert all(report[k] for k in ['all_carried_weapon_states_match','solid_eye_available','mk_ii_available','unearned_bandana_stays_locked','unearned_stealth_stays_locked','camo_tables_match'])
assert report['handover_log_entries']==1
(ROOT/'docs/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
