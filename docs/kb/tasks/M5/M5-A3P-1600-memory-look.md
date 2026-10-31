---
id: M5-A3P-1600
title: "Cinematics: the memory look (@memory), for Kesh's memory (Ch16) and the Undertow's six memory layers (Ch20)"
role: cinematics
status: review
owner_session: "claude/m2-slice (cinematics)"
depends_on: []
reviewer: art
milestone: M5
request-from: lead
---
## Goal
A remembered scene has to read as remembered with no UI: act2_ch16_direction.md K01–K08 (Kesh's memory, "desaturated
to white, soft edges") and act3_ch20.md (each layer's memory, held and slowed). ADR 0207 opened Act III per track;
Kesh's memory is Act II, so it ships first.

## Acceptance criteria
- [x] `@memory on|off [sec] [look=<id>]` (cues.json; `CutsceneMemory`, `game/cutscene/cutscene_memory.gd` and
      `.gdshader`): a screen layer under the letterbox, the fade and the box; drains the colour, washes toward the look's
      colour, softens and pales the edges; eases on sequencer.json's `memory.ease`; the scene's end takes it off.
- [x] Looks are data (sequencer.json `memory.looks`): `white` (Kesh's memory) and `held` (the Undertow, toward
      glimmer_held `#7FC6D9`).
- [x] ch16_kesh_memory uses it (on under the white fade-in, off under the white fade-out).
- [x] Tests: test_cutscene_sequencer (eases in, out, and the end clears it; an unknown look changes nothing);
      test_cutscene_directives (cues.json keys read).
- [x] Viewed on lavapipe (K04 with and without): the shader compiles, the held motes go grey, the edges wash to white,
      the box stays on top.
- [ ] Art review of the two looks' numbers against the colour script.

## Notes
- The Ch20 drafts (docs/kb/story/act3/drafts/ch20/) can open each memory with `@memory on 1.5 look=held`.
- Kesh's memory has no set yet: K01–K08 frame the open dark past the Choir's floor (the sea a thousand years ago, the
  six Lamplighters and young Sefir are not built). The motes and the look carry it until env-art's memory set lands.

## Review log
