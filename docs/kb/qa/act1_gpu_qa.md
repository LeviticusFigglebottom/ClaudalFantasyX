# Act I on the real GPU: what reads unfinished or wrong (pc-gpu, ADR 0041)

The PC runs Act I on an RX 9070 XT (Windows 10, Godot 4.6.3 official, Vulkan) at the High preset, 2560×1440. It lists
only what shows on the real GPU or reads unfinished there: GI and lighting, shaders, the water, LOD pop, z-fighting, the
Undertow, and hitches over 33 ms. Lavapipe gate drift is not listed here. Each row names its owner per ADR 0041's split:

- env-art: the Prologue to Ch4 zones;
- env-art-b: the Ch5–9 zones and the arenas;
- creatures: enemies and villagers;
- creatures-b: bosses and Vowbound;
- characters: the party and named NPCs;
- battle-presentation: VFX;
- slice-polish: the slice cutscenes;
- act1-chapters: placement and flow;
- ui-menus;
- audio.

Pass A captures every manifest shot through `tools/gpu_bench/capture_preset.tscn` at High ×2.667. Pass B is the walk:

```
slice_sweep.tscn -- --walk=res://tools/gpu_bench/act1_walk.json --preset=high --res=2560x1440 --budget --stills=<dir>
```

It covers the title, New Game into the Prologue, each chapter as F8 starts it (its arrival story plays), every spawn of
every zone, one battle per arena and every Act I boss intro. Contact sheets go on `gpu/act1-qa-<n>` under
`docs/kb/qa/gpu/act1/`.

**Pass A, 2026-10-28:** all 341 manifest shots captured at High ×2.667 on integration 048b0a7f (1074 s). The 31 shots with a node or time_scale setup were re-captured with capture_preset's new `--setup`; without it the slice cutscene shots render navy and haluna_h10_dock_night renders in daylight. Read well on the GPU: Haluna, the Shell Shrine, the Tamsule galleries and moorings, the Coilspire path, and the tideline, causeway, raft, route, shoals, derelict and matron arenas. The other boss intros read well too. Contact sheets: `docs/kb/qa/gpu/act1/pass_a/`.

**Pass B, 2026-10-28:** the Act I walk on lead/gate-ft-beach on the RX 9070 XT at High 2560×1440.
- It covers the title, New Game, Ch1–Ch9 by chapter start, every spawn, the zones a chapter doesn't start in, one battle per arena and every boss, with stills every 5 s and dialogue tapped.
- 122 segments, 401 stills in 1666 s. The sheets are in `docs/kb/qa/gpu/act1/pass_b/`, a selection; all 401 stills are on the PC.
- Read well on the GPU: Oruvel, the Hullgnaw, Drownbell, Bottle Hermit and Spar-Wraith fights, Tamsule's galleries and the Tidecup UI, the Coilspire path, the Ch8 stair hold.
- The walk's "spawns" right after New Game moved Rhen around Haluna during the beach cutscene. That is a walk artefact, not a finding.

**The human's run fix (M2-CHR-513), filmstrip:** `pass_b/run_cycle_ch01.jpg` is Rhen running in Ch1 at High, a still every 0.12 s, from behind and from the side (`run_cycle_walk.json`).
- The legs alternate with a full stride, the feet plant, and the arms swing close at the sides. There's no arm or leg flop: **the run reads grounded**.
- In Haluna the same filmstrip never shows Rhen: the field camera at the Village spawn looks down an empty lane (row 21).

**Re-check on big15 (lead/gate-big15 @ 6466a6f5, 2026-10-28):** the 48 shots behind the open rows, at High ×2.667 with `--setup` (`recheck_big15/`).
- **Fixed (15):**
  - Iskarra and the vigil set, now in colour (1, 2); the verse steps (3).
  - The Brine camp and road, dressed (5); Corrow's mole and stair, Ch9's road and strand (7–9).
  - The Ch8 wall arenas (10); the Reach intro, dressed, with no wedge (11).
  - Ysolde's model (13) and Ilun's (14) in battle; the terraces, readable (16).
  - Moll's hair (29); the beach with both faces (20).
- **Still open (12):**
  - The ferry deck, too dark (4); the Coilspire grid lines (6, 27).
  - **Moll, still a capsule in his arena and intro (12)**.
  - The Underway lit rectangles (15); the Undertow eye rings (17); the green rectangle in the Prologue water (19).
  - The cameras in walls: Ch1, the wake, Brightwater (23–25).
  - Ashcrown greybox (26); Corrow's sphere rocks (28).
- Rows 21–22 and 30–42 need the walk (next).

