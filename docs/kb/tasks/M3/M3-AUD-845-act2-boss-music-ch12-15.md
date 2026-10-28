---
id: M3-AUD-845
title: "Act II boss music, Ch12 and Ch15: avalanche_ram and wakefin"
role: audio
status: blocked
owner_session: "audio worktree agent"
reviewer: design
depends_on: [M3-AUD-839]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
Two of the six Act II boss cues in docs/kb/audio/act2_finals.md, each two synchronized stems mastered as the Cinder
Matron's (one shared gain and one limiter curve, equal lengths, LOOPSTART 0, the seam in a silent sixteenth):
- `avalanche_ram` (Ch12, the Keth Pass road): built on Keth Pass's world (E minor Aeolian, 6/8, the pipes in hocket,
  the wind and the pass-cords, the big drum) turned into a charge. Stem 1 the fight, stem 2 its rage (under 50% HP).
- `wakefin` (Ch15, the drifting barge in the dark): built on Unlamped's world (E-flat minor, its vigil, its sea and
  drone) turned into a fight: menace under the water, the blade's cut, no bright attacks. Stem 1 the circling,
  stem 2 the breaches (the second half).

Sources only: the audio lands with LFS (ADR 0039), with its music.json and PROVENANCE rows.

## Acceptance criteria
- [x] `assets_src/music/act2/avalanche_ram.py`: E minor, 6/8 at 92 dotted quarters a minute (twice the pass's 46),
      64 bars, an 83.48 s loop. Rows in render_all.py `ACT2_FINALS`.
      Measured (`render_all.py --act2 --only act2/avalanche_ram --determinism`): the full stack −16.05 LUFS, true
      peak −1.63 dBTP; stem 1 alone −17.94 LUFS (TP −2.28), stem 2 alone −20.05 LUFS (TP −3.34); the stack is +1.9
      LU over stem 1. Seam jump ×0.25 / ×0.89, flux ×0.75 / ×0.75 (p1 / p2). 1,073,196 + 1,052,301 bytes. Each
      file is identical on a second render.
- [x] `assets_src/music/act2/wakefin.py`: E-flat minor, 4/4 at 102 BPM (twice Unlamped's 51), 32 bars, a 75.29 s
      loop. Rows in render_all.py `ACT2_FINALS`.
      Measured: the full stack −16.09 LUFS, true peak −1.32 dBTP; stem 1 alone −17.95 LUFS (TP −1.94), stem 2
      alone −20.13 LUFS (TP −1.81); the stack is +1.9 LU over stem 1. Seam jump ×0.21 / ×0.92, flux ×0.52 / ×0.53.
      810,465 + 736,512 bytes. Each file is identical on a second render. Its limiter curve is the stricter of the
      stack's and each stem's, because the breaches' sub drop partly cancels stem 1's bass. With the stack-only
      curve, stem 2 alone peaked at −0.38 dBTP.
- [x] Every melody is original. The themes borrow only our own cells, loaded from the zones' sketches and never
      retyped: Keth Pass's `TUNE` and Unlamped's `VIGIL`. No samples, recordings or generated audio.
- [x] `python3 -m unittest tools/tests/test_act2_finals.py` passes. No file under `assets/audio/music/act2/` is
      committed.

## Intended music.json rows (land with the audio, in the LFS commit)
```json
"avalanche_ram": {
  "stems": ["res://assets/audio/music/act2/avalanche_ram_p1.ogg", "res://assets/audio/music/act2/avalanche_ram_p2.ogg"],
  "start_stems": [0],
  "_note": "Ch12 boss (M3-AUD-845): stem 1 the fight; stem 2 its rage, brought in under 50% HP"
},
"wakefin": {
  "stems": ["res://assets/audio/music/act2/wakefin_p1.ogg", "res://assets/audio/music/act2/wakefin_p2.ogg"],
  "start_stems": [0],
  "_note": "Ch15 boss (M3-AUD-845): stem 1 the circling; stem 2 the breaches, brought in for the second half"
}
```
and under `battle.phases`:
```json
"ram_rage": {"stems_on": [1], "sec": 2.0, "_note": "M3-AUD-845: the Avalanche Ram under 50% HP, its rage (the bellow, the avalanche) over 2 s"},
"wakefin_breaching": {"stems_on": [1], "sec": 4.0, "_note": "M3-AUD-845: the Wakefin's second half, the breaches over 4 s"}
```
The `battle.encounters` rows (`ch12_avalanche_ram -> avalanche_ram`, `ch15_wakefin -> wakefin`) wait until the
encounters exist.

## Notes
- The stems are rendered into the scratchpad, not the repo. Re-render with
  `python3 tools/audio/render_all.py --act2 --only act2/<cue> --determinism`, one cue at a time: each takes about
  3–4 minutes a render on the shared machine.
- act2_finals.md's Measured column waits for the Lead. Agents don't edit that file.

## Review log
