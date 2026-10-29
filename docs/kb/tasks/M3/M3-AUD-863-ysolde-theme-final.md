---
id: M3-AUD-863
title: "Ysolde's theme at final quality: `ysolde_theme` grown from the sketch into an A A' B A'' duet loop (ADR 0041)"
role: audio
status: review
owner_session: "audio worktree agent"
reviewer: design
depends_on: [M3-AUD-820, M3-AUD-861]
milestone: M3
request-from: lead
---
## Goal
`ysolde_theme` plays under C4-07 (`ch04_the_ink.dlg`, she re-inks the Velamir shells at night) and C4-09
(`ch04_gangplank.dlg`, alone at the gangplank at dawn with her appointment). It was a 61 s sketch (M3-AUD-820).
ADR 0041 puts Act I at final quality, so the cue becomes its final at the same path, keeping its identity: the
cold plucked board zither built from fourths and fifths, the reed drone that does not breathe, C major (the
Order's key) with a Lydian F# half, and the gilded bowl. The final grows that identity into a developed form with a
second voice, an alto zither, that answers the line, exact and cold like her. Nothing warm is added: no rubato, no
vibrato, and no third under the line in the low register.

## Form (4/4 at 63 BPM, a bar is 3.81 s; times from bar 1's downbeat)
| Bars | Time (s) | Section | Music |
|---|---|---|---|
| 1-8 | 0.0-30.5 | A | the sketch's statement, the zither alone with its open C-G strings: to a held E, to a held G, the falling answer home to C; bowl at bar 1 |
| 9-14 | 30.5-53.3 | A' | the first phrase again; the alto zither answers each held note (E, G, C) with falling fourths; the answer is cut to its last two bars; bowl at bar 9 |
| 15-20 | 53.3-76.2 | B (Lydian) | the sketch's B up to a held A, then two new bars falling by fourths to a held B over the C drone; the counter answers with F#; bowl at bar 15 |
| 21-24 | 76.2-91.4 | A'' | the falling answer returns with F natural, the descent to G with the counter's last D-G, and a bar of the drone alone back to bar 1; bowl at bar 21 |

## Acceptance criteria
- [x] `assets_src/music/ysolde_theme.py` edited in place. The docstring is no longer a sketch's: it gives the form with
      timings and the original-material check, extended to the new Lydian bars and the counter-line (clear of Sefir's
      motif and answer, Ansedra's court tune and bowls, and the Hush; the counter never touches C#).
- [x] The JOBS row is unchanged (`music_loop`, `ysolde_theme.ogg` + `ysolde_theme.loop.json`), so the cutscenes'
      `@music ysolde_theme` plays the final by name.
- [x] Seamless loop, 24 bars: 91.43 s (4,032,000 samples), LOOPSTART 0, LOOPLENGTH 4,032,000; the tags match the
      sidecar (`downbeat_offset_s` 0.238, a sixteenth's lead-in). Seam jump x1.10, flux x0.84.
- [x] Stereo Vorbis **q3**, **801,794 bytes** (0.80 MB). The cap is 0.90 MB, and the file grows 297,613 bytes over the
      sketch's 504,181, within the 0.45 MiB of plain-git budget left.
- [x] −16.01 LUFS integrated; true peak −1.57 dBTP (decoded); momentary max −7.30.
- [x] `python3 tools/audio/render_all.py --only ysolde_theme --determinism` reports both files identical
      (ogg sha256 `4d54764038b3`, sidecar `83185d99a5c5`).
- [x] Bus balance, measured, relative to the line (0 LU): counter −4.0, drone −9.1, open strings −9.9, bowl −13.4.
- [x] `LINE`, `BAR`, `BEAT`, `SCATTER`, `lacquer_box` and `zither` are unchanged, so `act3/dace_ledger.py`, which
      imports her line and voice, renders as before.
- [ ] The main session lands the `.ogg`/`.loop.json` (byte-checked against the worktree render) and the
      PROVENANCE/listening-notes rows.

Gates: `validate_data` passes. No Godot run, no screenshots, and no tools change, so `unittest` was skipped. The
loudness test needs the LFS files and can't run in a worktree, so loudness was checked in render_all's table.

## Listening points
- Bar 10 (about 34 s): the first time the alto zither answers the held E. It should read as a copy, correct and a
  register lower, not as warmth.
- Bars 19-20 (about 69-76 s): the new Lydian close on a bare B over the C drone, then F natural at bar 21 takes it
  back. The sound should be cool and bright, with nothing in it resolving.
- The wrap (bar 24 into bar 1): a bar of the drone alone, then the open strings and the bowl. The seam should be
  inaudible.

## Review log
