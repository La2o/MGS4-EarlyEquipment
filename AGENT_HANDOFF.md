# MGS4 Early Equipment — agent handoff

Prepared 2026-11-02. This is the entry point for another AI agent taking over
the project. It records implementation, local artifacts, testing evidence,
important mistakes to avoid, and unfinished work. It is not a transcript of
every tool call. All paths and process details describe this Windows machine;
recheck them before operating on a game process.

## 1. User objective and current result

The user wants earned New Game Plus equipment available at the opening of
MGS4, instead of waiting for Metal Gear Mk. II. They also requested direct
launch without the Master Collection launcher, continued self-testing, save
safety, repeated-NG+ checks, and cutscene skipping while testing.

Implemented and installed: native Windows x64 ASI **0.4.0**. Latest release
package: **0.4.1**, which updates documentation after manual-save tests; its
ASI is unchanged from 0.4.0. The normal installed game was restarted after
testing. Test DLLs were verified absent from that process. Recheck live state;
do not reuse an old PID or window handle.

The mod restores earned inventory/ammo/camo using the original game procedures.
It does not grant unearned Bandana or Stealth. It recognizes restored inventory
to avoid repeated early refills and skips the duplicate Mk. II inventory
procedure when earned weapons/permanent equipment are already present. The
story and camo procedures still execute. Cutscene skipping is test-only and is
not a feature installed in the user's game.

**Do not say everything has been tested or promise zero corruption risk.** A
complete campaign and full traversal from Clear Data to Mk. II have not been
played. Other-mod combinations and other executable builds are unverified.
An optional question asking which other mods to test was sent; no answer was
received before this handoff. Only Early Equipment was installed as an ASI.

## 2. Read these files first

1. `README.md`: user-facing behavior, install/remove, launch and backup.
2. `docs/implementation.md`: native implementation and test methodology.
3. `docs/validation.json`: aggregate status; some older detail reports are
   explicitly inherited from 0.3.0 where the activation implementation is unchanged.
4. `docs/story-tests.json`: repeated NG+ and actual Mk. II stage branches.
5. `docs/manual-save-tests.json`: actual Save UI/file writer and cold loads.
6. `docs/save-roundtrip-tests.json`, `docs/save-safety.json`,
   `docs/backup-tests.json`: codec, original-file comparisons, backup checks.
7. `docs/PROJECT_STRUCTURE.md`: directory/file responsibilities.
8. `docs/WORKSPACE_TREE.txt`: exhaustive local tree, with junction targets shown
   instead of traversed game assets; nested `.git` contents summarized. It is an
   untracked snapshot of the earlier Codex workspace and lists private paths.

The handoff archive contains project source, reports, local test harness source,
and the latest release ZIP. Private save fixtures, game files, compiler, runtime
dumps and complete third-party research checkouts are excluded. Keep the full
local workspace privately if the next agent needs to reproduce live tests.

## 3. Workspace, target and Git state

```text
Workspace: %USERPROFILE%\Claude\MGS4-EarlyEquipment
           (moved 2026-11-02 from %USERPROFILE%\Codex\MGS4-EarlyEquipment)
Shell: PowerShell
Game root: C:\Program Files (x86)\Steam\steamapps\common\METAL GEAR SOLID 4
Executable: <game root>\MGS4\mgs4.exe
Saves: <game root>\mgs4_savedata_win
Installed mod: <game root>\MGS4\scripts\MGS4EarlyEquipment.asi
Installed log: <game root>\MGS4\scripts\MGS4EarlyEquipment.log
Installed loader: <game root>\MGS4\winmm.dll
Backup launcher: <game root>\Launch-MGS4.cmd
```

The project root is a local Git repository on branch `main`, initialized
2026-11-02. It has no remote and nothing has been pushed. Submodules in
`external/` are pinned upstream tags: MinHook v1.3.4, MGS4 Best Trainer Ever
V2.7.0 (ProcessHandle and save decoder for the harness) and bbtracker v0.5.0
(VPAK reader, research notes). Run `git submodule update --init` after a fresh
clone. Owned harness scripts are tracked in `tests/live/` and `re/`; their
private inputs/outputs stay in ignored `research/` and `build/`. Other nested
`.git` directories belong to research checkouts under ignored `research/`.
`.gitignore` excludes `/research/`, `/tools/`, `/build/`, `/backups/`, `/dist/`,
`*.log` and the generated `docs/WORKSPACE_TREE.txt`. Do not blindly force-add
ignored directories containing private/game material.

