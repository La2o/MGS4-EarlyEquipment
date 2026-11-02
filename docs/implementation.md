# Implementation notes

## Verified target

- Executable SHA-256: `656ede900b03467e4ed05a00eca35f0ac306ce57a8f29a76a20e5a5410d02900`
- Internal build: `Pela_[MPA]_x64_BGFX_0.0.16_Release_ww_[Code]e9923cfe_[DataNew]4a9b66e6_2026_0911`
- Native x64, ASLR enabled. All addresses below are module-relative RVAs.

## State and restoration

`0x1c28b28` points to `linkvarbuf`; `0x1c28b38` points to `varbuf`.
Completed runs at `linkvarbuf+0` are a **16-bit** value. Treating the first four
bytes as one counter incorrectly includes a separate field at `+2`.

The following tables were identified in a local save, verified against live
memory, and then confirmed by decompiling the original stage script:

| varbuf offset | Type | Carry-over contents |
| --- | --- | --- |
| `0x129a` | `uint16[95]` | Weapon and attachment ownership states |
| `0x1358` | `int16[68]` | Ammo pools |
| `0x13e0` | `int16[99]` | Item states/counts |
| `0x14a8` | `uint32[64]` | OctoCamo pattern entries |
| `0x15a8..0x1828` | six `uint16[64]` tables | OctoCamo properties |

In `s01a10l`, procedure 291 restores NG+ inventory at scenario progress 18 by
calling procedures 295 and 296. The ASI runs those two self-contained procedure
bodies on the game thread after the main task scheduler returns. It uses the normal GCL
argument stack with one local variable for each call. The bodies contain no
stage-specific procedure calls or resource references.

Procedure 295 restores only nonzero weapon states, nonnegative ammo pools,
and nonnegative item states below ID 61. It raises pools 1/12/61 to at least
41/36/30, exactly as the original handover does. Procedure 296 restores the
OctoCamo tables. This avoids rewriting inventory tables from a worker thread.

The Solid Eye identifies a restored early inventory because it is present in
clear data and absent from the pre-Mk. II loadout. Its presence prevents repeated
restoration and refills across frames or after loading an already-restored save.
For the later duplicate guard, the mod also requires carried weapon ownership
and permanent equipment to still be present. Version 0.4.0 derives this guard
directly from inventory, with no transient session flags. This also recognizes
an already-restored checkpoint loaded directly at the handover. An untouched
checkpoint still executes the native restoration procedure.

## Hooks

| RVA | Function |
| --- | --- |
| `0x740280` | Main task scheduler; restoration check after original execution |
| `0x3ed630` | Execute indexed GCL procedure; duplicate handover guard |
| `0x3ed5f0` | Execute a GCL body with arguments and local count |
| `0x3edd10` | Get current GCL script context |
| `0x3ee030` | Decode a GCL block header |

The duplicate guard checks scenario 18, the stage code, completed-run count,
restored inventory, and a byte-for-byte match of the original 360-byte inventory
procedure. It does not suppress the camo procedure or story/cutscene procedure.
Runtime hooks are installed by MinHook only after the disk hash and plaintext
entry signatures match. Unsupported builds are logged and left unmodified.
Release builds contain no test RPC interface and require untouched function
entries; optional development detour chaining is compiled only with EE_DEV_CHAIN.

`tests/game_probe.c` is a local test helper, never installed or packaged. It runs
native calls on the game thread, snapshots transient state, and restores it
before the next frame. Activation fixtures cover the stage, scenario, difficulty,
clear-count width, source validation, and existing inventory boundaries. Real
opening-world tests use only the release ASI plus this helper; development ASI
exports are used for isolated activation fixtures. See `validation.json` and the
individual JSON reports for the exact scope and limits.

## Research tools and credits

