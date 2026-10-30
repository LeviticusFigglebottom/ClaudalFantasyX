---
id: M5-A3P-1010
title: "Ch20 scripts in the game: down the eye, the six Vowbound and their releases, the Cage, the thank-yous (ADR 0207)"
role: narrative
status: review
owner_session: "claude/act2-plan"
depends_on: [M5-A3P-1006]
reviewer: cinematics
milestone: M5
---
## Goal
Ch20 follows Ch17–Ch19 into the game from the Act III drafts.

## Done
- The 18 Ch20 scenes are moved (git mv) to `game/data/dialogue/ch20/`, and their headers are no longer marked as drafts. dlgc compiles them.
- **Flags:** 9 Ch20 flags declared in `flags.tres`: `ch20_started`, six `ch20_<vowbound>_released`, `ch20_cage_broken`, `ch20_complete`.
- **New speakers (10):**
  - the six Vowbound: `ilun kahre virel hesk nhoa ethren`. They speak under their living names (Teyo, Daro, Wenna, Ama, Ressa, Corran) as aliases.
  - the four founders: `orin_tesk halde_moor isse_varan cael_imbrey`.
  - Each has a placeholder portrait and an appended voice row (`voices.json`). The name rows are in `game/data/loc/ch20.csv` (new, registered).
- **Light:** every release ends on its keepsake rising alone, and the founders stay held after the Cage. `tools/act3_rules.py` allows a lift in `*_release.dlg` only.

## Not in this task (requests)
- M5-A3P-1011 → cinematics: staging and flow.
- M5-A3P-1012 → audio.
- M5-A3P-1013 → combat: the seven encounters, the fight lines and the release flags.

## Review log
