import sys,struct,pathlib,zlib,json
from game_rpc import GameRpc,ROOT
import mgs4save
r=GameRpc();b=r.base
ptr=lambda x:struct.unpack('<Q',r.proc.read_bytes(b+x,8))[0]
s=ptr(0x1c28b28);snapshot=ptr(0x1c28b30);v=ptr(0x1c28b38);vsnap=ptr(0x1c28b40)
assert r.call(b+0x4b2200)==0
# Simulate a checkpoint commit in this disposable game instance only.
scratch=r.proc.alloc_near(b,0x1000);r.proc.write_bytes(scratch,bytes.fromhex('69 c9 2b 08 04 06 ef a0 6e 00 00'));r.proc.write_bytes(scratch+0x100,bytes(16))
r.call(b+0x3ed5f0,scratch,scratch+0x100,0)
expected_clears=struct.unpack('<H',r.proc.read_bytes(s,2))[0]
r.proc.write_bytes(snapshot,r.proc.read_bytes(s,0x5b40));r.proc.write_bytes(vsnap,r.proc.read_bytes(v,0x2800))
obj=r.proc.alloc_near(b,0x12000);assert obj
r.proc.write_bytes(obj,bytes(0x12000))
print('Native serialize result',r.call(b+0x4ba910,obj,obj+0x10000,obj+0x10100))
size=struct.unpack('<I',r.proc.read_bytes(obj+0x92a8,4))[0];assert size==0x8344
encoded=r.proc.read_bytes(obj+0xd60,size);decoded=mgs4save.decrypt(encoded)
assert struct.unpack_from('<H',decoded)[0]==expected_clears and decoded[0x34:0x3b]==b's01a10l'
assert struct.unpack_from('<h',decoded,0x526+6*2)[0]==1
assert decoded[0x1d4:0x292]==r.proc.read_bytes(s+0x1d4,190)
assert decoded[0x526:0x5ec]==r.proc.read_bytes(s+0x526,198)
path=(ROOT/'build/save-sandbox/native-save-roundtrip.bin');path.write_bytes(encoded)
checksum=struct.unpack('<I',r.proc.read_bytes(obj+0x92b0,4))[0];assert checksum==zlib.crc32(encoded)%0xd658
version=struct.unpack('<I',r.proc.read_bytes(b+0x1c28b48,4))[0]
print('Serialized payload',size,'checksum',checksum,'version',hex(version))
(ROOT/'build/save-test-context.json').write_text(json.dumps({'base':b,'object':obj,'checksum':checksum,'version':version,'size':size}))
r.close()
