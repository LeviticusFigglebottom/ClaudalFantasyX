---
id: M1-ART-03
title: Sync color script and Haluna brief with the vertical-slice script
role: character
status: review
owner_session: art-stream-2
reviewer: narrative
depends_on: [M1-NAR-02]
milestone: M1
request-from: "narrative"
---
## Goal
Narrative's beat sheet changed two art facts.

## Acceptance criteria
- [x] color_script.md Ch2 dawn frame allows the nine held motes Cutscene A shows around Rhen
- [x] haluna.md moves the Drownbell boss from 17:30 to about 18:15 (after the 18:05 song)
- [x] Vowbound lit as bound light (story decisions_log) reflected in the color rules

## Notes
See docs/kb/story/decisions_log.md and beats/vertical_slice.md.

Done (art-stream-2), docs only:
- `color_script.md`: `ch02` glimmer is now `glimmer_held`, energy 0.6, exactly 9 motes in H06 only, ≤ 1% of the frame, with no fill light and seaward drift at 0.05–0.10 m/s. `ch03` has a per-shot glimmer table (S08 bound 1.2, S09 lift 2.5, C08 held 1.5). Sea-glow for `ch02`/`ch03` went 0.03 → 0.04, the palette floor, since 0.03 could not render. Rule 2 now covers the Vowbound (N-05) and the oil lantern (N-02). A review log was added.
- `environments/haluna.md`: `ch03_boss` is re-timed to 18:15 (sun 2°/270°, `#FF9F46` at 2.0, afterglow fill, sea-glow 0.04), with a phase-2 flood blend to the sun on the horizon. The old 17:30 light became `ch03_steps` (S06). Lighting notes were added. H06 was reframed as a side-on two-shot so Asha's facial beat reads, and given the motes. H01, H05, S06–S10, and C08–C10 were synced to the script. The wake-shell wall is confirmed (N-03).
- `README.md`: bound light was added to convention 2. The Narrative open questions are marked resolved (N-01 to N-04, with links). A palette check of the slice's `@vfx` cues was added.
- `palette.json` 0.1.1: the usage text of `glimmer_held` and `glimmer_bound` was corrected. Hex and linear values are unchanged.
- `characters/asha.md` and `rhen.md`: resolved notes (N-01, N-02, N-04).

**Script changes requested from Narrative** (not made here, since `.dlg` is outside Art's paths):
1. `ch03_the_first_verse.dlg`, node `steps`: `grade: ch03_shrine_int` → `grade: ch03_steps`. S06 is exterior (outer steps, sea behind), and the interior grade is oculus-only.
2. `ch03_the_first_verse.dlg`, node `threshold`: `@camera C08 blend=0.0` → `@camera C08 blend=0.0 grade=ch03_boss`. The node's grade is `ch03`, but C08 lives in the 18:15 boss light.
3. Optional (Cinematics): `ch02_girl_on_the_beach.dlg` `@camera H01 blend=3.0` blends from 0.4 m on the beach to 180 m offshore in 3 s, which will read as a whoosh. Consider `blend=0.0` (a cut) or a slow crane.

## Review log
