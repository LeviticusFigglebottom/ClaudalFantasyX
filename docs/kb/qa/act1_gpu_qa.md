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

**Status:** each row is `open` until the owner fixes it, then `fixed @ <sha>` once the PC has seen the fix on the GPU.

## Findings

| # | Where (shot or walk segment) | What reads wrong on the GPU | Owner | Status | Pass |
|---|---|---|---|---|---|
| 1 | iskarra_p01_plaza_dusk, iskarra_i02, iskarra_i03 (the Prologue) | Greybox: untextured white towers and cylinders, grey/green capsule stand-ins, a checkerboard plaza with teal shading, and nothing past the plaza edge (the haze shows through). | env-art | open | pass A (2026-10-28, integration 048b0a7f) |
| 2 | slice_prologue_vigil_line | The vigil set is untextured: white columns and a flat floor behind dressed heroes. | env-art (set), slice-polish (shot) | open | pass A (2026-10-28, integration 048b0a7f) |
| 3 | slice_verse_steps (ch03/first_verse) (**fixed in big14**: the textured shrine stage) | Untextured white pillars and steps under flat pastel light. | env-art | open | pass A (2026-10-28, integration 048b0a7f) |
| 4 | ch04_ferry_deck | Nearly black at High; the deck is unreadable, and a large orange sphere in the foreground reads unlit. | env-art | open | pass A (2026-10-28, integration 048b0a7f) |
| 5 | ch06_brine_camp, ch06_brine_road | Flat untextured sand under a uniform haze; the camp's tent reads as a box. Nothing breaks up the ground. | env-art-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 6 | ch08_coilspire_hall | Very dark, with a noisy repeating brick texture. Thin green lines grid the walls (z-fighting or a stray decal). | env-art-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 7 | ch08_corrow_arrival | The harbour mole is a flat untextured slab. | env-art-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 8 | ch08_corrow_stair, ch09_corrow_road | A grey capsule stand-in stands in frame (an NPC placeholder). | act1-chapters (placement), creatures (villager) | open | pass A (2026-10-28, integration 048b0a7f) |
| 9 | ch09_corrow_strand | Nearly black at High; the strand is unreadable. | env-art-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 10 | battle_arena_wall_head, battle_ch08_stair_hold (**fixed in big14**: textured battlements and sea) | Greybox arena: untextured battlements, a flat floor and a grey wall. | env-art-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 11 | battle_boss_intro_reach | Greybox backdrop (untextured slabs). A hard-edged bright wedge of light cuts across the frame. | env-art-b; the wedge: rendering | open | pass A (2026-10-28, integration 048b0a7f) |
| 12 | battle_arena_camp, battle_boss_intro_inquisitor (big14 adds Moll's model, moll_*: check in battle) | Inquisitor Hadric Moll is a grey capsule (a boss without a mesh). | creatures-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 13 | battle_choreo_cast, _read, _toll | Ysolde is a tan capsule in battle. | characters | open | pass A (2026-10-28, integration 048b0a7f) |
| 14 | battle_choreo_summon, _vowbound_rise (big14 adds creature_ilun: check in battle) | Ilun (Vowbound) is a teal dome stand-in. | creatures-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 15 | battle_arena_underway, _underway_tower | Hard-edged rectangular lit patches on the floor (a light or GI leak) in an otherwise dark arena. | env-art-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 16 | battle_arena_terrace, _ash_terrace_lanternfall | Very dark at High; the party is barely lit against the terraces. | env-art-b | open | pass A (2026-10-28, integration 048b0a7f) |
| 17 | undertow_eye (also undertow_night) | Concentric streak rings at the eye's centre, and a grid-like dither over the cloud body. Possibly a still-frame TAA effect: to check in motion in pass B. | rendering (pc-gpu) | open | pass A (2026-10-28, integration 048b0a7f) |
| 18 | slice_causeway_harrier_view (**reframed in big14**) | No harrier in frame (the lavapipe baseline has none either): a framing or timing gap, not a GPU issue. | slice-polish | open | pass A (2026-10-28, integration 048b0a7f) |
| 19 | Prologue vigil terrace (New Game) | A hard-edged, bright-green rectangle in the water beside the terrace (also on lavapipe in iskarra_p01). | env-art | open | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 20 | Ch2 beach arrival (ch02_girl_on_the_beach) | Rhen is never in frame. Four lines are framed on empty sky (Rhen's view on his back?) with no face in it. | slice-polish, hero-integration | open | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 21 | Haluna field start (after the beach; Village spawn too) | The field camera starts over the shallows with Rhen not on screen; Asha and Toma walk ahead, spaced. | hero-integration | open | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 22 | Scene changes: New Game→Prologue, Ch1, Ch2, the first fight | Hidden frames over ADR 0029's 1000 ms: 3025 / 1276 / 2017 / 1669 ms (warm), up to 4058 ms cold. Dwell hitches > 33 ms: 9 / 14 / 8. | rendering (prewarm), act1-chapters | open | big14 playtest (2026-10-28, gpu/gate-big14-shots) |
| 23 | ch01_bell_room, ch01_kell_stall, ch01_scale_hull | The camera sits in or against a wall: Rhen's "Morning. Don't get up.", Mother Kell's and the Scale-Man's lines play over a wall with no speaker in frame. | act1-chapters (shot cameras), env-art | open | pass A, big14's new shots (2026-10-28) |
| 24 | zone_wake_h02, zone_wake_h08, zone_wake_c01 | The camera is inside a black wall (h02) or pressed against a shell-covered surface (h08, c01). | env-art | open | pass A, big14's new shots (2026-10-28) |
| 25 | brightwater_landing_f06 | The camera is pressed against a wooden wall; f01 is very dark. | env-art | open | pass A, big14's new shots (2026-10-28) |
| 26 | ch05_ashcrown_causeway, _forecourt, _tiers | Greybox: untextured grey stepped tiers and flat grey dunes under a flat sky (the smoke column is the only finished element). | env-art-b | open | pass A, big14's new shots (2026-10-28) |
| 27 | ch08_coilspire_gate | The green grid lines on the brick walls (row 6) show here too. | env-art-b | open | pass A, big14's new shots (2026-10-28) |
| 28 | ch09_corrow_rocks | The rocks read as piles of black spheres against the wall. | env-art-b | open | pass A, big14's new shots (2026-10-28) |
| 29 | moll_face, moll_face_yield, moll_three_quarter | Moll's hair has white blotches through it (alpha or specular on the GPU). | characters | open | pass A, big14's new shots (2026-10-28) |
| 30 | battle_arena_drowned_choir_ring, _iskarra_spire_crown, _undertow_cage, _undertow_heart(_letting); battle_arena_keth_seep_terrace | Capsule stand-ins. If these arenas are later-act (paused under ADR 0041), this row is for the record only. | creatures-b | open | pass A, big14's new shots (2026-10-28) |

## Frame-time budget per zone (ADR 0029/0037, the walk with --budget)

| Segment | gpu med / p99 ms | frame p99 / max ms | hitches > 33 ms | hidden max ms | visible max ms | Budget |
|---|---|---|---|---|---|---|
