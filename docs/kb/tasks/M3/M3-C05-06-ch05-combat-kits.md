---
id: M3-C05-06
title: Ch5 combat follow-ups (Kerrid's real kit, Kahre, the Matron's smart band, the Quench Charm)
role: combat
status: review
owner_session: claude/battle-presentation (session_01UPFyEA8QkJULH74MGgnMvJ; the Lead, 10-29: the Swell techniques)
depends_on: [M3-C05-02]
milestone: M3
request-from: cinematics
---
## Goal
M3-C05-02 made Ch5 playable with provisional combat data. Each item below is marked PROVISIONAL (`_note`) in the data and needs a combat design pass:
1. **Kerrid** (`characters.json`, kerrid.md, act1_ch05.md §9 Combat 17–18).
   - Today he has stats and four skills: Attack, Fluke Cleave (`fluke_cleave`, Armor Break for 3 turns, rank 5), Snub the Line (`snub_line`, Power Break for 3 turns, rank 5) and Anchor Fall (power 18, rank 7).
   - Still needed: his Swell (the *weighted swing* input), a Lattice start node, and starting gear beyond the placeholder Anchor-Cleaver and Plain Wraps.
   - **Distinguish Fluke Cleave from Toma's Shell Breaker.** Shell Breaker applies a permanent Armor Break (duration -1), which is stronger than Kerrid's. The sheet suggests weakening Shell Breaker to "a little, for a short time", but that moves `sandbox_reef`'s bands, so it needs re-measuring.
   - **The skill names avoid the FF terms.** "Armor Break" and "Power Break" are also skill names in a Square Enix game, so his skills got original names. The statuses keep their existing names.
2. **Kahre** (`vowbound.json`, vowbound.md §2): "raw lightning damage that ignores defence" has no engine rule yet; `forge_bolt` is a plain lightning spell. Last Strike is a stand-in. No sim suite calls him.
3. **The Cinder Matron's `smart` band** (balance_targets.md, Ch5).
   - It is report only: with two reserves and Asha's Mend, `smart` wins every seed, whatever the tuning. The table's 75–92% needs time pressure, for example an AI condition on turns since the phase began (an "at least" counterpart to `turn_mod`; `tools/validate_data.py` AI_CONDITIONS), or an escalating Pour.
   - Then give `smart` its band.
4. **Cleanses and reactions** (battle_ctb.md): show a reaction on the HUD (the quench re-crusting her), and add a battle VFX hook for it.
5. **The Quench Charm** is a key item. The sheet wants an accessory with a Fire ward, and `equipment.json` has only weapon and armor slots. Decide the accessory slot, then add a `ch05_matron` variant suite with the charm.
6. **The Pemakar shop tier** (sheet §9 Combat 21; Kerrid's first smith-made weapon included). The Ch5 loadouts stand in with Haluna's post-Drownbell weapons.
7. **The Coral Hooks' Ember Edge heals the Matron**, who absorbs fire. Decide whether that lesson is wanted, or whether the forge-construct should only resist fire.

## Acceptance criteria
- [ ] The PROVISIONAL notes are gone from the Ch5 rows, or each is ruled on in this task's notes.
- [ ] Every Ch5 suite passes `sim.py --check`, and the Matron's `smart` has a band.
- [ ] No pre-Ch5 band moves; if one does, re-measure it and log why.

## Notes
- **2026-10-29, battle-presentation (the Lead's 10-29 assignment: the Swell part of item 1).**
  - **Kerrid's Swell is The Long Hold** (`long_hold`): physical, power 14, one foe, accuracy 100, rank 3, no MP.
    That is Return Tide's band (formulas.md § Swell, "Their techniques": 20 at good, 26 perfect).
  - **Its input is the weighted swing** (`swell.json` `weighted_swing`). It is a `brace` row with one blow: hold
    Confirm while the cleaver coils (graded at 1.1 s) and let go on the count at 2.4 s. +45% at good, +90% perfect,
    like every input. No new input kind and no new constant.
  - The presentation was staged in M3-BPR-422 (choreo `swing`, effect `swell_weighted_swing`). It was viewed in his
    Matron fight with `tools/vfx/swell_finisher_sheet.gd`.
  - **Still open in item 1 (not this pass):** his Lattice start node, his starting gear, and Fluke Cleave against
    Shell Breaker. Items 2–7 are untouched.
  - **To review (combat):** the Swell part only. The other items stay open on this task for a combat pass.

## Review log
