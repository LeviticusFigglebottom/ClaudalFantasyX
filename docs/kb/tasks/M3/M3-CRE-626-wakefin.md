---
id: M3-CRE-626
title: "Build the Wakefin (Act II, Ch15 boss) from its design sheet"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-a1b527f817c65c013 (creatures, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-620]
milestone: M3
request-from: lead
---
## Goal
The fourth Act II build from M3-CRE-620's sheets: the Wakefin (`wakefin`, docs/kb/art/creatures/act2/wakefin.md)
through the creature pipeline (docs/kb/art/creatures/pipeline.md). It is an Undertow-spawn sailfish whose dorsal sail
has grown into a tall swept blade. In battle it is mostly that blade, cutting the water. **Its first PC render is
pending:** this environment may not render (human directive), so the model was checked numerically from the GLB, and
its review shot has no baseline.

## Acceptance criteria
- [x] `assets_src/creatures/wakefin/build_wakefin.py` on the creature kit:
      - **Shape.** A long, laterally compressed fish, 6.0 m from the tail lobes' tips (z −3.0) to the bill's point
        (z +3.0). The body is 4.7 m from the peduncle to the snout, 0.8 m deep at most, and the bill is 1.1 m long.
        It has a tall swept dorsal blade (its root runs 2.75 m along the back, and its tip stands at y 2.21), a
        forked tail of two sickle lobes, sickle pectorals, thin pelvic rays, an anal fin and a small second dorsal.
      - **Colours.** The body is wet `lacquer_black`, lifted toward `abyss_navy` (with a little `deep_teal_shadow`, so
        it stays on the albedo floor) on the flanks and belly, with faint sailfish bars. The blade's membrane is
        `deep_teal_shadow` low down, where the sea-glow lights it from below, going black upward, and its rays are
        black.
      - **Lights.** A `sea_glow` seam runs along each flank: a band of the body's own quads in its own `seam` slot,
        emitting the sea's light, not glimmer, and tapering at its ends. Eight `spawn_wound` wounds run along the
        spine, alternating sides beside the ridge from behind the head to the tail. They are the weak points, on the
        `body` slot's emission mask, as slits with raised lips. Every colour is a palette.json swatch.
