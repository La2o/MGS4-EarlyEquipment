"""Disposable checkpoint fixture using complete authentic Red Zone world state."""
import sys,struct,pathlib,json
from game_rpc import GameRpc,ROOT
r=GameRpc();b=r.base;ptr=lambda x:struct.unpack('<Q',r.proc.read_bytes(b+x,8))[0]
s=ptr(0x1c28b28);v=ptr(0x1c28b38)
untouched='--untouched' in sys.argv
template=(ROOT/'research/save_decrypted.bin').read_bytes();link=bytearray(template[:0x5b40]);var=bytearray(template[0x5b40:0x8340])
if not untouched:
 assert struct.unpack('<H',r.proc.read_bytes(s,2))[0]==2
 for a,n in [(b+0x1d84344+0x48,1),(b+0x1d81f30+18*0x18,17)]:r.proc.write_bytes(a,struct.pack('<h',n))
 scratch=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(scratch,bytes.fromhex('69 c9 2b 08 04 06 ef a0 6e 00 00'));r.proc.write_bytes(scratch+0x100,bytes(16));r.call(b+0x3ed5f0,scratch,scratch+0x100,0)
 live=r.proc.read_bytes(s,0x5b40);currentvar=r.proc.read_bytes(v,0x2800)
 # Full inventory and camo regions; retain authentic stage/world data elsewhere.
 link[0:2]=live[0:2]
 for start,end in [(0x1d4,0x5ec),(0xa9c,0xad0),(0x4bb8,0x4fb8)]:link[start:end]=live[start:end]
 var[0x129a:0x18a8]=currentvar[0x129a:0x18a8]
struct.pack_into('<I',link,0x54,18)
trace=(ROOT/'build/save-sandbox/MGS4/EEGameProbe.trace.log')
(ROOT/'build/meeting-context.json').write_text(json.dumps({'untouched':untouched,'trace_offset':trace.stat().st_size,'clears':struct.unpack_from('<H',link)[0]}))
r.proc.write_bytes(ptr(0x1c28b30),bytes(link));r.proc.write_bytes(ptr(0x1c28b40),bytes(var))
print('Authentic Red Zone checkpoint, untouched inventory' if untouched else 'Second-cycle checkpoint: 1 ration, 17 M4 reserve, earned Stealth')
print('Reload:',r.call(b+0x5bcb0,0));r.close()
