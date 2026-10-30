# The flat-engine (`flat_engine`), Ch14 boss part

**Where:** the stern of Warden Malcor Venn's pursuit barge on Ansedra's still lagoon at night (act_outline Ch14).
In phase 1 the engine pulls the water flat and still round the party, so the timeline slows; Liss breaks it. The
Warden (a person) is the characters track's. This sheet is the machine on his barge.

## The idea

A bound Lit Age engine: a squat iron-and-brass drum on the barge's stern, half sunk through the deck into the
water, with a ring of long paddles held flat in the water like oars at rest. They are not rowing: they **press**,
fanning out on every side and laying the lagoon smooth. A salt-glass window on the drum shows its bound light,
steady (`glimmer_bound`, a construct, README rule 3). Its weak points are the paddle hinges, which glow
`spawn_wound` (ADR 0151: one small closed mark each).

The one exaggeration: **the paddles**. A real stern-mounted paddle drum, its paddles grown long and held flat,
smoothing water instead of moving it.

## Silhouette

- A 1.8 m drum on the stern deck, a short chimney with a bell-shaped cowl, and eight paddles 3 m long fanned on the
  water in a half ring astern and abeam (they lie at y 0, the water).
- **Broken:** the drum split along a seam, its window cracked dark, the paddles slack and fallen at odd angles.

## Palette

The drum `lacquer_black` iron with `brass` bands going `bronze_patina`; the window `salt_glass` with the bound light
behind it in `glimmer_bound`; the paddles `timber_weathered` darkened wet to the waterline; the hinges `spawn_wound`.
The lagoon at night is dark, so the window and hinges are its only lights.

## Battle read and clips

- **At battle distance:** a dark drum on the stern with a steady teal window, and a fan of paddles flat on the
  water.
