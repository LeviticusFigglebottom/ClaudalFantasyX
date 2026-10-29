---
id: M3-AUD-854
title: "Primitive audit (audio): the field's interact prompt, using something, and the codex notice had no sound"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: ui
depends_on: [M3-AUD-832]
milestone: M3
request-from: audio
---
## Goal
TRACK-RULES' self-directed backlog, step 4: audio's own "parts look primitive" audit. In the field, three common
moments made no sound.
- The interact prompt appearing over something usable.
- Pressing interact on an Interactable when it opens nothing that sounds: a sign, a look, a stand-in.
- A codex entry's notice.

## Acceptance criteria
- [x] screen_sfx.py: `ui_prompt_in` (one tiny glass tick, −14 dB, at most once in 0.9 s) and `ui_interact` (a soft
      cloth-muffled tap and a faint bar, −8 dB). Both are on target and deterministic.
- [x] ui_sfx.json hooks:
      - `Interactable.used` plays `ui_interact`. It is unlisted in priority, so the menu or dialogue it opens wins
        that frame;
      - `InteractPrompt.is_showing()` turning on plays `ui_prompt_in`;
      - `CodexNotice.is_showing()` plays `ui_tip`.
- [x] Tests: test_screen_audio covers a real Interactable's touch and the real InteractPrompt (silent while
      hidden). `screen_audio` 11/0, `audio` 170/0, `field` 147/0, `interact` 13/0, `shrine` 37/0.
- [ ] By ear: is the prompt tick subtle enough when walking past a row of villagers?

## Review log
