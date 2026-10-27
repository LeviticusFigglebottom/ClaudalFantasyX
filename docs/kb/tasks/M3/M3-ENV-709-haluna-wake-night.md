---
id: M3-ENV-709
title: "Haluna's wake night for Ch4 (M3-C04-03's Haluna half): the causeway head's lamps and feast, the wake shells' states"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-701, M2-ENV-02]
milestone: M3
request-from: cinematics
reviewer: rendering
---
## Goal
act1_ch04.md §9 (M3-C04-03): on M2-ENV-02's night, the causeway head as a feast with about 100 oil lamps, Asha's
shell set in the Pilgrim's Wake gap beside Imra's (faded, then re-inked), Ysolde's ink kit. The dressing must show
only in Ch4's states, so it is data the chapter's zone toggles, not part of every Haluna visit.

## Acceptance criteria
- [x] Kit pieces (`dressing.py`): `ground_lamp`, `feast_mat`, `ink_kit`, `wake_shell_single` (a shell on a carved
      stand; its state is the material: `kit_wake_shell_inked`, `kit_wake_shell_faded`, new).
- [x] `HalunaDresser` `story_sets`: each set is a hidden `StorySets/StorySet_<name>` (a plain Node holds them, so
      HalunaCollision never boxes a set); `story_set(name)` returns it. Sets in `haluna_layout.json`:
      `ch04_wake` (100 lamps lining the path to the Wake and ringing it, six feast mats, the ink kit, ten warm
      lights with fog energy 0), `ch04_shell_asha` (inked), `ch04_shell_imra_faded`, `ch04_shell_imra_inked`.
- [x] Tests: `tests/unit/test_haluna_story_sets.gd`; `--filter=haluna` 52/0 (with test_haluna_zone's ground probes).
- [ ] act1-chapters: Ch4's zone shows the sets by flag (`ch04_shell_set` → `ch04_shell_asha`; Imra's faded until
      re-inked) once Haluna's wake moves onto `ch02/haluna` (ADR 0035), and keeps the dock unlit (skip
      `HalunaZone.set_night`'s dock lanterns). The per-window unlit toggles and the dawn's guttering (scale the set's
      lights' energy) are theirs. PC renders of the H12–H16 shots when they exist.
