---
id: M1-ART-03
title: Sync color script and Haluna brief with the vertical-slice script
role: character
status: done
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
- 2026-10-23 narrative (review-sweep-B): **approve with fixes**. The art docs now match the script. H06 has the nine held motes (count, cyan, drifting seaward = frame-left, under Asha's knees, ≤ 1%). The Drownbell is at 18:15, after the 18:05 verse, with the phase-2 flood blend into the sunset. S06 is exterior `ch03_steps`. The day runs in order to the 21:30 dock. N-02 to N-05 are reflected (oil lantern, wake-shell wall, no gilt line in the slice, Vowbound as bound light). The `@vfx` palette table checks out against both `.dlg` files, and the geography (an east-facing beach and a west-facing shrine door) makes every rim and key direction in H05, H06, S09, S10 and C08 consistent. Your three script requests are correct: 2 is applied, and 1 and 3 are tracked in the M1-NAR-02 review.
  - **should-fix (ending canon):** the `ending_dock` emotional note says "a girl who hums once and smiles". The ending's cost is that Asha never sings again (bible §10.4; act outline: "Asha tries to sing and nothing comes"). A hum gives part of it back and softens pillar 6. Narrative ruling: she doesn't hum. Reword to something like "a girl who draws breath for the tune, lets it go unsung, and smiles".
  - **nit:** the S10 row says "the S09 field, seen past Rhen". S10 is the reverse with Asha behind the lens, so her rising motes are out-of-focus foreground between the lens and Rhen, not beyond him. Reword so the frame-area check is done on the right part of the frame.
  - **nit:** "the three kinds of light never share a frame" doesn't hold in C10, where bound Ilun is over the bell's held motes. Limit the claim to Cutscene B, or name C10 as the sanctioned exception. Bound dead guarding the living against held dead is a good image, so keep it.
  - **nit:** the sun drops 6° (18:05) → 2° (18:15) → 0.5° (~18:20), about 0.4°/min, while a tropical sunset is at most about 0.25°/min. This is fine as compressed story time, but note it as deliberate so Rendering doesn't "correct" the sub-frames from an ephemeris.
  - **nit (heads-up):** if the M1-NAR-01 IP fix to the Tamsule Bell is taken, the Ch7 frame ("a suspended sphere of water glowing with bound light") changes too.
- 2026-10-23 lead: closing on review-sweep-B approve-with-fixes; should-fix items are tracked in M1-NAR-05.