- [bbtracker](https://github.com/zexk/bbtracker), MIT: initial live-state pointer
  documentation and VPAK index format.
- [MGS4 Best Trainer Ever](https://github.com/ajikfan/MGS4-Best-Trainer-Ever), MIT:
  live item/weapon table documentation used for read-only cross-checks.
- [Jayveer/Gcx](https://github.com/Jayveer/Gcx), MIT: GCX decompilation.
- [Jayveer/libgcl](https://github.com/Jayveer/libgcl): interpreter research used
  to identify and verify the corresponding native x64 functions.
- [MinHook](https://github.com/TsudaKageyu/minhook), BSD: native hooks.
- [Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader), MIT:
  bundled x64 loader, renamed from `dinput8.dll` to its supported `winmm.dll` name.

The ASI contains original wrapper/hook code, MinHook, and 548 bytes of the local
game's restoration procedure bodies. Complete game scripts, saves, runtime
dumps, downloaded research repositories, and compiler tools stay in ignored
local directories and are not part of the release archive.

## Save safety validation (0.4.0)

The package retains the verified prelaunch save backup introduced in 0.3.1,
with a fail-closed launcher and timestamped snapshots.

In a separate copy of the executable and save folder, the original native
serializer at RVA `0x4ba910` produced a 0x8344-byte encoded payload. It was written
to a private test file and read back, then passed to the native load/checksum
routine at `0x4ba400`. All decoded payload bytes matched on three runs. Inventory
and currency were recovered into the checkpoint buffers. A native Continue
reload at `0x5bcb0` rebuilt the actual world with the restored inventory; the mod
log showed no repeated handover. Flipping a payload bit caused native error 2
and rejection, confirming checksum validation remains active.

The test helper never shipped. Original gameplay save files were not modified.
These codec tests are detailed in `save-roundtrip-tests.json`; the later manual
save tests below additionally exercise the native interface and outer writer.

## Manual save and cold-load tests (package 0.4.1)

The ASI binary is unchanged from 0.4.0. A fresh isolated executable and copied
save folder were used. The normal title Load Game UI loaded the copied opening
NG+ save. The release restored earned equipment. The native pause constructor
at RVA 0x4d7c00 and main-list selection field were used to open/select Save,
because automated keyboard events were ignored. Save, New Save and Yes were
then confirmed through the native UI with mouse input. The file writer created
a new 33613-byte MGS4.SAV plus native metadata and icon files.

All 95 weapon states, 68 ammo pools, 99 item states and camo bytes in that file
matched the live game. A fresh process with only the release ASI loaded the new
slot through the normal title UI; inventory/camo/carry arrays matched exactly,
and there was no new early-handover log entry.

A reduced-live-stock control saved the previous checkpoint's 3 rations/300 M4
rounds, matching the game's explicit checkpoint warning. This is native save
semantics, not evidence of a mod refill bug. After a native-sync checkpoint
fixture entered the actual Mk. II stage branch, normal movie completion and
checkpoint creation retained 1 ration/17 M4 rounds. Another manual UI save
wrote those checkpoint values and all current weapon/ammo/item states. A cold
load through the title UI with the ASI and test helper absent retained all
inventory/camo/carry arrays exactly. See `manual-save-tests.json`.

## Repeated NG+ and Mk. II stage tests

The native title procedure 198 initializes NG+ from a simulated second Clear
Data fixture, including procedures 73/75 capturing inventory/camo into carry
tables. The normal title_movie stage then loads s01a00l. The opening restored
the fixture's latest 3 rations, 77 M4 reserve rounds, and earned Stealth, without
granting Bandana. Starting the same Clear Data again restored those same values.
This tests the native NG+ initialization path; it does not simulate completing
every act or use the Clear Data selection UI.

For the actual Mk. II stage branch, the test invokes native inventory sync
command 6ea0ef before committing the disposable checkpoint. It then uses the
complete authentic Red Zone world-state template with current inventory and
carry data. This is necessary: copying linkvarbuf without synchronizing native
live inventory creates an invalid test checkpoint missing the restored gear.
That fixture error is not evidence of a product save/refill bug.

The second-cycle stage executed procedures 291, 295, 296 and 998, then the normal
movie completion callback 1001. After tutorials, rendered gameplay resumed at
scenario 19 with 1 ration, 17 M4 reserve rounds, earned Stealth, and no Bandana.
An untouched original-inventory control executed the native handover normally,
restoring Solid Eye and difficulty-capped supplies. Movie completion callbacks
and checkpoint fixtures avoid a full opening-route playthrough. Test helpers
and cutscene skipping are not installed in the user's game.