Supported target: Steam Windows x64 1.4.1, App ID `2492670`.
Only this executable SHA-256 is accepted:

```text
656ede900b03467e4ed05a00eca35f0ac306ce57a8f29a76a20e5a5410d02900
```

Internal build:
`Pela_[MPA]_x64_BGFX_0.0.16_Release_ww_[Code]e9923cfe_[DataNew]4a9b66e6_2026_0911`.
All addresses below are RVAs relative to the current ASLR module base.

## 4. Deliverables and hashes

| Artifact | SHA-256 |
| --- | --- |
| `dist/MGS4-EarlyEquipment-0.4.1.zip` | `1a7425db3185de44517575034263770db3ddec988dda66d7c2db68138ec16cc8` |
| `dist/MGS4/scripts/MGS4EarlyEquipment.asi` | `95e32eba9fc9a407ceb4acd1aca8ead614c1ee9ed4b55184ecc0068c44f62574` |
| `dist/MGS4/winmm.dll` | `57ec56390c92a18b82f58855e63c93985e254d1e29d5f75cbc28dc08f96c8a12` |

Release ZIP has exactly eight allowlisted entries: README, launch CMD, backup
PowerShell script, loader, ASI, two licenses, and SHA256.json. No saves, game
assets, PDBs or test helpers. The loader is Ultimate ASI Loader x64 10.0.2;
MinHook source is v1.3.4. Older ZIPs in dist are retained historical artifacts.

## 5. Implementation and evolution

`src/early_equipment.c` checks the disk SHA-256 and native entry signatures
before installing MinHook scheduler/indexed-GCL-procedure hooks. Restoration
runs on the game thread after the original scheduler. It requires completed
runs > 0, one of difficulties 20/30/35/40/50, opening stage s01a00l/s01a05l/
s01a10l, and scenario < 18. Policy is in `src/policy.h`.

Carry tables are validated before use. The original self-contained inventory
body is 360 bytes, camo body 188 bytes, generated into `src/restore_script.h`.
Calls use a non-null empty GCL argument structure and one local variable. A
native refresh command follows. Solid Eye live item 6 == 1 identifies an
already-restored loadout and prevents repeated early restoration.

At s01a10l/scenario 18, the duplicate guard requires completed runs, a byte-for-
byte match of the original inventory procedure, valid carry data, Solid Eye,
all carried weapons and all earned permanent items 6..60. Spent consumable
counts do not invalidate the guard. Missing equipment permits normal handover.

Work progressed through 0.1/0.2 development, 0.3 inventory-based validation,
0.3.1 verified launch backups, 0.4 removal of transient session flags from the
duplicate guard, and 0.4.1 documentation after extended manual-save testing.
0.4 derives the guard from actual inventory so it also recognizes a checkpoint
loaded directly in a fresh process. Do not reintroduce a global applied/cycle
flag that can suppress handover for a different untouched save.

Important harness corrections: an early story fixture copied link buffers
without native live-inventory synchronization, so its checkpoint lacked gear.
That failed fixture was **not evidence of a product save/refill bug**. Another
early cross-stage fixture copied only the stage name/hash and produced a black
world; it was replaced with authentic complete Red Zone world-state fixtures.
Do not cite either abandoned fixture as a proven game/mod failure.

## 6. Tests actually performed

