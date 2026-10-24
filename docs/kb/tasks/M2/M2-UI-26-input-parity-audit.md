---
id: M2-UI-26
title: Input parity audit: every screen fully usable with keyboard, mouse and controller
role: ui
status: review
reviewer: lead
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
- [x] A parity test per screen, walked with all three devices, with what fails fixed:
  - [x] title and Settings hub;
  - [x] Settings pages (Accessibility, Controls; Graphics is the same SettingsPage);
  - [x] field menu and its pages (Swell modes, Quit, Map, Bestiary; the Menus track's Items, Equip, Lattice, Status): `test_input_parity_{field_menu,map,bestiary,items,equip,lattice,status}.gd`. Fixes in the Menus track's files (Lattice board drag and zoom, its click test) were sent to that track through the lead;
  - [x] shop and inn;
  - [x] save and load (Systems-owned `game/ui/save/`: hover, wheel and the dialog-choice hover added; Systems to accept, and M2-ARC-06's hover bug is fixed by it);
  - [x] dialogue box, choices and backlog (and the hold to skip): `test_input_parity_dialogue.gd`; click-to-advance and wheel-to-backlog in DialogueAssist, `UiFocus` hooked into m2-slice's CutsceneChoices (one line), the right button holds Cancel;
  - [x] tips and prompts (the glyph switches with the device): `test_input_parity_glyphs.gd`; the prompt follows `InputNames.using_pad`, the tip card refills on a device change, dialogue lines fill `{action}` (one line in the Architect's DialogueBox); M2-FP-28 asks m2-slice to rewrite two Ch1 tutorial lines that spell out keys;
  - [x] battle command menus, targeting, Swell inputs, read and result panels, battle pause: `test_input_parity_{battle,swell}.gd`; mouse targeting (`BattlePointer`), the mouse plays every Swell input (`SwellRingView.pointer_event`), the Read panel's click (it was 0 x 0). The battle pause has no mouse affordance (noted in ui.md).
- [x] Screens owned by other roles: minimal hooks, listed for their owners to accept.
  - **Systems,** `game/ui/save/`: slot hover, wheel, dialog-choice hover.
  - **Architect,** `game/ui/dialogue/dialogue_box.gd`: the `{action}` fill hook.
  - **m2-slice,** `game/cutscene/cutscene_choices.gd`: the `UiFocus` hover hook.
  - **Menus track,** `game/ui/menus/lattice/`: pan and zoom. The Menus track has merged it.
  - **Request M2-FP-28:** the Ch1 tutorial lines should name their bindings with `{action}`.

## Open
- **The battle pause has no mouse way in** (P, Pause, pad Start only). An on-screen button would move every battle shot. Lead: decide whether Cancel at the command root should open it, or a small corner button should.
- **`battle_controller.gd` is at exactly 1000 lines** after the targeting hook. The next change there must move logic into a helper first.

## Review log
