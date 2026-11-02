import sys,struct,time
from game_rpc import GameRpc
r=GameRpc();b=r.base;empty=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(empty,bytes(16))
end=time.monotonic()+35;done=set()
while time.monotonic()<end:
 s=struct.unpack('<Q',r.proc.read_bytes(b+0x1c28b28,8))[0];p=struct.unpack('<I',r.proc.read_bytes(s+0x54,4))[0];script=r.call(b+0x3edd10);count=struct.unpack('<I',r.proc.read_bytes(script+8,4))[0]
 if count==1046 and r.proc.read_bytes(s+0x34,7)==b's01a10l':
  if p<=12 and 'opening' not in done:
   print('Skipping opening through normal completion callback 995',flush=True);r.call(b+0x3ed630,995,empty);done.add('opening')
  elif p==14 and 'redzone' not in done:
   print('Skipping Red Zone introduction through completion callback 1000',flush=True);r.call(r.export('test_complete_cutscene'));done.add('redzone')
  elif p==17:
   print('Playable pre-Mk. II state reached',flush=True);break
 time.sleep(.3)
else:raise TimeoutError('Opening skip did not reach progress 17')
r.close()
