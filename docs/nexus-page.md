# Nexus Mods page text

Source for the Nexus Mods page fields, kept here so later releases update the
same wording. The description is Nexus BBCode.

## Name

MGS4 Early Equipment

## Version

0.4.2

## Summary

IN ALPHA - BACK UP YOUR SAVES. Start New Game Plus with your earned gear from the opening area instead of waiting for Metal Gear Mk. II. Uses the game's own carry-over routines: nothing unearned, normal ammo limits. Testing has been thorough, but more testers are needed.

## Page settings

Game: Metal Gear Solid 4: Guns of the Patriots - Master Collection
(`metalgearsolid4mc`). Category: Miscellaneous. Tag: Gameplay. Gallery image:
`docs/nexus-card.png`, an original text card with no game artwork. Main file:
display name `MGS4 Early Equipment 0.4.2 (alpha)`, version 0.4.2.

## Credits (Permissions step)

MinHook by Tsuda Kageyu (BSD 2-Clause): function hooking, compiled into the mod.
Ultimate ASI Loader by ThirteenAG (MIT): bundled as MGS4/winmm.dll.
Research: bbtracker by zexk (MIT), MGS4 Best Trainer Ever by ajikfan (MIT), Gcx and libgcl by Jayveer.
The mod embeds 548 bytes of the game's own script bytecode (the two carry-over routines). They belong to Konami and are not covered by this mod's MIT License.

## Custom permissions (Permissions step)

The mod's own code is under the MIT License: you may re-upload, modify, convert and reuse it, including in other mods, as long as you keep its copyright and license notice (licenses/MGS4-EarlyEquipment.txt in the archive, and https://github.com/La2o/MGS4-EarlyEquipment).
Bundled third-party parts keep their own licenses: Ultimate ASI Loader (MIT) and MinHook (BSD 2-Clause).
Not covered: the game script bytecode embedded in the mod, which belongs to Konami.

## Main file description

ALPHA - BACK UP YOUR SAVES. Extract into the game folder (the one that contains MGS4). Contains the mod, Ultimate ASI Loader, an optional launcher that backs up your saves first, and licenses.

## Description (BBCode)

```bbcode
[center][size=5][b][color=#ff5555]IN ALPHA - BACK UP YOUR SAVES[/color][/b][/size]
Testing so far has been thorough, but the mod still needs more testers before it can be called stable. See [b]Help test it[/b] below.[/center]

[line]

In [b]Metal Gear Solid 4[/b] New Game Plus, the game only hands over the gear you earned when you meet Metal Gear Mk. II. This mod gives it to you from the opening area instead.

It runs the game's own carry-over routines, so you get exactly what your Clear Data holds, with the game's normal ammo limits. It never adds equipment you didn't earn.

[size=4][b]Requirements[/b][/size]
[list]
[*]Metal Gear Solid 4 from the Master Collection on Steam (Windows), game version 1.4.1. The mod checks the exact game executable and stays inactive on any other build, so a game update disables it until the mod is updated.
[*]A completed playthrough: start NG+ from your Clear Data, or load an NG+ save from Act 1 before the Mk. II meeting.
[/list]

[size=4][b]Install[/b][/size]
[list=1]
[*]Close the game.
[*]Extract the archive into the game folder, the one that contains the [b]MGS4[/b] folder. By default: C:\Program Files (x86)\Steam\steamapps\common\METAL GEAR SOLID 4
[*]Already using other ASI mods? Keep your existing loader (winmm.dll or dinput8.dll in MGS4) and copy only MGS4\scripts\MGS4EarlyEquipment.asi.
[/list]
After loading NG+, MGS4\scripts\MGS4EarlyEquipment.log should contain "Restored earned inventory".

[size=4][b]What it does[/b][/size]
[list]
[*]Restores your carried weapons, ammo, items and OctoCamo as soon as NG+ gameplay starts in Act 1, on any difficulty.
[*]At the Mk. II meeting it skips the game's second handover when your gear is already there, so spent ammo and rations stay spent. The story scene still plays.
[*]No infinite ammo or health, no extra Drebin Points, and no unearned unlocks such as the Bandana or Stealth.
[*]Doesn't change how the game saves. Saves load normally after removing the mod.
[/list]

[size=4][b]Optional launcher with save backups[/b][/size]
Launch-MGS4.cmd starts MGS4 directly, skipping the Master Collection launcher, after making a verified backup of your saves in MGS4-SaveBackups. Keep Steam running. It starts the game in English; edit the two lines at the top of the file to change the language.

[size=4][b]Testing so far[/b][/size]
[list]
[*][b]Real play:[/b] an NG+ save on The Boss Extreme, loaded in the Red Zone before Mk. II. Gear was restored on load, the Mk. II meeting and cutscene played normally, and the duplicate handover was skipped.
[*][b]Starting NG+ from Clear Data:[/b] tested with simulated Clear Data in game memory through the game's own NG+ setup.
[*][b]The Mk. II meeting:[/b] the game's real story branch in two NG+ cycles; spent supplies stayed spent.
[*][b]Saving:[/b] the game's own save and load code round-tripped saves exactly, and Save-menu saves reloaded with exact inventory, with and without the mod.
[/list]
Not tested yet: a complete playthrough, other game versions, other mods, Linux and Steam Deck.

[size=4][b]Help test it[/b][/size]
Reports from these situations help most:
[list]
[*]Starting NG+ from Clear Data at the very beginning of the game.
[*]Saving after the Mk. II meeting and loading that save again.
[*]Checking that ammo and rations spent before Mk. II stay spent after it.
[*]Other difficulties, other languages, Linux or Steam Deck.
[/list]
Post what you did and what you saw, with MGS4\scripts\MGS4EarlyEquipment.log, in the Bugs tab or on [url=https://github.com/La2o/MGS4-EarlyEquipment/issues]GitHub issues[/url].

[size=4][b]Uninstall[/b][/size]
Close the game and delete MGS4\scripts\MGS4EarlyEquipment.asi. Leave winmm.dll if other mods use it.

[size=4][b]Source and credits[/b][/size]
Source code (MIT License): [url=https://github.com/La2o/MGS4-EarlyEquipment]github.com/La2o/MGS4-EarlyEquipment[/url]
Uses MinHook (BSD 2-Clause) and bundles Ultimate ASI Loader (MIT). Research credits: bbtracker, MGS4 Best Trainer Ever, Gcx and libgcl.
Unofficial fan mod, not affiliated with or endorsed by Konami.
```
