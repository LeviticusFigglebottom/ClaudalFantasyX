---
id: M3-CRB-008
title: "Ilun, Kahre and Virel (Act I Vowbound): final-quality check, intro (rise) and VFX anchor bones"
role: character
status: review
owner_session: "creatures-b (claude/creatures-b; worktree agents)"
reviewer: art
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041. The three Act I Vowbound (built by creatures: M3-CRE-638/640/641) are self-rendered at battle distance and in the call; any primitive read is fixed; each gets `vfx_core` and `vfx_keepsake` anchor bones (the summon and Swell effects start at the keepsake). As allies they carry no weak point in Act I (their held forms are Act III, paused).

## Done (2026-10-28)
- **Ilun** (d5101f4f): a thick manta, a knotted net of light, plumes, the float; 15.6k tris; wingspan 5.1 m.
- **Kahre** (6c7e72a3 + polish 6150705d): stone-and-iron anatomy, keratin plates, the anvil sternum, the casque with the
  hammer grown into it, a filament mane; 17.8k tris.
- **Virel** (bfd23910): an open S kite-serpent, varied scorched sail panels on a cane spine, a kite-dragon head, the
  tuning key; 17.8k tris; body 4.85 m (her test's Flare Line check 5.0 → 4.5 m).
- All three: `vfx_core` and `vfx_keepsake` (unweighted), held forms and `release` intact; Blender verify identical;
  Godot vowbound 83/0; pinned by tests/unit/test_creature_bosses_act1.gd. Each viewed in its self-render.
- Open: a true see-through spectral material needs a kit change (creatures'); Kahre's wrist seam is ragged up close;
  Virel's S is near edge-on from the held shot's front view; no portraits yet (ui-menus' bake).

## Review log
