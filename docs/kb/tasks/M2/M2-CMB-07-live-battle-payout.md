---
id: M2-CMB-07
title: Live battles pay out lume and drops (M2 blocker), with the victory panel listing them
role: combat
status: doing
owner_session: worktree-agent-aa4303cb02313a538
reviewer: lead
depends_on: [M1-CMB-06, M1-PRG-02]
milestone: M2
request-from: "lead"
---
## Goal
M2 blocker. `BattleEngine.currency_award()` and `drop_awards()` are computed at victory, but only the balance simulator reads them: a live battle never pays, so the purse stays at 0 and the shop and inn (M2-UI-06) are unusable.

## Acceptance criteria
- [ ] At a live victory (`persist_progress` on, no capture fixture) the engine's lume goes into the purse (`Wallet.earn`) and its drops into the bag (`Inventory.add`), through `PartyGoods` over `Game.state`, exactly once per battle. Escape and defeat pay nothing. Fixtures and tests never touch the save.
- [ ] The victory panel lists the lume (and the purse after it) and one row per dropped item, through loc keys.
- [ ] A starting purse from data, if the economy design needs one.
- [ ] Tests: a won battle raises currency and inventory exactly as the engine computed; a save/load round trip keeps them.

## Review log
