---
id: M2-UI-13
title: Accessibility audit (4/5): full control remapping, keyboard and pad
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-UI-09]
milestone: M2
request-from: lead
---
## Goal
SPEC §6.11 asks for input remapping. Nothing exists yet. Add a Controls page to the Settings hub that rebinds every player action, keyboard and pad separately, and saves the bindings.

## Acceptance criteria
- [ ] A data list of the remappable actions (ui_* and the game's own), each with a loc label.
- [ ] A Controls page (SettingsPage family) that shows each action's key and pad binding. Confirm listens for the next key or button. A binding that is already used is swapped, never left duplicated. "Reset to defaults" restores them.
- [ ] Bindings save to user://settings.cfg [controls] and load at boot (before the title takes input).
- [ ] Cancel can never be unbound, and listening can always be backed out of by keyboard Escape or pad B (hard-wired), so the player cannot lock themselves out.
- [ ] Tests (the model is node-free; listening is driven with synthetic events), and a shot of the page.

## Review log
