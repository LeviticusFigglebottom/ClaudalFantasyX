---
id: M3-RND-03
title: "Sefir's revenant tells: a reflection that never ripples and a shadow that is faintly too sharp"
role: rendering
status: todo
owner_session: ""
depends_on: [M3-CHR-02]
milestone: M3
request-from: character
---
## Goal
The story's revenant tells for Sefir (`docs/kb/story/characters/sefir_aurane.md`, act1_npcs.md §1.10): **his
reflection in water never ripples**, and **his shadow is faintly too sharp**. Art supplies the actor and the names;
the effects are Rendering's (the water shader, the shadow setup).

## Acceptance criteria
- [ ] A render layer for "still" actors (proposed name `still_reflection`; Rendering picks the bit, avoiding 19 and 20,
      which the sequencer's key light and UndertowHalfRes already use) whose meshes the water's ripple distortion skips
      in the planar or screen-space reflection, so his reflection stays a mirror while everyone else's breaks up.
- [ ] A per-actor shadow without the soft penumbra the other characters get (for example a separate light-mask layer
      lit by a copy of the key with `shadow_blur` 0, or a per-actor contact-hardening override), "faintly" too sharp:
      noticeable side by side with Ysolde or Asha, not a hard cut-out.
- [ ] A test scene or shot pair beside another hero, viewed.

## Notes
- The actor: `assets/characters/sefir/sefir.glb` (`sefir_lod1.glb` for distance), stage
  `game/levels/_tests/characters/sefir/sefir_stage.tscn`.
- Environment owns the Brine Shoals water and the barge (M3-ENV-1000); the effect should be a shader or layer feature
  any level can use, so his Act II scenes (Ansedra's pools, the Drowned Choir) get it too.

## Review log
