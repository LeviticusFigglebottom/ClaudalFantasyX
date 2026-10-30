---
id: M4-A2P-053
title: "The Kirru people (base, eldest, child, clutch) and the Ullari woman"
role: character
status: review
owner_session: "claude/characters"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
The Kirru are a people, never monsters: one Kirru base from Pell's rig, with age and size variants, name-shells, and the farewell-tide's turning-away clip; plus the Ullari woman of Ch12's side scene.

## Acceptance criteria
- [x] Built, rigged, clipped; shots viewed; never a heron or otter enemy silhouette (act2_roster).
- [x] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch10, Ch12.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 (characters, ADR 0205): done.
  - **The Kirru base** is Pell's build with variants (`assets_src/characters/pell/pell_variant.py`; overrides in
    `assets_src/characters/kirru/variants/<id>.json`). build_pell.py, pell_textures.py and write_materials.py take
    `--variant`; without it Pell builds byte-identical. A variant writes its own head and body maps and shares
    Pell's cloth, fur and feather atlases.
  - **The variants:**
    - `kirru_elder`: 2.24 m, a grizzled grey coat, a deeper neck S, a pale thin crest, faded cloth.
    - `kirru_adult`: a woman of the ring, 2.12 m, warm fur, sage cloth.
    - `kirru_child`: 1.95 m, "already taller than Rhen", darker and plain, a small crest, ochre cloth.
    - None has Pell's notched ear. Each carries a name-shell and a fishing staff (Pell's props), and a cloth dye
      through the opt-in `_look.cloth_tint`.
  - **Clips:** Pell's idiom with no battle contract (a people, never monsters): idle, walk, talk, go_still,
    listen_tilt, and `back_to_sea` (the farewell-tide's turning away, back to the party, head bowed). Field wrappers
    are at `assets/characters/villagers/kirru_*/kirru_*_actor.tscn` for ZoneCast.
  - **The Ullari woman** (`ullari_woman`, villager build), for Ch12's pass-cord: layered weaving (an oatmeal wool
    top, a dark wool skirt, a woven madder shawl), an indigo sash, a knotted keth cord on her wrist, a plain `sad`
    row, and the `tie_knot` and `touch_knot` clips.
  - **Shots (pending baselines, viewed):** kirru_*_{front,face,back_to_sea} and villager_ullari_woman_*.
  - **Checks:** the rig probes pass Pell's limits; test_kirru 4, test_pell, test_villagers and test_hero_clips pass;
    the 3-path verify covers pell, kirru_* and villager_ullari_woman.
  - **Known limits:** at a close-up the Kirru faces are Pell's head re-coloured (the same muzzle and eyes). The
    elder's grey face reads pale and smooth.

## Review log
