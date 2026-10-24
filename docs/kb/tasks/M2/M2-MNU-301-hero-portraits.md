---
id: M2-MNU-301
title: Hero portraits in every menu, rendered from the characters track's models
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-05]
milestone: M2
request-from: lead
---
## Goal
The human's playtest note: "parts look primitive". Replace every placeholder initial or box in the menus (Status, Equip, Lattice, Formation, Shop) with real portrait renders of Rhen, Asha and Toma, made from the characters track's models by a reproducible lavapipe portrait renderer under `tools/`, with a PROVENANCE row for each image. Add expression variants where the face shapes allow. See ADR 0120.

## Acceptance criteria
- [ ] `tools/portraits/` renders every portrait from source (the hero `.glb`, hero materials, face poses) on lavapipe; one command rebuilds them all.
- [ ] Portrait PNGs under `assets/ui/portraits/heroes/`, each with a PROVENANCE row.
- [ ] Expression variants (neutral plus those the face poses allow).
- [ ] A small `HeroPortraits` lookup (id + emotion → texture, falling back to neutral, then to the old initial).
- [ ] Status, Equip, Lattice, Formation and Shop show them; tests; shots re-approved after viewing.

## Review log
