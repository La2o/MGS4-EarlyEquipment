# Project structure and transfer guide

Prepared 2026-11-02. Start with `../AGENT_HANDOFF.md` for the project history,
implementation, native reference, test evidence and remaining work.

`WORKSPACE_TREE.txt` is the exhaustive local inventory, including generated and
ignored directories. Its junction entries name external targets instead of
recursing into the installed game's assets. Nested Git metadata is summarized.
It is an untracked snapshot of the earlier Codex workspace path and lists
private save paths; `git ls-files` is the inventory of tracked source.
This guide explains the structure rather than listing the compiler's thousands
of headers individually.

## Project-owned source and documentation

```text
MGS4-EarlyEquipment/
|-- AGENT_HANDOFF.md             Start here: full agent handoff
|-- .gitignore                  Excludes local research/build/tools/saves/dist/logs
|-- .gitattributes              Line-ending normalization; CRLF for .cmd
|-- .gitmodules                 MinHook submodule definition
|-- README.md                   User guide and current validation summary
|-- build.ps1                   Compile ASI and run policy checks with Zig
|-- install.ps1                 Hash-guarded local installer; preserve ASI loader
|-- package.ps1                 Eight-entry release ZIP and SHA-256 manifest
|-- Launch-MGS4.cmd             Verified backup, then native game launch
|-- Backup-MGS4Saves.ps1         Retained timestamped backups and hash checks
|-- src/
|   |-- early_equipment.c       Native hooks, target/source validation, restoration
|   |-- policy.h                Opening-stage/difficulty/NG+ eligibility
|   `-- restore_script.h        Generated inventory/camo GCL procedure bodies
|-- tests/
|   |-- policy_test.c           Ten activation-policy checks
|   |-- game_probe.c            Development-only game-thread RPC and fixtures
|   |-- backup_test.py          Backup/launcher integration tests
|   `-- launch_marker.c         Minimal fake game for launcher test assertions
|-- docs/
|   |-- PROJECT_STRUCTURE.md    This guide
|   |-- WORKSPACE_TREE.txt      Complete local path inventory (untracked)
|   |-- implementation.md       Native design, addresses, test methodology, credits
|   |-- validation.json         Aggregate status and test limits
|   |-- activation-tests.json   Nine runtime activation fixtures; historical version
|   |-- runtime-tests.json      Inventory/guard tests; historical version
|   |-- opening-world-tests.json Real-world opening samples; historical version
|   |-- story-tests.json        Native NG+ reset and Mk. II stage branch results
|   |-- save-roundtrip-tests.json Native codec/validator round trips
|   |-- manual-save-tests.json  Save UI, native writer, cold loads with/without ASI
|   |-- save-safety.json        Baselines, backup and save-safety summary
|   |-- save-integrity.json     Earlier compact save-integrity result
|   |-- backup-tests.json       Backup/launcher results
|   `-- package-tests.json      Verified latest release ZIP, hashes, installed ASI
`-- external/minhook/           Submodule: upstream MinHook v1.3.4 (c3fcafd)
```

Some JSON detail reports intentionally retain the version that was actually
tested. `validation.json` records which earlier checks were inherited. Do not
silently relabel older results as newly rerun tests.

## Local-only directories

| Directory | Contents and purpose | Transfer/publication treatment |
| --- | --- | --- |
| `research/` | Project-created Python live tests, injection/RPC clients, state captures, GCX extraction/disassembly; third-party research checkouts and private decrypted game/save data | Whole directory ignored. Selected harness source included in handoff ZIP; raw saves, dumps and extracted game scripts excluded. |
| `tools/zig-windows-x86_64-0.13.0/` | Local Zig compiler, Windows runtime and headers | Ignored; install Zig separately on another machine or retain locally. |
| `build/` | Policy/marker executables, test DLLs/PDBs, temporary private fixtures, snapshots, three sandbox roots | Ignored. Do not publish or treat stale addresses/PIDs as reusable. |
| `backups/` | Two original-save backup snapshots | Private; ignored and excluded from handoff ZIP. |
| `dist/` | Current release payload, licenses, SHA256.json and retained historical release ZIPs | Ignored; latest release ZIP included in handoff archive as a deliverable. |

