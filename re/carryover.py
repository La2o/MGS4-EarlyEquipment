import pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'external/mgs4trainer'))
import mgs4save
d=(ROOT/'research/save_decrypted.bin').read_bytes()
for i,v in enumerate(struct.unpack_from('<95H',d,0x6dda)):
    if v: print('W',hex(i),mgs4save.WEAPON_NAMES.get(i),v)
print('ITEMS')
for i,v in enumerate(struct.unpack_from('<99h',d,0x6f20)):
    print(hex(i),v)
