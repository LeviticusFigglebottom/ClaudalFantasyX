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
| 17 | undertow_eye (also undertow_night) | Concentric streak rings at the eye's centre, and a grid-like dither over the cloud body. Possibly a still-frame TAA effect: to check in motion in pass B. **pass 3: the concentric streak rings at the eye's centre and a dot dither over the cloud body are still there (still frame).** | rendering (pc-gpu) | still open @ 84422d11 | pass A (2026-10-28, integration 048b0a7f) |
| 18 | slice_causeway_harrier_view (**reframed in big14**) | No harrier in frame (the lavapipe baseline has none either): a framing or timing gap, not a GPU issue. **pass 3: a harrier is in the sky.** | slice-polish | fixed @ 84422d11 | pass A (2026-10-28, integration 048b0a7f) |
| 19 | Prologue vigil terrace (New Game) | A hard-edged, bright-green rectangle in the water beside the terrace (also on lavapipe in iskarra_p01). **pass 3: no green rectangle in the water (iskarra_p01, the New Game Prologue).** | env-art | fixed @ 84422d11 | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 20 | Ch2 beach arrival (ch02_girl_on_the_beach) | Rhen is never in frame. Four lines are framed on empty sky (Rhen's view on his back?) with no face in it. **Fixed on lead/gate-ft-beach @ 93d0741e**: Rhen in the shallows, Asha kneeling beside him, both faces in frame. | slice-polish, hero-integration | fixed @ 6466a6f5 | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 21 | Haluna field start (after the beach; Village spawn too) | The field camera starts over the shallows with Rhen not on screen; Asha and Toma walk ahead, spaced. On ft-beach the camera starts below the waterline, looking up through the surface. **pass 3: New Game now runs the Prologue into the beach cutscene, and the walk's spawns stay inside it, so the field start after the beach was not reached. Needs a hand playthrough.** | hero-integration | open (not re-checkable) | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 22 | Scene changes: New Game→Prologue, Ch1, Ch2, the first fight | Hidden frames over ADR 0029's 1000 ms: 3025 / 1276 / 2017 / 1669 ms (warm), up to 4058 ms cold. Dwell hitches > 33 ms: 9 / 14 / 8. | tech / ui (loading) | open | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 23 | ch01_bell_room, ch01_kell_stall, ch01_scale_hull | The camera sits in or against a wall: Rhen's "Morning. Don't get up.", Mother Kell's and the Scale-Man's lines play over a wall with no speaker in frame. **pass 3: kell_stall and scale_hull fixed (the speaker is in frame). ch01_bell_room: the camera is behind Rhen and the room is washed out by a thick orange haze; no listener in frame (also the BellRoom1 spawn).** | act1-chapters (shot cameras), env-art | still open @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 24 | zone_wake_h02, zone_wake_h08, zone_wake_c01 | The camera is inside a black wall (h02) or pressed against a shell-covered surface (h08, c01). **pass 3: zone_wake_* shots are gone from the manifest. In the walk, the haluna_wake DockShore spawn puts the camera inside Rhen's body; FeastEdge, InkLamp and WallDawn look straight down, dark, with the party tiny.** | env-art | still open @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 25 | brightwater_landing_f06 | The camera is pressed against a wooden wall; f01 is very dark. **pass 3: f06 fixed (deck and props read). f01 is still dark (lower half black); the Brightwater landing pier is a black slab at night in the walk (new row 47).** | env-art | still open @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 26 | ch05_ashcrown_causeway, _forecourt, _tiers | Greybox: untextured grey stepped tiers and flat grey dunes under a flat sky (the smoke column is the only finished element). **pass 3: dressed dark-stone tiers and stairs.** | env-art-b | fixed @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 27 | ch08_coilspire_gate | The green grid lines on the brick walls (row 6) show here too. **pass 3: no green grid lines.** | env-art-b | fixed @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 28 | ch09_corrow_rocks | The rocks read as piles of black spheres against the wall. **pass 3: broken laterite, not spheres.** | env-art-b | fixed @ 84422d11 | pass A, big14's new shots (2026-10-28) |
| 29 | moll_face, moll_face_yield, moll_three_quarter | Moll's hair has white blotches through it (alpha or specular on the GPU). | characters | fixed @ 6466a6f5 | pass A, big14's new shots (2026-10-28) |
| 30 | battle_arena_drowned_choir_ring, _iskarra_spire_crown, _undertow_cage, _undertow_heart(_letting); battle_arena_keth_seep_terrace | Capsule stand-ins. If these arenas are later-act (paused under ADR 0041), this row is for the record only. | creatures-b | open | pass A, big14's new shots (2026-10-28) |
| 31 | Ch2 beach (ft-beach), newgame_13–17 | Asha's skirt balloons into a large blue mass over Rhen's chest and passes through him while she kneels. **pass 3: the skirt is still a blue balloon over Rhen's chest (slice_beach_h05/h06, New Game's beach in the walk).** | characters | still open @ 84422d11 | big14 playtest on lead/gate-ft-beach (2026-10-28) |
| 32 | Ch2 beach (ft-beach), newgame_28–29 | When Rhen stands, "Toma Okeru," and "To Asha. Who is very glad…" are framed on his waist and legs; no heads in frame. **pass 3: slice_beach_standing frames all three heads.** | slice-polish | fixed @ 84422d11 | big14 playtest on lead/gate-ft-beach (2026-10-28) |
| 33 | Every battle's result screen (pass B: 506 times in 122 segments) | `SCRIPT ERROR: Trying to cast a freed object` at `BattleResultPanel._set_count` (battle_result_panel.gd:266): the count-up runs on after the panel is freed when the result is left quickly (a fast player does the same). **pass 3: no `_set_count` SCRIPT ERROR in the 141-segment walk (0 lines).** | ui-menus | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 34 | ch06_ridge_skippers (BattleRequest with return ch06/brine_shoals) | The fight plays on the blank test stage against Lantern Eel, Reef Crab and Gull Harrier, not its arena (brine_shoals_afternoon) and Shoal Skippers. The encounter or its arena falls back to the battle sandbox. **pass 3: still the blank test stage against Lantern Eel, Reef Crab and Gull Harrier. Its first still shows the Inquisitor fight's name plate, which fits battle-presentation's double-submit diagnosis (M3-BPR-427, not on big18).** | act1-chapters (encounters), env-art-b (arena) | still open @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 35 | ch06_inquisitor (in battle) | Inquisitor Moll is still a grey capsule in his fight; moll_* has his model since big14, but the battle doesn't use it (row 12). **pass 3: Moll modelled in his live fight (spear, red pauldrons, the hound).** | creatures-b | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 36 | ch08 undertows_reach (in battle) | The Reach's arm fills most of the frame and passes over the party and the parapet for the whole fight. **pass 3: the arm stays behind the parapet in the rain; the party and HUD are clear.** | battle-presentation (camera), creatures-b | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 37 | ch03 spawns AfterHarrier, Encounter, BeforeHarrier (the causeway) | A follower stands between the camera and Rhen: Toma's shield fills the frame centre; at BeforeHarrier Rhen isn't in frame at all. **pass 3: at Encounter, Toma's shield is between the camera and Rhen; at AfterHarrier, his shield sits at frame centre.** | hero-integration (party spawn and follow) | still open @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 38 | coilspire spawns SpireBase, Tier2, Tier4 | The field camera is pressed against the spire wall with Rhen out of view: the camera doesn't pull in when the tower blocks it. **pass 3: SpireBase and Tier2 read from above. Tier4: the camera is inside Rhen's head. Encounter: the camera looks at open sea with no Rhen.** | hero-integration (field camera), env-art-b (spawns) | still open @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 39 | ch09 spawns RoadGate; Ch9 start | At RoadGate the camera sits behind the gate rocks with Rhen barely visible. In Ch9 Rhen walks alone though Asha and Toma are in the chapter's party (also no Toma in Ch4's field and battles). **pass 3: Ch9 Rhen walks alone on the strand and at RoadGate (the RoadGate camera is now clear of the rocks). Ch4: Toma is in Haluna's field at the chapter start, but the walk's Brightwater battles (started from the location) field only Rhen and Asha: re-check with the chapter's own encounter flow.** | act1-chapters | still open @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 40 | ch01 underway arenas (ch01_wickfry, ch01_oil_slug, in battle) | Row 15's hard rectangular lit floor patches show in live play. The Oil Slug is a small dark shape, hard to see against the floor. **pass 3: the slug is readable in battle (lit orange spines); no rectangles.** | env-art-b; creatures (the slug's read) | fixed @ 84422d11 | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 41 | Scene entries (pass B timings, not budget-grade) | Coilspire's entry has a 4324 ms hidden frame, the worst in Act I; field battles about 1.9 s. The budget run gives the per-zone table below. | tech / ui (loading) | open | pass B (2026-10-28, lead/gate-ft-beach @ 93d0741e) |
| 42 | Ch5 fresh entry (F8 chapter start) | A visible frame of 61.6 ms after the fade (ADR 0029: 50 ms), on top of a 6178 ms hidden frame. | tech / ui (loading) | open | budget check, fresh launches (2026-10-28) |
| 43 | field_hud_over_haluna_wake | The shot's backdrop `res://game/levels/_tests/haluna_wake_dressing/haluna_wake_dressed.tscn` does not exist on this tree. The load fails (`instantiate` on null, then `make_current` on null) and capture_preset hangs until the 25-min timeout. The gate will hang the same way. | ui-menus (shot), env-art (the wake's dressed scene) | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 44 | ch08 Corrow (ch08_corrow_arrival/_stair/_flood/_lake/_storm, crowd_zone_corrow, npc_corrow_storm_figure[_near], the ch08 walk after Bastion) | Freeing any Corrow scene prints 4 × `Parameter "material" is null` (material_casts_shadows, is_animated, get_instance_shader_parameters, update_dependency). Only scenes with the storm figure do it, and the storm-figure shots alone do it too: its mesh keeps a freed material (hero-integration's PC-QUEUE ask). | creatures (the storm figure, M3-HER-1142) | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 45 | ch05_ashcrown_crown, crowd_zone_ashcrown | The crown's bench and step faces carry a stretched, streaky texture (UV stretch); it reads low-quality next to the clean paving. | env-art-b | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 46 | moll_face, moll_face_yield | A dead-straight hard shadow edge runs down the face's midline (a cast shadow, likely the spear shaft, across the key). It reads as a split face in his close-ups. | characters (look-dev light or spear placement) | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 47 | brightwater_ferry (F8 location, night), spawns Landing and FerryAft | The landing pier fills the field view as a pure-black slab (no moon fill reaches it). At FerryAft the camera is inside the cabin, pressed against Rhen. | env-art | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 48 | ch04 (F8 chapter start) | The "End of the first playable" card plays before Ch4 opens in Haluna. | act1-chapters (flow), slice-polish | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 49 | ch05 / pemakar (F8 start and location), spawns Harbour, HarbourRoad, Weir | Near-black frames at the night harbour: only the lamp blooms read; the party is unreadable. InnGate and FromAshcrown read. | env-art-b (night fill), act1-chapters (spawn cameras) | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 50 | ashcrown spawn Crown | Toma stands sunk to his chest in the crown's floor. | hero-integration (party spawn), env-art-b | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 51 | ch09 / corrow_night strand (field camera) | The grave mounds read as soft, blurred orange rectangles (a low-resolution texture under the field camera). | env-art-b | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 52 | brine_b05_barge_channel | The barge is untextured: a flat off-white hull, canopy and seat. | env-art-b | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 53 | battle_arena_coilspire_headland_path | The backdrop hill is coarse large flat facets in deep shadow behind the party. | env-art-b | open | pass 3 (2026-10-30, big18 + integration @ 84422d11) |
| 54 | sefir_front, _three_quarter, _back, _clip_raise_palm; sefir_face, _face_stylized | The gown reads as a rigid flat-shaded cylinder with no folds. In the face shots the hair is a flat translucent cap, with stretched ribbon strands floating off the head and shoulders. | characters | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 55 | villager_child/reed/netmender/kell/sabe/scaleman/garo/fenn/smith_face | Sparse spiky hair cards with bald scalp between them; on white-haired NPCs the hair reads as flakes. The child's and Sabe's brows are clumps of separate cards. | characters | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 56 | asha_clip_run | In the run, the skirt and underskirt stay a rigid untextured cone with no legs showing, so she seems to slide (cf. M1-QA-09). | characters | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 57 | battle_choreo_summon | Ilun spawns overlapping the eel and the gull; the gull's body passes through the eel. | battle-presentation | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 58 | ch01_hullgnaw_rises, ch01_net_pen, ch01_o07_name_board | Ch1 dialogue shots with nothing to see: hullgnaw_rises and net_pen are nearly black, with no Hullgnaw and no Child (the speaker) in frame. In o07 the camera is pressed against the hull, with no name board and no Skipper Sadi. | slice-polish (Ch1 staging, Lead 10-29), act1-chapters | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 59 | ch01_o10_gull | The gull is a crude faceted low-poly bird on a plain box block: it reads as a stand-in. | env-art | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 60 | slice_verse_hall | The camera is jammed between Rhen's shoulder and Toma's shield; Rhen speaks but is mostly out of frame. | slice-polish | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 61 | battle_arena_seawall_stairhead_surge | The Surge's dark body fills half the frame against the camera; the boss doesn't read. | battle-presentation (camera), creatures-b | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 62 | pemakar_p11_sea_cut_weir_day | The weir slabs read as flat, near-untextured grey boxes. | env-art-b | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |
| 63 | battle_boss_intro_matron | Stretched-UV streaks on the mouldings left of the boss, and a flat light-grey panel behind her shoulder. | env-art-b | open | pass 3 A (2026-10-30, big18 + integration @ 84422d11; reviewed and spot-checked) |

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
