import sys,struct,pathlib,zlib,json
from game_rpc import GameRpc,ROOT
import reports
import mgs4save
r=GameRpc();ctx=json.loads((ROOT/'build/save-test-context.json').read_text());b=r.base;obj=ctx['object'];assert b==ctx['base']
ptr=lambda x:struct.unpack('<Q',r.proc.read_bytes(b+x,8))[0]
s=ptr(0x1c28b28);snapshot=ptr(0x1c28b30)
encoded=(ROOT/'build/save-sandbox/native-save-roundtrip.bin').read_bytes();decoded=mgs4save.decrypt(encoded)
rows=[]
for n in range(3):
 r.call(b+0x4b2240,0)
 r.proc.write_bytes(obj+0xd60,encoded);r.proc.write_bytes(obj+0x6dc,struct.pack('<I',ctx['checksum']))
 r.proc.write_bytes(snapshot+0x1c0,struct.pack('<I',123));r.proc.write_bytes(snapshot+0x1d4,bytes(190))
 result=r.call(b+0x4ba400,obj);error=r.call(b+0x4b2200)
 output=r.proc.read_bytes(obj+0xd60,len(encoded));currency=struct.unpack('<I',r.proc.read_bytes(snapshot+0x1c0,4))[0]
 assert result==0 and error==0 and output==decoded
 assert currency==struct.unpack_from('<I',decoded,0x1c0)[0]
 weapons=struct.unpack('<95H',r.proc.read_bytes(snapshot+0x1d4,190))
 saved=struct.unpack_from('<95H',decoded,0x1d4)
 assert all(weapons[i]==x for i,x in enumerate(saved))
 assert r.proc.read_bytes(b+0x1d84344+6*0x48,2)==b'\x01\x00'
 rows.append({'roundtrip':n+1,'native_load_result':result,'native_error':error,'decrypted_bytes_exact':True,'currency_restored':True,'weapon_states_match':True,'solid_eye_present':True})
# Negative control proves the native corruption check is active.
bad=bytearray(encoded);bad[0x200]^=0x40
r.proc.write_bytes(obj+0xd60,bytes(bad));r.proc.write_bytes(obj+0x6dc,struct.pack('<I',ctx['checksum']))
result=r.call(b+0x4ba400,obj);error=r.call(b+0x4b2200);assert result==0xffffffff and error==2
r.call(b+0x4b2240,0)
report={'scope':'Native save serializer and native load/validation routines on the game thread, isolated sandbox, serialized payload written to disk and read back. This does not exercise the manual-save UI or outer file writer.','payload_bytes':len(encoded),'roundtrips':rows,'intentionally_damaged_payload_rejected':True,'damaged_payload_error':error,'mod_save_encoder_decoder_hooks':False}
reports.save('save-roundtrip-tests.json',report,r.pid);print(json.dumps(report,indent=2));r.close()


