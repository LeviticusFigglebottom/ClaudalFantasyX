# 0172 — Build-time audio render from a committed checksum manifest (the fallback to Git LFS)

- **Status:** proposed (a prototype only; nothing has switched over. The storage decision is the human's.)
- **Date:** 2026-10-27
- **Roles affected:** audio, tech, Lead, the PC runner (CI), everyone who runs the game from a checkout
- **Author role:** audio

## Context
ADR 0171 raised the audio budget to 72 MiB so that Act I could ship committed. Shipped audio is now 70.1 MiB. The
Act II finals and Act III (docs/kb/audio/act3_plan.md estimates 60–85 MB for Act III alone) cannot be committed
under that budget. They also cannot be committed under CLAUDE.md §8's 5 MB file rule or ADR 0005's deferral of LFS.
The Lead sent the storage question to the human: Git LFS, or a build-time render. Audio was asked to prototype the
render path, measure it on 4 CPUs and write the trade-offs.

The render path is possible at all because every shipped audio file is reproducible from source (CLAUDE.md §2):
`tools/audio/render_all.py` renders each of its jobs from `assets_src/music` and `assets_src/sfx` with
`tools/audio/synth/`, and `--determinism` already proves that two renders on one machine give identical bytes.

## The prototype
`tools/audio/build_render.py` (with tools/tests/test_build_render.py):
- **`--write-manifest M`** hashes every file render_all's JOBS name, as committed, into a manifest. Each job gets
  an **input key**: the sha256 of its source and of every repo-local module it imports, followed through
  `assets_src/sfx`, `assets_src/music` and `tools/audio` (synth/ included), plus the numpy version, the ffmpeg
  version line and the Python minor version. A change to `synth/dsp.py` therefore re-renders the jobs that import it,
  and nothing else.
- **`--ensure`** makes every file exist under `--out-root` with the manifest's sha256. A file that already matches
  is kept. A missing or different file is taken from the cache (`~/.cache/hymn-undertow/audio_render/<key>/`), or
  else rendered: in parallel, longest jobs first, each job in a fresh process. The result is then checked against
  the manifest, and any difference is reported.
- **`--plan`** prints what `--ensure` would do, and why.

The cache works like an import cache: it is keyed by inputs, never committed, and rebuilt on a miss. Godot's own
import cache (`.godot/imported`) is still built by `godot --import` from the rendered `.ogg` files, so the render runs
before the import.

## Measurements (this cloud container: 4 CPUs, numpy 2.5.3, ffmpeg 6.1.1, Python 3.13)
| What | Time |
|---|---|
| **Cold build**: all 94 jobs, 896 files, 73 MB, into an empty tree with an empty cache, 4 workers | **1605 s wall (26.8 min)**; 6310 s of job time, so the pool ran at 3.9× |
| The longest single jobs | haluna_dawn 219 s, undertow_rising 214 s, the_ebbing 187 s, stillguard_inquisitor 176 s, undertows_reach 172 s |
| One render_all job, serially (render plus render_all's loudness and loop checks) | oruvel 106.5 s, the_ebbing 205.1 s, cinder_matron 116.4 s, seawall_hold 136.3 s, creature_sfx 102.9 s, field_ambience 142.5 s, act1_cutscene_sfx 59.7 s, hero_foley 13.0 s |
| The render alone (oruvel, without render_all's metering) | 55.6 s: the metering is about half of render_all's time, and a build does not need it |
| **Warm check**: a tree that already matches | **1.9 s** |
| **Cache fill**: an empty tree, every key cached | seconds per job (a file copy); the run took 167 s only because one job's key had changed and it rendered |
| A change to one cue's source | that job only: 13–219 s |
| A change to a shared synth module | every job that imports it; for `synth/dsp.py` that is nearly all of them, about the cold build |

The machine was also running Godot tests and other renders for part of the cold build, so 26.8 min is an upper
bound for this container. With 4 workers, the wall time can't drop below the longest job (about 3.6 min), and more
workers bring it closer to that floor.

**Determinism:** 895 of 896 files rendered byte-identical to the committed ones. The one difference was intended:
`tamsule_bell.ogg`'s source was changed during the run (M3-AUD-835). **Across machines it is not yet measured.** The
known risks:
- numpy's SIMD-dispatched transcendentals (sin, exp) can differ by an ulp between CPUs (AVX-512 against AVX2);
- another numpy, ffmpeg or libvorbis version changes the bytes;
- the FDN reverbs accumulate float error.

The input key includes the toolchain, so a different machine misses the cache instead of silently reusing it. The
manifest check would still report the drift.

## Options
1. **Git LFS** for `assets/audio/**` (or only the new, large files). The bytes stay exactly what was heard and
   reviewed, and nothing changes for anyone running the game. The costs: an LFS quota and bandwidth (every
   revision of every cue is kept forever, and audio is iterated often), and LFS set up on every clone, CI runner
   and agent container.
2. **A build-time render** (this prototype): the `.ogg` files leave git and a committed manifest of checksums
   replaces them. It needs no storage growth and no quota. The costs:
   - every fresh checkout, CI run and export renders first (27 min cold on 4 CPUs, seconds when warm);
   - the toolchain must be pinned (numpy, ffmpeg and libvorbis versions in tools/requirements.txt and the
     containers), or the manifest check must allow drift;
   - tests that load audio (`ResourceLoader.exists` on a row's files) need the render first;
   - the `.import` files stay committed (scenes and resources name their UIDs).
3. **A hybrid**: Act I's finals stay committed (ADR 0171, 70.1 MiB, already reviewed). Act II and Act III render at
   build time behind this manifest, with the cache kept on the PC runner and restored into cloud containers.

## Decision
None yet. Audio recommends **option 3** if the human does not want LFS, and **option 1** if they do (it is
simpler). Before option 2 or 3 can be accepted, one check is needed: **render on the PC runner against this
container's manifest** and count the files that differ. If any do, pin the toolchain, or relax the check to
measured loudness and peak against targets.py (the bytes would then differ between machines, though every file
would still meet its target). Nothing is switched over by this ADR.

## Consequences
- **If accepted:**
  - `assets/audio/**/*.ogg` for the rendered acts move to `.gitignore`;
  - `tools/ci_local.sh` and the PC runner run `build_render.py --ensure` before `godot --import`;
  - validate_data's PROVENANCE check reads the manifest instead of the files;
  - test_audio_loudness measures the rendered tree;
  - a reviewer listening to a branch must render it first, so the listening notes name the manifest's key for each
    cue they describe.
- **What it costs to watch:** the cache's size (73 MB for Act I, and every changed key adds a copy, so prune by
  age) and the toolchain pin.
- **Whatever the decision:** the prototype stays a tool. `--plan` against a manifest written from the committed tree
  already answers "is everything rendered from the sources as committed?", which `--determinism` only answers per
  job.
