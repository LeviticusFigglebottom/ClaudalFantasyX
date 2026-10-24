---
id: M2-AUD-11
title: `saltgrass_causeway`: the B06 field bed
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-02]
milestone: M2
request-from: lead
---
## Goal
vertical_slice.md §6: "Wind, sparse plucked strings, open fifths, a walking pulse." B06, the slice's route. m2-slice places it when the zone exists.

## Acceptance criteria
- [x] An original seamless loop at −16 LUFS, listening notes, a music.json cue row (and a zone row once ch03/saltgrass_causeway exists).

## Notes
- 2026-10-24 audio (claude/audio): `assets_src/music/saltgrass_causeway.py`: an 80 s seamless loop, A minor pentatonic over open fifths, 84 BPM walking pulse (plucked strings through the lute body from haluna_village), a breathing wind bed, a sparse plucked melody, kettle gongs; −16.1 LUFS, −1.7 dBTP. music.json cue row added (`resume`); the zone row waits for `ch03/saltgrass_causeway` (m2-slice adds `{scene, music: saltgrass_causeway}` when the zone lands). Listening notes added. Original material (see the docstring); byte-reproducible (render_all --determinism).

## Review log
