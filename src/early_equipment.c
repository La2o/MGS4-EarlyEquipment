#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wincrypt.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include "MinHook.h"
#include "policy.h"
#include "restore_script.h"

static unsigned char *base;
static wchar_t log_path[MAX_PATH];
typedef void (*UpdateFn)(void);
typedef int (*ExecProcFn)(int, void *);
typedef int (*ExecBodyFn)(unsigned char *, void *, int);
typedef unsigned char *(*BlockFn)(unsigned char *, int *);
typedef struct { uint16_t argc; intptr_t *argv; } GclArgs;
typedef struct { uint32_t *table; int count; unsigned char *body; unsigned char *main; } Script;
typedef Script *(*GetScriptFn)(void);
static UpdateFn original_update;
static ExecProcFn original_proc;
static ExecBodyFn exec_body;
static GetScriptFn get_script;
static BlockFn get_block;

static void log_line(const char *format, ...) {
    FILE *f=_wfopen(log_path,L"a");
    if (!f) return;
    SYSTEMTIME t; GetLocalTime(&t);
    fprintf(f,"%02u:%02u:%02u ",t.wHour,t.wMinute,t.wSecond);
    va_list ap; va_start(ap,format); vfprintf(f,format,ap); va_end(ap);
    fputc('\n',f); fclose(f);
}
static int readable(const void *p, SIZE_T size) {
    MEMORY_BASIC_INFORMATION m;
    if (!p || !VirtualQuery(p,&m,sizeof(m)) || m.State!=MEM_COMMIT ||
        (m.Protect&(PAGE_NOACCESS|PAGE_GUARD))) return 0;
    return (uintptr_t)p >= (uintptr_t)m.BaseAddress && size <= m.RegionSize-((uintptr_t)p-(uintptr_t)m.BaseAddress);
}
static unsigned char *state(void) {
    unsigned char *p=*(unsigned char **)(base+0x1c28b28);
    return readable(p,0x5b40)?p:NULL;
}
static int16_t solid_eye(void) {
    return *(int16_t *)(base+0x1d84344+6*0x48);
}
static int carry_is_valid(unsigned char *v) {
    if (!readable(v,0x2800)) return 0;
    const uint16_t *w=(uint16_t *)(v+0x129a);
    const int16_t *i=(int16_t *)(v+0x13e0);
    if (w[0]!=0 || w[1]!=2 || i[0]!=0 || i[0x13]!=0 || i[6]!=1) return 0;
    for (int n=0;n<95;n++) if (w[n]>2) return 0;
    for (int n=0;n<99;n++) if (i[n]<-1) return 0;
    return 1;
}
static void hand_over(void) {
    unsigned char *s=state();
    if (!s) return;
    if (!eligible(*(uint16_t *)s,*(uint16_t *)(s+6),*(uint32_t *)(s+0x54),(char *)s+0x34)) return;
    /* The Solid Eye always carries forward. Its presence also identifies an
       early save already restored in a previous session. Do not refill it. */
    if (solid_eye()==1) return;
    unsigned char *v=*(unsigned char **)(base+0x1c28b38);
    if (!carry_is_valid(v)) return;
    Script *script=get_script();
    if(!readable(script,sizeof(*script)) || script->count<=0 || !readable(script->body,4)) return;
    int before=solid_eye();
    GclArgs args={0,NULL};
    log_line("Starting inventory handover on the game thread at %.7s / %u.",s+0x34,*(uint32_t *)(s+0x54));
    exec_body(restore_inventory,&args,restore_inventory_locals);
    exec_body(restore_camo,&args,restore_camo_locals);
    /* The normal handover follows restoration with this native refresh command. */
    unsigned char refresh[]={0x69,0xc9,0x2b,0x08,0x04,0x06,0x99,0x51,0x98,0x00,0x00};
    exec_body(refresh,&args,0);
    if (solid_eye()==1) {
        log_line("Restored earned inventory and camo at %.7s, progress %u, completed runs %u (Solid Eye %d -> 1).",
            s+0x34,*(uint32_t *)(s+0x54),*(uint16_t *)s,before);
    } else log_line("Restoration did not validate; Solid Eye is %d.",solid_eye());
}
static void update_hook(void) {
    original_update();
    /* Executes on the game thread, after the task scheduler finishes this frame. */
    hand_over();
}
#ifdef EE_DEV_CHAIN
/* Test builds can chain this session's known development modules. Release
   builds require unmodified game signatures and contain no RPC/export API. */
