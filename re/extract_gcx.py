import pathlib,importlib.util,zlib,struct
import lz4.block
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('vpak',str(ROOT/'external/bbtracker/scripts/list-vpak.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
root=pathlib.Path(r'C:\Program Files (x86)\Steam\steamapps\common\METAL GEAR SOLID 4\MGS4\ww\stage')
out=(ROOT/'research/scripts');out.mkdir(exist_ok=True)
for pak in root.glob('*.pak'):
    with pak.open('rb') as f:
        entries=list(v.entries(f))
        for e in entries:
            name,flags,size,stored,off,*_=e
            if not name.endswith('.gcx'):continue
            f.seek(off);d=f.read(stored or size)
            if flags:
                try:
                    boundaries=(0,)+e[-1]+(len(d),)
                    d=b''.join(lz4.block.decompress(d[a:b],uncompressed_size=min(e[5],size-i*e[5])) for i,(a,b) in enumerate(zip(boundaries,boundaries[1:])))
                except Exception:
                    print(name,'header',d[:24].hex());continue
            stage=name.split('/')[-3]
            (out/(stage+'.gcx')).write_bytes(d)
            print(stage,len(d))
