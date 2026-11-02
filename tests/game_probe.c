/* Development-only game-thread RPC helper. Never included in release archives. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "MinHook.h"
typedef struct { volatile LONG pending,done; uint64_t fn,args[4],result; } Rpc;
static Rpc *rpc;
static void (*update)(void);
static int (*exec_proc)(int,void *);
static int observed_proc(int id,void *args) {
    unsigned char *b=(unsigned char *)GetModuleHandleW(NULL),*s=*(unsigned char **)(b+0x1c28b28);
    int trace=s && ((!memcmp(s+0x34,"s01a10l",7) && (id==291||id==295||id==296||id==998||id==1001)) ||
                  (!memcmp(s+0x34,"title",5) && (id==198||id==73||id==75||id==58||id==199)));
    int before=trace?*(int16_t *)(b+0x1d84344+0x48):0;
    int eye_before=trace?*(int16_t *)(b+0x1d84344+6*0x48):0;
    int missing_weapon=-1,missing_item=-1,snapshot_eye=-99;
    if(trace && id==295){
        unsigned char *v=*(unsigned char **)(b+0x1c28b38),*snap=*(unsigned char **)(b+0x1c28b30);
        snapshot_eye=*(int16_t *)(snap+0x526+12);
        for(int n=1;n<95;n++)if(*(uint16_t *)(b+0x1d825aa+n*0x50)<*(uint16_t *)(v+0x129a+n*2)){missing_weapon=n;break;}
        for(int n=6;n<61;n++)if(*(int16_t *)(v+0x13e0+n*2)>=0 && *(int16_t *)(b+0x1d84344+n*0x48)<0){missing_item=n;break;}
    }
    int result=exec_proc(id,args);
    if(trace){
        FILE *f=fopen("EEGameProbe.trace.log","a");
        if(f){fprintf(f,"proc=%d stage=%.7s progress=%u clears=%u ration=%d->%d eye=%d result=%d before_eye=%d snapshot_eye=%d missing_weapon=%d missing_item=%d\n",id,s+0x34,
            *(uint32_t *)(s+0x54),*(uint16_t *)s,before,*(int16_t *)(b+0x1d84344+0x48),
            *(int16_t *)(b+0x1d84344+6*0x48),result,eye_before,snapshot_eye,missing_weapon,missing_item);fclose(f);}
    }
    return result;
}
static void hooked_update(void) {
    update();
    if(InterlockedCompareExchange(&rpc->pending,0,1)==1) {
        typedef uint64_t (*Call)(uint64_t,uint64_t,uint64_t,uint64_t);
        rpc->result=((Call)(uintptr_t)rpc->fn)(rpc->args[0],rpc->args[1],rpc->args[2],rpc->args[3]);
        InterlockedExchange(&rpc->done,1);
    }
}
typedef struct {uint16_t argc;intptr_t *argv;} Args;
/* Invoke the game's normal scene-completion callback, including its cleanup
   and stage transition. This skips the movie without assigning scenario flags. */
__declspec(dllexport) uint64_t test_complete_cutscene(uint64_t a,uint64_t c,uint64_t d,uint64_t e){
    (void)a;(void)c;(void)d;(void)e;
    unsigned char *b=(unsigned char *)GetModuleHandleW(NULL),*s=*(unsigned char **)(b+0x1c28b28);
    if(memcmp(s+0x34,"s01a10l",7))return 0;
    uint32_t p=*(uint32_t *)(s+0x54);if(p!=18 && p!=14)return 0;
    Args args={0,NULL};((int (*)(int,void *))(b+0x3ed630))(p==18?1001:1000,&args);
    return *(uint32_t *)(s+0x54);
}
/* All transient edits happen after a frame and are undone before the next.
   Return 1 means the Mk. II procedure was skipped, with the spent ration kept. */
