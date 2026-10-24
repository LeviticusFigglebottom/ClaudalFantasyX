---
id: M2-UI-26
title: Input parity audit: every screen fully usable with keyboard, mouse and controller
role: ui
status: doing
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
The human's ask: every screen fully usable with the keyboard, the mouse and a controller.
- **Mouse:** hover highlights and moves focus; click confirms; right click or the back button cancels; the wheel scrolls lists; the Lattice board pans and zooms by drag and wheel.
- **Controller:** every focus path is reachable, with no focus traps and no lost focus after a popup closes.
- **Prompt glyphs** switch with the last device used.

## Acceptance criteria
- [x] Shared input (ADR 0036): the `UiInput` autoload (mouse cancel, pad defaults in every scene, last device) and the wheel on every `MenuPage` list.
- [x] `tests/input_driver.gd` (`InputDriver`): real key, pad and mouse events through the root viewport.
- [ ] A parity test per screen, walked with all three devices, with what fails fixed:
  - [x] title and Settings hub;
  - [x] Settings pages (Accessibility, Controls; Graphics is the same SettingsPage);
  - [ ] field menu and its pages (Swell modes, Quit, Map, Bestiary; the Menus track's Items, Equip, Lattice, Status);
  - [ ] shop and inn;
  - [ ] save and load;
  - [ ] dialogue box, choices and backlog;
  - [ ] tips and prompts (the glyph switches with the device);
  - [ ] battle command menus, targeting, Swell inputs, read and result panels, battle pause.
- [ ] Screens owned by other roles: fix what the audit finds there minimally (one-line hooks), or file a request task and note it in the live log.

## Review log
