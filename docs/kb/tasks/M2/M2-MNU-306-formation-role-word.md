---
id: M2-MNU-306
title: "A role word for each hero (characters.json) for the Formation page"
role: progression
status: todo
owner_session: ""
reviewer: ui
depends_on: [M2-MNU-07]
milestone: M2
request-from: ui
---
## Goal
The Formation page (M2-MNU-07) lists each hero by name, portrait and line, but it cannot say what each hero is *for* in a fight, because `game/data/battle/characters.json` has no role field. A player choosing who stands in the line needs one word per hero (the kind of thing that says "breaks guards" or "keeps the line alive"), in the game's own voice.

## Acceptance criteria
- [ ] `game/data/battle/characters.json` gains a `role_key` per hero (Rhen, Asha, Toma, Ysolde, and Pell once his row exists, M3-C09-07), pointing at a loc key.
- [ ] The words are added to a loc file (a new `game/data/loc/roles.csv` is fine) with one short word or two-word phrase each, original to this game and checked against `tools/banned_terms.txt` (no borrowed job or class names).
- [ ] `tools/validate_data.py` (or the existing characters check) knows the field is optional or required, as design prefers.

## Notes
- The UI side is small and the ui-menus track does it as soon as the field lands: the Formation row shows the word under the name (`game/ui/menus/formation/`), and the 130 % text-size fit is checked there.
- The enemies already carry `role_answer` (which hero answers each foe); a hero's role word should read well beside that.

## Review log