__declspec(dllexport) uint64_t test_handover_guard(uint64_t mode,uint64_t unused1,uint64_t unused2,uint64_t unused3) {
    (void)unused1;(void)unused2;(void)unused3;
    unsigned char *b=(unsigned char *)GetModuleHandleW(NULL);
    unsigned char *s=*(unsigned char **)(b+0x1c28b28);
    uint32_t progress=*(uint32_t *)(s+0x54);
    int16_t *ration=(int16_t *)(b+0x1d84344+0x48);
    int16_t stock=*ration;
    unsigned char link[0x5b40],var[0x2800],weapons[95*0x50],items[99*0x48],ammo[68*0x18];
    unsigned char *v=*(unsigned char **)(b+0x1c28b38);
    memcpy(link,s,sizeof(link));memcpy(var,v,sizeof(var));
    memcpy(weapons,b+0x1d82580,sizeof(weapons));memcpy(items,b+0x1d84330,sizeof(items));memcpy(ammo,b+0x1d81f20,sizeof(ammo));
    *ration=stock>1?stock-1:0;
    int16_t spent=*ration;
    *(uint32_t *)(s+0x54)=18;
    if(mode==1) {
        /* Emulate loading an untouched pre-handover inventory in this same cycle. */
        *(uint16_t *)(b+0x1d825aa+0x18*0x50)=0;
    }
    Args args={0,NULL};
    ((int (*)(int,void *))(b+0x3ed630))(295,&args);
    uint64_t skipped=*ration==spent;
    memcpy(s,link,sizeof(link));memcpy(v,var,sizeof(var));
    memcpy(b+0x1d82580,weapons,sizeof(weapons));memcpy(b+0x1d84330,items,sizeof(items));memcpy(b+0x1d81f20,ammo,sizeof(ammo));
    *(uint32_t *)(s+0x54)=progress;*ration=stock;
    return skipped;
}
__declspec(dllexport) uint64_t test_activation_fixture(uint64_t fn,uint64_t mode,uint64_t source_var,uint64_t unused) {
    (void)unused;
    unsigned char *b=(unsigned char *)GetModuleHandleW(NULL),*s=*(unsigned char **)(b+0x1c28b28),*v=*(unsigned char **)(b+0x1c28b38);
    unsigned char link[0x5b40],var[0x2800],weapons[95*0x50],items[99*0x48],ammo[68*0x18];
    memcpy(link,s,sizeof(link));memcpy(var,v,sizeof(var));
    memcpy(weapons,b+0x1d82580,sizeof(weapons));memcpy(items,b+0x1d84330,sizeof(items));memcpy(ammo,b+0x1d81f20,sizeof(ammo));
    memcpy(v,(void *)(uintptr_t)source_var,0x2800);
    *(uint16_t *)s=1;*(uint16_t *)(s+2)=1;*(uint16_t *)(s+6)=50;*(uint32_t *)(s+0x54)=0;memcpy(s+0x34,"s01a00l",8);
    int16_t *eye=(int16_t *)(b+0x1d84344+6*0x48),*ration=(int16_t *)(b+0x1d84344+0x48);
    *eye=-1;*ration=2;
    if(mode==1)*(uint16_t *)s=0;
    if(mode==2)*(uint32_t *)(s+0x54)=19;
    if(mode==3)memcpy(s+0x34,"s02a10l",8);
    if(mode==4)*(uint16_t *)(s+6)=99;
    if(mode==5)*(uint16_t *)(v+0x129c)=0;
    if(mode==6){memcpy(s+0x34,"s01a05l",8);*(uint32_t *)(s+0x54)=4;}
    if(mode==7){memcpy(s+0x34,"s01a10l",8);*(uint32_t *)(s+0x54)=17;}
    if(mode==8)*eye=1;
    ((uint64_t (*)(uint64_t,uint64_t,uint64_t,uint64_t))(uintptr_t)fn)(0,0,0,0);
    uint64_t result=(*eye==1?1:0)|(*ration==2?2:0);
    memcpy(s,link,sizeof(link));memcpy(v,var,sizeof(var));
    memcpy(b+0x1d82580,weapons,sizeof(weapons));memcpy(b+0x1d84330,items,sizeof(items));memcpy(b+0x1d81f20,ammo,sizeof(ammo));
    return result;
}
static DWORD WINAPI init(void *unused) {
    (void)unused;
    HANDLE map=CreateFileMappingW(INVALID_HANDLE_VALUE,NULL,PAGE_READWRITE,0,4096,L"Local\\MGS4EarlyEquipmentTests");
    if(!map)return 1;
    rpc=MapViewOfFile(map,FILE_MAP_ALL_ACCESS,0,0,4096);if(!rpc)return 2;
    memset(rpc,0,4096);
    unsigned char *b=(unsigned char *)GetModuleHandleW(NULL);
    if(MH_Initialize()!=MH_OK || MH_CreateHook(b+0x740280,hooked_update,(void **)&update)!=MH_OK ||
       MH_CreateHook(b+0x3ed630,observed_proc,(void **)&exec_proc)!=MH_OK || MH_EnableHook(MH_ALL_HOOKS)!=MH_OK)return 3;
    return 0;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID reserved) {
    (void)reserved;
    if(reason==DLL_PROCESS_ATTACH){DisableThreadLibraryCalls(module);HANDLE t=CreateThread(NULL,0,init,NULL,0,NULL);if(t)CloseHandle(t);}
    return TRUE;
}
