---
draft: pre-gate
---
# The heresy state (from Ch14)

- **The flag:** `ch14_declared_heretics` (act2_plan §4.2), set in Ch14 C2 when the Conclave springs the trap. It never
  clears in Act II.
- **The rule for the player:** what changed must be visible before they try, and every refusal says why in one line.

## 1. Save shrines: the Order's go dark and refuse

- **Plan default (act2_plan §4.2):** Order shrines go dark and refuse; Saltwright and Kirru places keep working; an
  un-dark shrine stands at every chapter boundary.
- **Data (at the gate):** a shrine gets `order: true` (SaveShrine export, or the shrine's row in locations.json). The flag
  makes an Order shrine **dark**.
- **In the field:**
  - a dark shrine's light is out (rendering: its glimmer off, a cold grey stone; env-art);
  - its interaction prompt reads "Dark shrine" instead of "Rest at the shrine";
  - pressing it shows one line and opens nothing: "The Order's light is out. It will not answer you."
- **The map:** a dark shrine's POI glyph is the shrine glyph hollow, with "Dark" in its legend line.
- **Shrine travel (M2-…, the shrine network):** dark shrines stay on the list, greyed, with the reason ("Dark: the Order's
  shrine"), so the player sees why a route is gone.
- **The first time:** the dark-shrine tip (tutorials.md).
- **The save menu itself:** unchanged (only working shrines open it).
- **Tests:** a shrine with `order: true` refuses after the flag and works before; travel lists it greyed; the prompt's
  text follows the flag; `test_qa_save_shrines` gains a heretic pass (every Act II chapter boundary has a working shrine).
- **Loc keys (6):** `SAVE_SHRINE_DARK_PROMPT`, `SAVE_SHRINE_DARK_REFUSED`, `SHRINE_TRAVEL_DARK_FMT`, `MAP_LEGEND_SHRINE_DARK`,
  `MAP_POI_SHRINE_DARK_FMT`, `CODEX_HERESY_*` (codex_bestiary.md).

## 2. Shops: the Order's refuse

- **Data:** `shops.json` rows get `order: true` (Ansedra's purveyor; any Order-run stall). Quellan's and Hollowmere's
  keepers are not Order.
- **Behaviour:** an Order shop's keeper refuses before the menu opens: one line, in the keeper's own voice ("Not to you.
  Not now."). The town menu never opens empty.
- **Loc keys (2):** `SHOP_ERR_HERETIC`, `SHOP_REFUSE_ANSEDRA_PURVEYOR` (the keeper's line).

## 3. The party's title (status menu, save slots)

- **Today:** the Status page header names the hero. There is no party title yet.
- **Act II:** the field menu's root header ("Along the Way") gains a subtitle line once `ch14_declared_heretics` is set:
  "Heretics of the Level". This is the act's only standing reminder; it is quiet, never red.
- **Save slots:** a heretic save's slot line carries the same word after the chapter ("Chapter 14 · Heretics"), so a
  player choosing a slot knows which side of the trap it is.
- **Loc keys (2):** `FIELD_MENU_SUBTITLE_HERETIC`, `SAVE_SLOT_HERETIC_TAG`.

## 4. People and barks

- Order NPCs' barks switch on the flag (state-changing dialogue: `.dlg` `<<if $ch14_declared_heretics>>` blocks,
  Narrative). The interaction prompt for a refusing NPC reads "Listen", as any bark does. No UI change.
- No random Stillguard fights (act2_roster): no encounter-table UI.

## 5. What does not change

- Battle UI, the party's kit and the Lattice: heresy is a story state, not a mechanic.
- Kirru (Reedhollow) and Saltwright (Hollowmere) shrines and keepers: they work as before. That is the point.

**Loc keys total (10)** plus the codex entry.
