---
draft: pre-gate
---
# Act II battle and field HUD

Pillar 4 is the rule for every item here: the player always knows who acts next and what an action costs. Every new
mechanic shows on the timeline, the help line or the target's Read, never only as a sound or a colour.

## Battle

### 1. Rooted (Ch10, the root crab's Root Drag)
- **A new status:** a rooted hero cannot be swapped out.
- **HUD:**
  - a status glyph (drawn, StatusGlyph's style: a root knot);
  - the Swap command greys with its reason ("Rooted: cannot leave the line");
  - the help line on Root Drag says it before it lands: "Roots the target: no swapping out".
- **Loc keys (5):** `STATUS_ROOTED`, `STATUS_ROOTED_DESC` ("Held by roots: cannot be swapped out."), `HUD_SWAP_ROOTED_FMT`,
  `HUD_HELP_ROOTS`, `HUD_FLOAT_ROOTED`.

### 2. Drain (Ch10, the fen leech; M4-CMB-1001)
- The leech's bite heals it by what it takes.
- **HUD:** the damage float on the hero, then a heal float on the leech in the drain colour. The help line on the foe's
  turn preview: "Drains: heals by the damage it deals".
- **Loc keys (2):** `HUD_HELP_DRAIN`, `HUD_FLOAT_DRAIN_FMT`.

### 3. Repair (Ch11, conduit crawlers mend the Lamp Engine)
- A crawler's repair restores a broken part.
- **HUD:**
  - the timeline marks the crawler's repair turn (intent: repair, like a charge);
  - the part's broken mark in the boss status clears with a float ("The lamps relight");
  - the help line on a crawler target: "Repairs the Engine's broken parts on its turn".
- **Loc keys (4):** `HUD_INTENT_REPAIR`, `HUD_HELP_REPAIRS`, `HUD_FLOAT_REPAIRED_FMT`, `ENEMY_CONDUIT_CRAWLER` (+ `LORE_`).

### 4. The flat-engine and its tide pulse (Ch14, Malcor Venn's barge)
- **Plan default:** the engine is a **part** (`break_parts`) with a timeline row for its pulse (role `tide`).
- **HUD:**
  - the timeline carries a "Flat-engine" entry. Each pulse slows the party, and the entry's chip shows the Slow it brings;
  - the boss status lists the part with its state ("Running" / "Broken");
  - Liss's breaking skill names the part in its help ("Breaks the flat-engine: the water moves again");
  - once broken, the entry leaves the timeline with a float.
- **Loc keys (6):** `PART_FLAT_ENGINE`, `HUD_PART_RUNNING`, `HUD_PART_BROKEN`, `HUD_ENTRY_TIDE_PULSE`, `HUD_HELP_BREAKS_ENGINE`,
  `HUD_FLOAT_ENGINE_BROKEN`.

### 5. The darkness fight (Ch15, the Wakefin on the unlamped barge)
- The arena is lit only by sea-glow; telegraphs are glow and sound (act2_plan §2 Ch15).
- **HUD rule:** darkness hides nothing the timeline shows. The Wakefin's chips, intents and Read work as in daylight. The
  HUD panels keep their contrast: no HUD dimming with the scene.
- **New:** a telegraph's sound also writes the help line on its turn ("A rush beneath the barge").
- **Loc keys (3):** `HUD_TELEGRAPH_WAKEFIN_RUSH`, `HUD_TELEGRAPH_WAKEFIN_DIVE`, `HUD_TELEGRAPH_WAKEFIN_RISE`. Combat names the
  moves; these keys follow them.

### 6. Element cycling (Ch16, Kesh; and Sefir's Abiding guard if it cycles)
- **HUD:** the element the foe will be next shows on its timeline chip (an element glyph) at least one turn ahead
  ("telegraph each shift on the timeline", act2_plan §2 Ch16). The Read panel lists the cycle.
- **Loc keys (3):** `HUD_HELP_ELEMENT_NEXT_FMT`, `HUD_READ_CYCLE`, `HUD_FLOAT_ELEMENT_SHIFT_FMT`.

### 7. Buff strip (Ch12, the cord moth's Unravel)
- Removes one helpful status. The float names it ("Unravels Bulwark"). The help line on Unravel: "Removes one helpful
  status".
- **Loc keys (2):** `HUD_HELP_STRIPS`, `HUD_FLOAT_STRIPPED_FMT`.

### 8. The step-hold and the storm's waking (Ch14, Ch16)
- Both use Ch8's set-piece HUD (`ObjectiveMeter`, M3-UI-100): an objective count and a locked hero. No new UI. Each
  needs only its own lines.
- **Loc keys (6):** `OBJ_CH14_HOLD_STEPS_FMT`, `OBJ_CH14_HOLD_STEPS_DONE`, `HUD_LOCKED_KERRID_STEPS`, `OBJ_CH16_HOLD_LINE_FMT`,
  `OBJ_CH16_HOLD_LINE_DONE`, `HUD_LOCKED_KERRID_LINE`.

## Field

### 9. Breath-fog (Ch12) and the rope-burns' held light (Ch10 on)
- Visual only (rendering and characters). No HUD.

### 10. The objective line and area titles for 15 zones
- The area maps and routes exist (M3-UI-206). The objective rows wait on the beat sheets.
- **Loc keys (about 40):** `OBJ_CH10_*` … `OBJ_CH16_*`, two to six per chapter, written with the beat sheets. Area titles
  come from `MAP_ROUTE_*` (exist).

### 11. Pell's absence (Ch10, Reedhollow)
- A `party` step leaves Pell outside. The field party (followers) and the menu's party cards drop him at once. The
  formation page shows him greyed: "Waits at the fen's edge".
- **Loc keys (1):** `FORMATION_AWAY_PELL_FEN`.
