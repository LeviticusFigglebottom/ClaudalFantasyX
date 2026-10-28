# 0041 — Act I at final quality first; later-act work is paused

- **Status:** accepted (the human's directive, 2026-10-28)
- **Date:** 2026-10-28
- **Roles affected:** all
- **Author role:** lead

## Context
Tracks have been building ahead into Act II and later (the Ch10–12 kits, Ch11/12/16 balance, Act II and III music, the Kite foley, Act II menus, the Drowner and Wakefin) while much of the game as it is played today still shows greybox geometry, capsule stand-ins and placeholder art. The human directed that all resources go into fleshing out the game as it is played and meant to be experienced: no greybox or placeholder assets, areas or enemies.

## Decision
1. **Scope is the playable game: the title through the end of Act I (the Prologue, the M2 slice, Ch1–Ch9, including the Tidecup Reefball match).** Every zone, prop, NPC, enemy, boss, Vowbound, cutscene, VFX, sound and menu a player meets on that path reaches final quality.
2. **Later-act work is paused:** Act II and later (Ch10+), the Act III ending, and later-act music, foley, creatures, kits, menus and balance.
   - Commit and push what is in flight, mark the task `status: blocked` with `blocked-by: ADR 0041`, and stop.
   - Work already on a branch is kept and merged as is if it passes the gate. Nothing is reverted.
3. **"Final" means:**
   - no greybox mesh or material and no capsule or box stand-in;
   - no placeholder texture, icon, portrait or temp sound;
   - no `TODO`/`placeholder` art in anything the player can see or hear;
   - every enemy has its real mesh, rig, animation set, battle VFX and sounds;
   - every area is dressed, lit and walkable, with no visible seams or holes.
4. **The inventory is the work list:** `docs/kb/qa/act1_final_inventory.md` (integration-qa owns it), backed by `tools/placeholder_audit.py`. Every row becomes a task for the owning role. Act I is done when the audit reports zero items and a full headless playthrough passes.
5. More cloud sessions may be added where a role is the bottleneck. Ownership in `docs/kb/ownership.md` is split by chapter so they don't collide.

## Consequences
- Act II content, music and balance slip; the vertical slice and Act I get much closer to shippable.
- The M2 review (SPEC §16 Q7) still belongs to the human. This ADR does not decide it.
- To lift the pause, the human says so, and a new ADR supersedes this one.
