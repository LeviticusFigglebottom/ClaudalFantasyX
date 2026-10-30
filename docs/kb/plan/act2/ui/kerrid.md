---
draft: pre-gate
---
# Kerrid's reveal (Ch15) in the party UI

- **The reveal** is at sea, by his own word (ADR 0020, 0022; act2_plan §4.3, §2 Ch15).
- **The rule:** his battle kit does not change (act2_plan §4.3). The UI changes only text and portraits.
- **The bible's words only:** "unrisen", "held". `tools/banned_terms.txt` bans the inspiring game's term for the lingering
  dead.
- **Before the reveal,** no UI may hint. Kerrid's breath shows no fog (rendering), and his rope-burns' held light shows in
  dim light (characters/rendering). Neither shows in any menu.

## 1. The codex page

- `kerrid` (People) keeps its Act I body until `ch15_kerrid_revealed`. Then a second body replaces it: what he told them
  about the stair at Corrow, in his own plain terms (the year only if his script says it). The entry shows **New** again (its read flag clears on the switch).
- **Loc keys (1):** `CODEX_KERRID_BODY_CH15`.
- Narrative writes it from kerrid.md §Act II and the reveal's script. It says "unrisen" once, as he does.

## 2. The dialogue portraits

- During the reveal his face rows are `grief` and `guilty` (art/characters/kerrid.md §face). `guilty` is not baked today.
- **At the gate:** add `guilty` to Kerrid's `portraits.json` emotions and bake it (portraits.md). DialogueBox falls back to
  neutral for a missing emotion, which would flatten the act's longest scene.
- **Test:** `test_hero_portraits` checks Kerrid has `guilty` once the row is added.

## 3. The Status page

- Act I's Status page shows Kerrid like any hero. After the reveal, one quiet line under his name and level, in
  `text_dim`: "Unrisen: held since the stair at Corrow" (no year: the beat sheets' rule that no one says 1001).
- No new stat, gauge or colour.
- **Loc keys (1):** `STATUS_MENU_KERRID_UNRISEN`.

## 4. Healing, revival and items

- **Ask Combat before the gate:** if any rule treats the unrisen differently, it must show where it applies. For example,
  if a revive item fails on him, its help says why, as Hollowed's does today ("{name} is Hollowed: this revive fells
  them"). If no rule differs (the plan says his kit doesn't change), nothing to build.
- **Loc keys (only if a rule exists):** `HUD_HELP_UNRISEN_<RULE>`.

## 5. Field presence and barks

- After the reveal his field barks change (Narrative, `.dlg` blocks on the flag), and Toma's do (his faith breaks).
- The party cards and the formation stay the same.
- No UI keys.

## 6. What the player must never see

- No status glyph, colour or tag in battle that marks him as unrisen. The reveal is a story beat, not a status.
- No codex or bestiary entry for "the unrisen" as a creature type.
- The Order's word for the Stilling stays in Narrative's text, never on a menu.

**Loc keys total (2–3).**