- [x] **The waterline (how the root height was chosen).** y 0 is the water's surface. The sheet wants the blade alone
      above the water, cutting it, so the waterline should fall where the blade meets the back. The spine axis (the
      root bone, the roll and pitch pivot at the body's centre, z 0.2) is set at y −0.38, the back's dorsal
      half-height under the blade's front root. In the rest pose, the front half of the blade's root then sits at y
      −0.059 to −0.016 (2 cm into the back). Over the idle's bob and bank it rides at −0.056 to +0.049, so the water
      cuts exactly where the blade leaves the back.
- [x] 11,128 triangles (budget 14k), 20 bones: root, head, `spine_0`..`spine_9` (head to tail), `bill`, `fin_0`..`fin_2`
      (the blade by height: each hinges along a line parallel to the back, so it leans, curls and flops without tearing
      its root, which is skinned to the spine under it), `pec_l`/`pec_r`, `tail_upper`/`tail_lower`. GLB 0.9 MB.
      Deterministic with `--threads 4`: `verify_blender_builds.py --job creature_wakefin` prints 5 identical.
- [x] Clips:
      - `idle` (4 s loop, in place): it circles. The body banks ±6° and yaws ±5° into the turn and back, and a
        swimming wave runs down the spine to the tail. The blade leans against the bank, its top curling a beat
        behind (the cut). It surfaces a little (+6 cm) twice a loop. There is no travel.
      - `attack` (1.6 s): the breach and the sweep. It sinks and coils (0.35 s), drives up nose-high (0.6 s), and at
        contact (0.8 s) the whole fish is out of the water, rolled 62° so the blade sweeps flat across the deck while
        the bill slashes. Then it falls back and settles.
      - `cast` (2.0 s): the dive. The head lifts and the blade flares (0.35 s). It noses down and goes under, the
        blade folding back, and the blade is fully under from about 0.9 s to 1.3 s (top at −0.69 m at 1.13 s). It
        rises steeply (1.5 s, the contact), the blade flaring, and settles.
      - `hit` (0.5 s): the blade jerks over and the body rolls away, peaking at 0.10 s.
      - `ko` (3.2 s): it jerks once, and the blade flops over flat. It rolls belly-up (165°) and floats up 0.4 m to
        lie at the surface, drifting 0.9 m away. No thrash.
      - `hit_b` and `idle_b`: the kit's variety clips.

      `--report` prints the same per-clip numbers without Blender (numpy skinning).
- [x] materials.json (`body` with the `spawn_wound` emission, `seam` with the `sea_glow` emission, `fin` with a rim
      sheen, `eye`) and write_materials.py; the Blender job; PROVENANCE rows (their own commit).
- [x] game/creatures/wakefin/wakefin_battle.tscn and the creatures.json row:
      - contacts: attack 0.8, cast 1.5 (it comes up under the target);
      - `ko_fade_sec` 1.2;
      - `stand_in.yaw_deg` 60 (three-quarter, so the 6 m body doesn't fill the lane side-on while the blade's swept
        profile still reads), with no hover: the model is authored with the water at y 0;
      - a `portrait` with yaw 60 and pitch 10, plus `rim_energy` 2.8 and `kick_energy` 1.8 like the other dark rows.

      No phases.
- [x] The import rule lists the folder, and the `.glb.import` runs the creatures post-import script.
- [x] tests/unit/test_creature_actor.gd checks that:
      - the cut and the dive play, and the cut's contact is 0.8 s;
      - it has no phases, and the rig has the sheet's bones;
      - the blade stands above 1.3 m in the idle and goes under the water at the dive's deepest second;
      - the KO ends belly-up, with every bone within 0.6 m of the surface.

      It was checked to fail with a 5 cm band (the flopped blade's bones lie at −0.36 to −0.08).
- [x] Shot `creature_wakefin` (three-quarter, idle) in tests/screenshots/shots.json, with its stage scene.
- [ ] **PC render pending:** no captures in the cloud environment (human directive). The PC renders `creature_wakefin`,
      a reviewer views it, and only then does its baseline go in.
- [ ] Encounter (not this task): an enemies.json row with `model` when the Ch15 encounter is designed.

## Numeric check (no render)
Measured from the exported GLB by evaluating every clip frame by frame: glTF node animation, joint matrices and
linear blend skinning. The numpy `--report` agrees to the millimetre. "Blade top" is the highest vertex skinned to a
`fin_*` bone.

| Clip | Length | Peak | Lowest..highest y over the clip | Blade top (min..max) | End of clip |
|---|---|---|---|---|---|
| rest | — | — | −1.245..2.212 | 2.21 | — |
| idle | 4.0 s | (loop) | −1.348..2.285 | 2.19..2.29 | loops to its start |
| attack | 1.6 s | 0.80 s (contact 0.8) | −1.435..2.742 | 1.12..2.74 | rest |
| cast | 2.0 s | 1.13 s (deepest) | −3.701..2.712 | −0.69 (1.13 s)..2.71 | rest |
| hit | 0.5 s | 0.10 s | −1.296..2.255 | 2.12..2.25 | rest |
| hit_b | 0.5 s | 0.10 s | −1.300..2.268 | 2.10..2.27 | rest |
| ko | 3.2 s | 3.20 s (end) | −1.277..2.212 | −0.04 (end)..2.21 | −0.458..0.787 |
| idle_b | 1.43 s | 0.80 s | −1.925..2.369 | 1.33..2.37 | rest |

- **Below y 0 by design:** the body hangs under the water in every clip but the attack's breach. The lowest rest
  point is the lower tail lobe's tip (−1.245). The cast's −3.70 is the bill at the bottom of the dive.
- **The KO ends at the surface.** The rolled body's back and the flopped blade's root are the lowest parts at −0.46.
  The blade lies flat out on the water and curls up to −0.04 at its tip. The belly, lobe and pectorals stand up to
  +0.79. The root rises 0.40 m (tools/tests' grounded-KO check: no sink).
- **The attack at contact:** the body's underside is clear of the water (the root at +1.15 m), and the blade sweeps
  flat out to the side.
- **Colours against palette.json.** The build's swatches are `lacquer_black` #1D1916, `abyss_navy` #061A2B,
  `deep_teal_shadow` #0E4A55, `sea_glow` #1C6B78, `spawn_wound` #3FE0C8 and `glimmer_held` #7FC6D9 (a 10% tint in
  the wounds' lips), all in palette.json, mixed or darkened. The slots' emission colours are `spawn_wound` (body)
  and `sea_glow` (seam).
  - Vertex albedo luminance (linear) is 0.0101..0.2252 against the floor (0.0101) and ceiling (0.8014). No vertex is
    below the floor; the darkest is `lacquer_black` itself.
  - The wound slits' albedo is `spawn_wound` × 0.65 (mean [40, 137, 123] on 41 vertices), and the seam is `sea_glow`
    on 332 vertices.

## Notes
- **The battle floor hides what is under y 0** only if the arena's floor or water plane is opaque. The sandbox floor
  is; the Ch15 barge arena needs a water surface at y 0 for the "mostly fin" read. Check on the PC render that the
  stage's floor cuts the body cleanly at the blade's root.
- The seam is a band of the body's quads, so it is about 6 cm tall and follows the section's rows, not a free curve.
  It sits a little above the lateral line, which is under water in the idle by the sheet ("when it rises to strike,
  the body shows").
- Not modelled, by the sheet: the sea-glow wake and the brightening along its path (the attack's telegraph), the
  dark water and the ring of sea-glow where it surfaces (the cast), the wake fading on the KO, and the
  `glimmer_held` motes the wounds shed. These are VFX; request them when the encounter exists.
- **For the first PC render:**
  - the blade's silhouette at battle distance (a swept black blade, not a shark's fin);
  - whether the low teal on the membrane reads as lit from below;
  - the portrait (yaw 60 with the dark rim and kick: the submerged body is in frame, since the portrait has no water);
  - the three-quarter shot's framing of a 6 m body.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
