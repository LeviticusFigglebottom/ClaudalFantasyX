---
id: M3-CMB-1252
title: "Request (ui-menus): field-usable abilities and a field cast API for the Magic page"
role: combat
status: done
owner_session: ""
depends_on: []
milestone: M3
request-from: ui
---
## Goal
To combat-systems (FAST-TRACK 5). ui-menus builds the field Magic page (M3-UI-1251) and needs the rules from you,
node-free and tested, in the shape the Items page already uses (`ItemBattleAction.resolve_on` on
`PartySheet.combatant(cid)`, written back with `GameStateData.record_vitals`):

1. **Data:** `"field_usable": true` on the skills castable outside battle (Mend, Chorus Mend, and any cure or
   revive spell), in skills.json.
2. **API** (a suggestion; any equivalent is fine, just name it in this task):
   - `FieldCast.usable(caster: BattleCombatant, db: BattleDB) -> Array[StringName]`: the caster's known
     field-usable skills (the same skill list battle offers: characters.json + the Lattice).
   - `FieldCast.refusal(caster, skill_id, targets: Array[BattleCombatant]) -> StringName`: &"" when it can be cast,
     else a reason id (not enough MP, silenced or fallen caster, no one it helps, target fallen, target full).
   - `FieldCast.cast(caster, skill_id, targets) -> Dictionary`: applies it with the battle's own formulas (no rng,
     or a fixed one, so the field never rolls), spends the MP, returns `{ok, mp_spent, healed: {id: amount},
     cured: {id: [status]}, revived: [id]}`.
3. **Tests** for the three, including that a field Mend heals what a battle Mend would at the same stats.

ui-menus writes the page, the target picker, the words and the save write-back against it.

## Notes
- 2026-11-03 (ui-menus): superseded by combat-systems' own M3-CMB-05 `FieldSpell` (claude/combat-systems @ da778b9e),
  which the Magic page now binds by name (FieldMagicRules.live). Nothing more is asked here.

## Review log
- 2026-11-03 ui (the requester): withdrawn, superseded by combat-systems' M3-CMB-05 FieldSpell; nothing to review.
