# M1-QA-09 on hardware: the heroes at High 2× and Ultra (PC, RX 9070 XT)

- **Head:** `claude/undertow-lead-handoff-ze8rrn` @ f580e756, fresh `.godot`. The first Windows import segfaulted at 3%,
  the known 4.6.3 import crash; the retry was clean, and a second import reported 0 errors.
- **Capture:** `tools/gpu_bench/capture_preset.tscn`, 49 shots (every `asha_*`, `rhen_*` and `toma_*` shot, plus
  `field_hero_party`, `field_hero_rhen_walk`, `field_hero_gait_strip` and `hero_cutscene_turn_strip`).
  - `--preset=high --scale=2` (1920×1080) took 120 s; `--preset=ultra` (960×540) took 100 s. Both exited 0.
  - The only log noise is the known `environment_set_ssr_roughness_quality` error from graphics_settings.gd:275.
- **Sheets:** `high2x/sheet_00..08.jpg` and `ultra/sheet_00..08.jpg`, six shots each in alphabetical order, labelled.
  The full-size PNGs are kept on the PC: say the word and they get pushed.
- **High vs Ultra:** every defect below shows the same way in both, so they are asset or rig problems, not preset ones.

## Findings (strict SPEC §14 read; ⚠ = a player sees it in normal play)

| # | Hero | Shots | Defect | Class → owner |
|---|---|---|---|---|
| 1 ⚠ | Asha | battle_idle, clip_face_west, clip_turn, clip_walk, q34, front, sleeve_s0/s4, hero_cutscene_turn_strip | **The staff isn't gripped.** The hand rests open, fingers splayed against or beside the shaft, and the staff stands on its own. `staff_hands.jpg` (left). | rig/anim: hand pose or prop attach → characters |
| 2 ⚠ | Asha | clip_run, clip_walk_cycle, clip_offer_hand | **The staff floats upright**, detached from both hands. In clip_offer_hand it stands behind her back, through the braid, while she kneels. | prop attach (staff follows the root, not a hand bone) → characters / hero-integration |
| 3 ⚠ | Asha | clip_kneel_over_rhen, clip_laugh | **The staff passes through the skirt** into the floor; the hand is again open on the shaft. `kneel_skirt_ultra_vs_high.jpg` (left two: High, Ultra). | anim/prop → characters |
| 4 ⚠ | Asha | clip_offer_hand | **The white underskirt turns into a rigid tube** under the front knee. It stays a cylinder, and the trailing shin pokes through the underskirt's sheet. `kneel_skirt_ultra_vs_high.jpg` (right). | skinning/cloth weights on the underskirt → characters |
| 5 | Asha | extreme_pose | **The raised knee stretches the skirt** into a pocket with smeared texture, and the underskirt shows through the blue layer. The staff isn't gripped either (item 1). `extreme_pose_skirt.jpg`. | skin weights (stress pose) → characters |
| 6 | Asha | battle_attack, extreme_pose | The gauze sleeve reads as a flat sheet at large arm angles. Acceptable at battle distance. | asset → characters (low) |
| 7 ⚠ | Toma | clip_turn, clip_walk_cycle, back, front | **The spear isn't gripped** (open hand over the shaft in clip_turn and front). It floats upright in clip_walk_cycle, and stands free in back. `staff_hands.jpg` (middle). | same as items 1 and 2 → characters |
| 8 | Toma | face_neutral, face_smile | The beard's edge reads as blotchy alpha cards along the jaw and cheek at close-up. | groom/material → characters |
| 9 | Rhen | battle_attack, battle_idle | No hooks in his hands. Expected at this head: M2-CHR-513 (characters @ 038d5651, render queued) adds them. | n/a (in flight) |

- **Clean:** Rhen's limbs and clothing in every clip (kneel, take_hand, walk_cycle and turn have no visible
  interpenetration); Asha's braid (it stays over the right shoulder, with no clipping through the vest at these
  angles); every face shot's silhouette; and the field_hero_* shots.
- **Not judged here:** the grief-mouth rigour items in the M1-QA-09 task file (lid/cheek boxes and the fault-A
  control). Those were captured on 10-24 and are a separate scope.
