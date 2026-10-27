---
id: M3-CRE-632
title: "Ground every remaining creature's clips (the rest of the M3-CRE-631 sweep) and extend GroundedClipsTest to all"
role: character
status: review
owner_session: "worktree-agent-acecbace78996e4ba"
reviewer: art
depends_on: [M3-CRE-631]
milestone: M3
request-from: creatures
---
## Goal
M3-CRE-631 grounded the reef crab, tide crawler and slag tortoise families with `common/grounding.py` and added
`GroundedClipsTest` (every frame's lowest skinned vertex at or above −0.005 m). Its sweep measured the other shipped
creatures that still go under the floor (depths and the full list are in the M3-CRE-631 task file):
- **Grounded creatures:** scuttler −0.37, Cinder Matron −0.35, shoal skipper −0.32, raid hound −0.22, Drownbell −0.22.
- **Fliers, even with their hover:** ashwing −0.63, gull harrier and stormgull −0.28.
- **Possibly by design (check against their sheets first):** the Mangrove Drowner (roots in water), the Undertow's
  Reach (rises from the water), the spar-wraith, the flue moth.

## Acceptance criteria
- [x] Each grounded creature passes GroundedClipsTest (grounding.py where a planted foot is the fix; re-key where a
      clip's body motion is)
- [x] The fliers' clips stay above the floor with their `stand_in.hover` applied; extend the test to add the hover
- [x] The by-design ones get an explicit, commented allow-list entry citing their sheet, or are fixed
- [x] GroundedClipsTest covers every creature (less the allow-list)
- [ ] Blender verify identical; one PC render of the affected creature and battle shots, viewed and re-approved.
      **Verify done, the render is pending (PC).**

## What was done (worktree agent, 2026-10-27)
Measured by skinning every baked frame of every clip from the GLB (no render), a flier with its `stand_in.hover`
added. Every creature in creatures.json is now at or above −0.005 m in every clip, except six whose sheets put them
below the floor (the allow-list below). creature_kit.py's clip bake is untouched.

- **`common/grounding.py`** (backward compatible: the 8 M3-CRE-631 GLBs rebuild identical):
  - the root may be a limb (a lift of the whole body; `Poser.resolve` used the last bone's matrix for a parentless one);
  - a limb may turn about a weighted axis `(wx, wy, wz)` (a leg splayed round a body, the Drownbell's);
  - an optional fifth item limits a limb to some clips (e.g. `("ko",)`);
  - `mesh` may be a list (a body and its extra meshes: the Drownbell's rim, the spar-wraith's shroud and sheath);
  - fliers pass `floor=-HOVER`.
- **Grounded creatures** (each build now exports `export_clips(...)` through grounding.py; the limbs are commented in
  each build as `GROUNDED_LIMBS`):
  - **scuttler:** its curl (hit, KO) brought its ends down past the pivot: the feelers turn up, then the body lifts the
    least it takes (the arch rises over its ends, up to 0.33 m in the KO's roll-up).
  - **Cinder Matron:** the hem hoop sits on the floor (y 0.06, was 0.05: −1 cm at rest); the hands turn the ladle and
    tongs up where they'd go through the floor (the pour's wind-back, 39°; the KO's sag, 32–38°).
  - **shoal skipper:** the fin tips rest on the floor (`FIN_TIP_Y`); the tail rides up when the head lifts (cast, hit:
    `spine2`, up to 18.5°); the KO tucks the fin it lands on under its belly (`KO_FIN`) and lifts the least it takes
    for the roll's pivot (0.17 m).
  - **raid hound:** the paws sit on the floor (`PAW_Y`, was 1.4 cm under); the KO's forearms lie flat along the floor
    (`KO_FORE` −20°: keyed +60 they went 0.22 m through it); in the lunge's crouch the forelegs reach forward at the
    shoulder the least it takes (up to 42°).
  - **Drownbell:** each leg swings up about its own outward axis where the toll, the slam or the blow would press a foot
    through the floor (up to 28°); the rope's trailing end rides up; the KO lifts the bell 4.6 cm to lie on its rim.
  - **bottle hermit:** the KO's shins curl up (`KO_CURL`; keyed −50 they drove the tips 0.19 m down); legs and claw turn
    up where the slump would press them through; the glass lifts the least it takes in the KO.
  - **vein sparker:** the KO sinks onto its belly (`KO_DROP` 0.05, was 0.09) with the legs splayed out flat
    (`KO_SPLAY`, was keyed down into the floor).
  - **spawn polyp** (and the **wall polyp**, which now exports through `sp.export_clips`): the core's tucked foot sits
    flat on the floor (was 1.2 cm under); each tube straightens at its foot the least it takes for its mouth to come to
    rest on the floor in the KO (28–39°); the base never squashes under the floor.
  - **tower limpet:** the forward lean (`TILT` 8°) put the foot's front 7.5 cm under: the sole, lining and lip are
    flattened at y 0; the shell lifts where its clamp or tip would press the rim through the floor (it rocks on the rim);
    the foot no longer sinks 3 cm in the KO.
  - **glassfry:** each shrimp that lands in the KO lifts the least it takes to lie on the floor.
  - **lamp engine:** the KO's feet lift up to 6.5 mm where the 3° pitch pressed them into the bottom.
  - **oil slug:** the hit's offset was keyed on every spine bone, so it added up along the chain (9 cm into the floor):
    it is on the first bone only; the strike bends up at `spine3` the least it takes (5.8°).
  - **spar-wraith** (fixed, not by design: its sheet's KO "drops to the deck"): the spar feet stand on the deck
    (`SPAR_FOOT_Y`, was 2.5 cm under); the hub no longer rocks 0.8° in the idle (it swung the deck-fast shrouds and the
    planted spars 2 cm through the deck); in the KO, `phase_drop` and the deck clips the head turns up and the body lifts
    the least it takes to lie on the deck (the KO dropped it 1.6 m, 0.9 m through).
  - **flue moth** (fixed, not by design: its sheet's KO "tips onto its side"): `open_wings` lifted with the wrong sign
    (its docstring says "lift"; it tipped the open wings 7–11 cm into the floor); the KO curls the legs in under it
    (`KO_CURL`), lays the right pair along the floor (`KO_WING`) and lifts the least it takes for the roll's pivot
    (0.16 m); a planted foot turns up as it rears or recoils.
- **Fliers** (`HOVER` in each build mirrors creatures.json; the KO still comes down by its hover,
  test_a_ko_ends_on_the_ground passes):
  - **ashwing:** the KO's wings closed downward (−55) and went 0.63 m through the floor once it rolled; they now close
    up over its back (`KO_WINGS`), the under wing and antenna fold up the least it takes, the body comes to rest on them
    (a lift of 1 cm).
  - **gull harrier** (and the **stormgull**, through `base.export_clips`): the twine hank lies along the ground after
    the fall; the neck holds the head off the floor as it lands breast first, the body settles onto it; in `hit_b` (the
    mirrored, heavier recoil) the flailing wing turns up at the shoulder (31°).
  - **squall wing:** the same for its neck, body and `hit_b` wing.
  - The gallery ray (−0.004 in the KO), cord moth, sail leech and fen leech were already clean with their hover.
- **Allow-list** (`GroundedClipsTest.ALLOW`, each commented with its sheet):
  - **hullgnaw:** rises out of the water between the raft's planks; its KO slides back down between them (act1/hullgnaw.md).
  - **lantern eel:** rises out of the water or sand; as built, its tail is buried (lantern_eel.md, Notes for the model).
  - **Mangrove Drowner:** stands in the water, roots black below the waterline, its KO sinks (act2/mangrove_drowner.md).
  - **Undertow's Reach:** a limb of the storm coming down over the wall from behind the parapet (act1/undertows_reach.md).
  - **Wakefin:** a fish, mostly a fin above the water; it breaches and dives (act2/wakefin.md).
  - **tannin archer:** half out of the fen's water on a root (y 0 is the water, the root's ends dip under: −0.083 at
    rest); its KO rolls off and sinks (act2/tannin_archer.md and the build's docstring).
- **Test:** `GroundedClipsTest` now covers every creature in creatures.json less `ALLOW`, fliers with their hover
  added; `test_the_allow_list_names_creatures` keeps the list current. The whole of test_creatures runs in about 8 s.
- docs/kb/art/creatures/pipeline.md: the "On the floor" bullet. PROVENANCE: the 19 GLB rows list `common/grounding.py`.

### Before / after (metres, the lowest vertex over all frames of each clip, a flier's hover added; KO end = its last frame)
| Creature | idle | attack | cast | hit | ko | hit_b | idle_b | other clips | KO end |
|---|---|---|---|---|---|---|---|---|---|
| scuttler (before) | -0.010 | -0.044 | -0.002 | -0.182 | -0.375 | -0.293 | -0.002 | | -0.328 |
| scuttler (after) | +0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | | -0.000 |
| cinder matron (before) | -0.010 | -0.114 | -0.010 | -0.010 | -0.345 | -0.010 | -0.010 | phase_change -0.010 | -0.345 |
| cinder matron (after) | +0.000 | -0.000 | +0.000 | +0.000 | -0.000 | +0.000 | +0.000 | all ≥ 0.000 | -0.000 |
| shoal skipper (before) | -0.016 | -0.016 | -0.162 | -0.026 | -0.318 | -0.057 | -0.016 | | -0.318 |
| shoal skipper (after) | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | | -0.000 |
| raid hound (before) | -0.016 | -0.153 | -0.014 | -0.014 | -0.221 | -0.014 | -0.014 | | -0.221 |
| raid hound (after) | -0.000 | -0.000 | +0.001 | +0.001 | -0.000 | +0.001 | +0.001 | | +0.043 |
| drownbell (before) | -0.043 | -0.151 | -0.219 | -0.103 | -0.046 | -0.096 | -0.072 | phase_change -0.064 | -0.034 |
| drownbell (after) | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | all ≥ 0.000 | +0.000 |
| bottle hermit (before) | -0.017 | -0.003 | -0.003 | -0.028 | -0.190 | -0.036 | -0.003 | | -0.189 |
| bottle hermit (after) | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | | +0.000 |
| vein sparker (before) | -0.010 | -0.004 | -0.004 | -0.004 | -0.179 | -0.004 | -0.004 | | -0.179 |
| vein sparker (after) | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | | +0.005 |
| spawn polyp (before) | -0.016 | -0.012 | -0.012 | -0.024 | -0.131 | -0.028 | -0.012 | | -0.131 |
| spawn polyp (after) | +0.000 | +0.000 | +0.000 | +0.000 | -0.000 | +0.000 | +0.000 | | +0.000 |
| wall polyp (before) | -0.009 | -0.005 | -0.005 | -0.017 | -0.025 | -0.021 | -0.005 | | -0.025 |
| wall polyp (after) | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | | -0.000 |
| tower limpet (before) | -0.075 | -0.075 | -0.077 | -0.075 | -0.105 | -0.102 | -0.075 | | -0.105 |
| tower limpet (after) | -0.000 | -0.000 | -0.000 | -0.000 | +0.000 | -0.000 | -0.000 | | +0.000 |
| glassfry (before) | +0.618 | +0.601 | +0.690 | +0.557 | -0.077 | +0.510 | +0.690 | | -0.077 |
| glassfry (after) | +0.618 | +0.601 | +0.690 | +0.557 | -0.000 | +0.510 | +0.690 | | -0.000 |
| lamp engine (before) | +0.000 | +0.000 | +0.000 | +0.000 | -0.007 | +0.000 | +0.000 | | -0.007 |
| lamp engine (after) | +0.000 | +0.000 | +0.000 | +0.000 | -0.000 | +0.000 | +0.000 | all ≥ 0.000 | +0.000 |
| oil slug (before) | +0.012 | -0.052 | +0.052 | -0.047 | +0.006 | -0.088 | +0.052 | | +0.006 |
| oil slug (after) | +0.012 | -0.000 | +0.052 | +0.042 | +0.006 | +0.038 | +0.052 | | +0.006 |
| spar wraith (before) | -0.045 | -0.025 | -0.025 | -0.025 | -0.907 | -0.025 | -0.025 | phase_drop -0.256, idle_deck -0.234, attack_deck -0.307, cast_deck -0.169, hit_deck -0.175 | -0.907 |
| spar wraith (after) | -0.004 | -0.004 | -0.004 | -0.004 | -0.004 | -0.004 | -0.004 | all ≥ 0.000 | -0.004 |
| flue moth (before) | -0.002 | -0.074 | -0.108 | -0.034 | -0.617 | -0.045 | -0.012 | | -0.617 |
| flue moth (after) | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | -0.000 | | +0.000 |
| ashwing (before) | +1.288 | +1.116 | +1.501 | +0.836 | -0.632 | +1.049 | +1.501 | | -0.632 |
| ashwing (after) | +1.288 | +1.116 | +1.501 | +0.836 | -0.000 | +1.049 | +1.501 | | +0.000 |
| gull harrier (before) | +0.692 | +0.149 | +0.507 | +0.362 | -0.281 | -0.104 | +0.651 | | -0.022 |
| gull harrier (after) | +0.692 | +0.149 | +0.507 | +0.362 | -0.000 | -0.000 | +0.651 | | +0.000 |
| stormgull (before) | +0.692 | +0.149 | +0.507 | +0.362 | -0.281 | -0.105 | +0.651 | | -0.022 |
| stormgull (after) | +0.692 | +0.149 | +0.507 | +0.362 | -0.000 | -0.000 | +0.651 | | +0.000 |
| squall wing (before) | +0.791 | +0.234 | +0.969 | +0.496 | -0.162 | -0.033 | +1.169 | | -0.139 |
| squall wing (after) | +0.791 | +0.234 | +0.969 | +0.496 | -0.000 | -0.000 | +1.169 | | -0.000 |

### Timing
Contact keys are untouched (corrections only turn or lift limbs at the existing frames). Measured from the GLBs (the
frame of the largest mean vertex displacement), every hit, hit_b and attack peak is the same frame as before, except
the squall wing's `hit_b` (0.27 s → 0.20 s, its wing corrected at 0.27 s). The hits peak at 0.07–0.13 s; the gulls'
(0.23 s) are as authored.

### Verify
`verify_blender_builds.py` prints identical for all 42 creature jobs (the 19 rebuilt here and the 23 others, which
grounding.py's change reaches through `common/**`).Run: 42 jobs, 0 failed, 0 uncovered, 208 s.

### Checks
- `godot --headless --import`; Godot `--filter=creature` (37 run, 0 failed) and `--filter=battle` (687 run, 0 failed);
- `python3 -m unittest tools.tests.test_creatures` (12 OK) and `tools.tests.test_blender_builds` (28 OK);
- `validate_data.py` (0 errors), `gdlint`, `gdformat --check` and `taskboard --check`.

No screenshot was rendered here (PC only).

### For the PC render (pending)
- **Shots:** `creature_scuttler`, `creature_cinder_matron`, `creature_shoal_skipper`, `creature_raid_hound`,
  `creature_drownbell`, `creature_drownbell_rim_broken`, `creature_drownbell_toll`, `drownbell_flood`,
  `creature_bottle_hermit`, `creature_vein_sparker`, `creature_spawn_polyp`, `creature_wall_polyp`,
  `creature_tower_limpet`, `creature_glassfry`, `creature_lamp_engine`, `creature_lamp_engine_opened`,
  `creature_oil_slug`, `creature_spar_wraith`, `creature_flue_moth`, `creature_ashwing`, `creature_gull_harrier`,
  `creature_stormgull`, `creature_squall_wing`, `battle_boss_intro_drownbell`, `causeway_c08_drownbell_disc_approach`,
  and the `battle_choreo_*` shots (the toll and the KO most).
- **What to judge:** the feet stay planted; the KO ends lie on the floor and read right (the scuttler rolled up, the
  skipper on its side with the fin tucked, the hound sphinx-like with forearms flat, the flue moth on its side with the
  legs curled, the ashwing's wings closed over its back, the spar-wraith's body on the deck); the tower limpet's
  flattened front sole; the flue moth's wings now lift as they open (buffet, flare); the spar-wraith's hub no longer
  sways (the body still does).

### Found, not fixed here
- The oil slug rests 5.2 cm above the floor (its lowest vertex at rest is +0.052; the idle dips to +0.012). It hovers a
  little, not by design that I can find in oil_slug.md. Worth a look with the render.

## Review log
