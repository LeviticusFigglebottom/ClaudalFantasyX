---
id: M3-CHR-03
title: "Act I named characters: Liss Varrow (hero path), Tavi Orse and Mother Kell (villager path)"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-03, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Build the Act I named characters from [`act1_npcs.md`](../../art/characters/act1_npcs.md) §2-§4.

**Path change from the brief:** Liss is built on the **hero** path (act1_npcs.md §0), because she is a party member. She
joins in Ch6, has a battle niche, a Swell input and a `speakers.json` portrait, and she carries the game's rawest grief
scenes. Tavi (Ch7) and Kell (Ch1) are villagers on pipeline.md §15. The Lead may split Liss into her own task; her
criteria below are already separate.

## Acceptance criteria
### Liss (hero path, act1_npcs.md §2)
- [ ] `assets_src/characters/liss/` on the shared modules. `liss_params.json` holds every number in §2.1 and §2.10.
      `liss_textures.py` has the **line-mark generator** (11 marks, right side only, the eleventh on the cheek), and
      later Saltwright builds can import it.
- [ ] M1-CHR-14 lessons apply:
      - the coat's long back is two leg-following tails with bones, not a tube;
      - the armholes sit at least 11.5 cm below the shoulder joint;
      - the launcher sits 2 cm off the thigh, on its own prop bone;
      - the hair tail's root is seated on the head SDF, and the scalp cards stop 12 mm short of it.
- [ ] Job `liss` with `"threads": 4`, byte-identical across two runs, with `PRE_ROUND` set. LOD0 at most 60k, LOD1
      about 28k, and the GLB under 5 MB.
- [ ] A `liss` entry in `tools/dev/rig_checks.json` (garments `Costume` and `WorkSleeve`; props `Launcher`; the `braid`
      entry for `HairTail:hair`). `rig_probe.py --hero liss --report` passes, or each ratchet is pinned with a viewed
      reason.
- [ ] Face poses (all 15 tags, §2.6) and clips (§2.8) through `hero_clips.py --hero liss`, with the other heroes'
      libraries byte-identical. A battle actor, `liss_battle.tscn`, on the LOD1.
- [ ] Shots `liss_front`, `liss_back`, `liss_face`, `liss_face_stylized`, `liss_silhouette_vs_rhen` and
      `liss_clip_haul_rope`. Baselines are viewed and approved.

### Tavi Orse and Mother Kell (villager path, act1_npcs.md §3-§4)
- [ ] `params/tavi.json` and `params/kell.json` from the drafts in §3.3 and §4.3, tuned against the face shots. Jobs
      `villager_tavi` and `villager_kell` with `"threads": 4`, byte-identical. LOD0 inside `test_villagers.py`'s 20–36k
      range, each GLB under 3 MB, and an `<npc>_actor.tscn` for each.
- [ ] `villager_hair` accepts a `female` hairline on the `short` kind (for Kell), if it doesn't already. If that module
      changes, every `villager_*` job is re-verified.
- [ ] Face poses `game/levels/_tests/characters/villagers/{tavi,kell}_face_poses.json`: all 15 tags, with the overrides
      in §3.4 and §4.5.
- [ ] The wick, the wick bundle and the trimming shears come from one source (`assets_src/characters/props/wick.py`, or
      wherever the build settles), with PROVENANCE rows. The same wick serves Rhen's tin and the E7 post-credits lamp.
- [ ] Shots `villager_tavi_front`, `villager_tavi_face`, `villager_kell_front` and `villager_kell_face`, plus a lineup
      with the Haluna villagers. Baselines are viewed and approved.

### All
- [ ] PROVENANCE rows for every output. `villagers_review.md` updated for Tavi and Kell, `liss_review.md` written, the
      live log updated, and a handoff.

## Notes
- Mother Kell is Oruvel's **chandler**, who never learned to swim (N-25 S1, ADR 0022 sweep-H S1). She is not "the old
  Oruvel diver": those glossary rows are superseded. She is never drawn as a mentor, or as a keeper Dace charged with
  his son (sweep-H B1).
- Echo watch for Liss (act1_npcs.md §2.2): no goggles, no yellow, no swirl patterns, and trousers rather than a skirt.
- Tavi's and Kell's extra clips belong to M3-CHR-04, because they need per-NPC clip lists in `villager_clips.py`.

## Review log
