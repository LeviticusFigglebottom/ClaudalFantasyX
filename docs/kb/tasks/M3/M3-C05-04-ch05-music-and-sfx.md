---
id: M3-C05-04
title: Ch5 music cues and SFX (Lanternfall, kerrid_stair, the second verse)
role: audio
status: review
reviewer: cinematics
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
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
- [x] Every cue id named in `game/data/dialogue/ch05/*.dlg` resolves, and `test_ch05_thread.gd` runs without "no music" or "no sound" warnings for Ch5.
- [x] Each asset has a PROVENANCE row and is reproducible from source.
- [x] Hook the trial's sounds (a run along the veins, the landing) to `AshcrownTrial`'s `ran` and `landed` signals on the zone root.

## Notes
- All Ch5 cues delivered (M3-AUD-821, M3-AUD-828): `pemakar_terraces` (as `terraces_of_ash`), `lanternfall`, `kerrid_stair` (its notes in motifs.py, so E3 can slow it), `ashcrown_trial`, `cinder_matron` (two stems, the Pour), `hush_second_verse` (thunder on *mir*), `kahre_summon` (a battle sfx row). No script calls `ashcrown_tiers`; the Ashcrown zone row covers the tiers.
- The trial's sounds hang on AshcrownTrial's signals through AshcrownAudio (M3-AUD-825: `ran` by outcome, `landed`).
- The day variant was not made: no flow switches Pemakar's time of day yet. Ask audio when one does.
- Checked 2026-10-27 (M3-AUD-833's resolution test and the thread runs): `--filter=_thread` (Ch1-Ch9, 34 tests) passes with no "no music" or "no sound" warning from any scene; the only sequencer warnings are other kwargs' placeholders (`@vfx drift=`, `@camera grade=`, `@sfx at=`).

## Review log
