---
id: M5-A3P-1005
title: "Request (audio): Ch18's new music cues and sounds"
role: audio
status: todo
owner_session: ""
depends_on: [M5-A3P-1003]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The Ch18 scripts (M5-A3P-1003) name cues that don't exist yet. Briefs: act3_ch18.md §6 and the drafts README "Music
cues the drafts name".
- **Resolved (2026-10-31, act2-plan):**
  - `kite_theme` → `kite_maiden_flight`, which plays into `the_kite` (M3-AUD-853);
  - `kite_night` → `the_kite`;
  - `reedhollow_return` → Ch10's `reedhollow`, a callback;
  - the zone row `ch18/kite` → `the_kite`.
- **Still asked:** `haluna_lifting`, and the sounds `sails_fill`, `clutch_hum`, `velamir_lullaby_hum`, `shell_into_water`, `names_murmured`.
- **Music:**
  - `kite_theme` (the maiden flight);
  - `reedhollow_return`;
  - `haluna_lifting`;
  - `kite_night`.
  - `farewell_tide` exists (Ch10's). The sheet asks for a version with Asha's hum under it, which `velamir_lullaby_hum` may supply.
- **Sounds** (`assets/audio/sfx/<id>.ogg`): `sails_fill`, `clutch_hum`, `velamir_lullaby_hum`, `shell_into_water`, `names_murmured`. `current_song` exists.

## Acceptance criteria
- [ ] Each cue and sound exists, with a PROVENANCE row.

## Review log
