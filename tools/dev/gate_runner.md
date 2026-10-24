# Running a Lead gate on the PC

The PC (RX 9070 XT, 24 threads, 32 GB, Windows 10, WSL2) carries the Lead's gate overhead. It runs the same
gates as `tools/ci_local.sh` in the Lead's container, on the same pinned Linux binaries, and posts the result in
`docs/kb/handoffs/live/pc-gpu.md`.

## Where it runs
- **WSL2 distro `hymn`** (Ubuntu 24.04, created for this; the `caper` distro is another project's, never use it).
  Everything runs as root, inside WSL's own filesystem (`/root/hymn`), never on `/mnt/c` (slow).
- Pinned tools in `/root/.cache/hymn/`, fetched by the repo's own scripts (once; again only when a pin changes):
  `python3 tools/dev/fetch_godot.py`, `fetch_render_deps.py`, `fetch_blender.py`.
- **No venv.** Blender honours `VIRTUAL_ENV` and then can't import its own numpy, so install into the distro's Python:
  `pip3 install --break-system-packages -r tools/requirements.txt pillow`.
- `C:\Users\Aaron\.wslconfig` caps WSL at 18 of 24 threads and **10 GB**, with `autoMemoryReclaim=dropCache`. At 14 GB
  plus the desktop, Claude Code reaped a gate for low system memory (2026-10-24). Use **2 screenshot shards**.
- WSL's `/tmp` is wiped when the distro idles: results go under `/root`.
- **Never keep `.godot/` between gates.** Godot doesn't reimport a model when only its post-import script changed,
  and a kept cache failed 3 `test_post_import` tests with stale LOD ranges and moved two arena shots. `sync.sh`
  cleans it; a fresh import costs about 30 s.
- **The clone has no GitHub credentials.** `tools/dev/pc_gate/sync.sh` copies the Windows checkout's `origin/*`
  refs (`C:\Users\Aaron\hymn_gpu`), so run `git fetch origin` on Windows first.

## Parity with the Lead's container (proved 2026-10-24)
- **d6a0886d (big7 merged): 196/196 shots pass**, as in the container. On lead/gate-big7 the runner failed the same
  two shots the container did (`save_shrine_field`, `settings_accessibility`), and the Lead re-approved both after viewing.
- Integration head 81651b7e (75 shots then):
- llvmpipe reports **"LLVM 22.1.8, 256 bits"** on this CPU, as in the container, so there's no width pin.
- All 75 shots pass. The three drifts the container has recorded match to five decimals: `water_horizon` 0.00507,
  `water_night` 0.00306, `haluna_h01_village_from_sea` 0.00189. 47 shots are 0.00000.
- llvmpipe's output doesn't depend on its thread count: three shots were bit-identical at `LP_NUM_THREADS` 3, 4
  and the default (24). So shards can use fewer threads each.
- Watch: `battle_vowbound_call` is at **0.00798** against its 0.00800 limit. That's this baseline's own drift, the
  same at every thread count, and the next unrelated change can tip it. Re-approve it before then.

## Measured (2026-10-24)
| Run | Wall | Result |
|---|---|---|
| Full gate, lead/gate-big8 @ aa55b77e (238 shots, 44 Blender jobs), 2 shards, 10 GB | 27.4 min (A 18.5 with Blender 16.7; B 27.3) | Godot 2324/0; 29 expected-kind shot drifts; 9 Blender DIFF (M2-CHR-11) |
| Full gate, d6a0886d (Blender skipped), lanes A and B at once | 16.3 min (A 10.5, B 16.2) | Godot 1940 run, 2 failed (the WSL clock flake, below); 196/196 shots |
| Full gate, lead/gate-big7 @ ab048d51 (Blender for 39 changed jobs) | 18.2 min (Blender 11.9) | 9 jobs DIFF (M2-CHR-11); 2 shots changed, which the Lead re-approved after viewing |
| `verify_blender_builds.py --all`, d6a0886d | 12.4 min | 41 jobs: 31 identical, 10 DIFF (M2-CHR-11) |
| Windows-native ci_local.sh (no Blender, no shots), integration head + NIT-04/05 | 10.4 min | 1480 tests (pre-big7 head), all gates pass |

The Lead's container takes 2-3 h per full gate.

## Known host differences (open)
- **Blender on an AVX2 host:** base_body, Rhen, Toma and seven villagers don't rebuild byte-identical. This
  i9-12900K has no AVX-512; the container does. Asha is identical because she uses M1-CHR-14's host snaps.
  **M2-CHR-11** opts the rest in. Until then, a Blender DIFF in those ten jobs on the PC is expected.
- **Two real-stall tests flake under load** (`test_frame_clock` and `test_boot_card`, `test_a_real_stall_*`). Under
  WSL2 the clock Godot reads (`CLOCK_MONOTONIC_RAW`) runs about 1% slow against the one sleeps use. They pass on an
  idle machine; **M2-ARC-12** adds a margin. Until then, rerun them alone (`-- --filter=frame_clock`,
  `--filter=boot_card`) before calling a FAIL.
- `tools/requirements.txt` doesn't list Pillow, which seven tools tests import. The runner installs it alongside.

## Running a gate
On Windows (Git Bash), then WSL:
```bash
cd /c/Users/Aaron/hymn_gpu && git fetch origin
# Run the scripts from a copy OUTSIDE the clone: gate.sh checks the clone out to <ref>.
wsl.exe -d hymn -u root -- bash -c 'cp /mnt/c/Users/Aaron/hymn_gpu/tools/dev/pc_gate/*.sh /root/ && \
  bash /root/gate.sh origin/lead/gate-<name> origin/claude/undertow-lead-handoff-423ixt 3'
```
`gate.sh <ref> <blender-base> [shards]` runs two lanes at once and prints a summary:
- **Lane A:** `tools/ci_local.sh` on the pinned Linux Godot: validators, tools and audio unittests, the task board,
  gdlint/gdformat, the manifest check, **Blender for the jobs changed since `<blender-base>`**
  (`HYMN_BLENDER_REQUIRED=1`), the Godot import, the full Godot suite, the coverage gate and the boot smoke test.
  Its own screenshot step is skipped (`HYMN_GODOT_RENDER=/nonexistent`) because lane B does it.
- **Lane B:** the whole screenshot manifest in `shards` parallel `capture.sh` runs (each in its own log directory,
  `LP_NUM_THREADS=3`), then one `compare.py`.
- Logs: `/root/gate_<ref>/` (`laneA.log`, `ci/`, `shard_*/`, `compare.txt`).

For the Blender reproducibility check across every job, run `HYMN_BLENDER=... python3 tools/dev/verify_blender_builds.py --all`
in the clone. Every job must be "identical".

## Load rules
- Keep the whole machine at or under 75% CPU and memory. Lanes A and B together with 2 shards stay under the cap (about 50% CPU).
  WSL's VM shares memory with the desktop, so check memory before adding shards.
- **Never during a GPU benchmark.** Gates and benchmarks alternate, so a benchmark always has a quiet machine.
- Kill only processes you started.

## Posting the result
Add a line to `docs/kb/handoffs/live/pc-gpu.md` on the PC's newest branch, and message the Lead:

    GATE <branch>@<sha>: PASS|FAIL, wall <min> min. Lane A: Godot <run>/<failed>, coverage ok, Blender <n>/<n> identical
    (changed since <base>), lint/data/unittests ok. Lane B: <n> shots compared, <failed> failed (worst: <id> <rmse>).

For a gate with expected drifts, push every failing shot's out and diff PNGs to a `gpu/gate-<name>-shots` branch
under `docs/kb/qa/gate-runs/<name>/`, with a README that groups them (see big8's).

On a FAIL, name the step and the first failing test or shot, and attach `compare.txt` or the failing log lines.

## Windows-native lane (no WSL)
`tools/ci_local.sh` also runs in Git Bash with the Windows Godot 4.6.3: Godot tests, coverage, unittests and lint.
Put shims for `python3`, `gdlint` and `gdformat` (`python -m gdtoolkit.linter` / `.formatter`) on PATH, set `GODOT`
to the Windows binary and `HYMN_SKIP_BLENDER=1`. Its screenshot step SKIPs: lavapipe and the pinned Blender are
Linux packages, so they belong in WSL. It's a cross-check, not the gate of record. It needs M2-NIT-04 and M2-NIT-05
for the tools unittests to pass on Windows.
