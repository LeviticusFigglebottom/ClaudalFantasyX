---
id: M2-CHR-03
title: Haluna villagers at slice quality (Neme, Osu, Pila, the lane child, three generic villagers)
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters; worktree subagent)"
reviewer: rendering
depends_on: [M1-CHR-03]
milestone: M2
request-from: lead
---
## Goal
The slice's speaking NPCs in Haluna (game/levels/ch02/haluna/haluna.tscn, m2-slice's scene) are capsule stand-ins.
Build them as characters from the base_body variants (MPFB2 donor, ADR 0021) with costume variants and face poses:
Neme, Osu (Pila's granddaughter), Pila, the lane child, and three generic villagers. Each GLB well under 5 MB.

## Acceptance criteria
- [ ] One reproducible build (Blender job, PROVENANCE rows) per villager GLB, shared modules reused, nothing copied.
- [ ] Face shapes from the shared API (asha.md §6.2) and a pose table per speaking NPC; costumes that read as Low
      Reaches villagers (story bible), with colour variants for the generic three.
- [ ] Review stage + shots on the hero stage, lavapipe baselines approved after viewing.
- [ ] characters.md lists the scene paths m2-slice swaps in for each capsule.

## Review log