| Area | Verified result and scope |
| --- | --- |
| Activation policy | 10 checks; 9 game-thread fixtures cover NG, NG+, late stage/progress, bad difficulty/carry, already-restored stock. Older activation details are marked as 0.3.0. |
| Opening worlds | Real s01a00l and s01a10l worlds; all 67 carried weapon/attachment entries, ammo/camo/items, actual M4 model load/equip. Fixtures seeded in disposable memory. |
| Actual Mk. II branch | Native stage setup/procedures 291/295/296/998, movie completion 1001 and scenario 19. Duplicate refill skipped; rendered gameplay returned after tutorials. |
| Second NG+ | Simulated second Clear Data passed through actual title proc 198 and title_movie -> s01a00l. Latest 3 rations/77 M4 rounds and earned Stealth restored; unearned Bandana stayed absent. No full game completion. |
| Restart same Clear Data | Same clear count 2 restarted through native NG+ initialization; original Clear Data stock restored again rather than the spent stock from the previous attempt. |
| Second-cycle meeting | 1 ration/17 M4 reserve and earned Stealth retained through actual meeting branch, scenario 19 and rendered world. |
| Untouched-save control | Actual stage handover ran with Solid Eye initially absent; restored it and native difficulty-capped supplies (3 rations/300 M4 reserve). |
| Native save codec | Three serializer/load round trips, exact decoded bytes and inventory/currency, checkpoint reload; deliberately damaged payload rejected with native error 2. |
| Manual early save | Normal title Load Game loaded copied user NG+ slot. Save/New Save/Yes UI wrote a new slot; all 95 weapons, 68 ammo pools, 99 items and camo matched live. Cold UI reload with release ASI matched inventory/camo/carry, with no repeated handover. |
| Manual post-meeting save | Native-sync checkpoint fixture entered actual meeting. Normal completion checkpoint kept 1 ration/17 M4 reserve. Save UI wrote those values; cold UI load with both ASI and test helper absent matched all inventory/camo/carry arrays and rendered the world. |
| Native checkpoint semantics | Reducing live stock after a checkpoint did not change that checkpoint's manual-save stock. The menu explicitly warns it saves last-checkpoint state. This behavior is retained. |
| Backup/launcher | Backup byte/hash verification; distinct retained backups; launch blocked on actual filesystem backup failure; successful backup launches marker/game; running-game backup rejected. |
| Packaging/install | Hash manifests/archive allowlist, matching installed ASI, unsupported installer/host rejection and clean release startup without development modules. |

UI test qualification: automated keyboard events were ignored. The local
helper invoked native pause construction and selected the Save row; mouse
confirmed the normal Save/New Save/Yes widgets. The native UI/file writer did
the saving, not a test script writing MGS4.SAV. Cold loads used the title UI.
Do not describe this as an entirely human-input-only playthrough.

Not tested: complete campaign, full opening route traversal, other executable
versions or other-mod combinations, exhaustive overwrite/recovery/power-loss
cases. No guarantee of safety under every failure or mod conflict.

## 7. Original saves and isolation

Original backup folders are `backups/saves-20261101-225809` and
`backups/pre-release-tests-20261101-231314`. Compared with the older backup, 12
of 14 original folder files matched. Only usersv/usersv.bak differed, timestamped
2026-11-02 00:56:07 before isolated story tests; gameplay saves matched. Do not
claim all 14 always matched the oldest backup.

Extended manual tests took a new baseline in
`build/ui-save-original-baseline.json`; all 14 originals were unchanged during
those isolated tests. A normal real-game launch afterward can write native
profile/settings files again. Keep comparisons tied to their baseline/time.

Latest verified launch backup at handoff:
`<game root>/MGS4-SaveBackups/20261102-151138-820-f8f57d6b` (14 files).
`Backup-MGS4Saves.ps1` retains previous backups, verifies copied/source hashes
and checks source stability. A completed backup contains BACKUP-SHA256.json.
The launch CMD fails closed on backup errors. Launching through Steam bypasses
that extra backup step. Do not restore or overwrite the user's real saves as
part of a test; use copied save folders.

Local sandbox roots under build:

- `save-sandbox`: original story/codec tests, release 0.4 and private fixtures.
- `ui-save-sandbox`: manual Save/Load tests, copied original plus new test slots.
  Its ASI is currently renamed `MGS4EarlyEquipment.asi.disabled` for the
  unmodded cold-load test. Do not confuse that state with the installed game.
- `scenario-sandbox`: earlier/incomplete alternate fixture; not final evidence.

Each sandbox has a separate mgs4_savedata_win. The game common/ww/Jpgs
directories are junctions to installed assets. **Never recursively clean these
trees with a method that follows junction targets.** No game assets are copied
into the handoff archive. Only one mgs4.exe instance should run during helper
tests because clients select by executable name and share an RPC mapping.

