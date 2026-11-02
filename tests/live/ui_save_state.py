"""Read-only state capture for manual menu save/load tests."""
import sys,struct,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'external/mgs4trainer'))
from mgs4trainer.core.winproc import find_pid,find_module_base,ProcessHandle
pid=find_pid('mgs4.exe');b=find_module_base(pid,'mgs4.exe');p=ProcessHandle(pid)
ptr=lambda x:struct.unpack('<Q',p.read_bytes(b+x,8))[0]
read=lambda a:struct.unpack('<h',p.read_bytes(a,2))[0]
s=ptr(0x1c28b28);v=ptr(0x1c28b38)
state={'pid':pid,'stage':p.read_bytes(s+0x34,8).split(b'\0')[0].decode(errors='replace'),'progress':struct.unpack('<I',p.read_bytes(s+0x54,4))[0],'clears':read(s),
 'weapons':[read(b+0x1d825aa+i*0x50) for i in range(95)],'ammo':[read(b+0x1d81f30+i*0x18) for i in range(68)],'items':[read(b+0x1d84344+i*0x48) for i in range(99)],
 'camo':p.read_bytes(s+0x4bb8,0x400).hex(),'carry':p.read_bytes(v+0x129a,0x60e).hex()}
print({**{k:state[k] for k in ['pid','stage','progress','clears']},'ration':state['items'][1],'M4_ammo':state['ammo'][18],'SolidEye':state['items'][6],'MkII':state['items'][7],'Bandana':state['items'][15],'Stealth':state['items'][16]})
if len(sys.argv)>1:pathlib.Path(sys.argv[1]).write_text(json.dumps(state,indent=2)+'\n')
p.close()
