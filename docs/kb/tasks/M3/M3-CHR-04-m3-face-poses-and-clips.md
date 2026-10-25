---
id: M3-CHR-04
title: "Face pose sets and story clips for the M3 characters (Ysolde, Sefir, Liss, Tavi, Kell)"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-01, M3-CHR-02, M3-CHR-03]
milestone: M3
request-from: lead
reviewer: cinematics
---
## Goal
Give every M3 character the face pose set and the Act I story clips their beats need, wired so Cinematics can drive
them with `@face` and `@anim`. The tables are in [`ysolde.md`](../../art/characters/ysolde.md) §6.2 and §10, and in
[`act1_npcs.md`](../../art/characters/act1_npcs.md) §1.6 and §1.8, §2.6 and §2.8, §3.4 and §3.5, and §4.5 and §4.6.

## Acceptance criteria
- [ ] **Face poses:** a `<id>_face_poses.json` for `ysolde`, `sefir`, `liss`, `tavi` and `kell`, each with all 15 tags of
      `game/data/dialogue/emotions.json`. The personal rules are applied: Ysolde's rest brow, Sefir's symmetry, and Liss's
      left-sided smile and rest scowl. The `face_poses` and `blink` entries are handed to Cinematics for
      `sequencer.json`, which is their file.
- [ ] **Hero clips** (`hero_clips.py`): the persona keys `breath`, `book` and `hands_joined` are added with defaults that
      keep Asha's, Rhen's and Toma's libraries byte-identical, and `test_hero_clips.py` proves it. The clips:
      - Ysolde: `board_step`, `vigil_book_shut`, `reink_shell`, `stand_apart`, `book_fan` (with the `book_fan` blendshape
        track) and `cast_glyph`;
      - Sefir: `raise_palm`, `incline_head`, `glance` and `pivot`, plus `walk_glide` for Ch13;
      - Liss: `crouch_shelter`, `carry_crate`, `bury_lamp`, `clock_lantern`, `point_up` and `haul_rope`.
- [ ] **Villager clips** (`villager_clips.py`): a per-NPC clip list read from the params file, with Tavi's
      `hand_on_shoulder`, `hear_news` and `name_rite`, and Kell's `press_wick`, `trim_wick` and `haggle_laugh`. The seven
      Haluna villagers' libraries stay byte-identical.
- [ ] **Rig guards over the new clips:** `rig_probe.py` for `ysolde`, `sefir` and `liss`, over every third key of every
      new clip, passes the `rig_checks.json` limits, or each ratchet is pinned with a viewed reason. The deep poses are
      `bury_lamp`, `crouch_shelter`, `haul_rope` and `cast_glyph`.
- [ ] **Tests:**
      - `test_hero_clips.py` checks that every `@anim <id> <clip>` in the M3 `.dlg` and cutscene files has a clip, that
        the feet stay on the floor in the standing clips, that Sefir's `idle` is still, and that the book sits at
        Ysolde's hip.
      - `test_villagers.py`, or a sibling test, checks that Tavi's and Kell's extra clips exist.
- [ ] **PROVENANCE:** rows for every new clip library and face pose file.
- [ ] **Shots:** one clip shot per character, on the hardest pose: `ysolde_clip_cast_glyph`, `sefir_clip_raise_palm`,
      `liss_clip_bury_lamp`, `villager_tavi_hear_news` and `villager_kell_press_wick`. Baselines are viewed and approved,
      with `HYMN_SHOTS` set to these ids.
- [ ] A handoff, and the live log updated.

## Notes
- Clips are pure Python, with no Blender. Rerun `hero_clips.py --hero <id>` after any rebuild that moves a skeleton.
- Reefball swimming clips belong to the Reefball match task, not this one.

## Review log
