---
id: M3-C06-05
title: Ch6 combat follow-ups (Liss's real kit, the hound's guard, the Smoke field, Toma's shove, two band exceptions)
role: combat
status: doing
owner_session: claude/battle-presentation (session_01UPFyEA8QkJULH74MGgnMvJ; the Lead, 10-29: the Swell techniques)
depends_on: [M3-C06-02]
milestone: M3
request-from: cinematics
---
## Goal
M3-C06-02 made Ch6 playable with provisional combat data (`_note` PROVISIONAL rows) and two small encounter rules (battle_ctb.md "Encounter rules: forbidden skills and yielding foes"). Each item needs a combat pass:
1. **Liss** (`characters.json`, liss_varrow.md, act1_ch06.md §9 Combat 21). Today she has stats, Attack, Reel Shot (a bolt that pushes its target down the timeline) and Flash Housing (Darkness), plus placeholder gear (Crank Launcher, Copper Work-Sleeve). Still needed: steal, combine and gadgets, her Swell (the *reel-stop*), and her Lattice start. Her first fight is Ch8; she is in no sim suite.
2. **The raid-hound guards the Inquisitor** (§5 phase 1): it should intercept single-target attacks on him and pounce on the striker, its turn jumping forward on the timeline (the preview showing it). There is no engine rule for either. Today it simply bites, and Toma's Challenge (Provoke) draws it.
3. **The Smoke field** (§5 phase 2): Darkness on the whole party every round while it holds, with Ysolde's magic never missing in it and Asha's cleanse lifting it. Today Torch the Hulk is a Darkness skill every third turn from 50%. The phase should also start when the hound is driven off.
4. **Toma's counter becomes a shove** for this fight (§5): the engine has no counters yet.
5. **The first-refusal bark** ("No. Not them.", §5 and UI 22): today it is Toma's first-turn prompt (`turn_prompt_hero`). Ysolde's field bark and the Inquisitor's yield bark are spoken in the scripts just before and after the fight. A battle-bark system would move all three.
6. **Two logged band exceptions** (balance_targets.md "Ch6"): `role_answer` is report only on the three skipper suites (Rhen, the answer, is already on the field, as with Ch4's leeches), and the Inquisitor's `smart` ceiling is lifted to 100% with a 25-mean-turn floor (as with the Spar-Wraith). Rule on both.
7. **The flats' groups were cut** to three foes: `ch06_flats_skippers` (three skippers) and `ch06_flats_mixed` (two skippers and two gulls) could not meet the regular band. The flats also share the ridges' random table, because GreyboxZone has one `encounters` block. Decide whether the flats get their own table (a zone-root feature) and their own band.
8. **Berserk and Confuse** auto-turns don't check `forbidden_skills`. No status in this fight causes them, but the rule should hold.
9. **The Pemakar shop tier** for the Ch6 loadouts (they carry Ch5's gear), and the B08 vendor's stock (it reuses `brightwater_purser`).

## Acceptance criteria
- [ ] The PROVISIONAL notes are gone from the Ch6 rows, or each is ruled on here.
- [ ] Every Ch6 suite passes `sim.py --check`, and each exception is kept or removed with a reason.
- [ ] No earlier band moves; if one does, re-measure it and log why.

## Notes
- **2026-10-29, battle-presentation (the Lead's 10-29 assignment: the Swell part of item 1).**
  - **Liss's Swell is Three-Reel Charge** (`three_reel_charge`): physical, power 9, every foe, accuracy 100, rank 3,
    no MP. It pushes each foe 1 rank down the timeline, because her gadgets alter turn order.
    - The band is Written Light's (every foe, power 10) less one point for the push: 13 at good, 17 perfect.
    - It is not magic, so Silence does not stop it.
  - **Its input is the reel-stop** (`swell.json` `reel_stop`): a three-beat `timing_ring`, one press per reel
    (0.7 s beats, peak at 0.65). +45% at good, +90% perfect.
  - The presentation was staged in M3-BPR-422 (choreo `reel`, effect `swell_reel_stop`). It was viewed on the Ch8
    hoist with `tools/vfx/swell_finisher_sheet.gd`.
  - **Still open in item 1 (not this pass):** steal, combine and her gadgets, and her Lattice start. Items 2–9 are
    untouched.

## Review log
