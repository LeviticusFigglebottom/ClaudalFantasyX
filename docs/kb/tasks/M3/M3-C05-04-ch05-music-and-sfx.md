---
id: M3-C05-04
title: Ch5 music cues and SFX (Lanternfall, kerrid_stair, the second verse)
role: audio
status: todo
owner_session: ""
depends_on: [M3-C05-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch5's scripts already cue the music and sounds the beat sheet asks for (act1_ch05.md §6). None of them exists yet, so the chapter plays silent; the sequencer warns "no music" and "no sound". Write and deliver:
- **Music:**
  - `pemakar_terraces` (town bed, with a day variant);
  - `lanternfall` (diegetic; it thins as the procession descends, down to one drum at the weir);
  - `kerrid_stair` (its first statement, ≤ 20 s; E3 must be able to slow it to a stop as `goodbye_kerrid`);
  - `ashcrown_tiers`;
  - `ashcrown_trial`;
  - `cinder_matron` (two stems, the second for the Pour);
  - `hush_second_verse` (with the thunder on *mir* as part of the cue);
  - `kahre_summon`.
- **SFX:** `plume_crackle`, `plume_thunder`, `vein_run`, `anvil_crack`, `matron_bank`, `weir_spill`, `crown_bell`.

Every melody is original (SPEC §2). The second verse's final Lamptongue text is Audio's (`ch05_kahre_014`–`017` are marked `#notr`).

## Acceptance criteria
- [ ] Every cue id named in `game/data/dialogue/ch05/*.dlg` resolves, and `test_ch05_thread.gd` runs without "no music" or "no sound" warnings for Ch5.
- [ ] Each asset has a PROVENANCE row and is reproducible from source.
- [ ] Hook the trial's sounds (a run along the veins, the landing) to `AshcrownTrial`'s `ran` and `landed` signals on the zone root.

## Notes

## Review log
