---
id: M1-ARC-12
title: Never drop equipment when the item tables are missing or fail to parse
role: architect
status: todo
owner_session: ""
depends_on: [M1-ARC-11]
milestone: M1
request-from: "qa"
---
## Goal
From the review-sweep-H entries (file:line references there).

## Acceptance criteria
- [ ] MUST: if item tables are empty or failed to parse, no loadout repair runs and no save is written over a slot (a guard plus a loud error); test with a broken equipment.json
- [ ] Unknown item ids are kept in the bag as unknown pieces (round-tripped untouched) rather than dropped; only equipping them is refused
- [ ] A confirmed manual save over a newer build's slot keeps a numbered copy (S2)
- [ ] ADR 0018 amendment wording corrected (~:61 'at worst a hero's piece comes off')
- [ ] Nits: the battle_engine petrify literal comment; `Narrator (asha)` with a space errors; the validate_data player-detection handles instanced players

## Review log
