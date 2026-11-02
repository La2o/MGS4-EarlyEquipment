"""Select the native pause menu's Save row in the disposable test instance."""
import sys,struct,time
from game_rpc import GameRpc
r=GameRpc();b=r.base;q=lambda a:struct.unpack('<Q',r.proc.read_bytes(a,8))[0];mask=0xfffffffffffff
pause=q(b+0x3b7c8b0)&mask
if not pause:r.call(b+0x4d7c00);time.sleep(.5);pause=q(b+0x3b7c8b0)&mask
assert pause
menu=q(pause+0x2c8)&mask;assert menu
n=struct.unpack('<I',r.proc.read_bytes(menu+0x1e0,4))[0];assert 0<n<10
rows=struct.unpack('<'+str(n)+'I',r.proc.read_bytes(menu+0x1e4,4*n));assert 8 in rows
r.proc.write_bytes(menu+0x1dc,struct.pack('<I',rows.index(8)))
print('Native Save row selected; confirm with normal UI input.')
r.close()
