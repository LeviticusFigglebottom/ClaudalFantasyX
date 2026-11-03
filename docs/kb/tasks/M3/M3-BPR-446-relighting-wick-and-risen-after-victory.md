---
id: M3-BPR-446
title: "Request (FAST-TRACK): check the Relighting Wick's battle VFX, and the fallen standing up on the result screen"
role: combat
status: todo
owner_session: ""
depends_on: [M3-CMB-03, M3-CMB-04]
milestone: M3
request-from: combat
reviewer: combat
---
## Goal
To battle-presentation. The human's playtest (2026-11-03), FAST-TRACK 5. combat-systems made the Relighting Wick (revive) reachable from Ch2 (Haluna Market, the Hullgnaw's and Spar-Wraith's drops), so players will use it far more in Act I.

## Asks
- [ ] The Wick's battle VFX (`effects.json` `relighting_wick`, the revive clip on a KO'd hero, `battle_sfx.json` "heal") reads clearly as a REVIVE, distinct from a Salt Tonic heal: a flame caught from the taper to the fallen one's chest (lore: the glossary's "Relighting Wick"; "lamp" is a living being's inner glimmer). If it already does, close with a note and a still.
- [ ] M3-CMB-04: after a won fight the KO'd now leave the battle at 1 HP (BattleSpoils.returning_party; the engine's combatants are not changed, so the stage keeps its KO poses). If a fallen hero should be seen getting up during the victory beat or the result screen, that is yours to stage; the data is `BattleSpoils.returning_party(engine)` (HP 1 for each member at HP 0 after a win).

## Review log
