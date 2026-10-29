# The Ebbing's motes (M3-C09-03)

Owner: env-art-b, for Rendering (the Lead, 2026-10-28: Ch9 is env-art-b's and the Ebbing is an Act I set piece).
The brief is act1_ch09.md §9 (Rendering). The fields are GlimmerField's (tech/glimmer.md).

| Piece | Path |
|---|---|
| Rig | `game/vfx/ebbing/ebbing_motes.gd` (`EbbingMotes`) |
| Data | `game/data/vfx/ebbing.json` |
| Placed by | ZoneKitDressing's `ebbing` row (`tools/act1/ch09_corrow_night.py`) |
| Test scene | `game/levels/_tests/ebbing/ebbing_shots.tscn` (every field at once; `Cameras/N11`, `N08`, `Strand`) |
| Shots | `ebbing_n11`, `ebbing_n08` (new, awaiting the Lead's baselines) |
| Tests | `tests/unit/test_ebbing_motes.gd` |
| Sequencer hook | request M3-ARC-1326 (`cutscene_vfx_hosts`, `play_vfx`) |

## How the brief is met

| Item | How |
|---|---|
| 1. Held only | Every field is built HELD (`build_field`). The rig has no `release()` call, and the test checks it. Asha's warm rim stays a character light. |
| 2. `sea_direction` | (0.1, 0, 0.995): out of the harbour mouth, from the `harbour_stream` mark toward `harbour_mouth`. The motes sink through the zone's water (−0.55, the Tide's `water_height_y`) and are absorbed. |
| 3. The staff | A `StaffHead` node on Asha's body (raised, at `head_offset_m`), strength 0.22 and radius 1.4 m on the fields whose rows say `staff`. The test replicates the process shader's held drift and orbit blend on the CPU and samples the stream under the raised head. Of the motes the staff holds, the median heads down and under 5 % rise. At full strength 38 % would rise, so the tuning is what holds. |
| 4. The mourners | Four grief anchors (`mourner_1..4`, strength 0.7, radius 0.8 m) on `mourners_motes` and `mourner_hand`. As the staff head passes within 3.5 m of a mourner, its pull eases to 0 over 4 s (`mourner_share`). The motes lag, settle back for a moment, and are drawn on. One field holds the staff plus four mourners, within the budget of 8. |
| 5. Density | Eight fields by the cue marks (low town, strand, mourners, the hand, the harbour stream, overhead, the wall-head, the harbour mouth). Their amounts sum to 11.35 × the 450-mote base: about 5,100 at High, 7,700 at Ultra and 1,800 at Low (amount_scale 0.35). The cues start them movement by movement, and `ends` stops the earlier fields as later ones begin. `height_bias` 2.0–3.0 packs the motes toward the water. |
| 6. Reflection | `still_water_reflection` on the low town, the harbour stream, overhead and the mouth: the river runs above and below the waterline. |
| 7. Absorption bloom | **Cut for now** (optional in the brief). The beat reads without it. |
| 8. The cutaway | `wallhead_motes`: no attractor, `follow_global_focus` off. Its mark is seaward of Kerrid (test_ch09_thread). |
| 9. The cue vocabulary | Request M3-ARC-1326. The sequencer would offer each `@vfx` to `cutscene_vfx_hosts` first, and `follow=` / `anchors=` kwargs are proposed. Until the hook lands the cues still draw the placeholder, and the rig plays only in its test scene. |

## Open
- **Cost per tier:** unmeasured. It goes to the PC's QA pass (the test scene holds every field at once).
- **The hook (M3-ARC-1326):** until it lands, the chapter shows the placeholder motes.
- **The staff's height:** `StaffHead` sits at the raised height. Once Asha's field body has a staff bone or prop, the
  rig should follow that instead, so a lowered staff (B07, toward the harbour mouth) pulls lower.