static int development_detour(unsigned char *entry) {
    HMODULE owner=NULL;
    if(entry[0]!=0xe9) return 0;
    unsigned char *target=entry+5+*(int32_t *)(entry+1);
    if(!readable(target,14)) return 0;
    if(target[0]==0xff && target[1]==0x25 && *(int32_t *)(target+2)==0)
        target=*(unsigned char **)(target+6);
    if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
        (LPCWSTR)target,&owner))return 0;
    return owner==GetModuleHandleW(L"MGS4EarlyEquipment.asi") ||
        owner==GetModuleHandleW(L"MGS4EarlyEquipmentLive.asi") || owner==GetModuleHandleW(L"EEGameProbe.dll");
}
__declspec(dllexport) uint64_t EeTest_RunHandoverNow(uint64_t a,uint64_t b,uint64_t c,uint64_t d) {
    (void)a;(void)b;(void)c;(void)d;
    hand_over();int value=solid_eye();
    return (uint64_t)(int64_t)value;
}
#endif
static int signature_matches(unsigned char *entry,const unsigned char *signature,SIZE_T size) {
    if(!memcmp(entry,signature,size))return 1;
#ifdef EE_DEV_CHAIN
    return development_detour(entry);
#else
    return 0;
#endif
}
static int restored_inventory_present(void) {
    unsigned char *v=*(unsigned char **)(base+0x1c28b38);
    if(solid_eye()!=1 || !carry_is_valid(v)){
        log_line("Handover inventory check: Solid Eye %d, carry valid %d.",solid_eye(),carry_is_valid(v));
        return 0;
    }
    const uint16_t *w=(uint16_t *)(v+0x129a);
    for(int n=1;n<95;n++)
        if(*(uint16_t *)(base+0x1d825aa+n*0x50)<w[n]){
            log_line("Handover inventory check: weapon %d is %u, carry %u.",n,*(uint16_t *)(base+0x1d825aa+n*0x50),w[n]);return 0;
        }
    /* Consumable stock may have been spent. Permanent equipment must still
       be present before a previous session's early handover can be reused. */
    const int16_t *items=(int16_t *)(v+0x13e0);
    for(int n=6;n<61;n++)
        if(items[n]>=0 && *(int16_t *)(base+0x1d84344+n*0x48)<0){
            log_line("Handover inventory check: item %d is absent, carry %d.",n,items[n]);return 0;
        }
    return 1;
}
static int is_inventory_restore(int id) {
    Script *script=get_script();
    unsigned n=((unsigned)id&0x7fff);
    if (!readable(script,sizeof(*script)) || !n || n>(unsigned)script->count ||
        !readable(script->table,(SIZE_T)n*4)) return 0;
    unsigned char *p=script->body+(script->table[n-1]&0xffffff);
    if (!readable(p,4)) return 0;
    int size=0; unsigned char *body=get_block(p,&size);
    return size==sizeof(restore_inventory) && readable(body,sizeof(restore_inventory)) &&
        !memcmp(body,restore_inventory,sizeof(restore_inventory));
}
static int proc_hook(int id,void *args) {
    unsigned char *s=state();
    /* Recognize restored checkpoints directly, including a fresh process
       loading at the handover, without depending on transient session flags. */
    if (s && *(uint16_t *)s &&
        *(uint32_t *)(s+0x54)==18 && !memcmp(s+0x34,"s01a10l",7) &&
        is_inventory_restore(id) && restored_inventory_present()) {
        log_line("Skipped duplicate Mk. II inventory handover.");
        return 0;
    }
    return original_proc(id,args);
}
static int supported_executable(void) {
    static const unsigned char expected[32]={0x65,0x6e,0xde,0x90,0x0b,0x03,0x46,0x7e,0x4e,0xd0,0x5a,0x00,0xec,0xa3,0x5f,0x0a,0xc3,0x06,0xce,0x57,0xa8,0xf2,0x9a,0x76,0xa2,0x0e,0x5a,0x54,0x10,0xd0,0x29,0x00};
    wchar_t path[MAX_PATH]; GetModuleFileNameW(NULL,path,MAX_PATH);
    HANDLE f=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,NULL,OPEN_EXISTING,0,NULL);
    HCRYPTPROV provider=0; HCRYPTHASH hash=0; unsigned char buffer[65536],digest[32]; DWORD size=0;
    int ok=f!=INVALID_HANDLE_VALUE && CryptAcquireContextW(&provider,NULL,NULL,PROV_RSA_AES,CRYPT_VERIFYCONTEXT) &&
        CryptCreateHash(provider,CALG_SHA_256,0,0,&hash);
    while(ok) { if(!ReadFile(f,buffer,sizeof(buffer),&size,NULL)) {ok=0;break;} if(!size)break; if(!CryptHashData(hash,buffer,size,0)){ok=0;break;} }
    size=sizeof(digest); if(ok)ok=CryptGetHashParam(hash,HP_HASHVAL,digest,&size,0) && !memcmp(digest,expected,32);
    if(hash)CryptDestroyHash(hash); if(provider)CryptReleaseContext(provider,0); if(f!=INVALID_HANDLE_VALUE)CloseHandle(f);
    return ok;
}
static DWORD WINAPI initialize(void *unused) {
    (void)unused;
    log_line("MGS4 Early Equipment 0.4.0 starting.");
    base=(unsigned char *)GetModuleHandleW(NULL);
    if (!supported_executable()) {log_line("Unsupported mgs4.exe SHA-256; mod inactive.");return 0;}
    /* Check plaintext as well: these are the exact Steam 1.4.1 function entries. */
    static const unsigned char sig_update[]={0x48,0x89,0x5c,0x24,0x10,0x56,0x48,0x83,0xec,0x20,0xe8,0x01,0xe3,0xa0,0xff};
    static const unsigned char sig_proc[]={0x48,0x89,0x5c,0x24,0x10,0x56,0x48,0x83,0xec,0x30,0x48,0x8b,0xf2};
    static const unsigned char sig_body[]={0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20,0x48,0x8b,0xc2};
    int ready=0;
    for(int n=0;n<300;n++) {
        if(signature_matches(base+0x740280,sig_update,sizeof(sig_update)) &&
           signature_matches(base+0x3ed630,sig_proc,sizeof(sig_proc)) &&
           !memcmp(base+0x3ed5f0,sig_body,sizeof(sig_body))) {ready=1;break;}
        Sleep(100);
    }
    if(!ready){log_line("Runtime signatures did not match; mod inactive.");return 0;}
    exec_body=(ExecBodyFn)(base+0x3ed5f0);get_script=(GetScriptFn)(base+0x3edd10);get_block=(BlockFn)(base+0x3ee030);
    MH_STATUS result=MH_Initialize();
    if(result!=MH_OK || MH_CreateHook(base+0x740280,update_hook,(void **)&original_update)!=MH_OK ||
       MH_CreateHook(base+0x3ed630,proc_hook,(void **)&original_proc)!=MH_OK) {
        log_line("Could not prepare hooks; mod inactive."); MH_Uninitialize(); return 0;
    }
    result=MH_EnableHook(MH_ALL_HOOKS);
    if(result!=MH_OK){log_line("Could not enable hooks (%d).",result);MH_Uninitialize();return 0;}
    log_line("Ready. Monitoring opening NG+ gameplay on the game thread.");
    return 0;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID reserved) {
    (void)reserved;
    if(reason==DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(module);
        GetModuleFileNameW(module,log_path,MAX_PATH);
        wchar_t *dot=wcsrchr(log_path,L'.'); if(dot)wcscpy(dot,L".log");
        HANDLE thread=CreateThread(NULL,0,initialize,NULL,0,NULL);if(thread)CloseHandle(thread);
    }
    return TRUE;
}