## 8. Build, install, package and direct launch

```powershell
Set-Location '%USERPROFILE%\Claude\MGS4-EarlyEquipment'
.\build.ps1
.\install.ps1
.\package.ps1
```

Compiler: `tools/zig-windows-x86_64-0.13.0/zig.exe`. build.ps1 accepts `-Zig`.
It builds the ASI and runs policy checks. Installer accepts `-GameRoot`, checks
the exact executable hash, preserves existing ASI loaders, backs up a replaced
ASI, and copies launch/backup scripts. A changed ASI cannot replace the installed
one while MGS4 runs. An identical mapped ASI is skipped. Before any rebuild,
remember that compiler/PE timestamps can change the file hash; compare actual
code and retest meaningful changes, not just version strings.

Python used locally (3.12; no other Python is installed on this PC):
`%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
The harness imports ProcessHandle and the save decoder from the
`external/mgs4trainer` submodule; `requirements-dev.txt` pins pefile, capstone
and lz4. Do not expect this interpreter path on another PC.

Use installed Launch-MGS4.cmd with Steam running. Test launches used environment
SteamAppId and SteamGameId = 2492670 and native arguments:

```text
-region eu -lan en -selfregion EU -resolution 0 -ctrltype AUTO
```

Working directory must be the relevant MGS4 folder. `--stage s01a10l` was used
for some debug fixture starts; omit it for the normal game. A renamed cloned
executable failed; use mgs4.exe. Start the actual game visibly. Hidden startup
caused misleading black capture/loading until activation in some experiments.

## 9. Local harness and reproduction pitfalls

`tests/game_probe.c` compiles to build/EEGameProbe.dll with MinHook sources. It
hooks the scheduler for game-thread RPC and observes indexed procedures. It
exports activation/handover/cutscene helpers. Never install/package it for users.
`tests/live/inject.py` loads only allowlisted development modules. Verify the
process's full executable path is a sandbox before injecting. Release ASI must
initialize before helper injection. Release has no EeTest/test_ API; the PE may
still export CRT/MinHook symbols, so an assertion of zero exports is incorrect.

`tests/live/game_rpc.py`: GameRpc().base/.pid/.proc, call(fn,*args), export(name),
close(). Shared mapping Local\\MGS4EarlyEquipmentTests, 4096 bytes: pending LONG
0, done LONG 4, function QWORD 8, four QWORD arguments 16, result QWORD 48.
Calls are stateful and unsafe against the wrong stage/process. No automatic
end-to-end suite exists; scripts require their documented setup.

Useful scripts in `tests/live/` (setup and full table in its README):

- `ui_save_state.py`: read-only live inventory/carry snapshot.
- `ui_select_save.py`: native pause/Save-row selection; confirm subsequent UI.
- `seed_story_checkpoint.py`: original pre-Mk. II checkpoint into snapshot.
- `start_mkii_story.py`: spent stock + native sync + scenario-18 checkpoint.
- `start_authentic_meeting.py`: full Red Zone template with current inventory;
  --untouched selects the negative control. Contains the old save-sandbox trace
  path; adapt it if using another sandbox.
- `start_next_ngplus.py`: requires title script (199 procs) and private
  build/next-clear-fixture.bin, invokes real title proc 198.
- `verify_next_ngplus.py`: requires title_movie (8 procs), completion proc 8,
  checks opening and merges its `next_NGplus` result. Opening scenario alone is
  not proof of input-ready gameplay: the first movie can still be running.
- `test_native_save.py`, `test_native_load.py`: same-process native codec tests;
  object addresses in build/save-test-context.json are stale after a restart.
- `re/disasm.py`, `re/extract_gcx.py`, `re/generate_restore.py`: local
  RE/extraction; see `re/README.md`. Private inputs stay in `research/`.

Some tests were orchestration snippets rather than saved runnable scripts. The
JSON reports capture results, not a promise of a one-command reproduction.
Scripts therefore never write `docs/`: results go to ignored `build/reports/`
with a `<name>.runs.json` log of script, time and loaded module hashes/versions.
Promote a result into `docs/` only by a reviewed manual merge.
The native-sync command must run before copying active link inventory into a
fixture snapshot. Use complete authentic world state for cross-stage fixtures.
Wait for actual movie proc 998 initialization before calling completion 1001.
Calling a completion too early can leave invalid fades/world state.

## 10. Native reference for continuing research

| RVA / offset | Meaning |
| --- | --- |
| 0x1c28b28 / 0x1c28b30 | Active/checkpoint link pointers (0x5b40 bytes) |
| 0x1c28b38 / 0x1c28b40 | Active/checkpoint var pointers (0x2800 bytes) |
| link + 0 / + 6 | Completed runs uint16 / difficulty uint16 |
| link + 0x2c / + 0x34 / + 0x54 | Stage hash / 7-char stage / scenario uint32 |
| link + 0x1d4 / + 0x350 / + 0x526 | 95 weapon states / 68 ammo / 99 items |
| link + 0x4bb8 | 0x400 bytes camo tables |
| 0x1d825aa + ID*0x50 | Native live weapon ownership uint16 |
| 0x1d84344 + ID*0x48 | Native live item state int16 |
| 0x1d81f30 + pool*0x18 | Native live reserve ammo int16 |
| 0x3ed5f0 | Exec GCL body(body, non-null empty args, locals) |
| 0x3ed630 | Exec indexed proc(id,args) |
| 0x3edd10 / 0x3ee030 | Current script / decode GCL block |
| 0x740280 | Main scheduler |
| 0x5bcb0 | Continue/reload(0), return title(1); world must be initialized |
| 0x3ecef0 | Snapshot -> active copy |
| 0x4ba910 / 0x4ba400 | Native serializer / loader+validator |
| 0x4b2200 / 0x4b2240 | Native save error get / set |
| 0x4d7c00 / 0x3b7c8b0 | Pause constructor / current pause handle |
| 0x4d40a0 | Set native menu state; menu+0x90, state 3 closes submenu |
| 0x73fdc0 / 0x73fe60 / 0x73fdd0 | Pause flags get / set / clear |

Native live -> link inventory sync is GCL command hash 6ea0ef (handler 0x64ba0).
Execute body `69 c9 2b 08 04 06 ef a0 6e 00 00`, empty args, locals 0. Refresh
985199 (handler 0x69de0) is not full inventory sync. M4 reserve is pool **18
decimal**, not hexadecimal 0x18 or pool 12. Original carry may exceed difficulty
caps: source M4 357 -> 300 and rations 5 -> 3 on difficulty 50 are normal.
Item IDs: ration 1, Solid Eye 6, Mk. II 7, Bandana 15, Stealth 16. States -1
mean absent; weapon state 1 locked, 2 usable.

Native save object: allocate/zero 0x12000 bytes. Encoded payload at +0xd60,
length +0x92a8 (0x8344), checksum +0x92b0. Native load expects checksum +0x6dc;
CRC32(encoded) % 0xd658. +0x90a0 lies inside the encoded payload (embedded
version), so do not overwrite it with plaintext before native decoding. Native
load fills checkpoint buffers. Check snapshot inventory/currency, then Continue
to rebuild active gameplay. Reset native error after intentionally damaged input.

Stage s01a10l: 291 setup, 295 inventory, 296 camo, 998 Mk. II movie, 1001 normal
completion to scenario 19/checkpoint. Callback 1000 ends Red Zone introduction
to scenario 17. Title proc 198 is the native NG+ initializer; title_movie proc 8
finishes the opening video. Test skips must target the loaded script, never a
hardcoded proc ID in a different stage. Not all prior first-area movie skip
attempts reliably terminated the actor; rely on the narrower report scope.

## 11. Suggested next steps

- Read evidence/limits before telling the user the project is ready or fully tested.
- Complete an actual opening-route/campaign playthrough if full gameplay
  certification is required; fixture transitions do not substitute for that.
- Test specific other mods only once the user names the combinations.
- Improve harness reproducibility. Keep historical report versions explicit
  when promoting results from `build/reports/` into `docs/`.
- The current release needs no known code fix from the latest tests. Preserve
  the verified ASI/release hashes unless intentionally changing/rebuilding it.

No publication, Git push or remote communication was performed for this project.
