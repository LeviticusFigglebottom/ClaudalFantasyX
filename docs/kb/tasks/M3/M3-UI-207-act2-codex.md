---
id: M3-UI-207
title: "Act II codex: the places of Ch10-16 and two peoples, each on its chapter's arrival flag"
role: ui
status: blocked
blocked-by: ADR 0041
owner_session: claude/ui (ui-menus)
reviewer: narrative
depends_on: [M4-C10-02, M4-C11-02, M4-C12-02, M4-C13-02, M4-C14-02]
milestone: M3
---
## Goal
The Lead routed this on 2026-10-27 at 23:37: Act II codex entries. Act II has only chapter-progress flags so far (act1-chapters' greybox). The set is therefore what a traveller learns on arriving:
- the places;
- the two peoples the party lives among (the Kirru, the Ullari).

The story's people (Tobin, Merel, Malcor Venn, the Saints) wait on the beat sheets and their flags.

## Acceptance criteria
- [x] Fourteen places, each unlocking on its chapter's `started`, `reached_*` or `entered_*` flag. They follow Coilspire in `codex.json`:
  - Ossa Fen and Reedhollow;
  - Sunken Vey and Lowlight;
  - Keth Pass, Quellan and Cloudloom;
  - Ansedra, the Sanctum of the Level, the Lamp Archive and the Lacquer Court;
  - Hollowmere;
  - the Pale Rim and the Drowned Choir.
- [x] Two world entries, after the Saltwrights:
  - the Kirru (`ch10_started`);
  - the Ullari (`ch12_started`).
- [x] Text is in `codex.csv`, the `codex_<id>_read` flags in `flags.tres`, and `check_codex` passes.
- [x] The text follows M3-NAR-01's rules: 2 to 4 sentences, in-world, and no later-act truth:
  - no Saint named before binding, no revenants, no Hush;
  - the meaning of mote direction is not spelled out;
  - Lowlight and Cloudloom carry no snow or ice (ADR 0015).
- [ ] Narrative reviews the text (the Review log below).
- [ ] The `field_menu_codex` shot's counts move (34 to 50 entries). RENDER-REQUEST is in the live log.
- [ ] Story entries for Ch10-16 once the beat sheets (M4-C10-01 onward) add their flags. Examples: the farewell-tide, Tobin and Merel, the wedding.

## Review log
- 2026-10-28, ui-menus: **paused (ADR 0041, the human's refocus on Act I at final quality).** What is built stays on claude/ui and merges as is; nothing is reverted. Resume when a new ADR lifts the pause.