Important `research/` groups:

- Top-level `.py`: owned orchestration/test/extraction scripts. See handoff for
  stateful setup requirements; these are not a turnkey end-to-end suite.
- `trainer/`: third-party trainer/save-reader source used for ProcessHandle,
  read-only save decoding and native-function research. MIT license retained.
- `bbtracker/`, `libgcl/`, `gcx/`, `patriot/`, `modloader/`: downloaded research
  dependencies/checkouts, not the production mod source.
- `scripts/`: extracted/decompiled game GCX/GCL files; local research only.
- `save_decrypted.bin`, buffer/dump `.bin` files: private test/game state;
  excluded from handoff ZIP and release.

Important `build/` groups:

- `save-sandbox/`: actual story/codec test game copy and separate copied saves.
- `ui-save-sandbox/`: actual Save/Load test game copy and private new save slots.
  ASI ends disabled in this copy for the unmodded compatibility test.
- `scenario-sandbox/`: earlier alternate fixture; not final validation evidence.
- `backup-test-*/`, `installer-fixture/`: synthetic integration fixtures.
- `EEGameProbe.dll`, `EEDev.asi`: development helpers; never ship/install in the
  normal game. Normal installed game was checked without these modules.
- `ui-*.json`, `*-context.json`, `*-fixture.bin`: local snapshots and runtime
  state. Native object addresses become invalid after process restart.

Sandbox `MGS4/common`, `MGS4/ww`, and `MGS4/Jpgs` are junctions to the installed
game. Do not traverse them for backup, cleanup, source export or public archives.

## Release layout

The current user release ZIP is `dist/MGS4-EarlyEquipment-0.4.1.zip`:

```text
README.md
Launch-MGS4.cmd
Backup-MGS4Saves.ps1
MGS4/winmm.dll
MGS4/scripts/MGS4EarlyEquipment.asi
licenses/MinHook.txt
licenses/Ultimate-ASI-Loader.txt
SHA256.json
```

It contains the unchanged tested ASI 0.4.0. PDBs, helper DLLs, personal saves,
complete game assets, compiler and raw research are excluded by the packaging
allowlist. `package.ps1` is for the user release; the separate handoff archive
has source/docs and is not an installable user-release replacement.

## Handoff archive

`dist/MGS4-EarlyEquipment-Agent-Handoff.zip` includes:

- Root handoff, source scripts, README and ignore rules.
- `src/`, `tests/`, `docs/`, and MinHook source/license.
- Project-created top-level `research/*.py`, plus the minimal MIT-licensed
  ProcessHandle and save-reader dependency source/license.
- `release/MGS4-EarlyEquipment-0.4.1.zip`.
- `HANDOFF-SHA256.json`, covering every other archive entry.

No private save fixtures or complete game files are included. Runtime research
scripts still require the local game, appropriate Python packages, and private
fixtures specified in AGENT_HANDOFF.md. The archive's entire file inventory
documents this original workspace; paths under generated/private directories
there do not imply those files are included in the archive.

## Git status and next-agent setup

The project root is a local Git repository on branch `main`, with no remote.
`external/minhook` is a submodule pinned to MinHook v1.3.4; run
`git submodule update --init` after cloning. Other nested Git directories belong
to research checkouts under ignored `research/`. Keep private/generated material
excluded. Owned live-test scripts currently live under ignored `research/`; move
them into a maintained harness directory if they should become part of a
reproducible repo.

Build uses Zig 0.13.0 and native Windows PowerShell. Live research additionally
uses Python, pefile and capstone. The user-facing release needs the supported
installed Steam game and its ASI loader; see README for exact installation and
the handoff for the supported executable hash and direct-launch arguments.
