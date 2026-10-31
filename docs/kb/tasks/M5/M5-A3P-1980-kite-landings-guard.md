---
id: M5-A3P-1980
title: "Kite traversal: every Kite landing puts the party on firm, dry ground (field guard)"
role: qa
status: review
owner_session: "hero-integration (claude/hero-integration, 2026-10-30)"
depends_on: [M3-UI-205]
milestone: M5
---
## Goal
Act III's Kite (SPEC §6.6, act_outline Ch18) flies the party to any place in `game/data/world/kite.json`. The map and
menu are ui-menus' (M3-UI-205); this task is the field side of the landing. Every destination and found secret must
land the party well.

## Acceptance criteria
- [x] `tests/integration/test_kite_landings.gd`: with the world open (`kite_flying` plus every row's flag), each
      landing's location is enterable, its zone has the named spawn, and the party placed there settles grounded
      within 1 s, no more than 1 m below the marker, out of deep water (FieldShore's `deep_water_m`), and does not
      fall walking 1.5 s out from it.
- [x] All 8 of today's destinations pass (`--filter=kite_landings`, 1/0). New rows (Act III towns, secrets) are
      checked as they land in kite.json.

## Notes
- 2026-10-30 (hero-integration): written and green on b38f751ee + this commit. Reviewer: qa.

## Review log
