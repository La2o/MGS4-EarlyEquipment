import pathlib,struct,hashlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
d=(ROOT/'research/scripts/s01a10l.gcx').read_bytes()
end=d.index(b'\xff'*4,4)
table=struct.unpack_from('<'+str((end-4)//4)+'I',d,4)
block=end+4
procstart=block+struct.unpack_from('<I',d,block)[0]+4
def getproc(n):
    entry=table[n-1];p=procstart+(entry&0xffffff)
    start=p+1;size=d[p]&15
    if size==14:
        size=struct.unpack_from('<H',d,start)[0];start+=2
    elif size==13:
        size=d[start];start+=1
    return d[start:start+size],(entry>>24)&15
out=['/* Generated from the local Steam 1.4.1 restoration procedures. */']
for n,name in [(295,'restore_inventory'),(296,'restore_camo')]:
    body,locals=getproc(n)
    print(name,'locals',locals,'bytes',len(body),'sha256',hashlib.sha256(body).hexdigest(),body[:12].hex())
    out.append('static unsigned char '+name+'[] = {\n'+',\n'.join('    '+', '.join(f'0x{x:02x}' for x in body[i:i+16]) for i in range(0,len(body),16))+'\n};')
    out.append(f'enum {{ {name}_locals = {locals} }};')
(ROOT/'src').mkdir(exist_ok=True)
(ROOT/'src/restore_script.h').write_text('\n'.join(out)+'\n')
