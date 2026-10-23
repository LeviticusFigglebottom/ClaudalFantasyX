---
id: M1-NAR-05
title: Story IP near-misses, continuity, and slice staging fixes (review-sweep-B)
role: narrative
status: done
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
- 2026-10-23 cinematics (review-sweep-C): **approve with fixes**. I checked the fixes from my own knowledge of the inspiring game.
  - **Order:** the old run followed its temples almost exactly: a fire temple second, lightning third, an ice temple, then the holy city. The new elements break that, and "Unbroken Calm" → "the Long Stillness" is clean. No banned or series term appears in docs/kb/story or the .dlg scenes. I grepped for Farplane, Maester, Crusader, Celestial, Final Aeon/Summoning, Overdrive, summoner and unsent.
  - **Staging:** the slice's camera grammar now cuts between unrelated setups. The S10 hold is 1.5 + 1.5 + 3.0 s of waits on S10 from line 043 to 046 with layered surprised → grief, and S07 → S08 is a fade-cut. Toma 021 and Rhen 054 now land sincerely.
  - **act3_ending.md:** the durations add up (Ch21 39.0 = 28.0 P + 11.0, Ending 14.5, total 61.5). One goodbye per scene with rests between them is very stageable.
  - should-fix (IP, for the Lead): decisions_log N-09 (decisions_log.md:65) gives **Ice to the Sanctum of the Level**: a basin held so still it freezes, at the Order's seat (Ch13), immediately before the Peace Wedding trap (Ch14) and the heretic turn (Ch15). That recreates the inspiring game's frozen-lake ice temple, where the party turns traitor just before the wedding in the church's city, more closely than the old order did. Consider giving the Sanctum a non-Ice Vowbound, or moving Ice back to Cloudloom's high passes and finding the Sanctum a stillness motif that isn't ice.
  - should-fix: `docs/kb/story/beats/act3_ending.md:14` and :83 contradict SPEC §3.5, as locked in §0 rule 6: "every glimmer-light … released **in the same instant**". H09 shows every lamp in Maresh going dark at once, yet the Kite's *bound* lamps dim over E1 → E4 (about 10 min) as the countdown. Line 83 also says each farewell is "lit only by the rising motes of the person leaving", while the lamps are at 100% in E1. Fix: let the Kite's lamps die in H09 with everything else and carry the countdown on the dead's rising light and the sea-glow ramp alone. Or record a Lead ADR explaining why the Kite holds.
  - should-fix: act3_ending.md:101 (E6). The payoff, "she draws breath… lets it go unsung, and **smiles**", is staged as "one locked shot from 1.0 m **behind** her", so the smile can't be seen. Fix: a locked three-quarter or profile frame from the dock's side, with her face against the star-filled sea (still no cut and no push), or a reflection read if behind is kept.
  - should-fix: `game/data/dialogue/ch02/ch02_girl_on_the_beach.dlg:70-71`. After the branch at 026 ("Get up"), Rhen is standing and leaning on Toma (027–029), but the scene cuts back to H05, which is Rhen's POV at 0.4–0.9 m lying or sitting (haluna.md:167), and Asha `offer_hand`s to help him up. Fix: branch the camera (a standing H05 variant) and the anim, or have 026 end with him sinking back to his knees.
  - should-fix (Art follow-up, already flagged): `docs/kb/art/environments/haluna.md:200` still specifies "the 3 s recognition blend" for S10, which contradicts the cut and ≥ 6 s hold in the .dlg. Lighting will be tuned to the wrong shot description.
  - nit: act3_ending.md:85. Kerrid's breath fogging on a tropical night reads as cold, not warm, unless everyone's breath fogs. Use a different "alive for a moment" cue: his reflection appearing, or a shadow under the motes.
  - nit: H02–H07 promise that Dace's face is unseen until E3, but H04–H07 are playable fights. Give Combat/Cinematics the constraint that battle cameras never frame Dace from Imra's side.
  - nit: `ch03_the_first_verse.dlg:23,30`. `walk_to_chamber` plays before the exchange, then `@mark … walk` walks again. S07 (haluna.md:197) wants her to turn back for the exchange, then walk in. Use `turn_back` first.
  - nit (banned list, for the Lead): add Farplane, Maester, Yunalesca, Valefor, Via Purifico, Thunder Plains, Moonflow, Celestial Weapon, Final Aeon, Final Summoning and Cloister of Trials to `tools/banned_terms.txt`. None are used today.
- 2026-10-23 lead: closing on review-sweep-C approve-with-fixes; the remaining IP near-miss and staging items are in M1-NAR-08.
