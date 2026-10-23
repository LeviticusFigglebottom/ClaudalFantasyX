---
id: M1-NAR-01
title: Story bible expansion, characters, voice guide, act outline, Vowbound
role: narrative
status: done
owner_session: "narrative-stream-1"
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §3: expand the seed before Chapter 2 production.

## Acceptance criteria
- [ ] bible.md, characters/*.md, voice_guide.md, beats/act_outline.md, vowbound.md
- [ ] Vertical-slice candidate chapter marked
- [x] glossary additions merged by the Lead

## Notes
Delivered 2026-10-22 (about 17.6k words). Reviewer: Cinematics, plus Lead for the pillar and guardrail check. Key outputs: the vertical slice is Ch2–3 at Haluna (Saltgrass Causeway, Shell Shrine, Vowbound Ilun, boss Drownbell). There are seven Vowbound, each leaving Asha's roster for good in Act III. 'unrisen' replaces the spec's working word.

## Review log
- 2026-10-22 lead: guardrail scan clean after rewording three meta-notes; banned list extended. Story review by Cinematics pending.
- 2026-10-23 cinematics (review-sweep-B): **approve with fixes**. The bible is stageable and sincere, and the ending keeps every SPEC §3.5 element (Kerrid lifts, Imra's last scene, Dace's goodbye said back, Asha alive but without song, the dark-sea dock, the post-credits oil lamp). The metaphysics hand Cinematics a visual grammar the player can learn without being told (up = released, down/seaward = held, still = bound), and the Ebbing is a set piece that rereads well in hindsight. `validate_data` and the banned-list grep are clean. The fixes are one continuity hole under the slice's central reveal and four IP near-misses that the list can't catch.
  - **should-fix (continuity, slice-critical):** `characters/rhen_sallow.md` and decisions_log N-08 both say Dace "learned [the verse] from Imra on the pilgrimage". He never came home from that pilgrimage, and he left when Rhen was eight, yet he "hummed it every night" to Rhen beforehand. Cutscene B's recognition depends on this. Fix: make the first verse a Velamir family lullaby that Imra sang before she was named (the line has given four Cantors), and have Dace know Imra earlier, for example through Saltwright trade at Haluna. Asha "forgot it until Ilun gave it back" still works. Update N-08, rhen_sallow.md and bible §6 together.
  - **should-fix (IP, structural near-miss):** the Vowbound element order matches the inspiring game's temple and summon sequence almost step for step: a fire temple second, lightning third, an ice temple, then the holy city's own summon, then the final one at the edge of the world. Mechanics are free, but this specific sequence is expression. Break the pattern: for example, put Coilspire (lightning) before Ember Terrace, or move Hesk (ice) to Act I, and/or give Ethren a non-Holy identity (Stillness or Time would fit the Order). Update vowbound.md, act_outline.md and color_script.md together.
  - **should-fix (IP):** the Tamsule Bell ("a sphere of seawater suspended in the air", with Reefball played inside it) is the inspiring game's signature sport-arena image, not just "an underwater sport". Change the arena form, for example a flooded Lit Age amphitheatre bowl, or a salt-glass ring-tank played at and below the surface. The Ch7 color script note ("suspended sphere of water") must change with it.
  - **should-fix (IP):** "Unbroken Calm" (sefir_aurane.md, bible §11) is a one-word synonym swap of a compound already on `tools/banned_terms.txt`, used for the same concept (the antagonist's permanent Calm). Bible §11 itself says never to build Calm compounds that echo existing IP. Rename it away from "Calm", for example "the Held Sea" or "the Long Stillness". "Last Calm" is acceptable but borderline. Add the new name's near-misses to the banned list if any turn up.
  - **should-fix (stageability, before Act III production):** Ch21 plus the Ending stacks Kesh's release, a three-phase Sefir fight, the Letting countdown, three separate goodbyes (Kerrid, Imra, Dace), the Kite landing and Asha's failed song. Write an ending beat sheet with a target duration per beat, mark which beats are playable and which are cutscene, and use one goodbye per scene with a rest beat between, so the goodbyes don't blur into one montage.
  - **nit (IP):** "Ultimate Weapon quests" (act_outline Ch18) is a recurring series term. Coin our own, for example "heirloom weapons".
  - **nit (IP, for Combat):** Ethren's "mass Protect/Shell" uses series spell names, and "Shell" is distinctive. Coin status names (for example Ward, Veil, Mend) when the status table is written.
  - **nit (staging):** Ch8 (a seawall defence with the Order using outlawed machines, then the hero running toward a figure in the storm and being pulled back) closely tracks the inspiring game's mid-Act-I set piece. It is spec-mandated, so keep it, but stage Rhen's beat differently, for example he freezes and the figure turns away, rather than sprinting toward it.
  - **nit (lore arithmetic):** 61 Calms in 1,012 years doesn't fit 30–40-year Calms until about 600 AL and 11–15 years after (that's 57 at most). Cantor #36 at about 712 AL also implies an average of about 20 years before then. Shorten the early Calms to about 18–25 years.
  - **nit:** the Watchers (rows of carved faces on a laterite wall) sit close to a real sacred site. The closed eyes and humming mouths transform it enough, but tell Art never to build them as multi-faced towers.
- 2026-10-23 lead: closing on review-sweep-B approve-with-fixes; should-fix items are tracked in M1-NAR-05.
