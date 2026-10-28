---
id: M3-C06-04
title: Ch6 music cues and SFX (the Stillguard hum, the silent poles, sefir_theme's first resolution)
role: audio
status: review
reviewer: cinematics
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
depends_on: [M3-C06-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch6's scripts (`game/data/dialogue/ch06/`) name these cues; none exist yet, so the sequencer warns and the chapter plays silent (act1_ch06.md §6, §9 Audio 23):
- **Music:** `brine_shoals` (field bed; a dawn variant for B10), `raid` (B03: almost no score; fire, a low frame drum, and the diegetic Stillguard hum as the melody, the Order's own hummed tune from the temple ambience), `stillguard_inquisitor` (B04, two stems: the hum motif made martial, then fire and choked brass for Torch the Hulk), `sefir_theme` (B05, first statement: it enters only after his first line and **resolves completely**, the first melody in the game that does; original, never an echo of the Hush), `liss_theme` (B06–B07), `shoals_dusk` (B08–B09). `silence` is the reserved fade-out.
- **SFX:** `camp_burn`, `stillguard_hum` (if not part of `raid`), `hatch_burst`, `raid_hound_bay`, `sail_pulled`, `barge_pole` (wood creak and Reed footfalls only, **no water sound**: the absence is the effect), `brine_iron_hiss` (the iron in the water; the only water sound in B05), `tide_ambience` (B09).
- The battle cue for the road's fights is `battle_standard`; the boss needs `stillguard_inquisitor` wired to the encounter.

## Acceptance criteria
- [x] Every cue and SFX id above exists and the Ch6 scenes play without sequencer audio warnings.
- [x] B05 has no water sound but the iron's hiss, and no sting (`test_ch06_thread` allows only `barge_pole` and `brine_iron_hiss` there).
- [x] PROVENANCE rows for every new asset.

## Notes
- All Ch6 cues delivered (M3-AUD-11, M3-AUD-20, M3-AUD-821): `brine_shoals`, `raid`, `stillguard_inquisitor` (stems), `sefir_theme`; SFX in act1_cutscene_sfx.py, with `barge_pole` carrying no water and `stillguard_hum` stating motifs.ORDER_HUM. The dawn variant is not made (no B10 time-of-day switch yet).
- Checked 2026-10-27 (M3-AUD-833's resolution test and the thread runs): `--filter=_thread` (Ch1-Ch9, 34 tests) passes with no "no music" or "no sound" warning from any scene; the only sequencer warnings are other kwargs' placeholders (`@vfx drift=`, `@camera grade=`, `@sfx at=`).

## Review log
