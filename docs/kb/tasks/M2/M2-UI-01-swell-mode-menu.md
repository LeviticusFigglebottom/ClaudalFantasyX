---
id: M2-UI-01
title: Swell mode menu and timing-input accessibility
role: ui
status: doing
owner_session: "worktree-agent-ab3d864d1e75fe481"
depends_on: [M1-CMB-04]
milestone: M2
request-from: combat
---
## Goal
SPEC §6.2 says the mode is selectable. M1-CMB-04 ships the rules (`BattleSwell.set_mode`, `unlocked`) with no menu, and Rhen's timing ring with no assist option.

## Acceptance criteria
- [ ] Players can choose a hero's fill mode from the unlocked ones, out of battle (party or Customize menu) and/or from the battle Swell page. Each mode row shows `name_key` and `desc_key`.
- [ ] An accessibility setting for timing inputs, such as a wider window or auto-good, applied through the input row rather than in the engine. Coordinate with Combat on the numbers in formulas.md § Swell.
- [ ] Art review of the Swell gauge placement and the ring panel (see tech/ui.md "Swell", deviations).

## Review log
