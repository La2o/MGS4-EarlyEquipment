# Live game harness

Python clients for the development-only helper `tests/game_probe.c`. They drive
a running `mgs4.exe` on its game thread to seed fixtures, skip movies through
native completion callbacks and check inventory. **Never point them at the
normal installed game or real saves.** Use a sandbox copy under `build/` with
its own `mgs4_savedata_win`, and run only one `mgs4.exe` at a time: the clients
select the process by executable name and share one RPC mapping.

These are stateful steps, not a turnkey suite. Each script expects a specific
stage, procedure count or earlier script; see `AGENT_HANDOFF.md` sections 9-10.

## Setup

- Windows x64, Python 3.12, and `pip install -r requirements-dev.txt`.
- `git submodule update --init`: `external/mgs4trainer` supplies
  `ProcessHandle` and the save decoder `mgs4save`.
- `build/EEGameProbe.dll`: build it like the release ASI in `build.ps1`, with
  `tests/game_probe.c` in place of `src/early_equipment.c`.
- `build/EEDev.asi` (activation tests only): `src/early_equipment.c` built with
  `-DEE_DEV_CHAIN`, which adds the `EeTest_RunHandoverNow` export.
- Private fixtures stay in ignored folders: `research/save_decrypted.bin`
  (decrypted copy of a real save) and `build/next-clear-fixture.bin`.

Start the sandbox game visibly, wait for the release ASI to log `Ready`, then:

```powershell
python tests\live\inject.py build\EEGameProbe.dll
```

Run scripts as `python tests\live\<script>.py` from any directory. Do not use
`python -I` or `-P`; the scripts import `game_rpc` from their own folder.

## Scripts

Results go to `build/reports/` unless a full path is shown.

| Script | Purpose | Writes |
| --- | --- | --- |
| `game_rpc.py` | Shared client: `GameRpc().call(fn, *args)`, `.export(name)`, `ROOT` | - |
| `reports.py` | Shared result writer with a provenance log; see Results | - |
| `inject.py <module>` | Load an allowlisted development module into the running game | - |
| `ui_save_state.py [out.json]` | Read-only live inventory/carry snapshot | Optional JSON |
| `ui_select_save.py` | Open the native pause menu and select Save; confirm with the mouse | - |
| `run_activation_tests.py` | Nine activation fixtures; needs `EEDev.asi` loaded too | `activation-tests.json` |
| `run_runtime_tests.py` | s01a10l restore and duplicate-guard checks | `runtime-tests.json` |
| `test_equip.py` | Equip the M4; spent rations stay spent | Adds checks to `runtime-tests.json` |
| `test_opening_world.py` | Sample the s01a00l opening for 12 seconds | `opening-world-tests.json` |
| `verify_live.py` | Historical 0.2.0 check against `build/live` | `validation-live.json` |
| `seed_story_checkpoint.py` | Load the pre-Mk. II checkpoint from the save fixture | - |
| `skip_opening.py` | Skip s01a10l movies until progress 17 | - |
| `start_mkii_story.py` | Spend stock, native sync, scenario-18 checkpoint, reload | `build/story-before.json` |
| `start_authentic_meeting.py [--untouched]` | Red Zone checkpoint with current or untouched inventory | `build/meeting-context.json` |
| `start_next_ngplus.py` | Simulated second Clear Data through title proc 198 | `build/ngplus-started.txt` |
| `verify_next_ngplus.py` | Skip the title movie, check the next NG+ opening | Merges `next_NGplus` into `story-tests.json` |
| `finish_repeated_opening.py` | Finish the opening movie, check same-Clear-Data restart | Merges into `story-tests.json` |
| `start_second_meeting.py` | Second-cycle spent stock into the Mk. II checkpoint | Merges into `story-tests.json` |
| `test_native_save.py` | Native serializer in a sandbox process | `build/save-sandbox/native-save-roundtrip.bin`, `build/save-test-context.json` |
| `test_native_load.py` | Three native load round trips plus a damaged payload; same process as the save test | `save-roundtrip-tests.json` |

`start_authentic_meeting.py` reads the trace log of `build/save-sandbox`; adapt
that path for another sandbox. Object addresses in `build/*.json` are stale
after the game restarts.

## Results

Scripts never write the tracked reports in `docs/`. Those also hold results
from one-off runs that no script reproduces, so an automatic rewrite would lose
evidence. Results go to ignored `build/reports/`. Beside each one,
`<name>.runs.json` records every run that wrote it: the script, the time, and
the path, SHA-256 and compiled version of each project module loaded in the
game. Report `version` fields come from the loaded ASI, never a fixed label.

To update the evidence, compare a result with its `docs/` counterpart and merge
the reviewed fields by hand, keeping the version that was actually tested.
`tests/backup_test.py` writes `build/reports/backup-tests.json` the same way.
