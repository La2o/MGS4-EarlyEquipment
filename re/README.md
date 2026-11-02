# Reverse-engineering scripts

Local research tools for the Steam 1.4.1 executable. Their inputs and outputs
are game-derived or private (memory dumps, extracted stage scripts, a decrypted
save) and stay in the ignored `research/` folder. Never commit those files.

Requirements: Python 3.12, `pip install -r requirements-dev.txt`, and
`git submodule update --init` (`external/mgs4trainer`, `external/bbtracker`).

| Script | Purpose | Reads / writes |
| --- | --- | --- |
| `probe.py` | Dump the link/var buffers and `.text` from a running game | Writes `research/buffer_*.bin`, `research/runtime_text.bin` |
| `strings_probe.py` | Dump `.rdata`; search strings and pointer references | Writes `research/rdata.bin` |
| `disasm.py func\|dis\|refs <rva> [size]` | Capstone over the `.text` dump; `func` uses the installed exe's unwind table | Reads `research/runtime_text.bin` |
| `extract_gcx.py` | Extract stage `.gcx` scripts from the installed game's `ww/stage/*.pak` | Writes `research/scripts/*.gcx` |
| `generate_restore.py` | Regenerate `src/restore_script.h` from s01a10l procedures 295/296 | Reads `research/scripts/s01a10l.gcx` |
| `carryover.py` | Print carried weapons and items from the save fixture | Reads `research/save_decrypted.bin` |

The current `research/runtime_text.bin` was captured with hooks installed, so
hooked function entries (for example `0x740280`) begin with a MinHook `jmp`.
On 2026-11-02, `generate_restore.py` reproduced `src/restore_script.h`
byte-for-byte.
