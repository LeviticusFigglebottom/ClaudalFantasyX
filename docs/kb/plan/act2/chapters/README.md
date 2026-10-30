---
draft: pre-gate
owner: chapters (was act1-chapters; act2_tracks.md)
---
# Act II chapter drafts (Ch10–Ch16): flows, triggers and POIs, encounters, field cameras

**Draft, pre-gate (ADR 0203).** These are docs only: no game data, scene or test changes until the Lead tags
`act1-complete`. They turn `docs/kb/plan/act2_plan.md` §2 into the four things the chapters track builds for each
chapter, written in Act I's conventions. The story track's beat sheets (M4-C1x-01) win any conflict on story; update
these drafts to match when they land.

| Chapter | Draft |
|---|---|
| Ch10 "Fen of the Kirru" | [ch10.md](ch10.md) |
| Ch11 "Lowlight" | [ch11.md](ch11.md) |
| Ch12 "The Cold Road" | [ch12.md](ch12.md) |
| Ch13 "Gold and Lacquer" | [ch13.md](ch13.md) |
| Ch14 "The Peace Wedding" | [ch14.md](ch14.md) |
| Ch15 "Unlamped" | [ch15.md](ch15.md) |
| Ch16 "The Edge of the World" | [ch16.md](ch16.md) |

## Conventions (from Act I)
- **Flow:** `game/data/flow/chapters/chNN.json` (ZoneStory). Each zone has `party`, `arrive` rows (a zone load), `beats`
  (run by a trigger's `{"beat": id}`, or by code through a config `*_beat` key) and `barks`. Steps: `place`, `play`,
  `set`, `chapter`, `party`, `zone` (`place_actor`, `hide_block`, `show_block`, `refresh_states`, `give`,
  `checkpoint`), `battle` (`victory_flag`, `return_spawn`, `party`, `reserve`, `objective_flag`), `go`, `scene`,
  `if_event`.
  - Flags are `chNN_<what happened>`, declared in `flags.tres`.
  - A beat that should run once is guarded by its own flag in `when.unset`.
- **Layout:** `game/levels/chNN/<zone>/<zone>_layout.json` holds spawns, marks, actors (`cast`, `cast_still`),
  triggers (`touch` or `interact`; `requires_flag`, `blocked_by_flag`, `sets_flag`, `once`), `shots`,
  `camera_volumes` (pan-follow), `states` (flag → hide/show/place) and `variants` (light).
  - Positions in these drafts are on the existing greybox frame (M4-C1x-02), where one is known. Each zone is re-laid
    once on its kit (`--relayout`, as Ch5–Ch9 were), and the drafts then follow the kit.
- **Party staging:** a stage actor for a party member hides that member's follower while it's visible.
  - Hand the party back after a scene: the sequencer's `hand_off` does it within 3 m of Rhen; otherwise use a flow
    `hide_block`.
  - Stage them again with `place_actor` before a scene that needs them away from Rhen (the Ch9 road lesson).
  - `@mark` always walks. There is no in-scene teleport, so cuts happen between scenes, with flow steps.
- **Encounters:**
  - **Random:** a zone `encounters` block. Aim for **about 3 random fights on a zone's critical route** (the Act I
    pass: gaps of 32–52 m, a 12 m grace; check with `tools/act1/flow_audit.py`'s companion density estimate).
  - **Scripted:** a flow `battle` step, with its `arena` in `encounters.json`.
  - Every row needs an arena; `tests/integration/test_act1_encounters_resolve.gd` extends to `ch1[0-6]_`.
  - **Bands** (`tools/balance/targets.json`, act2_plan §2):
    - regulars: naive 5–35%, role ≥ 90%, smart ≥ 95%, p90 ≤ 40 turns;
    - bosses: naive ≤ 3%, role 55–80%, smart 70–90%, p90 ≤ 80;
    - set pieces: the Ch8 set-piece curve (`scripted_escape` counts as a win).
  - All suites run on a **Ch10 loadout**: the Act II shops, Lattice progress through Ch9, Pell in.
- **Cameras:**
  - **Scene shots:** an id per zone letter plus a number (Act I: H, F, D, P, A, W, R, N). Each is framed on its subject,
    checked with `tools/act1/shot_check` (line of sight; the solver for a clear view) and viewed in
    `tools/act1/cutscene_stills`.
  - **Field:** the hub orbit, plus pan-follow `camera_volumes` wherever the orbit sees a wall, a roof or a void. Check
    every map POI with `tools/act1/poi_views.py`.
  - **Pacing:** no scene holds past its script beyond a visible walk ending (STILLS_TIMING TAIL).
- **Map POIs:** `game/data/ui/zone_maps.json` (UI's file; chapters moves POIs with their sources). Sources are
  `spawn:`, `trigger:`, `actor:` or `mark:`; `test_zone_map_pois` keeps them on their sources.
- **Guards to extend at the gate:**
  - the `_thread` test per chapter;
  - `tools/act1/flow_audit.py` (`ACT1_CHAPTERS` to ch10–ch16);
  - the encounter-resolve test;
  - `act1_cutscene_walks` and `hero_cutscene_snaps` over the new scenes.

## Shared Act II items the chapters track needs from others
- **Story:** the seven beat sheets and `.dlg` (M4-C1x-01).
- **Characters:** the Kirru, Ullari, Ansedra and Saltwright crowds, plus Tobin, Merel, Liss's father, Malcor Venn and
  the Abiding guard.
- **Creatures:** the regulars and bosses (data exists for the regulars).
- **Env-art:** each zone's kit, dressing and collision.
- **Battle-presentation:** the arenas' VFX.
- **Combat seat** (folded into chapters, act2_tracks): drain, rooted, repair, part-break targeting, the timeline-slow
  field, element cycling (act2_plan §4.6).
