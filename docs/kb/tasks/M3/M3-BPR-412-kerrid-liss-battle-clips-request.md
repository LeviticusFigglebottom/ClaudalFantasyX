---
id: M3-BPR-412
title: "Kerrid's and Liss's battle clips for their kits' staging (contract clips and contact markers)"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-505]
milestone: M3
request-from: combat
---
## Goal
Battle-presentation has staged the Act I party kits (test_battle_party_kits: every kit skill resolves to a real
style with a contract clip and camera shots). Kerrid and Liss are still capsules in battle. When their models land
(Kerrid: M3-CHR-505), these are the contract clips their kits play. Each strike clip needs a `contact` marker, so the
reaction and the impact land on the blow (BattleClips.contact_sec, docs/kb/tech/battle_presentation.md "Clip contract").

| Hero | Skill | Style (choreo.json) | Clip played | Contact marker on |
|---|---|---|---|---|
| Kerrid | attack, fluke_cleave, snub_line | melee (a run, a lunge) | `attack` | the blow |
| Kerrid | anchor_fall (heavy, rank 7) | finisher (a longer run, a bigger lunge, the finisher framing) | `finisher` | the anchor's fall |
| Liss | attack | melee | `attack` | the blow |
| Liss | reel_shot (ranged) | item (a short step and a throw: she casts her line from range, never runs) | `item` | the line's release |
| Liss | flash_housing (blinds a foe) | support (a step, a cast) | `cast` | the flash |

Both also need the shared ones: `idle`, `ready`, `hit`, `dodge`, `defend`, `ko`, `victory` and the optional `revive`.
Until a clip exists, BattlePlaceholderClips keys a generated pose (M2-BPR-10). A real clip of the same name wins, with
no code change.

## Acceptance criteria
- [ ] Kerrid and Liss battle scenes with the clips above (contact markers on the strike clips).
- [ ] battle-presentation re-checks a freeze-frame per skill on a PC render.

## Review log
