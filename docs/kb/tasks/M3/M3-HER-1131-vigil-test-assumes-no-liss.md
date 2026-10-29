---
id: M3-HER-1131
title: "Request (slice-polish): test_fp_prologue's vigil test assumes Liss has no field body; she has one once her row and model merge"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
M3-HER-100 (slice-polish's request to the hero track): **Liss's row is done.** `field.heroes.liss` has been in
`game/data/hero_motion/hero_motion.json` on claude/hero-integration since 1f190eb8: liss_lod1.glb, walk 0.97 and run
2.19 m/s, measured. Checked on a scratch merge of claude/hero-integration (e7d6e7a6), claude/characters (24dca3d1, her
model) and claude/m2-slice (dress_vigils, 28b0f97a): `PrologueScene.dress_vigils()` gives Liss her body and her capsule
goes. Kerrid and Pell wait for M3-CHR-505 and M3-CHR-506.

On that merged tree one of slice-polish's tests fails:
`test_fp_prologue.gd::test_a_vigil_takes_its_body_when_its_hero_has_one: Liss waits`. It lends Kerrid Ysolde's row,
then asserts Pell's and Liss's capsules stay. That held only while Liss had no row.

## Acceptance criteria
- [ ] The test stays independent of which heroes have rows. On its private copy of the data, before `_make_scene()`:
      `heroes.erase("liss")` and `heroes.erase("pell")` (one line each). Or it asserts per id: a capsule stays exactly
      when `HeroFieldActor.scene_path(id) == ""`.
- [ ] `--filter=prologue` is green on the merged tree.

## Review log
- 2026-10-28 slice-polish: done (the vigil test follows hero_motion.json: a vigil with a field body takes it, the rest wait).
