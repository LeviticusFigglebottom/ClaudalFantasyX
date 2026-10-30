# The Wakefin (`wakefin`), Ch15 boss

**Where:** the open sea at night, aboard the drifting bridal barge with no lamp (act_outline Ch15: "an
Undertow-spawn that followed the first wake out of Ansedra's lagoon"). Fought in the dark, by sea-glow.

## The idea

Undertow-spawn drawn by the first wake in four hundred years. It is a long, black, sail-finned fish: a real
sailfish's shape, its dorsal fin a tall blade that cuts the water and stands 2.2 m above it. In the dark it is
mostly that fin, and the sea-glow it stirs runs along its flanks like a lit seam. When it rises to strike, the
body shows: wet lacquer black, the wounds along the spine.

The one exaggeration: **the fin**. A sailfish's dorsal sail, grown into a blade that can cut a barge's rail.

## Silhouette

- Most of the fight: the fin alone, a tall swept blade circling the barge, with a bright sea-glow wake.
- On the attack: the whole fish breaches alongside, 6 m long, the bill first.
- Nothing else in the game is a fin in the water: it reads at once, even in the dark.

## Palette

Body and fin `lacquer_black` to `abyss_navy`, clearcoat-wet; fin membrane `deep_teal_shadow` where the sea-glow
lights it from below; the wake and flank seam `sea_glow` (VFX and emission); wounds along the spine `spawn_wound`.
The scene has no other light (pillar 4: the timeline and the sea-glow still say who acts next).

## Battle read and clips

- **At battle distance:** a black blade with a glowing wake, circling.
- `idle`: it circles at the barge's edge (the fin cuts and turns), surfacing a little on each pass.
- `attack` (the cut): it breaches along the rail and the fin sweeps across the deck; contact at 0.8 s of 1.6 s.
  The telegraph is the sound and the sea-glow brightening along its path.
- `cast` (the dive): the fin goes under, the water goes dark, then a ring of sea-glow marks where it comes up.
- `hit`: the fin jerks and the body rolls; peak near 0.1 s.
- `ko`: it rolls belly-up and drifts away from the barge, the wake fading.

Budget ≤ 14k triangles. Rig: a spine chain of 10, the bill, the dorsal fin (3 bones, so it folds and flares),
pectorals, tail lobes.

## Review shots (M3-CRE-635)

- `creature_wakefin`: the battle read, the creature stage's opaque floor at the waterline, so the blade alone.
- `creature_wakefin_body`: the same stage with `show_floor = false`, seen from high on its flank (`flank_high`):
  the whole fish under its waterline, for reviewing the body, the seam and the wounds.

The eight spine wounds are open seams (M3-CRE-635): longer (0.24 to 0.54 m), three section rows wide, wandering
across the rows like a tear, their lips raised and faintly lit. They lie at the waterline, so in battle they show
when it breaches.

## As built (M4-CRB-004, the Act II move pass; ADR 0041 §3)

**Budget:** 11,128 triangles (≤ 14k; the torn tip's 56 are their own mesh), 25 bones, 24 clips. GLB 2.3 MB.

**Rig.** `breach` is the new root, at the surface under the body's centre: the fish's travel across the water (the
intro's long pass, a strike's lean toward the barge, the close circle's stand-off, the KO's drift) runs on it, and the
body's rise, dive and roll run on `root` under it. `blade_tip` (child of `fin_2`) carries the blade above the ragged
tear line (y ≈ 1.74), so the ram can tear the tip off. Anchors, unweighted: `vfx_wound` (the third spine wound, on
`spine_2`), `vfx_core` (mid-body, `spine_3`), `vfx_phase` (the blade's base, `fin_0`); creatures.json `vfx_anchors`
names the first two.

**Mesh.** The blade's first row is wet with the sea-glow it stirs (the seam slot, fading a row up), so in the dark the
blade reads as a black fin with a lit cut where it meets the water; the flank seam and the wounds glow through the
water. The tip above the tear is its own mesh, `BladeTip`, hidden after `phase_close`. No new material slot.

**Staging (needs battle-presentation).** The clips are authored for the fish staged in the water off the barge's far
beam toward the bow, at (−5.0, −0.6, −6.5) and `stand_in.yaw_deg` 90 (build_wakefin `STAGE_POS`, `STAGE_YAW`): broadside
to the battle camera (its flat faces the camera, never edge-on), about 16 m off, inside the frame, the bill toward the
party along the hull. There the idle stands 2.4 m off the hull and the close circle 1.25 m; the ram touches it (0.06 m);
over the barge every vertex stays 0.3 m above the rail and deck (`tools/tests/test_wakefin.py` skins every clip of the
GLB there against the barge's mesh). Two staging facts for M4-A2P-062: the arena's `BossAnchor` (−10, −0.6, −1.5) is
outside the battle camera's frame (42° off its axis; the half-width is 33.5°) and puts the bill into the bow, and the
battle today seats a boss on enemy slot 0, which is on the deck. The fish should be seated at the staging above (or the
anchor moved there), and its strikes should not travel (`travel: none`): each clip carries its own reach.

**Clips** (every clip starts and ends on its phase's idle first frame; the wide circle's on `idle`, the close
circle's on `idle_close`; `ready` and `ready_close` are loops entered by the row's blend, as Act I's are):

| Clip | Length | Contact | What moves |
|---|---|---|---|
| `idle` | 4.0 s loop | — | it circles: banks and turns, a swimming wave down the spine, the blade leaning and curling |
| `idle_b` | 1.6 s | — | the blade dips and folds back under a swell, then rises and flares |
| `ready` | 1.6 s loop | — | it rides higher, turns its blade's flat toward the party and stands it tall |
| `intro` | 3.0 s | — | the blade rises out of flat water 4 m back down its line, turns away, then comes in on one long banking pass |
| `attack` (Fin Cut) | 1.6 s | 0.8 | wind-up 0–0.55: the blade folds back low, body coiled away, tail cocked; then it drives up out of the water alongside, rolling so the blade sweeps across toward the deck; falls back on its side |
| `dive` (Sound Dive) | 2.6 s | 1.0 | 0–0.5: head up, blade stood tall (the telegraph); it sinks till only the blade's top cuts the water and glides there (1.0–2.0, the blade stays in view: evasive, never gone), then rises |
| `rise_strike` (Wakefin Rise) | 1.8 s | 0.85 | 0–0.7: it sinks to the blade's top and slides in toward the barge's side; bursts straight up, bill first, 4.3 m high, then topples away from the barge |
| `wake_wash` | 1.6 s | 0.75 | 0–0.6: turns hard away, tail lobes high out of the water and cocked; whips the tail across and slaps it down |
| `cast` | 2.0 s | 1.5 | the generic magical fallback (the old dive-and-rise) |
| `hit`, `hit_b` | 0.5 s | peak 0.1 | the blade jerks over, the body rolls away; `hit_b` (authored) snaps the blade back and rolls it toward the barge, shoved under |
| `phase_close` | 2.0 s | 0.85 | turns in and surges at the barge, rolls its blade away and slams its flank into the hull; the tip tears off and is flung out into the far water; it rebounds into the tight circle |
| `idle_close` | 4.0 s loop | — | the tight circle: 1.2 m nearer the barge, banking harder, the blade raised and torn |
| `bill_strike_close` (Bill Strike) | 1.4 s | 0.7 | 0–0.55: rears beside the bow, bill raised high; stabs it down and in, drops back |
| `ko` | 3.2 s | — | it jerks once, the blade flops flat, it rolls belly-up to the surface and drifts 1 m out from the barge |
| `*_close` | as above | as above | `attack`, `cast`, `dive`, `rise_strike`, `wake_wash`, `hit`, `hit_b`, `ready`, `ko` from the close circle |

**Clip map for combat** (skills are combat's; creatures.json has no `clip_by_skill` until the skills exist in
skills.json; the `contact` times are already in the row):

| Skill id (proposed) | Clip | Contact (s) | In `close_circle` |
|---|---|---|---|
| `fin_cut` | `attack` | 0.8 | `attack_close`, 0.8 |
| `sound_dive` | `dive` | 1.0 (it is under) | `dive_close`, 1.0 |
| `wakefin_rise` | `rise_strike` | 0.85 | `rise_strike_close`, 0.85 |
| `wake_wash` | `wake_wash` | 0.75 | `wake_wash_close`, 0.75 |
| `bill_strike` | `bill_strike_close` | 0.7 | (phase 2 only) |
| phase `close_circle` | `phase_close` (`idle_close`, hides `BladeTip`) | 0.85 (the ram) | — |

**Viewed (self-rendered, llvmpipe):** `creature_wakefin` and `creature_wakefin_body` (the blade's sea-glow cut now
reads low on the blade; otherwise as before), and every clip at five beats on the bridal barge at night from the battle
camera and from a close camera on the deck. At 16 m the blade reads as a fin in black water; the breaches (Fin Cut,
Wakefin Rise, Bill Strike) clear the far rail against the water, their seams and wounds lit; the dive leaves a blade
top in view; the torn tip shows a ragged top after the ram. Not judged: the wake and the ring of sea-glow (VFX,
M4-A2P-058/062) and the seam brightening (rendering).
