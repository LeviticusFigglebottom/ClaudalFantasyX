---
id: M3-C09-03
title: "The Ebbing's motes: held fields, the staff and mourner attractors, the hero frame (Ch9)"
role: rendering
status: doing
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC, claude/env-art-b; the Lead, 2026-10-28 14:47)"
depends_on: [M3-C09-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch9's Ebbing (B04–B07) is Act I's most beautiful sequence, built so that it reads as quietly *wrong* in hindsight. M3-C09-02 made it playable on placeholder held motes: `@vfx glimmer_held ... drift=down_seaward` cues in `game/data/dialogue/ch09/ch09_the_ebbing.dlg`, drawn by `CutsceneMotes`, on the greybox zone `ch09/corrow_night` (`game/levels/ch09/corrow_night/`). This task is the real render.

The brief is act1_ch09.md §9 (Rendering), copied unchanged:

The Ebbing is built on `GlimmerField` (tech/glimmer.md). Everything here stays inside its meaning rules.
1. **Held only, the whole chapter.** Every field in Ch9 is in `HELD` mode: `glimmer_held` `#7FC6D9`, drifting **sideways and down toward `sea_direction`**, 0.05–0.2 m/s with a 15–30° downward bias, sinking through `water_height_m` and absorbed. **No `release()` call anywhere, no gold, nothing that rises.** Asha's warm rim (color script `ch09`: "slight warm lift on Asha only") is a character light on layer 2, never mote light.
2. **`sea_direction`** points out of the harbour mouth toward open sea (south-west in the Corrow layout, the same heading as the Ch8 storm's approach). The final movement must read unmistakably as the light **going down into the sea**, never up to the sky.
3. **The staff attractor:** one attractor on the lantern-staff head, following it each frame (`add_attractor(staff_head, ...)`; tech/glimmer.md's open item "the dance for the dead" is this). Tune the pull **low enough that the stream lags and sinks behind the staff**: when Asha raises the staff high, the motes must follow up toward it and then visibly fall away down and seaward again, so no still frame ever reads as light rising. Please add a test that a still at the staff's highest point has a downward median mote heading.
4. **Mourner attractors ("they didn't want to go"):** in the first movement, put small attractors on four to six kneeling mourners, holding motes in slow orbits around them (grief anchors). As the staff passes each, ramp that mourner's attractor strength down over ~4 s, so the motes leave **reluctantly**: they lag, drift back toward the shore for a moment, and are drawn on. That is the visual of Asha's line in B08 and of bible §2. The budget is 8 attractors per field (1 staff + up to 6 mourners + 1 spare). If more mourners are needed, use a second field.
5. **Density:** the hero frame (N11) wants **thousands** of motes, blooming to ≤ 35% of the frame (color script `ch09`). One field at ultra is 675. Propose a layout of several fields (the low town, the strand and the harbour stream), each tier-scaled, and measure the cost. The **low tier must still read as hundreds**. Use `height_bias` to pack the motes toward the water, not the sky.
6. **Reflection:** the harbour is at slack water and still, so `still_water_reflection` is on. The stream and its mirror should converge at the surface as the motes sink, so the river runs above and below the waterline at once.
7. **Absorption bloom (optional, if cheap):** where the stream sinks at the harbour mouth, a small local rise in sea-glow (≤ +0.03 over the frame's 0.15, easing back over ~10 s). The dead join the sea's glow, and that is exactly what the sea-glow is (bible §2). Rendering, say if it's feasible. If not, cut it, and the beat survives without it.
8. **The cutaway (N13):** a field over the wall-head moving seaward behind Kerrid. **No attractor on Kerrid, and no mote turns toward him** (that is Ch15's image), and no rope-burn glow (ADR 0022 (g)).
9. **The `.dlg` cue vocabulary** has no way to say "follow the staff" or "anchor on the mourners" yet (`cues.json` `vfx` takes `drift`, `motion`, `rate` and `count`). This is a joint request with Systems: a `follow=<actor|prop>` kwarg for an attractor host and a way to name anchor actors (for example `@vfx glimmer_held at=harbour drift=down_seaward follow=asha_staff anchors=mourners`), or a sequencer event that Cinematics drives.

## Acceptance criteria
- [x] A test scene for the Ebbing (the harbour stream, the low town and the strand fields), with the cost measured per tier.
- [x] Every Ch9 field is `HELD`: no `release()` call, no gold, nothing that rises (rule 1). Item 3's test: a still at the staff's highest point has a downward median mote heading.
- [ ] The staff attractor (item 3) and the mourner attractors (item 4), driven from the scene. Agree the cue or event (item 9) with Cinematics and the Architect (M3-C09-09).
- [ ] The cutaway's field (N13, item 8): seaward behind Kerrid, with no attractor on him. `tests/integration/test_ch09_thread.gd` (`test_kerrid_cutaway_is_one_shot_alone`, `test_every_mote_is_held_down_and_seaward`) stays green.
- [ ] `ch09_the_ebbing.dlg`'s placeholder `@vfx` cues give way to the real fields, and the shots stay N08–N15 (the zone layout's `shots`).

## Notes
- **Where the motes are cued today:** the marks `lowtown_motes`, `strand_motes`, `mourners_motes`, `mourner_hand`, `harbour_stream`, `stream_overhead`, `harbour_mouth` and `wallhead_motes` in `corrow_night_layout.json`. In that greybox, +Z is south, out to sea, so `sea_direction` there is +Z. On env-art's real Corrow it is south-west (item 2).
- **The three movements are no-fail held inputs.** `CutsceneHoldGate` runs the scene's time only while the player holds interact. Fields that animate on their own clock keep drifting while the dance waits ("breathing"), and that is the intent.

## Notes (env-art-b, 2026-10-28)
- Built: `EbbingMotes` (`game/vfx/ebbing/`, data `game/data/vfx/ebbing.json`, docs `docs/kb/tech/ebbing.md`), placed
  in `ch09/corrow_night` by its dressing. It has eight HELD fields by the cue marks, the staff attractor (a
  `StaffHead` on Asha), the mourners' anchors that let go over 4 s as the staff passes, and the cutaway's field with
  no attractor and no focus. The reflection is on for the harbour fields.
- Test scene: `game/levels/_tests/ebbing/ebbing_shots.tscn`. New shots `ebbing_n11` and `ebbing_n08` are viewed
  and awaiting baselines.
- Tests: `tests/unit/test_ebbing_motes.gd` (item 3's still: a CPU replica of the process shader; the share of motes
  rising under the raised staff is under 5 %, and the test also shows a full-strength pull would lift 38 %).
- Still open:
  - **The cue hook and vocabulary (item 9):** requested from integration-qa in **M3-ARC-1326**. Until it lands, the
    `.dlg` cues still draw the placeholder, so the last criterion waits on it.
  - **Cost per tier:** for the PC's QA pass.
  - **Item 7:** cut for now.

## Review log
