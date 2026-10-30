---
id: M4-A2P-051
title: "Malcor Venn and Sefir's Abiding guard: field and battle actors"
role: character
status: review
owner_session: "claude/characters"
depends_on: []
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
The two people bosses: Malcor Venn (a Warden fighting as a living-seeming man; field, cutscene and battle actor) and the Abiding guard (battle actors), with Stillguard and Conclave dressing for the court. Act I's Stillguard boss is the precedent for human battle actors.

## Acceptance criteria
- [x] Models, rigs, battle clip sets, sounds requested (M4-A2P-092); review shots viewed.
- [x] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch14, Ch16.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 (characters, ADR 0205): done on the Stillguard kit (stillguard_variants.json `named`). Every new
  switch is opt-in: Moll, the squad, Ivo and the officer are byte-identical on all 3 numpy paths.
  - **Warden Malcor Venn** (`venn`) wears Moll's kit in a Warden's dyes: black lacquer and gold, an order_marble
    tunic and a lacquer_red sash (moll_textures.cloth_atlas `palette`, sg_textures.dyed_cloth). He has a grey crop,
    a heavy **halberd** (sg_halberd.py, on the spear's bone) and no shield (build_moll `no_shield`).
    - **Clips:** Moll's battle contract and yield (B09's "driven back"), with a two-handed parry for `defend`.
    - **Actors:** a battle actor `game/characters/foes/venn_battle.tscn` and a field wrapper
      `assets/characters/villagers/venn/venn_actor.tscn`.
  - **Sefir's Abiding guard** (act2_ch16.md 5a: Stillguard elite in veiled gold lacquer, living) is three builds
    with the helm and a gauze **veil** (sg_helm.veil). Each has the sash and a battle actor
    (`game/characters/foes/abiding_*_battle.tscn`).
    - `abiding_halberd` (the Veiled halberdiers): Venn's halberd and keys.
    - `abiding_bulwark` (the Bulwark casters): Moll's brine-iron and shield and Moll's keys.
    - `abiding_captain` (the Captain of the Veil): the halberd, with the veil and the sash in lacquer_red.
  - **Shots (pending baselines, viewed):** venn_* (7) and abiding_* (6).
  - **Rig probes:** all four pass. Limits are pinned only where Moll's own mechanisms show (the knee fold in the
    kneel, the armpit sleeve crease), each with its reason.
  - **Sounds:** requested via M4-A2P-092 (audio has the Abiding guard's stings; Venn's halberd swing, settle and parry
    are to add).
  - **Known limits:** the veil reads as a stiff gold curtain at a close-up. In Venn's parry the left hand stops at
    the chest, short of the haft. Venn's face and crop are at Ivo's level.
  - **Design note:** docs/kb/plan/act2/bosses/abiding_guard.md (01:30) drew three pale hooded lamp-hook bearers. The
    newer Ch16 beat sheet (01:53) and ch16_the_choir.dlg have veiled gold lacquer, four Veiled and a Captain; this
    build follows the beat sheet.

## Review log
