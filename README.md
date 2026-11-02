# MGS4 Early Equipment

Package **0.4.1** (tested ASI **0.4.0**) - Windows x64 ASI mod for **Metal Gear Solid 4 — Master Collection, Steam 1.4.1**.

Restores the equipment carried from your completed playthrough during an opening
New Game Plus stage, before meeting Metal Gear Mk. II. It uses the
game's own inventory and camo restoration procedures, including the normal
starting-ammo minimums. It does not grant equipment absent from your clear data.

## Installed on this PC

The mod is installed in:

```text
C:\Program Files (x86)\Steam\steamapps\common\METAL GEAR SOLID 4\MGS4\scripts\MGS4EarlyEquipment.asi
```

Start NG+ by loading Clear Data, or load an opening NG+ save after installation.
Check `MGS4\scripts\MGS4EarlyEquipment.log` for a `Restored earned inventory`
entry. The mod also recognizes an early save that already contains its gear,
so loading that save does not refill everything again.

`Launch-MGS4.cmd` in the game's root starts MGS4 directly and skips the Master
Collection launcher. Keep Steam running. The shortcut currently uses English
and the European region, matching this PC's original launch arguments.

## Save protection

Use `Launch-MGS4.cmd` for a verified backup before each launch. It copies the
complete `mgs4_savedata_win` folder into a new timestamped folder under
`MGS4-SaveBackups` beside the game, verifies SHA-256 hashes, and checks that the
source did not change during copying. Old backups are retained. If backup
creation or verification fails, the launcher stops before starting the game.
Launching through Steam directly does not run this backup step.

The ASI leaves the native save encoder, checksum validation, and file writer
unchanged. Three round trips through the native save serializer/loader passed in
an isolated game copy, followed by a real checkpoint reload with gear intact.
A deliberately damaged payload was rejected by the native checksum validator.
The native Save/New Save/Yes interface also wrote new slots before and after
Mk. II. The early save cold-loaded with the release ASI and exact inventory,
ammo, items, camo and carry data, without a repeated handover. The post-Mk. II
save retained 1 ration and 17 M4 reserve rounds and cold-loaded with the ASI
removed. A helper opened the pause menu and selected its Save row because test
keyboard input was ignored; normal UI confirmations and the native file writer
performed the saves. This is evidence against corruption, not a guarantee
against every crash, power loss, or conflict with another mod.

Manual saving follows the game's last checkpoint. Changes made after that
checkpoint are not necessarily included until the next checkpoint. The test
confirmed this native behavior; the mod does not replace it.

To recover a backup, close MGS4, keep a copy of the current save folder, and copy
a timestamped backup containing `BACKUP-SHA256.json` back into
`mgs4_savedata_win`, excluding
`BACKUP-SHA256.json`. Never restore while the game is running. Local test details
are in `docs/save-roundtrip-tests.json`, `docs/manual-save-tests.json`, and
`docs/backup-tests.json`.

## Install elsewhere

Extract the release ZIP into the install folder containing the `MGS4` directory.
If you already have an ASI loader, retain your existing loader and copy only
`MGS4\scripts\MGS4EarlyEquipment.asi`. The bundled `winmm.dll` is Ultimate ASI
Loader x64 10.0.2. Source checkout users can run `install.ps1 -GameRoot '...'.`

## Behavior and compatibility

- Activates only with a completed playthrough, in `s01a00l`, `s01a05l`, or
  `s01a10l`, with scenario progress below 18.
- Uses the carry-over weapon states, ammo pools, item counts, and OctoCamo tables.
  The game's restoration routine excludes iPod tracks from this handover.
- Preserves locked versus usable weapon states. It grants no infinite ammo,
  infinite health, extra currency, or unearned Bandana/Stealth unlocks.
- Skips the later duplicate inventory handover when the carried weapons and
  permanent equipment are already present, including checkpoints loaded in a
  fresh session. Spent supplies stay spent. Mk. II's story sequence still runs.
- Refuses to hook any executable with a different SHA-256. Steam updates need
  a verified compatibility update to this mod.
- Other mods that replace these script functions or the opening loadout may
  conflict. Compatibility with trainers has not been tested.

## Validation status

The build passes ten activation-policy checks and nine game-thread activation
fixtures, including normal New Game, invalid carry data, later stages, and
already-restored saves. Cold-start loading through the installed ASI loader passed.

The release ASI restored carry-over equipment in the actual first playable area
(`s01a00l`, progress 1) and before Mk. II (`s01a10l`, progress 17). All 67 carried
weapon/attachment entries matched; ammo and camo matched; Solid Eye and Mk. II
were present, while unearned Bandana and Stealth stayed locked. The M4 model
loaded and equipped in both worlds. Spent rations stayed spent across frames.
The native Mk. II inventory procedure skipped a duplicate refill, and still ran
for an unmodified inventory loaded in the same completed-run cycle.

Version 0.4.0 additionally passed the actual Mk. II stage branch in two NG+
cycles. The second cycle retained 1 spent ration and 17 M4 reserve rounds through
the handover and returned to rendered gameplay. A simulated second Clear Data
fixture ran through the native title NG+ procedure and restored its latest
stock and newly earned Stealth at the opening, with an unearned Bandana absent.
Restarting that same Clear Data restored its saved stock again. An untouched
inventory still receives the normal Mk. II handover.

These tests used disposable process-memory Clear Data and checkpoint fixtures,
native inventory synchronization, and movie completion callbacks. They did not
complete another full playthrough or walk the entire opening route. Three
native save round trips and a checkpoint reload retained the second cycle's
spent stock and earned equipment. All gameplay save files match the pre-test
backup. Of the 14 files in the full save folder, only `usersv` and `usersv.bak`
differ; their write timestamps precede the isolated story tests. Current copies
and the original backups are retained. Details are in `docs/validation.json` and
`docs/story-tests.json` in the source checkout. Backups and development test
modules are not shipped.

## Remove

Close MGS4 and remove `MGS4\scripts\MGS4EarlyEquipment.asi`. Leave `winmm.dll`
if other ASI mods use it. The mod changes runtime state; equipment already
written by a subsequent game save remains in that save. Use the pre-test backup
if you need the original save state.

## Build

Use Zig 0.13.0 for Windows x64, then run:

```powershell
.\build.ps1 -Zig 'C:\path\to\zig.exe'
```

MinHook v1.3.4 sources are in `external/minhook`. The generated script header
contains only the two restoration procedures, extracted from the local game's
`s01a10l` GCX; no complete game assets are shipped.

Technical details and credits are in `docs/implementation.md`.