- `idle`: the paddles press in a slow wave round the ring (a few degrees each); the window breathes very slightly.
- `cast` (the stilling): every paddle presses down together, and the window brightens and holds.
- `hit`: the drum jolts and one paddle kicks up (its peak near 0.1 s).
- `break` (the `broken` phase, M4-CRB-009): the seam splits, the window goes dark (the shader's emission is static,
  so the broken mesh swaps in on the clip's first frame), and the paddles fall slack. `ko` is the stop.
  *(Before M4-CRB-009 the `ko` was the break.)*
- No `attack`: it does not strike. The pipeline wants the clip, so `attack` is a copy of `cast`.

**Break part:** `whole` / `broken` meshes for CreatureActor `break_parts`, keyed to the charge skill that breaks it
(Liss's, once Ch14's combat kit names it; until then the creatures.json row lists no part).

Budget ≤ 8k triangles. Rig: drum, chimney, eight paddle hinges.

## As built: the final-quality move pass (M4-CRB-009, ADR 0041 §3, ADR 0205)

Audited from the battle camera on `bridal_barge_night` (the Ch14 lagoon arena doesn't exist yet). The engine stood on
the water 7 m beyond the enemy line, at the depth design §1 gives phase 1. I also audited it up close. Budget:
**7,620 triangles** (3,810 for each of `Engine` and `EngineBroken`, and only one shows at a time; ≤ 8k), 4,281 vertices,
16 bones (13 plus 3 anchors), 14 clips. The four materials are unchanged (`iron`, `window`, `hinge`, `timber`), so there
is no new `.tres`. The portrait is re-baked.

**Fixes (what read wrong from the battle camera):**
- **Stand-in yaw 90° → 20°** (creatures.json `stand_in`). At 90° the window faced the party and the battle camera saw the
  drum side-on as a black can, with no light and the seam edge-on. At 20° the window faces the camera (design §1: "faces
  the camera with its window"), the paddle fan opens toward the party, and the seam (az 25°) opens toward the camera.
- The lid read as one black disc from above. It now has a **brass ring plate** (vertex colour only, no triangles).
- The drum's seam faces are now **brass plating inside** (bright toward the middle, black iron at the wall), so the open
  split shows a raw brass face, not black on black.
- **The broken stance is a pose, not a baked mesh.** `Engine` and `EngineBroken` share one rest geometry. The broken
  mesh differs only in its lights: the window glass crazed and dark, the hinge marks out. Its split, toppled and slack
  shape comes from the rig: the `broken` phase's `break` clip ends on it and `idle_broken` holds it. So the swap on the
  break's first frame (the phase's `hide`/`show`) changes only the lights, and every broken clip moves the broken mesh
  correctly. The old baked mesh would have been posed twice by any clip.
- **The broken read at battle distance:** the only light goes out, the stack lies over 24° with its cowl, the halves
  stand 14° apart, the paddles are slewed off the fan (±4–12°), and two are jammed up off the water on snapped hinges
  (`paddle1` 26°, `paddle6` 34°). It reads as a dark, ragged wreck next to the running engine's steady teal eye and
  neat fan.

**Anchors (unweighted):** `vfx_wound` (the hinge mark of `paddle3`, the near hinge left of the window, on `paddle3`),
`vfx_core` (the window's centre, on `half_a`), and `vfx_phase` (the seam's face toward the party, at mid height, on
`drum`: the crack and the first ripple's cue). The row's `vfx_anchors` names `vfx_core` and `vfx_wound`.

**Clips.** Every whole clip starts and ends on the running idle's first frame. The broken hits start and end on
`idle_broken`'s first frame. `break` runs from the idle to the broken stance. The KOs start on their stance and end
free (then the fade). A test holds each of these to within 1 cm. Paddles are kept on the water by `grounding` in every
clip, and the drum's skirt is kept above the waterline in every clip.

| Clip | Length | Contact | What moves |
|---|---|---|---|
| `idle` | 6.0 s loop | — | running: a slow wave of presses round the ring (up to 5°), a drum throb, the cowl sways |
| `idle_b` | 1.6 s | — | the governor knocks twice: the drum jumps, the cowl rattles, the wave hitches |
| `intro` | 2.6 s | — | every paddle rises together to 20° (to 1.45 s), held; all slam flat at 1.95 s, the drum drops, the cowl jolts |
| `ready` | 1.4 s loop | — | the paddles held a hand off the water and trembling, the drum up |
| `cast` (flat_pulse) | 1.6 s | 0.8 | 0–0.7 s every paddle lifts to 16° and the drum rises and leans back; at 0.8 s all press flat; they hold, then return to the wave |
| `attack` | 1.6 s | 0.8 | a copy of `cast` (the pipeline wants the clip; it never strikes) |
| `hit`, `hit_b` | 0.7 s | peak 0.1 | the drum jolts, the cowl rocks, and one paddle (3, or 5 for `hit_b`) kicks up |
| `ko` | 2.4 s | — | the stop: the wave dies, the paddles sag flat, the drum shudders and settles listing, the stack leans |
| `break` | 2.8 s | 0.6 (the crack) | the window is already dark; the strike jolts the drum and kicks the near paddles; at 0.6 s the seam cracks, the halves fall apart (14°), the stack topples (24°), and the paddles go slack one by one while two jam up |
| `idle_broken` | 5.0 s loop | — | nothing runs: the slack paddles rock on the water, the jammed ones tremble, the stack creaks |
| `hit_broken`, `hit_b_broken` | 0.7 s | peak 0.1 | the split drum jolts, its halves rock open, the stack rattles, and a slack paddle (6, or 1) kicks |
| `ko_broken` | 2.4 s | — | a last shudder: the jammed paddles fall slack, the halves sag to 17°, the stack goes over to 34° |

**creatures.json (in):** `contact` `{attack 0.8, cast 0.8, break 0.6}`; `loop` `[idle, ready, idle_broken]`;
`vfx_anchors`; and the phase `broken`: `{"clip": "break", "idle": "idle_broken", "hide": ["Engine"], "show":
["EngineBroken"], "sec": 0, "clips": {"hit": "hit_broken", "hit_b": "hit_b_broken", "ready": "idle_broken", "ko":
"ko_broken"}}`. The broken engine has no action clip: once broken it stops pulsing (the design), so combat gives it no
turn.

**Clip map and break part for combat** (not in the row: `flat_pulse` and Liss's lent break skill, M4-A2P-023, aren't in
skills.json yet, and validate_creatures rejects unknown skills). When they land, paste:

```json
"clip_by_skill": {"flat_pulse": "cast"},
"break_parts": {"<liss_break_skill>": {"whole": ["Engine"], "broken": ["EngineBroken"]}}
```

| Skill id | Clip | Contact (s) | Broken stance |
|---|---|---|---|
| `flat_pulse` | `cast` | 0.8 | none (it stops) |
| Liss's lent break | `break` (via `enter_phase(&"broken")`) | 0.6 (the crack: ripple VFX at `vfx_phase`) | ends on `idle_broken` |

**How combat breaks it.** Liss's skill calls the actor's `enter_phase(&"broken")`. That plays `break`, swaps the
lights on the first frame, and idles on `idle_broken`. The `break_parts` row is optional bookkeeping
(`is_part_broken`). It swaps the same two meshes, so it is harmless alongside the phase. Used **alone**, without the
phase, it would show the dark window on a running, unsplit drum, so always enter the phase.

