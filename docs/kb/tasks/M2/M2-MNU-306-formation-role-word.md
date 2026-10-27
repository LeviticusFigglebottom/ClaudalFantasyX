---
id: M2-MNU-306
title: "A role word for each hero (characters.json) for the Formation page"
role: progression
status: review
owner_session: "claude/ui (ui-menus; progression's UI-adjacent work, Lead 2026-10-27)"
reviewer: ui
depends_on: [M2-MNU-07]
milestone: M2
request-from: ui
---
## Goal
The Formation page (M2-MNU-07) lists each hero by name, portrait and line, but it cannot say what each hero is *for* in a fight, because `game/data/battle/characters.json` has no role field. A player choosing who stands in the line needs one word per hero (the kind of thing that says "breaks guards" or "keeps the line alive"), in the game's own voice.

## Acceptance criteria
- [x] `game/data/battle/characters.json` gains a `role_key` per hero (Rhen, Asha, Toma, Ysolde, and Pell once his row exists, M3-C09-07), pointing at a loc key.
- [x] The words are added to a loc file (a new `game/data/loc/roles.csv` is fine) with one short word or two-word phrase each, original to this game and checked against `tools/banned_terms.txt` (no borrowed job or class names).
- [x] `tools/validate_data.py` (or the existing characters check) knows the field is optional or required, as design prefers.

## Notes
- The UI side is small and the ui-menus track does it as soon as the field lands: the Formation row shows the word under the name (`game/ui/menus/formation/`), and the 130 % text-size fit is checked there.
- The enemies already carry `role_answer` (which hero answers each foe); a hero's role word should read well beside that.

## Implementation notes (ui-menus, 2026-10-27)
- `characters.json`: `role_key` on all six heroes (`ROLE_RHEN`..`ROLE_LISS`), words in `game/data/loc/menus_formation.csv`: Swift striker, Mender, Holds the line, Hexes and elements, Breaks armour, Tinker and thief (from lattice.md's niches and the M3 hero notes; checked against banned_terms.txt).
- `tools/validate_data.py` `character_role_errors`: every hero row needs a non-empty `role_key` (loc-checked like every `*_key`); `tools/tests/test_character_roles_validate.py`.
- Formation: the role word leads the place line ("Swift striker · Active line, place 1 of 3"; `FORMATION_MENU_ROLE_PLACE_FMT`), so the detail gains no height (a separate line pushed the fallen warning out at 130 %). `PartySheet.hero_role(id)`; `FormationMenu.role_text()` / `place_line()`.
- Tests: `test_formation_menu.gd` `test_the_role_word_shows_under_the_name`; formation 18/0, party 24/0, pseudo 22/0.
- Note for reviewers: Kerrid's and Liss's kits are provisional (M3-C05-06, M3-C06-05); revisit their words if the kits change.

## Review log
