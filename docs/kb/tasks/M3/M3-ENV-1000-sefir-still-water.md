---
id: M3-ENV-1000
title: "Brine Shoals (Ch6): Sefir's barge leaves no wake and his reflection never ripples"
role: environment
status: doing
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-CHR-02, M3-RND-03]
milestone: M3
request-from: character
---
## Goal
Sefir first appears at the end of the Ch6 Brine Shoals raid on his white barge, poled through the smoke, which
**leaves no wake** (ADR 0017, `docs/kb/story/characters/sefir_aurane.md`). His reflection in the water never ripples
(act1_npcs.md §1.10). The barge and the water are Environment's; the layer and shadow feature is Rendering's
(M3-RND-03).

## Acceptance criteria
- [ ] The Brine Shoals water honours Rendering's still-reflection layer for Sefir (and for anything on the barge with
      him, if the beat wants it).
- [x] The barge's hull moves through the water without a wake or ripple ring, while the Order's other boats leave one.
      (env-art 2026-10-27: the Brine Shoals kit's `boat_wake` piece and `env_boat_wake.gdshader`; the barge gets none.)
- [ ] Viewed in a shot with Sefir on the barge (his stage is `game/levels/_tests/characters/sefir/sefir_stage.tscn`;
      his `pivot` clip turns him 30 degrees in place on the barge, no step).

## Notes
- His actor: `assets/characters/sefir/sefir.glb`; clips in `assets/characters/sefir/anim/sefir_clips.tres`.

- **Renumbered (Lead merge, big9, 2026-10-24):** filed as M3-ENV-01. M3-ENV-01 is env-art's Tamsule Bell kit (named in code); the characters track filed this request under the same id. Now M3-ENV-1000, from the Lead's id block (CONSOLIDATED §4).

- **env-art, 2026-10-27 (in progress):**
  - **The wake.** There was no boat wake anywhere in the water, so I built one for the boats that move. It is the
    Brine Shoals kit's `boat_wake` (`bs_wake.py`): a 16 m Kelvin wake with arms opening at 19.5°, the churned centre
    track, and the origin at the stern on the waterline, trailing toward −X. Its material is `bs_wake`, on the new
    `game/shaders/environment/env_boat_wake.gdshader`:
    - foam streaks drift with `hymn_wind_time` at `speed_m_s`;
    - `speed_m_s` 0 hides the wake (a moored boat);
    - alpha-blended with no depth write; list it in the layout's `prop_no_shadow`.
  - **The preview.** The Brine Shoals preview poles a vendor boat up the channel beyond the barge, with its wake
    trailing back toward the barge's bow. It shows in B05. The white barge has no wake piece, and a test pins that.
  - **For act1-chapters (Ch6 dressing):** put a `boat_wake` at the stern of every boat that moves in a beat, with
    `y` = water and the yaw = the boat's heading (the wake's local +X). Never give the white barge one.
  - **Next: the reflection.** Add a `RevenantTells` node with `actor_path` set to Sefir, beside the barge in the
    Ch6 barge beat. That waits for M3-RND-03 (`gpu/m3-rnd-03-sefir-tells`, in review) to reach the integration
    branch. The Brine Shoals water already uses the project's `water_surface_body.gdshaderinc`, so it honours the
    layer as it is. Then a shot with Sefir on the barge.

## Review log
