import sys,struct,pathlib,json
from game_rpc import GameRpc,ROOT
r=GameRpc()
fixture=(ROOT/'research/save_decrypted.bin').read_bytes()[0x5b40:0x8340]
assert len(fixture)==0x2800
remote=r.proc.alloc_near(r.base,0x3000);assert remote
r.proc.write_bytes(remote,fixture)
run=r.export('test_activation_fixture')
handover=r.export('EeTest_RunHandoverNow','EEDev.asi',ROOT/'build/EEDev.asi')
cases=[('opening NG+',0,1),('normal NG, separate +2 field is nonzero',1,2),('after Mk. II',2,2),('later act',3,2),('invalid difficulty',4,2),('invalid carry buffer',5,2),('second opening area',6,1),('pre-Mk. II area',7,1),('already restored, spent ration',8,3)]
report=[]
for name,mode,expected in cases:
    result=r.call(run,handover,mode,remote)
    row={'test':name,'actual':result,'expected':expected,'passed':result==expected};report.append(row);print(row)
    assert result==expected,name
(ROOT/'docs/activation-tests.json').write_text(json.dumps(report,indent=2)+'\n')
r.close()
