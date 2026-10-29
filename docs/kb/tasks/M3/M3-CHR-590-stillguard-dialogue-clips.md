---
id: M3-CHR-590
title: "Stillguard dialogue clips: walk_torch, hold_arm, kneel_palms_flat, let_go (Ch6), shake_head (Ch8)"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-508]
milestone: M3
request-from: ""
reviewer: cinematics
---
## Goal
The Stillguard models (M3-CHR-508) have idle, walk, stand_watch_seaward, shield_up and level_spear. The Act I dialogue
also calls on them for these, which they don't have yet:
- Ch6 raid: `walk_torch`, `hold_arm` (the girl's arm held over the brazier), `kneel_palms_flat` (the Stilling posture)
  and `let_go`.
- Ch8: `shake_head`.

## Acceptance criteria
- [ ] Each clip is built as a story spec (requested_clips.json, the shared ones where they exist) on the Stillguard
      personas, with the spear and shield held or set down sensibly. The rig probe is clean.
- [ ] `hold_arm` is staged with the Ch6 wright girl; the contact point is noted for Cinematics.
- [ ] Self-rendered and viewed.

## Review log
