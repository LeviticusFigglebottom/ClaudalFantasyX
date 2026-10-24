---
id: M2-ART-03
title: Art sign-off on the Undertow's storm events and chapter presets (M2-RND-05)
role: character
status: doing
owner_session: "env-art"
depends_on: [M2-RND-05]
milestone: M2
request-from: rendering
---
## Goal
M2-RND-05 built the Undertow as an event (docs/kb/tech/undertow.md, "Storm events"):
- torn rents;
- curtains of held light off the wounds;
- lightning bolts and the exposure flash;
- rain, the zone shadow, and the storm in the sea's reflection;
- chapter presets, including the Ch21 Letting.

Its acceptance asks Art to confirm the `spawn_wound` usage. This package asks for that, and for a read of the new looks against the colour script. As for M2-ART-01, the Art Director takes this under the character role.

**Key frames** are in `docs/kb/qa/gpu/rnd05/` (RX 9070 XT, 960×540). `*_high` frames use the High preset; the others use the capture rig's scene defaults.

| Frame | What to look at |
|---|---|
| `before_after_high` | Day, dusk and night, before (left) and after (right): the rents, the curtains and the reflection |
| `day_ch08_high`, `dusk_high`, `night_high`, `eye_high` | The four storm moods with every event part on |
| `strike_ch08` | A cloud-to-sea bolt with a fork (Ch8 storm wall) |
| `landfall_ch08` | Preset `ch08_landfall`: under the canopy's edge, the zone shadow at full and heavy rain ("darkens to near-night by 16:40") |
| `letting_ch21` | `unbinding` 1: the wounds, the curtains and the throat streaks turned to `glimmer_lift`, and rising |
| `dusk_low` | Low (shells): the rents and the curtains on the cheap tier |

The test scene is `game/levels/_tests/undertow/undertow_test.tscn`. A storm property in the inspector, or `Storm:preset` / `Storm:unbinding` in a shot's setup (`docs/kb/qa/gpu/2026-10-24-rnd-05-pending-shots.json`), shows any preset.

## Acceptance criteria
- [ ] **`spawn_wound` for the storm's rents.** palette.json limits `spawn_wound` to "creature weak points only". The Undertow's rents use it, because the storm is the spawn's source (SPEC §7.5, bible §9). Either extend the usage note in palette.json, or name the swatch the rents should use. That's an edit to Art's file.
- [ ] **The rents read as torn seams.** Each has an open glowing core, a dark torn lip and a faint halo of the poured-out light (undertow.json `wounds.lip_*` and `halo_*`). Confirm, or give the change: wider or darker lips, or less halo.
- [ ] **The curtains of held light** (`streamers`): cyan, sliding down, hanging from the rents to the sea. Confirm the count, brightness and width, or give the change.
- [ ] **Lightning:** the bolt's colour (the ch20 key `#C4D6FF`), width and fork count. The exposure flash is the colour script's Ch8 "2.0× exposure for 2 frames", capped at two a second and gentler under reduced motion. Confirm it for every storm chapter, or say which chapters drop it.
- [ ] **Rain and the zone shadow** in `landfall_ch08`: is near-night dark enough, and does the rain read as rain, not scratches?
- [ ] **The Letting** (`letting_ch21`): `glimmer_lift` at full on the rents is near-white at this exposure. Confirm, or set the Ch21 preset's `wound_intensity` and the `unbinding.rise_ratio` speed.
- [ ] **Presets** (undertow.json `presets`, from the colour script): `ch01_arrival`, `ch08_seawall`, `ch08_landfall`, `ch20_interior`, `ch21_heart` and `ch21_letting`. Confirm the values, or give the changes. Rendering applies them.

## Review log
