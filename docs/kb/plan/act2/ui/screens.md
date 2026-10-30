---
draft: pre-gate
---
# Act II screens (new and changed)

Each entry lists the beat that needs it, what the player does, the controls on every device, and its loc keys.

## 1. The document reader (Ch13, the Lamp Archive; then the codex's records)

- **Need:** act2_plan §2 Ch13. Liss lays the founders' lamp-ledgers, the Cantor roll and Corran's line side by side. The
  player finds the matching hand. SPEC §6.11's codex "text records" grow into this. ADR 0016: nobody says "revenant".
- **Screen:** a full-screen framed page (UiFrame, the codex's look) holding **two or three record panes** side by side.
  - Each pane is a scrolled page of the record in its own voice (the codex's record style: `CodexRecordSpot`, M3-NAR-01).
  - A **hand mark** is a highlighted span in a pane, the same hand across panes.
- **Play:**
  - Left/Right (or the shoulders) move between panes; Up/Down scroll the pane.
  - Confirm on a span marks it.
  - When the marks across panes match (data: `matches`), the reader draws a thin gold rule between them, and the scene's
    flag is set (the cutscene continues).
  - Cancel closes; nothing is lost, and the marks stay.
- **Pillar 4 / clarity:** the help line says how many hands are still to match ("Two hands left to find").
- **Reduced motion:** the rule appears without its draw-on.
- **After Ch13:** the codex's Records category opens any found record in the same reader, single pane: Wenna's marks
  (Ch8, Ch11), Ama's keth (Ch12), the Archive set.
- **Data (to write at the gate):** `game/data/lore/records.json`: per record, its panes' text keys, its spans (by sentence
  index) and its matches; `game/data/ui/document_reader.json` for the layout.
- **Tests:** the parity test (pad, keys, mouse: click a span, wheel scrolls); pseudo-locale fit; aspect audit; a shot per
  layout (two panes, three panes).
- **Loc keys (12 plus the records' own text):**
  - `READER_TITLE_FMT` ("{record}"), `READER_HELP`, `READER_HELP_MOUSE`, `READER_HANDS_LEFT_FMT`, `READER_ALL_FOUND`,
    `READER_MARK`, `READER_UNMARK`, `READER_PANE_FMT` ("{n} of {count}");
  - `RECORD_ARCHIVE_LEDGER_TITLE`, `RECORD_CANTOR_ROLL_TITLE`, `RECORD_CORRAN_LINE_TITLE`, `RECORD_AMA_KETH_TITLE`;
  - each record's body in sentences: `RECORD_<ID>_<NN>` (Narrative writes them; about 60 sentence rows across Ch8–Ch13).

## 2. Seven heroes: formation, status, party rows

- **Need:** act2_plan §4.1. From Ch10 all seven travel, three active and four in reserve.
- **Formation:** the reserve page shows four rows. Today's `formation_menu.json` reserve `max_rows` covers this; check the
  pseudo-locale walk at seven. Pell's row (M3-C09-07) is the hard dependency.
- **Status and Equip:** their hero lists already scroll (MenuPage). The field menu's party cards show the **active three**
  (unchanged); the Status page lists all seven.
- **Battle:** the party panel stays three rows; the Swap command lists four reserve heroes. The swap list's `max_rows` (7)
  holds them.
- **Loc keys:** none new (names exist: `CHAR_*`).

## 3. The Vowbound list (six callable in Act II)

- **Need:** act2_plan §4.4. Nhoa, Hesk and Ethren join Ilun, Kahre and Virel. Kesh is bound at the end of Ch16 but is
  first called in Act III (`kesh_summon` is Act III's H03).
- **Today:** a Vowbound's call is its caller's skill ("Call Ilun", Asha), so each hero's Skills page lists only their own
  calls. Nothing to build. Check: a caller with two or more Vowbound (the plan names the callers per Vowbound in
  vowbound.json) sees them in Skills, in bind order.
- **The status page:** a "Bound" line under Swell lists the hero's Vowbound (new section, one line).
- **Loc keys:** `SKILL_CALL_NHOA`, `SKILL_CALL_HESK`, `SKILL_CALL_ETHREN`, `SKILL_CALL_KESH` (Kesh's call shows in Act III);
  `VOWBOUND_NHOA`, `VOWBOUND_HESK`, `VOWBOUND_ETHREN`, `VOWBOUND_KESH`; `STATUS_MENU_BOUND`, `STATUS_MENU_BOUND_NONE`.

## 4. Pell's Listen (he learns enemy abilities by listening; ADR 0201)

- **Need:** Pell fights from Ch10 (M3-C09-07). SPEC §3 (v1.5): "learns enemy abilities by listening to them".
- **Battle:** Pell's command list has **Listen** (a stance that costs a turn of rank). While he listens, a learnable
  ability used near him is **heard**: a float over Pell ("Heard: Tannin Jet") and a line in the battle log. A heard ability
  joins his **Calls** page (his learned skills) after the fight, with the victory panel's own row: "Pell learned …".
- **Help line:** on Listen, "Pell listens this turn. An ability used near him, he can learn." On a foe in the Read panel, a
  learnable ability carries a small ear mark; one Pell already knows carries the mark filled.
- **Bestiary:** each foe's page lists its abilities with the same ear marks.
- **Status page:** Pell's page has a "Heard" section: how many of the learnable abilities he knows ("Heard 3 of 12").
- **Loc keys (10):** `SKILL_LISTEN`, `HUD_HELP_LISTEN`, `HUD_FLOAT_HEARD_FMT`, `HUD_LOG_HEARD_FMT`, `HUD_RESULT_LEARNED_FMT`,
  `HUD_READ_LEARNABLE`, `HUD_READ_KNOWN`, `BESTIARY_LEARNABLE`, `STATUS_MENU_HEARD`, `STATUS_MENU_HEARD_FMT`; plus
  `HUD_CMD_CALLS` (his learned-skills page title) if Combat names it so.

## 5. Shops in Act II, and the heresy rules

- **Need:** act2_plan §4.5, §4.2. The Ansedra, Quellan and Hollowmere rows exist. Reedhollow trades only if the Kirru
  trade (Narrative). Order shops close to heretics from Ch14 (see [heresy.md](heresy.md)).
- **Screen changes:** none to the shop screen itself. A shop flagged `order: true` in shops.json refuses a heretic party
  with its own line before the menu opens.
- **Loc keys (5):** `SHOP_REEDHOLLOW_KIRRU` (if it exists), `INN_QUELLAN`, `INN_ANSEDRA_GUEST` (Sefir's house: a free rest,
  "You are his guests"), `INN_HOLLOWMERE`, `SHOP_ERR_HERETIC` (in heresy.md).

## 6. The act break (Ch16)

- **Need:** act2_plan §2 Ch16 C9: the act break, a Rhen voice-over, then Act III's card (`act_card.json acts."3"`, exists).
- **Screen:** none new. The act card and subtitle exist. Check: the break's voice-over plays as subtitles (M2-UI-100), and
  the card follows. The save prompt that follows an act break: the chapter autosave already covers it.
- **Loc keys:** none (Narrative's voice-over lines live in the .dlg).
