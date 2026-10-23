---
id: M1-NAR-05
title: Story IP near-misses, continuity, and slice staging fixes (review-sweep-B)
role: narrative
status: review
owner_session: narrative-stream-3
reviewer: cinematics
depends_on: [M1-NAR-01, M1-NAR-02]
milestone: M1
request-from: "cinematics"
---
## Goal
Fix the guardrail (SPEC §2) and staging findings from review-sweep-B on NAR-01/NAR-02/ART-03.

## Acceptance criteria
- [x] IP: reorder the Vowbound elements and temples so the sequence no longer mirrors the inspiring game's order (decisions_log N-09)
- [x] IP: rename 'Unbroken Calm' away from 'Calm' compounds; add the old name to tools/banned_terms.txt (N-10; now "the Long Stillness")
- [x] Continuity: the Dace/Imra lullaby origin (Velamir family lullaby known before she was named) (N-11, N-08 corrected)
- [x] Act III: Ch21+Ending beat sheet with durations, one goodbye per scene (`docs/kb/story/beats/act3_ending.md`)
- [x] Slice staging: cuts instead of blends between unrelated setups; Asha 014/015 on H05; S10 recognition cut at 043 held ≥6 s; layered surprised→grief face (N-13)
- [x] Pillar 1: rework Toma 021 and 'Small world.' (054)
- [x] Art doc ending_dock: no hum (rewrite the wording in docs/kb/art) (N-14)

## Notes
- **New Vowbound order** (temples and chapters unchanged): Ilun Water (Ch3), Kahre **Lightning** (Ch5, Ashcrown), Virel **Fire** (Ch8, Coilspire), Nhoa Glimmer (Ch11), Hesk **Holy** (Ch12, Cloudloom), Ethren **Ice** (Ch13, Sanctum of the Level), Kesh all six (Ch16). The release order in the dive is unchanged.
- **Renamed terms (for the Lead's glossary.md):** Ember Terrace → **Ashcrown** (Lightning temple; zone `ch05/ember_terrace` → `ch05/ashcrown`); "Unbroken Calm" → **the Long Stillness**; Coilspire is now the Fire temple, Cloudloom the Holy temple, and the Sanctum of the Level the Ice temple. The Vowbound rows' elements change as above. New swells: *Last Strike* (Kahre), *Flare Line* (Virel), *Still Water* (Ethren). New: **the Velamir lullaby**, **heirloom weapons** (replaces the act outline's series term), **the Weir** (only if the human changes the Reefball form). Bible §3's heading is now "the Cycle of Calms".
- **Glossary blocks the gate:** `tools/banned_terms.txt` now bans "Unbroken Calm", and `docs/kb/glossary.md:89` still uses it. That is the only `validate_data` error on this branch, and it is outside Narrative's paths. The Lead must replace that row in the same merge. With that one row replaced (tried locally, not committed), `tools/ci_local.sh` passes end to end.
- **Reefball arena:** the form is unchanged (SPEC §6.10, the human's call). N-12 describes how to make the sphere ours (a bell hung mouth-down, a held drop that weeps, bound light, a rescue-drill rite where you score by bringing the float *up*) and gives one alternative form (the Weir).
- **Not touched:** the `steps` node's `grade:` header (M1-ART-04).
- **For Art (not edited, outside this task's art scope):** haluna.md S10 still says "the 3 s recognition blend", which should become "the ≥ 6 s recognition hold from line 043, layered face". The color script Ch8 and Ch12 notes are still physically right (Coilspire copper, Cloudloom ice), but Art may want beacon fire in Coilspire.
- **For Combat:** the element and status assignments in N-09; Ethren's wards need coined names (never the series' spell names).
- Also fixed (review nits, Narrative's paths): the Ch8 staging is a freeze, not a run toward the figure; "Ultimate Weapon" became heirloom weapon quests; Asha's sheet says "wards" instead of series spell names; a silent `@wait 0.6` before ch02 006; "Nope" became "No".

## Review log
