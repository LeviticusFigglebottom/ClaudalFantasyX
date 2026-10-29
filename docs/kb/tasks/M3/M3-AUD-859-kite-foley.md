---
id: M3-AUD-859
title: "The Kite's foley: the deck beds in flight and after H09, the engines' stopping, and E4's landing by hand"
role: audio
status: blocked
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: env-art
depends_on: [M3-AUD-836]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
This is the backlog's next-act step: the Act III SFX listed in act3_plan.md §2, for the Kite (M3-ENV-725,
docs/kb/art/environments/kite.md). Plain git has about 0.5 MiB left of its 72 MiB budget after M3-AUD-857, so Act III
SFX follow the music: they are rendered sources held for Git LFS (ADR 0039).

## Acceptance criteria
- [x] assets_src/sfx/act3/kite_foley.py writes the files below into assets/audio/sfx/act3/. It uses render_all.py
      `ACT3_SFX`, rendered with `--act3`.
      - kite_deck: a 40 s loop at −26.13 LUFS integrated. Wind, Virel's sailcloth luff and snap
        (vowbound_sfx.py), stays thrumming and whistling with the gusts, timber creaks, and both lift engines as a
        steady hum that never pulses, with the vane ring's whirr. Every drone fits a whole number of cycles in the
        loop, so there is no seam.
      - kite_deck_dark: a 40 s loop at −26.14 LUFS. The same deck after H09 with no engines; the wind carries it. It
        covers E1 to E3. E4's `@music silence` scene keeps its own foley, and E5 needs the room tone of nothing.
      - The one-shots, all at their targets in targets.py:
        - kite_engine_stop at −20.03 (H09: the hum sinks to a quarter, the vanes slow, the drum's last knock);
        - kite_lantern_out_1..2 at −24;
        - kite_sail_fill_1..2 at −21;
        - kite_rope_strain_1..3 at −21 (E4's hold);
        - kite_landing at −18.03 (hard, and survived);
        - kite_tiller_1..2 at −24;
        - kite_chest_open at −22 (the ledger chest).
      - All 16 files are byte-identical across `--determinism`. The total is 0.94 MiB, with peak memory at 1.3 GB.
- [x] tools/tests/test_act2_finals.py checks that every ACT3_SFX job renders from assets_src/sfx/act3/ into
      assets/audio/sfx/act3/, and that nothing there is tracked until `.gitattributes` routes it to LFS.
- [x] LFS is live: the 16 files are committed in Git LFS (9ee9c410's parent), each with its `.import` and sidecar.
      - The two beds are imported with `loop=true`.
      - PROVENANCE rows are added.
      - `game/data/audio/sfx_act3.json` holds rows for the one-shots.
      - Still to do: the zone row `ch18/kite` → ambience `kite_deck` once that scene exists, and the ending cutscenes
        using `kite_deck_dark`.

## Review log