**big38 sign-off check (2026-10-31), integration @ 8b546285, RX 9070 XT, High 1440p.**
- **ACT I IS NOT READY TO SIGN OFF.** What isn't clean:
  1. **The art rows, still open:**
     - 54: Sefir's hair;
     - 55: Fenn's and Sabe's white hair caps;
     - 56: Asha's run skirt (the hem-momentum fix is still in progress);
     - 61: the Surge's dark mass in its arena;
     - 62: the flat Pemakar weir slabs;
     - 75: the near-black going-under u10;
     - 77: the Oruvel pen-split light streaks and grey box horizon;
     - 78: Ashcrown court's grey doorway void;
     - 79: the Ashcrown plume and the black hands;
     - 80: the Pemakar hillside;
     - 81: the Brine camp ground seam;
     - 84: the Coilspire speckle (low).
  2. **Partly fixed:** 17 (the eye's arcs), 24 (DockShore dark), 47 (the landing pier dark) and 82 (the Corrow storm, flood and lake dark around the figures).
  3. **Timing, not re-measured:**
     - row 74's in-fight stutter and the return on big37/38;
     - row 64 (fight-start visible frames over 50 ms);
     - row 90 (the wake entry's visible spike);
     - Haluna's ~12 s first entry.

     **The PC's monitor is off.** A 10 s fight renders ~410 frames instead of ~1450, even on big36, so every real-GPU timing is invalid until someone switches the screen on. keep_display_on.ps1 is running for 24 h but cannot power a monitor that's off.
  4. **Crashes and memory:** rows 68 and 88 were last seen on big36/37 (Haluna cold 1 of 3, one return probe segfault, two runaway runs over 5 GB). They need re-checking with the screen on.
- **Clean on big36–38:** 18, 34, 37, 38, 39, 46, 51, 59, 66, 76, 83 and 85, with every Act I hidden frame under 1 s (big36's walk). Stills: `docs/kb/qa/gpu/act1/pass7_big38/`.

**big37 re-measure (2026-10-31), integration @ f5305b15 (the row 85 clean shutdown, the jog counter-turn, Asha's skirt), RX 9070 XT, High 1440p.**
- **Act I sign-off: NOT YET.**
- **Row 74:** the big37 numbers (1.36–9.05 s) are INVALID. The display was off (see the row 74 correction). The real-GPU timings must be re-run with the screen on.
- **The jog:** the side view runs with a brisk stride and the arms low. The back and front segments stopped at the dock edge (the spawn faces the water, and the shore guard holds Rhen), so the counter-turn wasn't judged.
- **Asha's skirt (row 56):** not fixed in asha_clip_run.
- **The lighting rows:** the same as big36 (76 and 83 fixed; 75 and 82 partly; 77–81 and 84 open).
- **Row 85:** no log loop at exit; C: has **79 GB free**.
- **The big36 row walk:** 34, 37, 38, 39, 51 and 66 are fixed; 47 is partly fixed; 24 is still open.
- Stills: `docs/kb/qa/gpu/act1/pass7_big36/` (wr_* is the row walk) and `.../pass7_big37/` (with the jog filmstrip).

**Pass 7 verify (2026-10-31), big36 @ 1983de0a (integration-qa's mid-fight prewarm, one load family at a time, and the tracks' pass-7 fixes), RX 9070 XT, High 1440p.**
- **Act I sign-off: NOT YET.** Act I is not clean on the real GPU. What's still open:
  - art rows: 17 (partly), 54, 55, 56, 61, 62, 75 (u10), 77, 78, 79, 80, 81, 82 (partly) and 84;
  - visible frames over 50 ms: the fight starts (row 64) and the wake entry (row 90);
  - row 74's in-fight stutter;
  - the crash and memory problems (rows 68 and 88): Haluna cold segfaulted 1 of 3, and 2 of 5 return probes passed 5 GB;
  - Haluna's first entry still takes 11.5–12.1 s covered;
  - the walk-only rows (24, 37–39, 47, 51, 66), awaiting the row walk now running.
- **Fixed on big36:** rows 18, 46, 59, 76, 83 and 85. Row 74's return is 1.18–1.22 s.
- **Hitches:** every Act I hidden frame is under 1 s (the clean walk, 135 segments). Act II is under 1.2 s except Sunken Vey's 6.9 s (row 89).
- **Act II first look, now complete** (all 11 locations; Cloudloom, Ansedra and Sanctum read). The rows from the big33 look still hold.
- **Safety:** every Godot run is wrapped in `timeout` with its output capped. C: has 79 GB free. A memory guard alerts at 8 GB per process. Its automatic kill was refused by the auto-mode classifier, so any kill is done by hand, by PID.

**Pass 7 (2026-10-31), the Act I sign-off check: integration claude/new-session-mj8c3c @ 5695a69c (big33), RX 9070 XT, High 2560×1440.** Sheets are in `docs/kb/qa/gpu/act1/pass7/` (rows_*, beauty_* with index_beauty.txt, the jog filmstrip); the Act II first look is in `docs/kb/qa/gpu/act2/first_look/`.
- **Pass A: all 769 shots**, with no script errors and no material-null.
  - Rows: 58 and 63 fixed. 17 partly (my fix is in; arcs remain). 18 regressed (no harrier). 46, 54 partly. 55, 56, 59, 61, 62 still open.
  - The beauty passes were reviewed with spot-checks: rows 75–84. The day zones read beautifully. The weak spots are night and storm exposure (Oruvel storm, Corrow storm, the going-under cutscene), unfinished backdrops (the Ashcrown plume, the Pemakar hillside, the Oruvel horizon boxes) and a ground seam at the Brine camp.
  - Underway caustics: good (a moving web on the floor; a warm lantern pool in the arenas).
- **The human's playtest fixes, on the GPU:**
  - **Jog:** brisk, yes; organic, mostly. The legs and arms are good; the torso is slightly stiff.
  - **Battle return (row 74):** same-zone returns take 0.9–1.0 s. The cross-zone Drownbell → Haluna is 1.24–1.35 s on integration-qa's branch (target met), but with new in-fight stutter.
  - **Oruvel dock edges:** the water guard holds.
  - **Encounter spacing:** 31–44 s between fights in every zone.
  - **New Game into the Prologue:** 1.5 s (pass 3), not re-run.
- **Zone-entry hitches (ADR 0205, ≤ 2 s hidden): all pass.**
  - Clean walk: every hidden frame under 1.2 s (Ch5 1200, launch 1141).
  - Fresh-process probes:
    - Oruvel 497, Underway 516, Haluna 539, the causeway 256, the shrine 252, Brightwater 296;
    - the wake 609, Ashcrown 526, Brine Shoals 384, the Bell Galleries 888;
    - Tamsule 739–767, Coilspire 778–826, Pemakar 1131–1292.
  - **Haluna's first entry** (cold, no resident warm): 430–435 ms hidden, but a **12.2–12.5 s covered entry** (10.5 s with residents). The black wait is long, though no frame breaks the bar.
- **Crashes (row 68) are frequent on big33.** Fresh processes segfault with no log:
  - Pemakar 2 of 3; Haluna cold 1 of 3;
  - the Act I walk once, at the Prologue spawns; the jog 1 of 3; the Drownbell probe 1 of 2.

  On integration-qa's branch: 0 of 5.
- **Not completed:**
  - The Act I visual walk re-run: Claude Code stopped it for low system memory after 66 stills, so it wasn't restarted. Pass A and the budget walk cover the same zones.
  - Act II's Cloudloom, Sanctum and Lamp Archive stills, lost when the disk filled (row 85). Ansedra and Sanctum also produced no load numbers.

**Battle-UI pass (2026-10-30, the Lead's pillar-4 ask), integration @ 0347aa74 (big21), High 2560×1440.** One fight per chapter: the Oil Slug, the tideline, the causeway shore, the Drownbell, the Spar-wraith, the Cinder Matron, Moll, the Tidecup match (Ch7) and the Undertow's Reach. Stills every 3 s; the sheets are in `docs/kb/qa/gpu/act1/pass5/battle_ui/`.
- **Reads well:**
  - the timeline (who acts next, foes marked);
  - the "Physical, one foe · acts again in N turns" help line;
  - the boss telegraphs ("The Toll comes in 2 of its turns · Rim 0/3"; "Close the Hand comes on its next turn");
  - "HP unknown until Read";
  - the greyed Escape/Swap with their reasons;
  - the Tidecup's costs ("Costs 2 on the clock, 2 breath", odds, the miss outcome).
- **New rows:** 69 (a wrong plural), 70 (faint damage numbers), 71 (the Spar-wraith dark at night), 72 (the Reach fight's party unreadable in the rain), 73 (Attack's "R3" label with no legend).
- The walk starts each fight from its location, not the chapter, so most fights field only Rhen. That's a walk artefact, not a finding.

**Pass 5 (2026-10-30), the Lead's open-row list, integration claude/new-session-mj8c3c @ 7dc3ab41 (big20), RX 9070 XT, High 2560×1440.** Stills are in `docs/kb/qa/gpu/act1/pass5/` (`index.txt`). The method matches pass 4: 47 shots, the row walk, the clean budget walk, and fresh-process probes.
- **Fixed (12):** 23, 25, 43, 44, 45, 49, 50, 52, 53, 57, 60, and **67, the hitch regression.**
  - Every walk entry is under 1 s hidden.
  - Fresh Brine Shoals ran 5/5 with no hang, 321–336 ms hidden.
  - Corrow is 451 ms fresh.
- **Partly fixed (10):** 24, 37, 38, 39, 46, 47, 51, 54, 55, 58.
- **Still open:** 17 (fix in review, 12cf79cb), 21 (can't be reached by the walk), 34, 56, 61, 62, 63, 64 (visible spikes at fight starts), 66 (Ch4's camera in a wall).
- **Regressed:** 59. ch01_o10_gull now looks down on a roof of ring decals, with no gull in frame.
- **Hitches (ADR 0205):**
  - All 138 walk segments pass the 2 s hidden bar.
  - The clean walk's only over-budget segments are row 64's 5 fight starts (visible 73–119 ms).

**Pass 4 (2026-10-30), open rows only, integration claude/new-session-mj8c3c @ 2f544938 (big19), RX 9070 XT, High 2560×1440.** Stills are in `docs/kb/qa/gpu/act1/pass4/`.
- **Method:**
  - 46 manifest shots behind the open rows, with `--setup`.
  - A walk of only the segments behind the walk-only rows (`tools/gpu_bench/act1_walk_rows.json`).
  - The clean `--budget` walk, plus fresh-process swaps of the heavy zones.
- **Most of the tracks' row fixes are not in big19 yet.** Their branch commits aren't ancestors of 2f544938, so those rows still read open. A pass 5 after big20 picks them up. The pending fixes:
  - env-art: 2e2233c3, 6afe97f1, f06c190d;
  - env-art-b: 1a6934e3;
  - battle-presentation: 921e5fec;
  - act1-chapters: fc564326;
  - my row 17: 12cf79cb.
- **Fixed (2):** 31 (Asha's skirt) and 48 (the Ch4 first-playable card).
- **Partly fixed (5):**
  - 24: three of the four wake spawns read;
  - 37: Rhen is in frame;
  - 39: Toma fights in Ch4, but Ch9 still has no followers;
  - 49: the Pemakar town reads, the harbour foreground doesn't;
  - 51: the graves read in the shot, not under the field camera.
- **Still open:** 17 (fix in review), 21 (can't be reached by the walk), 23, 25, 34, 38, 43, 44, 45, 46, 47, 50, 52–63.
- **New rows:**
  - 66: Ch4's field camera starts inside a wall for about 10 s.
  - 67: the heavy zones' entries are back over 2 s on big19 (Ch6 2.56–2.86 s, Corrow 3.77 s fresh, and one Brine Shoals probe hang).
- **Hitches:**
  - 135 of 138 walk segments pass the 2 s hidden bar.
  - The clean walk's over-budget segments are the 3 entries in row 67 and the 6 fight starts in row 64 (visible frames over 50 ms after the fade).
  - Every spawn is within budget.

**Pass 3 (2026-10-30), lead/gate-big18 @ 37a90b4c with integration cf03aa8d merged (gpu/act1-qa-3 @ 84422d11), RX 9070 XT, High 2560×1440.** Contact sheets are in `docs/kb/qa/gpu/act1/pass3/`. `pass_a/index_*.txt` and `pass_b/index.txt` name every tile.
- **Pass A:** 618 of 619 manifest shots, at High ×2.667 with `--setup`, in 3464 s + 6 min.
  - The 619th shot, field_hud_over_haluna_wake, can't load its backdrop and hangs the capture (row 43).
  - `focus_*` covers the open rows and the tracks' PC-QUEUE shots; `pq_*` covers Pell, the Oil Slug and the storm figure; `rest_*` covers the other 488.
- **Pass B:** the walk, 141 segments and 452 stills in 1802 s.
  - act1_walk.json now includes ch04/haluna_wake, ch05/pemakar and ch09/corrow_night.
  - New Game now runs the Prologue straight into the beach cutscene, and the walk's spawn segments stay inside it (Prologue, Ch1 bell room, Ch2 beach). Those stills are walk artefacts, not findings.
- **Re-check of the open rows:**
  - **Fixed (14):** 4, 6, 12, 15, 18, 19, 26, 27, 28, 32, 33, 35, 36, 40.
  - **Still open:** 17, 21 (not reachable by the walk), 23 (bell room only), 24, 25 (f01 only), 31, 34, 37, 38, 39.
  - **New rows:** 43–63.
- **Record only:**
  - Test rigs nobody plays reuse greybox or capsule stand-ins: glimmer_*, underwater_below/_window/_waterline, field_lane_fixed, field_court_pan, field_causeway_dolly, save_shrine_field and the save menus over it, wildlife_stage, field_hero_party, npc_stage_field. So do the battle UI shots on the sandbox disc (battle_hud_preview, battle_choreo_*, battle_statuses, and so on).
  - The title shows "Development build (bootstrap)", the dev-build label.
  - The later-act arenas (Keth seep, Iskarra spire crown, Undertow cage and heart, lowlight engine hall, Ossa fen roots, the bridal barge, the drowned choir) keep their capsule enemies: row 30, paused by ADR 0041.
- **The tracks' PC-QUEUE, answered on the GPU:**
  - **characters, Pell (pell_front, pell_face, pell_storm_ch8):** under the warm key the fur reads as a smooth, flat brown at full figure, with no strand or sheen break-up. The face is a uniform warm orange that reads plastic. The whiskers and the crest feather read. The arms read thin. This is the same at any GPU level; it's the material, not lavapipe.
  - **creatures:**
    - The Oil Slug reads in battle (row 40).
    - The Corrow storm figure: the cyan rim glow blooms and the rain falls over it. The near shot reads as a smooth, featureless glowing mannequin (fine if that's the intent).
    - Freeing the storm figure is the source of hero-integration's `Parameter "material" is null` (row 44).
  - **creatures-b / battle-presentation:**
    - Moll fixed (rows 12, 35); the Reach fixed (row 36).
    - The Spar-wraith reads on the derelict deck at night (its spine glow). Its 45° turn can't be judged from 5-second stills; it needs a capture in motion (open).
  - **act1-chapters:** rows 34 and 39 are still open (see the rows).
  - **slice-polish:** row 18 fixed, row 32 fixed.
  - **ui-menus:** row 33 fixed (0 `_set_count` errors).
  - **hero-integration:**
    - The material-null error comes from the Corrow storm figure (creatures, row 44).
    - M1-QA-09's Asha grief re-check: still waiting on M1-RND-24 and M1-CHR-12 (both not done on big18).
  - **env-art:**
    - The ferry deck and the derelict at night read under the moon fill (row 4 fixed; the derelict D01 reads).
    - The bell room's haze is too thick: the room washes out orange behind a backlit Rhen (row 23).
    - The Ch4 wake's night lagoon glows strongly turquoise from the dock (haluna_wake DockEnd), brighter than the sky. Tone it down if the night should stay dark.
    - Rows 4 and 19 are fixed; 23, 24 and 25 are still open.
  - **env-art-b:** the camp fires' cost and RND-21/26 are in "Pass 3 costs" below.
  - **audio:** the real-speaker listening checks need the human; skipped.

**Status:** each row is `open` until the owner fixes it, then `fixed @ <sha>` once the PC has seen the fix on the GPU.

## Findings

| # | Where (shot or walk segment) | What reads wrong on the GPU | Owner | Status | Pass |
|---|---|---|---|---|---|
| 1 | iskarra_p01_plaza_dusk, iskarra_i02, iskarra_i03 (the Prologue) | Greybox: untextured white towers and cylinders, grey/green capsule stand-ins, a checkerboard plaza with teal shading, and nothing past the plaza edge (the haze shows through). | env-art | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 2 | slice_prologue_vigil_line | The vigil set is untextured: white columns and a flat floor behind dressed heroes. | env-art (set), slice-polish (shot) | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 3 | slice_verse_steps (ch03/first_verse) (**fixed in big14**: the textured shrine stage) | Untextured white pillars and steps under flat pastel light. | env-art | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 4 | ch04_ferry_deck | Nearly black at High; the deck is unreadable, and a large orange sphere in the foreground reads unlit. **pass 3: readable at High: moon-lit sail and deck lanterns, no orange sphere.** | env-art | fixed @ 84422d11 | pass A (2026-10-28, integration 048b0a7f) |
| 5 | ch06_brine_camp, ch06_brine_road | Flat untextured sand under a uniform haze; the camp's tent reads as a box. Nothing breaks up the ground. | env-art-b | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 6 | ch08_coilspire_hall | Very dark, with a noisy repeating brick texture. Thin green lines grid the walls (z-fighting or a stray decal). **pass 3: no green grid lines; the hall reads as red brick.** | env-art-b | fixed @ 84422d11 | pass A (2026-10-28, integration 048b0a7f) |
| 7 | ch08_corrow_arrival | The harbour mole is a flat untextured slab. | env-art-b | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 8 | ch08_corrow_stair, ch09_corrow_road | A grey capsule stand-in stands in frame (an NPC placeholder). | act1-chapters (placement), creatures (villager) | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 9 | ch09_corrow_strand | Nearly black at High; the strand is unreadable. | env-art-b | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 10 | battle_arena_wall_head, battle_ch08_stair_hold (**fixed in big14**: textured battlements and sea) | Greybox arena: untextured battlements, a flat floor and a grey wall. | env-art-b | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 11 | battle_boss_intro_reach | Greybox backdrop (untextured slabs). A hard-edged bright wedge of light cuts across the frame. | env-art-b; the wedge: rendering | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 12 | battle_arena_camp, battle_boss_intro_inquisitor (big14 adds Moll's model, moll_*: check in battle) | Inquisitor Hadric Moll is a grey capsule (a boss without a mesh). **pass 3: Moll modelled in his intro and arena_camp.** | creatures-b | fixed @ 84422d11 | pass A (2026-10-28, integration 048b0a7f) |
| 13 | battle_choreo_cast, _read, _toll | Ysolde is a tan capsule in battle. | characters | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 14 | battle_choreo_summon, _vowbound_rise (big14 adds creature_ilun: check in battle) | Ilun (Vowbound) is a teal dome stand-in. | creatures-b | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 15 | battle_arena_underway, _underway_tower | Hard-edged rectangular lit patches on the floor (a light or GI leak) in an otherwise dark arena. **pass 3: the floor patches are sand-covered slabs (texture), no hard light rectangles; none in live play either.** | env-art-b | fixed @ 84422d11 | pass A (2026-10-28, integration 048b0a7f) |
| 16 | battle_arena_terrace, _ash_terrace_lanternfall | Very dark at High; the party is barely lit against the terraces. | env-art-b | fixed @ 6466a6f5 | pass A (2026-10-28, integration 048b0a7f) |
| 17 | undertow_eye (also undertow_night) | Concentric streak rings at the eye's centre, and a grid-like dither over the cloud body. Possibly a still-frame TAA effect: to check in motion in pass B. **pass 3: the concentric streak rings at the eye's centre and a dot dither over the cloud body are still there (still frame).** **Fixed on gpu/row17-undertow-eye-rings @ 12cf79cb (M3-RND-29, in review).** The rings were the storm sea: its foam and throat-glow log-spirals winding to the axis, and specular off the funnel's interpolated normals. They're anti-aliased, the streaks redirected, and the normal is now computed per pixel; +0.02–0.10 ms. The dither is a frozen-clock still artefact: it reads smooth with the storm playing. **pass 4: unchanged on big19; the fix (gpu/row17-undertow-eye-rings @ 12cf79cb) is not merged yet.** **pass 5: unchanged on big20; the fix (12cf79cb) is not merged.** **pass 7: 12cf79cb is in. The dense fine rings at the axis are gone; the foam's surge-crest arcs and a few thin streaks remain at the eye (pc-gpu follow-up: fade the rings term inside the throat).** **big36: a few arcs remain at the eye.** | rendering (pc-gpu) | partly fixed @ 1983de0a | pass A (2026-10-28, integration 048b0a7f) |
| 18 | slice_causeway_harrier_view (**reframed in big14**) | No harrier in frame (the lavapipe baseline has none either): a framing or timing gap, not a GPU issue. **pass 3: a harrier is in the sky.** **pass 7: slice_causeway_harrier_view has no harrier in frame (slice-polish's recheck).** **big36: the harrier is in the sky.** | slice-polish | fixed @ 1983de0a | pass A (2026-10-28, integration 048b0a7f) |
| 19 | Prologue vigil terrace (New Game) | A hard-edged, bright-green rectangle in the water beside the terrace (also on lavapipe in iskarra_p01). **pass 3: no green rectangle in the water (iskarra_p01, the New Game Prologue).** | env-art | fixed @ 84422d11 | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 20 | Ch2 beach arrival (ch02_girl_on_the_beach) | Rhen is never in frame. Four lines are framed on empty sky (Rhen's view on his back?) with no face in it. **Fixed on lead/gate-ft-beach @ 93d0741e**: Rhen in the shallows, Asha kneeling beside him, both faces in frame. | slice-polish, hero-integration | fixed @ 6466a6f5 | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 21 | Haluna field start (after the beach; Village spawn too) | The field camera starts over the shallows with Rhen not on screen; Asha and Toma walk ahead, spaced. On ft-beach the camera starts below the waterline, looking up through the surface. **pass 3: New Game now runs the Prologue into the beach cutscene, and the walk's spawns stay inside it, so the field start after the beach was not reached. Needs a hand playthrough.** **pass 4: still not reachable by the walk.** **pass 5: still not reachable by the walk.** | hero-integration | open (not re-checkable) | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 22 | Scene changes: New Game→Prologue, Ch1, Ch2, the first fight | Hidden frames over ADR 0029's 1000 ms: 3025 / 1276 / 2017 / 1669 ms (warm), up to 4058 ms cold. Dwell hitches > 33 ms: 9 / 14 / 8. **pass 3, clean High run: New Game into the Prologue and the beach 382 ms worst hidden (1.55 s entry), Ch1 390, Ch2 388, the first fight 133 ms. Every visible frame is within 50 ms.** | tech / ui (loading) | fixed @ 84422d11 (ADR 0205) | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 23 | ch01_bell_room, ch01_kell_stall, ch01_scale_hull | The camera sits in or against a wall: Rhen's "Morning. Don't get up.", Mother Kell's and the Scale-Man's lines play over a wall with no speaker in frame. **pass 3: kell_stall and scale_hull fixed (the speaker is in frame). ch01_bell_room: the camera is behind Rhen and the room is washed out by a thick orange haze; no listener in frame (also the BellRoom1 spawn).** **pass 4: ch01_bell_room is unchanged: hazy, with Rhen from behind (act1-chapters' fc564326 is not in big19).** **pass 5: Rhen speaks in frame in the Underway room, and the haze is gone.** | act1-chapters (shot cameras), env-art | fixed @ 7dc3ab41 | pass A, big14's new shots (2026-10-28) |
| 24 | zone_wake_h02, zone_wake_h08, zone_wake_c01 | The camera is inside a black wall (h02) or pressed against a shell-covered surface (h08, c01). **pass 3: zone_wake_* shots are gone from the manifest. In the walk, the haluna_wake DockShore spawn puts the camera inside Rhen's body; FeastEdge, InkLamp and WallDawn look straight down, dark, with the party tiny.** **pass 4: FeastEdge, InkLamp and WallDawn now read, with the party visible. DockShore still puts the camera inside Rhen.** **pass 5: DockShore still puts the camera inside Rhen; the other wake spawns read.** **big36 row walk: the DockShore camera is still inside Rhen.** **big38: DockShore's camera is no longer inside Rhen; he is fully in frame, dark against the night sky.** | env-art | partly fixed @ 8b546285 | pass A, big14's new shots (2026-10-28) |
| 25 | brightwater_landing_f06 | The camera is pressed against a wooden wall; f01 is very dark. **pass 3: f06 fixed (deck and props read). f01 is still dark (lower half black); the Brightwater landing pier is a black slab at night in the walk (new row 47).** **pass 4: f01's lower half is still black; f06 is fine (env-art's 2e2233c3 is not in big19).** **pass 5: f01 is lit and its figures read.** | env-art | fixed @ 7dc3ab41 | pass A, big14's new shots (2026-10-28) |
| 26 | ch05_ashcrown_causeway, _forecourt, _tiers | Greybox: untextured grey stepped tiers and flat grey dunes under a flat sky (the smoke column is the only finished element). **pass 3: dressed dark-stone tiers and stairs.** | env-art-b | fixed @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 27 | ch08_coilspire_gate | The green grid lines on the brick walls (row 6) show here too. **pass 3: no green grid lines.** | env-art-b | fixed @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 28 | ch09_corrow_rocks | The rocks read as piles of black spheres against the wall. **pass 3: broken laterite, not spheres.** | env-art-b | fixed @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 29 | moll_face, moll_face_yield, moll_three_quarter | Moll's hair has white blotches through it (alpha or specular on the GPU). | characters | fixed @ 6466a6f5 | pass A, big14's new shots (2026-10-28) |
| 30 | battle_arena_drowned_choir_ring, _iskarra_spire_crown, _undertow_cage, _undertow_heart(_letting); battle_arena_keth_seep_terrace | Capsule stand-ins. If these arenas are later-act (paused under ADR 0041), this row is for the record only. | creatures-b | open | pass A, big14's new shots (2026-10-28) |
| 31 | Ch2 beach (ft-beach), newgame_13–17 | Asha's skirt balloons into a large blue mass over Rhen's chest and passes through him while she kneels. **pass 3: the skirt is still a blue balloon over Rhen's chest (slice_beach_h05/h06, New Game's beach in the walk).** **pass 4: Asha kneels beside Rhen with a flat skirt; nothing passes through him (h05/h06; characters 23ee1e74).** | characters | fixed @ 2f544938 | big14 playtest on lead/gate-ft-beach (2026-10-28) |
| 32 | Ch2 beach (ft-beach), newgame_28–29 | When Rhen stands, "Toma Okeru," and "To Asha. Who is very glad…" are framed on his waist and legs; no heads in frame. **pass 3: slice_beach_standing frames all three heads.** | slice-polish | fixed @ 84422d11 | big14 playtest on lead/gate-ft-beach (2026-10-28) |
| 33 | Every battle's result screen (pass B: 506 times in 122 segments) | `SCRIPT ERROR: Trying to cast a freed object` at `BattleResultPanel._set_count` (battle_result_panel.gd:266): the count-up runs on after the panel is freed when the result is left quickly (a fast player does the same). **pass 3: no `_set_count` SCRIPT ERROR in the 141-segment walk (0 lines).** | ui-menus | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 34 | ch06_ridge_skippers (BattleRequest with return ch06/brine_shoals) | The fight plays on the blank test stage against Lantern Eel, Reef Crab and Gull Harrier, not its arena (brine_shoals_afternoon) and Shoal Skippers. The encounter or its arena falls back to the battle sandbox. **pass 3: still the blank test stage against Lantern Eel, Reef Crab and Gull Harrier. Its first still shows the Inquisitor fight's name plate, which fits battle-presentation's double-submit diagnosis (M3-BPR-427, not on big18).** **pass 4: still the test stage.** **pass 5: still the test stage.** **big36: ridge_skippers is fought on the Brine Shoals arena against Shoal Skippers (Kerrid in the party).** | act1-chapters (encounters), env-art-b (arena) | fixed @ 1983de0a | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 35 | ch06_inquisitor (in battle) | Inquisitor Moll is still a grey capsule in his fight; moll_* has his model since big14, but the battle doesn't use it (row 12). **pass 3: Moll modelled in his live fight (spear, red pauldrons, the hound).** | creatures-b | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 36 | ch08 undertows_reach (in battle) | The Reach's arm fills most of the frame and passes over the party and the parapet for the whole fight. **pass 3: the arm stays behind the parapet in the rain; the party and HUD are clear.** | battle-presentation (camera), creatures-b | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 37 | ch03 spawns AfterHarrier, Encounter, BeforeHarrier (the causeway) | A follower stands between the camera and Rhen: Toma's shield fills the frame centre; at BeforeHarrier Rhen isn't in frame at all. **pass 3: at Encounter, Toma's shield is between the camera and Rhen; at AfterHarrier, his shield sits at frame centre.** **pass 4: Rhen is now in frame at AfterHarrier and Encounter; Toma's shield still fills one side.** **pass 5: Encounter is clean; at AfterHarrier, Toma's shield is still at frame right.** **big36: at AfterHarrier and Encounter the party walks in clear view, with no shield in the camera.** | hero-integration (party spawn and follow) | fixed @ 1983de0a | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 38 | coilspire spawns SpireBase, Tier2, Tier4 | The field camera is pressed against the spire wall with Rhen out of view: the camera doesn't pull in when the tower blocks it. **pass 3: SpireBase and Tier2 read from above. Tier4: the camera is inside Rhen's head. Encounter: the camera looks at open sea with no Rhen.** **pass 4: at Tier4 the camera is still in Rhen's head; Encounter still looks at open sea.** **pass 5: Tier4 is now a clear top view of Rhen; Encounter still looks at open sea.** **big36: Tier4 is a clear top view of Rhen; Encounter frames Rhen on the path.** | hero-integration (field camera), env-art-b (spawns) | fixed @ 1983de0a | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 39 | ch09 spawns RoadGate; Ch9 start | At RoadGate the camera sits behind the gate rocks with Rhen barely visible. In Ch9 Rhen walks alone though Asha and Toma are in the chapter's party (also no Toma in Ch4's field and battles). **pass 3: Ch9 Rhen walks alone on the strand and at RoadGate (the RoadGate camera is now clear of the rocks). Ch4: Toma is in Haluna's field at the chapter start, but the walk's Brightwater battles (started from the location) field only Rhen and Asha: re-check with the chapter's own encounter flow.** **pass 4: the Ch4 fights now field Rhen, Asha and Toma. In Ch9 Rhen is still alone at Strand and RoadGate.** **pass 5: Ch4 is fixed (Toma fights). In Ch9 Rhen is still alone at Strand and RoadGate.** **big36: in Ch9, Asha and Toma follow Rhen at Strand and at RoadGate.** | act1-chapters | fixed @ 1983de0a | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 40 | ch01 underway arenas (ch01_wickfry, ch01_oil_slug, in battle) | Row 15's hard rectangular lit floor patches show in live play. The Oil Slug is a small dark shape, hard to see against the floor. **pass 3: the slug is readable in battle (lit orange spines); no rectangles.** | env-art-b; creatures (the slug's read) | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 41 | Scene entries (pass B timings, not budget-grade) | Coilspire's entry has a 4324 ms hidden frame, the worst in Act I; field battles about 1.9 s. The budget run gives the per-zone table below. **pass 3: under ADR 0205's 2 s in the walk (worst Ch8 1817 ms). The fresh-process swap sweep leaves Corrow at 2151 and Pemakar at 2016 ms, just over.** | tech / ui (loading) | mostly fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 42 | Ch5 fresh entry (F8 chapter start) | A visible frame of 61.6 ms after the fade (ADR 0029: 50 ms), on top of a 6178 ms hidden frame. **pass 3: Ch5 entry 1772 ms hidden, 16.5 ms visible (walk); Pemakar's fresh swap 16.0 ms visible.** | tech / ui (loading) | fixed @ 84422d11 | budget check, fresh launches (2026-10-28) |
| 43 | field_hud_over_haluna_wake | The shot's backdrop `res://game/levels/_tests/haluna_wake_dressing/haluna_wake_dressed.tscn` does not exist on this tree. The load fails (`instantiate` on null, then `make_current` on null) and capture_preset hangs until the 25-min timeout. The gate will hang the same way. **pass 4: still hangs the capture (env-art's f06c190d is not in big19).** **pass 5: the shot captures the wake feast beach at night.** | ui-menus (shot), env-art (the wake's dressed scene) | fixed @ 7dc3ab41 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 44 | ch08 Corrow (ch08_corrow_arrival/_stair/_flood/_lake/_storm, crowd_zone_corrow, npc_corrow_storm_figure[_near], the ch08 walk after Bastion) | Freeing any Corrow scene prints 4 × `Parameter "material" is null` (material_casts_shadows, is_animated, get_instance_shader_parameters, update_dependency). Only scenes with the storm figure do it, and the storm-figure shots alone do it too: its mesh keeps a freed material (hero-integration's PC-QUEUE ask). **pass 4: still 4 × material null after ch08_corrow_arrival and the storm-figure shots.** **pass 5: 0 `material is null` in 47 shots, the storm-figure shots included.** | creatures (the storm figure, M3-HER-1142) | fixed @ 7dc3ab41 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 45 | ch05_ashcrown_crown, crowd_zone_ashcrown | The crown's bench and step faces carry a stretched, streaky texture (UV stretch); it reads low-quality next to the clean paving. **pass 4: unchanged.** **pass 5: the crown benches read as dark speckled stone.** | env-art-b | fixed @ 7dc3ab41 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 46 | moll_face, moll_face_yield | A dead-straight hard shadow edge runs down the face's midline (a cast shadow, likely the spear shaft, across the key). It reads as a split face in his close-ups. **pass 4: unchanged.** **pass 5: moll_face is clean; moll_face_yield has a hard diagonal shadow across the nose and cheek.** **pass 7: moll_face is clean; moll_face_yield still has a hard shadow across one side of the face.** **big36: moll_face_yield is clean, with no hard shadow.** | characters (look-dev light or spear placement) | fixed @ 1983de0a | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 47 | brightwater_ferry (F8 location, night), spawns Landing and FerryAft | The landing pier fills the field view as a pure-black slab (no moon fill reaches it). At FerryAft the camera is inside the cabin, pressed against Rhen. **pass 4: the landing pier is still a black slab; FerryAft is still against Rhen.** **pass 5: the landing pier is lit and reads; FerryAft's camera is still against Rhen.** **big36: the landing pier is lit by one lantern and still very dark; FerryAft's camera is close behind Rhen but readable.** **big38: the landing pier is still very dark (one lantern); FerryAft reads.** | env-art | partly fixed @ 8b546285 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 48 | ch04 (F8 chapter start) | The "End of the first playable" card plays before Ch4 opens in Haluna. **pass 4: Ch4 opens on the wake (Toma's line) with no first-playable card. Then see row 66.** | act1-chapters (flow), slice-polish | fixed @ 2f544938 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 49 | ch05 / pemakar (F8 start and location), spawns Harbour, HarbourRoad, Weir | Near-black frames at the night harbour: only the lamp blooms read; the party is unreadable. InnGate and FromAshcrown read. **pass 4: the Pemakar harbour shot shows the town and stair now, but the foreground and the Harbour, HarbourRoad and Weir spawns are still near-black.** **pass 5: the Harbour and HarbourRoad spawns read, with the party lit by the lamps. Note: the ch05_pemakar_harbour shot's foreground is still dark.** | env-art-b (night fill), act1-chapters (spawn cameras) | fixed @ 7dc3ab41 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 50 | ashcrown spawn Crown | Toma stands sunk to his chest in the crown's floor. **pass 4: Toma is still sunk at the Crown spawn.** **pass 5: no sunk Toma at the Crown spawn.** | hero-integration (party spawn), env-art-b | fixed @ 7dc3ab41 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 51 | ch09 / corrow_night strand (field camera) | The grave mounds read as soft, blurred orange rectangles (a low-resolution texture under the field camera). **pass 4: in ch09_corrow_strand the graves read as sand mounds. Under the field camera they are still soft orange rectangles.** **pass 5: the shot is fine; under the field camera the graves are still soft orange rectangles.** **big36: under the field camera the graves read as sand mounds with stakes.** | env-art-b | fixed @ 1983de0a | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 52 | brine_b05_barge_channel | The barge is untextured: a flat off-white hull, canopy and seat. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: the barge has wood and cloth.** | env-art-b | fixed @ 7dc3ab41 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 53 | battle_arena_coilspire_headland_path | The backdrop hill is coarse large flat facets in deep shadow behind the party. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: the headland hill is textured, with no large facets.** | env-art-b | fixed @ 7dc3ab41 | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 54 | sefir_front, _three_quarter, _back, _clip_raise_palm; sefir_face, _face_stylized | The gown reads as a rigid flat-shaded cylinder with no folds. In the face shots the hair is a flat translucent cap, with stretched ribbon strands floating off the head and shoulders. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: the gown is pleated now; the hair is still a cap with floating strands.** **pass 7: the gown is pleated; the hair is still translucent strands floating off the head.** **big36: Sefir's hair is still translucent strands.** **big38: unchanged.** | characters | still open @ 8b546285 | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 55 | villager_child/reed/netmender/kell/sabe/scaleman/garo/fenn/smith_face | Sparse spiky hair cards with bald scalp between them; on white-haired NPCs the hair reads as flakes. The child's and Sabe's brows are clumps of separate cards. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: Netmender, Kell, Scaleman, Garo, Smith and the child read as short hair. Fenn's and Sabe's white hair is still a cap with a flaky rim.** **pass 7: Fenn's and Sabe's white hair is still a cap with a flaky rim.** **big36: Fenn's and Sabe's white hair is still a cap.** **big38: unchanged.** | characters | still open @ 8b546285 | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 56 | asha_clip_run | In the run, the skirt and underskirt stay a rigid untextured cone with no legs showing, so she seems to slide (cf. M1-QA-09). **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: the run skirt is still a rigid cone.** **pass 7: the run skirt is still a rigid cone.** **big36: the run skirt is still a rigid cone.** **big37 (the skirt fix): asha_clip_run's skirt is still a stiff flared bell with no legs reading through; it does not move with her stride.** **big38 (the hem-momentum WIP, 10811699): asha_clip_run is still a stiff bell; the side and back panels' momentum can only be judged in motion.** | characters | still open @ 8b546285 | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 57 | battle_choreo_summon | Ilun spawns overlapping the eel and the gull; the gull's body passes through the eel. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: Ilun is clear of the gull and the eel.** | battle-presentation | fixed @ 7dc3ab41 | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 58 | ch01_hullgnaw_rises, ch01_net_pen, ch01_o07_name_board | Ch1 dialogue shots with nothing to see: hullgnaw_rises and net_pen are nearly black, with no Hullgnaw and no Child (the speaker) in frame. In o07 the camera is pressed against the hull, with no name board and no Skipper Sadi. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: the Hullgnaw and the Child are now in frame but dark; o07 is a readable two-boat frame (no Sadi in frame).** **pass 7: the Hullgnaw is lit in frame; the Child and two others read; o07 frames the name board.** | slice-polish (Ch1 staging, Lead 10-29), act1-chapters | fixed @ 5695a69c | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 59 | ch01_o10_gull | The gull is a crude faceted low-poly bird on a plain box block: it reads as a stand-in. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: ch01_o10_gull now looks straight down on a roof covered in ring decals, with no gull in frame.** **pass 7: the camera is back on the gull, but the gull is still a crude faceted wooden bird on a post.** **big36: a modelled white gull with a yellow beak, on the post.** | env-art | fixed @ 1983de0a | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 60 | slice_verse_hall | The camera is jammed between Rhen's shoulder and Toma's shield; Rhen speaks but is mostly out of frame. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: Rhen and Toma are framed in the doorway over the sea.** | slice-polish | fixed @ 7dc3ab41 | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 61 | battle_arena_seawall_stairhead_surge | The Surge's dark body fills half the frame against the camera; the boss doesn't read. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: the Surge's dark body still fills the left 40% of the frame.** **pass 7: unchanged.** **big36: the Surge's dark mass still fills the left of the frame.** **big38: unchanged.** | battle-presentation (camera), creatures-b | still open @ 8b546285 | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 62 | pemakar_p11_sea_cut_weir_day | The weir slabs read as flat, near-untextured grey boxes. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: the weir slabs are still flat grey.** **pass 7: unchanged.** **big36: the weir slabs are still flat grey.** **big38: unchanged.** | env-art-b | still open @ 8b546285 | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 63 | battle_boss_intro_matron | Stretched-UV streaks on the mouldings left of the boss, and a flat light-grey panel behind her shoulder. **pass 4: unchanged (the track fixes, e.g. env-art-b 1a6934e3, env-art 6afe97f1 and battle-presentation 921e5fec, are not in big19).** **pass 5: there's still a flat bright panel behind the Matron.** **pass 7: a lattice window, no flat panel.** | env-art-b | fixed @ 5695a69c | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 64 | Fight entries: ch02_tideline, ch03_causeway_shore, the Drownbell, ch04_bottle_hermit, ch05_cinder_matron, ch06_inquisitor | A visible frame over ADR 0042's 50 ms in the 60 frames after the fade lifts: 78.6 / 123.0 / 98.4 / 108.4 / 141.6 (swap sweep) / 55–70 ms. The boss fights also do it in a fresh process. Likely a first-draw compile in the intro VFX or the boss rig, after the fade has lifted. **pass 4: unchanged on big19 (tideline 77, causeway 120, Drownbell 95, Hermit 117, Moll 50 ms).** **pass 5: still there (tideline 73, causeway 119, Drownbell 107, Hermit 117, Moll 82 ms).** **Cause found on big21 @ 0347aa74 (slice_sweep --pipeline-trace now also prints process, render_cpu, render_gpu and new nodes):** the spike is on the first visible frame (f=0), with **zero pipeline compiles** and render CPU 0.3–0.6 ms / GPU 2.0–2.5 ms. The time is main-thread script: BattleBossIntro._begin() runs when the screen uncovers, and its _frame_boss() spends **339 ms (the Drownbell), 98 (the Hermit), 79 (the Matron) and 54 (Moll)**, each time choosing the hero shot. That is BattleBossHeroShot.search (M3-BPR-423): fill × fov × yaw × height candidates, up to 5×5×7 per height, each with triangle-mesh sight lines and foreground rays. The card takes 0.5 ms and the clip 0. (Local timing, not committed.) **Fix:** compute the hero pose while the fade still covers the screen (at the first turn, before the reveal), or spread the search over frames. The tideline and causeway fights no longer spike on big21 (their tip banners). The Drownbell got worse: 346–353 ms (98–107 on big18–20). | battle-presentation (BattleBossHeroShot / BattleBossIntro) | open, cause found | pass 3 hitches (2026-10-30, clean High walk + GPU swap sweep) |
| 65 | arena_camp (M3-RND-21), tamsule_bell_kit T01/T03 (M3-RND-26) | Over the 0.3 ms cost target at High 1440p. The smoke columns cost 0.31 ms for three (about 0.42 ms for four). The Tamsule drop costs 0.36–0.43 ms. The fires themselves are cheap (0.03 ms). | env-art-b | open | pass 3 costs (2026-10-30) |
| 66 | ch04 (F8 chapter start), after the opening cutscene | For about 10 s the field camera sits inside an orange wall (ch04_03/05 nearly fully dark), then settles above the lane. **pass 5: still about 10 s with the camera inside a wall (ch04_02/03/05).** **big36: Ch4 opens on the lit village lane; no wall.** | hero-integration (field camera), env-art | fixed @ 1983de0a | pass 4 (2026-10-30, integration @ 2f544938) |
| 67 | Heavy zone entries on big19: Ch6 Brine Shoals, Corrow, Ch7 | **Over ADR 0205's 2 s again (a regression from big18).** Clean walk: Ch6 2557 ms hidden (big18 1653), Ch7 1567 (936), Ch8 1915. Fresh-process GPU swap: Brine Shoals 2857 ms hidden with a 4.5 s entry, and one of two runs printed no stats within 600 s (a hang). Corrow 3769 ms hidden with a 5.2 s entry (big18 2151). **pass 5 on big20: every walk entry is under 1 s (Ch5 950, Pemakar 917, Coilspire 488, Ch6 295, Ch8 414). Fresh-process swaps: Brine Shoals 5/5 with no hang, 321–336 ms hidden (instantiate 2398 ms, prewarm_wait_frames 416, a 6.1–6.4 s covered entry); Corrow 451/453 ms; Tamsule 450; Coilspire 542. claude/ui @ 329e7bce was not needed, so not measured.** **Re-probe on big21 (integration @ 0347aa74, which includes ui-menus' 329e7bce):** fresh Brine Shoals 5/5 with no hang, 240–248 ms hidden, though the covered entries lengthen to 8.1–8.4 s (6.1–6.4 on big20). Corrow 375/377 ms (entries 8.3–8.5 s); Tamsule 444; Coilspire 518. Walk ×2: Ch6 254–262, Ch7 412, the Bell Galleries 420–447, Ch8 344–348, Coilspire 496–499. The first of three walks crashed on the Ch6 entry: row 68. | tech / ui-menus (loading), env-art-b (ch06/ch08 weight) | fixed @ 7dc3ab41 | pass 4 hitches (2026-10-30, integration @ 2f544938) |
| 68 | Ch6 (Brine Shoals) entry in the hitch walk, big21 @ 0347aa74 | **A segfault (exit 139) in 1 of 3 walks**, right after the title, on the Ch6 entry, with no crash backtrace. Just before it come "Another resource is loaded from path ... (possible cyclic resource inclusion)" errors for reed_b.glb and reed_d.glb, two threaded loads of the same villager model. The 2 walks that completed print 10 of these lines each. It fits ui-menus' four-loads-in-flight change (329e7bce) loading one model twice; the Godot 4.6.3 threaded-load crash path. **pass 7:** on big33 the crash is more frequent. Fresh processes segfault at startup or on an entry with no log (stdout lost): the Act I walk at the Prologue spawns, the jog filmstrip (1 of 3), the swap probes for Tamsule and Coilspire, Haluna cold (2 of 3) and the Drownbell probe (1 of 2). On integration-qa's branch (one load family at a time): 0 segfaults in 5 Drownbell → Haluna runs. | ui-menus (ResidentLoads / scene_loads), creatures (reed variants share sub-resources?) | open | row 67 re-probe (2026-10-30, integration @ 0347aa74) |
| 69 | Battle help line (the Drownbell, Spar-wraith, Matron and Reach fights) | "Physical, one foe · Rhen acts again in **1 turns**": a wrong plural ("next" is used for 0). | ui-menus | open | battle-UI pass (2026-10-30, integration @ 0347aa74, High 1440p) |
| 70 | Damage numbers: ch02_tideline, ch08 undertows_reach (and other bright or rain arenas) | The party's damage numbers on foes are a faint translucent grey (115, 62, 203 over the beach sand; 132 in the Reach's rain). They barely read. Damage taken (red) and the dark Underway's white numbers read fine. | battle-presentation (damage numbers), ui-menus | open | battle-UI pass (2026-10-30, integration @ 0347aa74, High 1440p) |
| 71 | ch04_spar_wraith (the derelict deck at night) | At battle distance the Spar-Wraith is a black silhouette against the night sea; only its cyan spine glow reads. It's hard to see what is acting. | creatures-b (rim or emissive), env-art-b (the arena's night fill) | open | battle-UI pass (2026-10-30, integration @ 0347aa74, High 1440p) |
| 72 | ch08 undertows_reach | In the rain the party is tiny, dark figures at the frame's right and the boss is a dark mass. The heavy rain overlay hides the party's turns. | battle-presentation (camera), env-art-b (the arena light) | open | battle-UI pass (2026-10-30, integration @ 0347aa74, High 1440p) |
| 73 | The command menu (every fight) | Attack is labelled "R3" at the right, with no legend, where the other commands show a cost or a reason (Swell "Ballast", Escape 70%, Swap "No time"). Pillar 4: what does an action cost? | ui-menus | open | battle-UI pass (2026-10-30, integration @ 0347aa74, High 1440p) |
| 74 | Battle victory → field return, cross-zone: the Drownbell (ch03/shell_shrine) → ch02/haluna | **8.2–8.6 s of covered (black) screen** between Return and Haluna appearing. The worst hidden frame is 317 ms, so it passes ADR 0205's per-frame bar, but this is the human's "multi-second black screen". Same-zone returns take 0.88–1.04 s to the field with input live (causeway 0.88, Ch4 sail leeches 0.97, Ch6 flats crabs 1.01, Oruvel scuttlers 1.04). The scripted tideline takes 1.12 s to the field; input then waits on its story beat. Probe: tools/gpu_bench/battle_return_probe.tscn. **ReturnPark re-measure (integration @ 9317c6b6 merged with claude/hero-integration @ 74c732fc, ADR 0209; the probe now has --fight-s):** the Drownbell → Haluna return is **2.87–3.03 s** to the field (was 8.2–8.6), with a 2.51–2.67 s covered entry. The scene is parked (parked true, instantiate 0 ms); a 10 s or a 20 s fight gives the same time. The rest is the reveal waiting on the shader prewarm: **prewarm_wait_frames 175**. That's still over the 1.5 s black target. Next: warm Haluna's pipelines during the fight, or let a parked scene skip the prewarm hold. No `Parameter "t" is null` error in 4 runs. 1 of 4 runs segfaulted while the Drownbell fight was starting (after a 5.1 s shrine entry), with no backtrace; see row 68. **Re-measure on 6df68f05 + claude/hero-integration @ 56410bdf (mid-fight Haluna prewarm), 5 runs of a 10 s fight:** field visible with input live in **1.24–1.35 s** (4 of 5; the first run after import 2.2 s), covered entry 0.80–0.88 s, prewarm_wait_frames 0, parked. **The 1.5 s target is met.** No `Parameter "t" is null` error, **0 segfaults in 5**. **The cost moved into the fight:** each run has 2 frames over 50 ms (76–86 ms) and 4–5 over 33 ms during the Drownbell fight. The same fight on big33 without the prewarm: worst 7.5 ms, none over 33 ms. Spread the warm over more frames, or into the fight's idle moments (the intro card, enemy think time). **big36 (5 runs, 10 s fight): 3 returned in 1.18–1.22 s (parked, prewarm 0), each with 2 in-fight frames of 77–79 ms. 2 of 5 runs passed 5 GB of process memory during the Drownbell fight's start and were stopped by my guard: see row 88.** **big37 (5 runs, 10 s fight): run 1 segfaulted; the others took 2.62 / 5.03 / 9.05 / 1.36 s to the field (big36: 1.18–1.22 s). The fight's frames got worse: worst 125–148 ms, 3–4 frames over 50 ms; in run 4 only 561 frames in 10 s (big36 ~1450). There were no leftover processes, memory was at 43% and CPU at 1% between runs, so the variance is in the build.** **CORRECTION (2026-10-31, the GPU bisect): the "big37 regression" was the machine, not the code.** A same-session control of big36 @ 1983de0a, the build that gave 1.18–1.22 s earlier, now gives 10.2 / 1.7 / 9.6 s with 418–486 fight frames. That's the same as big37 with row 85 (8cb73872), the storm material (f6c23ed1) or the jog (b15dc909) reverted: 1.3–13.5 s, 401–542 frames. The PC's keep-display-on had expired that morning, and with the monitor off the Vulkan present stalls (pc-gpu.md: "The monitor must stay physically ON"). It's restarted for 24 h; re-measure with the screen on. The valid numbers are big36's 1.18–1.22 s. | integration-qa (the cross-zone return: Haluna's load is not resident from the shrine) | fixed (return) @ 1983de0a; big37 to re-measure with the display on | pass 7 playtest checks (2026-10-30, integration @ 5695a69c = big33) |
| 75 | ch01_going_under_u10, ch01_going_under_u11 | The going-under cutscene frames are near-black (u10: 83% of pixels under 20/255, only a hull highlight and motes) and murky green (u11). The player can't tell what they're looking at. **big36: u11 is readable (a pale seabed); u10 is still near-black.** **big37: unchanged.** **big38: unchanged.** | slice-polish | still open @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 76 | zone_oruvel_storm_o16, zone_oruvel_storm_o12 | The storm deck is too dark to read: o16 has a mean of 32/255, and the pen water and nets merge into one dark mass. o12 is borderline. They need ambient or lightning fill. **big36: the storm deck is lit and the figures read.** **big37: still fixed.** | env-art | fixed @ f5305b15 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 77 | oruvel_o17_pen_split | Straight pale light streaks cut across the open water, and the horizon is a row of plain grey box buildings (greybox). **big36: unchanged (the straight light streaks and the grey box horizon).** **big37: unchanged.** **big38: unchanged.** | env-art | still open @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 78 | ch05_ashcrown_court | The open doorway shows a flat untextured grey void with no exterior backdrop. The brazier figure is crushed against the black pillars. **big36: the doorway still shows a flat grey void.** **big37: unchanged.** **big38: unchanged.** | env-art-b | still open @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 79 | ashcrown_a10_plume_from_the_rim, ashcrown_a01_approach | The ash plume reads as a solid lumpy clay mesh, not smoke. a10's foreground mound is a flat untextured slope; a01's giant hands are flat unlit black cut-outs. **big36: unchanged.** **big37: unchanged.** **big38: unchanged.** | env-art-b | still open @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 80 | pemakar_p04_harbour_day | The hillside behind the village is one flat brown surface, almost untextured, under flat light: the upper half reads unfinished. **big36: unchanged.** **big37: unchanged.** **big38: unchanged.** | env-art-b | still open @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 81 | ch06_brine_camp | A lighter ground plane ends in a straight hard edge across the mud flat behind the tent (a seam). **big36: unchanged.** **big37: unchanged.** **big38: unchanged.** | env-art-b | still open @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 82 | ch08_corrow_storm, ch08_corrow_flood, ch08_corrow_lake | Storm frames crushed to black: corrow_storm has 59% of pixels under 20/255, with the watcher heads pure silhouettes. corrow_flood's figures are black on a bright wall. corrow_lake is muddy, with a flat roof plane filling the foreground. They need rim or fill light. **big36: corrow_storm's watcher heads are now rim-lit; corrow_lake and corrow_flood are still dark, with figures in silhouette.** **big37: the Corrow storm, flood and lake frames are still dark around the figures.** **big38: unchanged (the Corrow storm, flood and lake are still dark around the figures).** | env-art-b, act1-chapters (corrow_lake's camera) | partly fixed @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 83 | ch01_bell_room | Still a heavy yellow-green haze over a flat wall (since row 23 was fixed, the haze changed colour but stays dense). **big36: the haze is gone, and Rhen is lit facing the camera.** **big37: still fixed.** | env-art | fixed @ f5305b15 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 84 | ch08_coilspire_gate, crowd_zone_corrow (low) | Up close, the torch-lit laterite's speckle reads as blocky low-resolution splotches. **big36: unchanged (low).** **big37: unchanged.** **big38: unchanged.** | env-art-b | still open @ 8b546285 | pass 7 beauty-pass lighting (2026-10-30, 5695a69c, High 1440p; reviewed and spot-checked) |
| 85 | Shutdown of a slice_sweep budget walk (big33) | After the walk finished, the process looped `Parameter "material" is null` at material_set_shader. Its log reached **59 GB and filled the C: drive** (the Act II stills that followed failed to write). The process also held 6.3 GB. Likely the same freed-material path as row 44, now in a loop at exit. **big36: no `material is null` loop at exit (0 lines in the budget walk's log).** | hero-integration / tech (shutdown order), creatures (the storm figure's material) | fixed @ 1983de0a | pass 7 (2026-10-31, big33 @ 5695a69c) |
| 86 | Act II first look: Ansedra Lacquer Court (dusk), Keth Pass spawns, Ossa Fen, Lamp Archive | The Lacquer Court's party are near-black silhouettes in a deep orange hall, and its Barge spawn is a dark box. Keth Pass's Encounter/FromQuellan spawns put the camera against a flat wall; RamArena's puts it inside Rhen. Ossa Fen is a flat dark mud plane with stark white water-edge cut-outs. Lamp Archive's Door spawn looks down on a plain grey slab (greybox?). Lowlight has a jagged white floor decal. (First look, 8 of 11 locations.) | env-art / env-art-b (Act II zones), act1-chapters (spawn cameras) | open | pass 7 (2026-10-31, big33 @ 5695a69c) |
| 87 | Act II hitches: Quellan fight and five spawns | Every Act II hidden frame is under 1 s (worst Keth Pass 579, Ossa Fen 570). Visible frames over 50 ms: the Quellan Avalanche Ram fight 176; spawns Sunken Vey Landing 72, Lowlight Gate 96, Keth Pass PassFoot 102, Lamp Archive Door 53, Ansedra CourtEntry 53. | battle-presentation (Quellan, likely row 64's hero search), tech | open | pass 7 (2026-10-31, big33 @ 5695a69c) |
| 88 | Process memory on big36 (the Drownbell fight's start, long walks) | 2 of 5 Drownbell → Haluna probes passed 5 GB of private memory at the fight's start, after only two scene loads (the 3 that completed peaked lower). The Act I budget walk plateaus at 5.8–7.0 GB of private memory while video memory stays at ~2.6 GB (big18: under 4 GB). A 16 GB machine is near its limit; the system reaped one run at critical memory (pass 7). Fresh processes still segfault: Haluna cold 1 of 3 (row 68). | integration-qa / tech (ReturnPark and ResidentLoads memory) | open | pass 7 verify (2026-10-31, big36 @ 1983de0a) |
| 89 | Sunken Vey (Act II Ch11) entry | A 6890 ms hidden frame on big36 (big33: 293 ms), over ADR 0205's 2 s. | tech / env-art-b (Act II) | open | pass 7 verify (2026-10-31, big36 @ 1983de0a) |
| 90 | haluna_wake entry (budget walk) | A 149 ms visible frame after the fade (ADR 0042: 50 ms). New on big33/big36. | tech (loading), env-art | open | pass 7 verify (2026-10-31, big36 @ 1983de0a) |

## Pass 3 hitches (2026-10-30, ADR 0205: hidden ≤ 2 s, visible ≤ 50 ms), High 2560×1440

**Clean walk:** `--budget` with no stills, on 84422d11. The per-zone rows are `act1_big18:*` in `docs/kb/qa/gpu/perf_baseline.csv`. The Lead asked for a quick confirm, so Low and Ultra were not run.
- **Every hidden frame passes the 2 s bar.** The six worst:

| Zone | Worst hidden frame |
|---|---|
| Ch8 | 1817 ms |
| Ch5 | 1772 ms |
| Pemakar | 1723 ms |
| Ch6 | 1653 ms |
| Ch9 | 1476 ms |
| Corrow-night | 1286 ms |

  Everything else is under 1 s; launch is 827 ms behind the boot card.
- **All 100 spawn segments are within budget.**
- **Visible frames over 50 ms**, all in fights, in the 60 frames after the fade:
  - the tideline (the first fight), 78.6 ms;
  - the causeway shore, 123.0 ms;
  - the Drownbell, 98.4 ms;
  - the Bottle Hermit, 108.4 ms;
  - Moll, 55.0 ms.

  Pass B, with stills, gave the same five, so the stills aren't the cause. **New row 64** (owner battle-presentation / tech).

**Fresh-process swap sweep:** `tools/loading/act1_swap_sweep.py`, run windowed on the GPU: ResidentLoads on, residents warmed, a cold process per target.
- Every change is covered by the fade.
- **Hidden frames over 2 s:** Corrow 2151 ms and Pemakar 2016 ms. Brine Shoals is 1933, Corrow-night 1808, Tamsule 1237, the Bell Galleries 1222 and Coilspire 1101; every other zone is under 1 s.
- **Field battles:** 366–739 ms hidden; entries 0.97–1.37 s.
- **Visible frames over 50 ms**, at the boss fights: the Cinder Matron 141.6 ms, the Bottle Hermit 121.4 ms, Moll 69.9 ms. The Hullgnaw is just under, at 47.7 ms.

**The PC-QUEUE timings:**
- **New Game to the beach:** 1.55 s, with a worst hidden frame of 382 ms (lavapipe's 15 s of black doesn't happen on the GPU).
- **The ShaderPrewarm boot:** 823 ms worst frame behind the boot card, a 2.9 s reveal wait, and 15.9 ms worst visible frame.
- **The Shell Shrine's cold first frame:** 217 ms hidden (fresh process).

## Pass 3 costs (env-art-b's PC-QUEUE), RX 9070 XT, High 2560×1440

Measured by difference with gpu_bench's new `--hide=<glob>`, which hides runtime-built dressing by name: GPU median over 600 frames, two runs each.
- **The camp fires (alpha-blended flame_tongue):**
  - arena_camp, 20 fire nodes: 2.59 → 2.56 ms, so **0.03 ms**. Cheap.
  - The ch06 Brine Shoals zone (Cameras/Camp): within its ±0.2 ms run-to-run noise, so not resolvable.
- **M3-RND-21, the smoke columns:** arena_camp's 3 SmokeColumns cost **0.31 ms** (2.59 → 2.28), so about 0.42 ms for four. **That's over the 0.3 ms target** at the arena's camera. The ch06 zone names its columns differently, so it wasn't isolated there.
- **M3-RND-26, the Tamsule drop:** **0.36 ms** at T01 (2.69 → 2.33) and **0.43 ms** at T03 (2.55 → 2.13). **That's over 0.3 ms.**

Both are filed as row 65 (env-art-b).

## Frame-time budget per zone (ADR 0029/0037, the walk with --budget)

The run (2026-10-28) is a warm, budget-only walk on lead/gate-ft-beach: High 2560×1440, dwell 4 s, nothing else on the box. **Every scene entry and every battle start is OVER ADR 0029's 1000 ms hidden-frame budget**. The overrun grows through the act, from ~1.1–1.3 s (Ch1) and ~1.8–2.2 s (Ch3) to **4.1–4.5 s from Ch5 on**. **It is scene weight, not accumulation.** A fresh launch straight into each chapter is slower than the walk, which had warm caches: Ch5 6178 ms, Ch8 6445 ms, Ch2 1973 ms hidden. Ch5's fresh entry also has a 61.6 ms visible frame (> 50 ms). **Every visible frame is within 50 ms**: no hitch shows after the fade lifts. GPU time stays far under 16.7 ms everywhere (the RX 9070 XT has headroom at High 1440p). Rows 22 and 41 track this (owner tech / ui, loading).

| Segment | gpu med / p99 ms | frame p99 / max ms | hitches > 33 ms | hidden max ms | visible max ms | Budget |
|---|---|---|---|---|---|---|
| launch | 0.07 / 0.13 | 2.8 / 5.6 | 0 | 460.6 | 2.8 | ok |
| title | 0.07 / 0.13 | 3.3 / 6.2 | 0 | 80.3 | 3.2 | ok (505 MB video) |
| prologue | 1.74 / 3.55 | 5.1 / 2053.6 | 10 | 2957.1 | 10.8 | OVER (1876 MB video) |
| ch01 | 2.11 / 2.30 | 3.0 / 7.6 | 0 | 1225.2 | 6.7 | OVER (1195 MB video) |
| ch01_b_ch01_wickfry | 2.56 / 2.76 | 4.8 / 18.6 | 0 | 1217.6 | 15.3 | OVER (1263 MB video) |
| ch01_b_ch01_oil_slug | 2.49 / 2.69 | 3.2 / 9.4 | 0 | 1131.4 | 13.8 | OVER (1264 MB video) |
| oruvel | 2.16 / 2.35 | 3.8 / 7.9 | 0 | 1310.0 | 9.0 | OVER (1368 MB video) |
| oruvel_b_ch01_scuttlers | 2.54 / 2.77 | 3.3 / 10.2 | 0 | 1186.1 | 13.0 | OVER (1209 MB video) |
| oruvel_b_ch01_hullgnaw | 2.56 / 2.78 | 3.3 / 10.6 | 0 | 1169.7 | 15.0 | OVER (1211 MB video) |
| ch02 | 3.30 / 3.74 | 8.2 / 38.9 | 2 | 1925.8 | 9.9 | OVER (1661 MB video) |
| ch02_b_ch02_tideline | 2.07 / 2.32 | 2.8 / 10.0 | 0 | 1313.9 | 14.8 | OVER (1211 MB video) |
| ch03 | 2.34 / 2.52 | 3.4 / 5.0 | 0 | 1805.6 | 8.8 | OVER (1404 MB video) |
| ch03_b_ch03_causeway_shore | 2.68 / 2.90 | 3.4 / 11.3 | 0 | 1909.6 | 14.5 | OVER (1402 MB video) |
| shell_shrine | 2.61 / 2.77 | 3.4 / 4.0 | 0 | 1541.1 | 6.9 | OVER (1610 MB video) |
| shell_shrine_b_drownbell | 2.47 / 2.75 | 3.3 / 11.1 | 0 | 2240.8 | 21.8 | OVER (1422 MB video) |
| first_verse | 1.63 / 1.80 | 2.4 / 33.5 | 1 | 1207.1 | 5.5 | OVER (1428 MB video) |
| ch04 | 0.04 / 2.81 | 4.7 / 1900.8 | 14 | 2885.7 | 9.8 | OVER (1848 MB video) |
| brightwater_ferry | 2.17 / 2.34 | 4.2 / 8.3 | 0 | 3065.3 | 8.3 | OVER (1752 MB video) |
| brightwater_ferry_b_ch04_sail_leeches | 2.42 / 2.68 | 3.2 / 12.7 | 0 | 1421.9 | 18.8 | OVER (1224 MB video) |
| brightwater_ferry_b_ch04_bottle_hermit | 2.35 / 2.60 | 3.1 / 13.8 | 0 | 1387.1 | 13.9 | OVER (1227 MB video) |
| brightwater_ferry_b_ch04_spar_wraith | 2.39 / 2.56 | 3.1 / 9.6 | 0 | 1465.9 | 17.4 | OVER (1228 MB video) |
| ch05 | 2.15 / 2.81 | 14.0 / 26.6 | 0 | 4497.8 | 16.0 | OVER (1954 MB video) |
| ashcrown | 1.93 / 2.10 | 4.2 / 6.1 | 0 | 3301.3 | 6.8 | OVER (1892 MB video) |
| ashcrown_b_ch05_stair_tortoises | 2.57 / 2.81 | 3.3 / 12.9 | 0 | 2152.2 | 16.1 | OVER (1461 MB video) |
| ashcrown_b_ch05_cinder_matron | 2.56 / 2.74 | 3.3 / 9.8 | 0 | 2120.3 | 26.7 | OVER (1461 MB video) |
| ch06 | 2.17 / 2.34 | 6.4 / 9.3 | 0 | 4484.3 | 9.6 | OVER (2238 MB video) |
| ch06_b_ch06_ridge_skippers | 1.03 / 1.27 | 2.5 / 1200.5 | 2 | 1976.9 | 21.6 | OVER (1492 MB video) |
| ch06_b_ch06_inquisitor | 2.37 / 2.60 | 3.1 / 9.7 | 0 | 2062.4 | 15.5 | OVER (1454 MB video) |
| ch07 | 2.28 / 2.64 | 6.1 / 13.4 | 0 | 4241.0 | 10.0 | OVER (2182 MB video) |
| tamsule_bell_galleries | 2.26 / 2.44 | 5.0 / 8.0 | 0 | 4084.9 | 11.4 | OVER (2180 MB video) |
| tidecup_match | 0.05 / 0.09 | 0.9 / 10.0 | 0 | 58.3 | 2.5 | ok (1079 MB video) |
| ch08 | 1.70 / 2.04 | 7.9 / 20.0 | 0 | 4465.3 | 8.6 | OVER (2169 MB video) |
| ch08_b_ch08_headland_gulls | 2.12 / 2.33 | 2.8 / 10.4 | 0 | 2003.5 | 14.1 | OVER (1459 MB video) |
| ch08_b_ch08_stair_hold_1 | 2.10 / 2.40 | 2.9 / 10.6 | 0 | 1986.3 | 15.2 | OVER (1455 MB video) |
| ch08_b_undertows_reach | 1.92 / 2.27 | 2.7 / 10.1 | 0 | 1994.9 | 14.7 | OVER (1457 MB video) |
| coilspire | 1.92 / 2.10 | 3.7 / 7.2 | 0 | 4312.7 | 12.3 | OVER (1932 MB video) |
| ch09 | 2.57 / 3.08 | 9.9 / 38.8 | 1 | 4158.3 | 16.8 | OVER (2195 MB video) |

Spawn segments (85, every spawn of every zone): all within budget; worst GPU p99 3.63 ms, worst visible frame 27.0 ms, 3 dwell hitches over 33 ms in all.
