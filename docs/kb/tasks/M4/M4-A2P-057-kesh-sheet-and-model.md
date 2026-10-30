---
id: M4-A2P-057
title: "Kesh, the First Voice: the design sheet, then the model"
role: character
status: review
owner_session: "creatures-b"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
The only Vowbound with nothing built. Split M3-CRE-649: write `docs/kb/art/creatures/vowbound/kesh.md` (a colossal woman of standing seawater, a robe of open choir-mouths, the lamp-key keepsake), then build her on the creature kit with the clip contract and an element-shift clip set.

## Acceptance criteria
- [x] Sheet written (docs/kb/art/creatures/vowbound/kesh.md); GLB 18,824 triangles (0.8k over the ~18k guide for the 88 mouths, justified in the sheet); 26 clips; review shot and battle-camera clip sheet viewed. Awaiting the rendering review.
- [x] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch16, §4.4.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`. Unblocked for this track by ADR 0205 §4 (Act II starts per track); claimed by creatures-b 2026-10-30.

- 2026-10-30 (creatures-b): built. The art sheet, `assets_src/creatures/kesh/` (build + materials), job `creature_kesh` (byte-identical, verified twice), `assets/creatures/kesh/`, `game/creatures/kesh/kesh_battle.tscn`, the creatures.json row (`vowbound_pending` on combat's M4-A2P-024/025), shot `creature_kesh` (pending_baseline), the portrait, PROVENANCE rows, tests `test_kesh_*` in tests/unit/test_creature_vowbound_act2.gd. The clip map for combat is in both sheets. Open items: the art sheet's "As built".
- 2026-10-30 (creatures-b, second pass on the coordinator's notes): water that flows (streaming bands, runnels, white breaking), a garment (a fitted bodice in its own satin `robe` slot with a Choir-stone cord at the neckline, and a stole), a face at the Act I bar, 46 carved mouths on stone plaques in flowing bands, and an idle with a hand at her heart. 19,366 triangles (within the ~20k allowed). Clip names, contacts, the clip map, height, grounding and framing kept. See the art sheet's "second pass".
- Reviewer: rendering (the water read in a daylight arena and the Choir; the heart's light; the face up close).

## Review log
