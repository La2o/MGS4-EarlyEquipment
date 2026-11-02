# MGS4 Early Equipment

An ASI mod for **Metal Gear Solid 4: Guns of the Patriots** in the **Master
Collection on Steam (Windows)**. In New Game Plus, the gear you earned in your
completed playthrough is available from the opening area, instead of only
after you meet Metal Gear Mk. II.

The mod runs the game's own carry-over routines, so you get exactly what your
Clear Data holds, with the game's normal ammo limits. It never adds equipment
you didn't earn.

Release 0.4.2. The mod file itself is version 0.4.0, which is what its log
reports; this release only updates the launcher, documentation and license.

## Requirements

- Metal Gear Solid 4 from the Master Collection on Steam, game version 1.4.1.
  The mod checks the exact `mgs4.exe` and stays inactive on any other build,
  so a game update disables it until the mod is updated.
- A completed playthrough: start NG+ from your Clear Data, or load an NG+ save
  from Act 1 before the Mk. II meeting.

## Install

1. Close the game.
2. Extract the ZIP into the game folder, the one that contains the `MGS4`
   folder. By default that is
   `C:\Program Files (x86)\Steam\steamapps\common\METAL GEAR SOLID 4`.
3. Already using other ASI mods? Keep your existing loader (`winmm.dll` or
   `dinput8.dll` in `MGS4`) and copy only `MGS4\scripts\MGS4EarlyEquipment.asi`.

The bundled `MGS4\winmm.dll` is Ultimate ASI Loader x64 10.0.2.

## Use

Load your Clear Data to start NG+, or load an NG+ save from Act 1 before
Mk. II. Your earned gear appears as soon as gameplay starts. To confirm, open
`MGS4\scripts\MGS4EarlyEquipment.log` and look for `Restored earned inventory`.
Loading a save that already has the gear doesn't refill it again.

At the Mk. II meeting the game normally hands over your gear and refills your
supplies. When your carried weapons and permanent equipment are already there,
the mod skips that second handover, so spent ammo and rations stay spent. The
Mk. II story scene still plays normally. If anything is missing, the game's
normal handover runs.

## Optional launcher with save backups

`Launch-MGS4.cmd` in the game folder starts MGS4 directly, skipping the Master
Collection launcher, and backs up your saves first. Keep Steam running.
Launching from Steam still works, just without the backup.

- **Language:** English by default. To change it, edit the two `set` lines at
  the top of `Launch-MGS4.cmd`; the comment above them lists the values.
- **Backups:** each launch copies the whole `mgs4_savedata_win` folder into a
  new timestamped folder under `MGS4-SaveBackups`, checks every file's SHA-256,
  and checks that nothing changed while copying. If the backup fails, the game
  doesn't start. Old backups are never deleted; remove them when you no longer
  need them.

To restore a backup, close MGS4 and keep a copy of your current
`mgs4_savedata_win`. Then copy the contents of a backup folder that contains
`BACKUP-SHA256.json` into `mgs4_savedata_win`, leaving out that JSON file.

## What it changes

- Activates only after a completed playthrough, in the Act 1 areas before the
  Mk. II meeting, on any difficulty.
- Restores carried weapons (keeping locked versus usable), ammo, items and
  OctoCamo, as the game's own Mk. II handover does. iPod tracks aren't part of
  that handover.
- No infinite ammo or health, no extra Drebin Points, and no unearned unlocks
  such as the Bandana or Stealth.
- Doesn't change how the game saves. Saves load normally after removing the
  mod. Manual saves store the last checkpoint rather than your exact current
  state; that is normal MGS4 behavior.

## Compatibility and testing

- Other mods that change the opening loadout or these story scripts may
  conflict. Trainers and other mod combinations haven't been tested.
- Linux and Steam Deck (Proton) haven't been tested. ASI loaders there usually
  need the Steam launch option `WINEDLLOVERRIDES="winmm=n,b" %command%`.

Tested on Windows with Steam version 1.4.1:

- **Starting NG+ from Clear Data:** tested with simulated Clear Data in game
  memory through the game's own NG+ setup; the opening movie was skipped. The
  latest earned gear and ammo were restored and unearned items stayed locked.
- **Act 1 areas:** gear restored in the first playable area (carry data placed
  in game memory) and just before Mk. II (a real NG+ save loaded from the title
  menu). Every carried weapon, ammo pool, item and camo matched.
- **The Mk. II meeting:** the game's real story branch ran in two NG+ cycles,
  with the cutscene skipped. Spent supplies stayed spent, while untouched
  inventory still got the normal handover.
- **Saving:** the game's own save and load code round-tripped saves exactly. A
  save made from the Save menu before Mk. II reloaded with the mod, and one
  made after Mk. II reloaded without it; both kept their exact inventory.

Not tested: a complete playthrough, other game versions, and every crash,
power-loss or mod-conflict case. Back up your saves.

## Remove

Close MGS4 and delete `MGS4\scripts\MGS4EarlyEquipment.asi`. Leave `winmm.dll`
if other mods use it. Gear already written to a save stays in that save.

## Building from source

Requires Zig 0.13.0 for Windows x64 and the Git submodules:

```powershell
git submodule update --init
.\build.ps1 -Zig 'C:\path\to\zig.exe'
.\package.ps1
```

`build.ps1` compiles the mod and runs its policy checks. Technical details are
in `docs/implementation.md`, test reports in `docs/`, and the live-game test
harness in `tests/live/`.

## License and credits

The mod's own code is under the MIT License; see `LICENSE`. The mod also
contains 548 bytes of the game's script bytecode (the two carry-over routines
in `src/restore_script.h`), extracted from MGS4. That bytecode is not covered
by the MIT License. Metal Gear Solid is a trademark of Konami Digital
Entertainment. This is an unofficial fan mod, not affiliated with or endorsed
by Konami.

- [MinHook](https://github.com/TsudaKageyu/minhook) (BSD 2-Clause): function hooks.
- [Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader) (MIT): bundled loader.
- [bbtracker](https://github.com/zexk/bbtracker) (MIT): MGS4 memory layout and archive format research.
- [MGS4 Best Trainer Ever](https://github.com/ajikfan/MGS4-Best-Trainer-Ever) (MIT):
  live inventory documentation and the save decoder used in testing.
- [Gcx](https://github.com/Jayveer/Gcx) (MIT) and
  [libgcl](https://github.com/Jayveer/libgcl): game script decompilation and
  interpreter research.
