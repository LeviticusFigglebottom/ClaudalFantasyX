---
id: M3-CMB-01
title: Ch8 Fisher Stair set-piece battle pieces (scripted timeline entries, objective victory, scripted escape, party locks)
role: combat
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel; m2-slice owns Act I gameplay and narrative). Ch8's evacuation set-piece (`docs/kb/story/beats/act1_ch08.md` §5a and §9 Combat) is three chained scripted battles plus the Undertow's Reach. All of it stays in the existing CTB engine, with no real-time system. It needs these new building blocks:
- **A scripted timeline entry with no HP,** used three ways:
  - **the Climb:** each of its turns brings a group up, and spawn delays push it back;
  - **the Surge:** untargetable, it brings in reinforcements;
  - **Pell:** a guest who casts a telegraphed Storm-Call that removes one moving spawn.
- **Victory on an objective,** a quota of Climb turns, plus a `scripted_escape` outcome for the Reach's last phase.
- **Untargetable / damage-immune phases.**
- **Party locks:** Toma is locked in his slot, with his Attack replaced by the Stand Firm counter stance; Kerrid is unavailable.
- **Skills:** Liss's Haul (Haste on the Climb) and Toma's Hold the Stair (he takes the next hit aimed at the Climb).
- **Fields:** the `storm_dark` field, and Virel's Flare Line clearing it.
- **Sim:** a `ward_guard` sim policy.
- **Bands:** waves at 85–95% role-answer; the Reach at 75–85% role-answer and ≤ 10% naive.

The engine stays headless and deterministic (CLAUDE.md §3). Formulas change only together with their docs and tests.

## Acceptance criteria
- [ ] Each piece lands with unit tests in `tests/unit`, the battle coverage doesn't drop, and `sim.py --check` passes with the new bands.
- [ ] The data schema is documented in `docs/kb/design` so M3-C08-02 can write the waves as data.

## Notes
- Requested by m2-slice (cinematics), the Act I owner. M3-C08-02 depends on this.

## Review log
