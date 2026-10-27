# Revenant tells (M3-RND-03)

Sefir's two tells, from the story (`docs/kb/story/characters/sefir_aurane.md`, act1_npcs.md §1.10): **his reflection in
water never ripples**, and **his shadow is faintly too sharp**. Both come from one node, `RevenantTells`
(`game/vfx/revenant/revenant_tells.gd`), with its numbers in `game/data/vfx/revenant_tells.json`. It works in any
level that has the project's water (`water_surface_body.gdshaderinc`) and shadowed DirectionalLight3Ds.

## Use

Add a `RevenantTells` (Node3D) anywhere in the scene and set `actor_path` to the actor's root (Sefir's character
node). It engages on the frame after `_ready`, so an actor that a parent adds in its own `_ready` is found.
- `still_reflection` and `sharp_shadow` switch each tell on its own.
- `lights` names the lights whose shadow of him turns sharp. Leave it empty for the brightest shadowed
  DirectionalLight3D in the current scene (the key).
- `engage()` and `disengage()` turn it on and off at runtime (a cutscene can call them). `_exit_tree` disengages.

## How it works

**The reflection.** The actor's capsule goes to the `hymn_still_actor_0` / `_1` globals every frame: the base and
radius, from his meshes' AABB padded by `capsule_pad_m`, with the heights in `hymn_still_actor_heights`.
- The water first tests the flat mirror ray against the capsules (as vertical cylinders).
- Where the ray meets one, it marches SSR along that flat ray. If the hit lands inside the capsule, that's his
  reflection, unrippled.
- Everything else, including the background seen past him, is marched along the rippled normal as before.
- The extra march only runs for the pixels where his mirror image falls.
- There are two slots. A third still actor gets none and ripples like anyone else, with a warning.

**The shadow.** A light can't soften one caster and not another, so:
1. The actor's meshes move to the **still layer** (18; 19 is the cutscene key light, 20 UndertowHalfRes). They
   move to it alone: a light casts any mesh that shares a layer with its `shadow_caster_mask`, so a mesh left
   on layer 1 too would still cast. Cameras and lights see layer 18 by default.
2. The key (the brightest shadowed DirectionalLight3D, or `lights`) drops that layer from its
   `shadow_caster_mask`, so it no longer casts him. The other lights (the rim) keep casting him softly.
3. Two copies of the key follow it every frame: one is shadowed, with `shadow_caster_mask` = the still layer and
   a `shadow_blur` (0.12) sharper than the key's (0.6 on the stage); the other is identical but `light_negative`
   and unshadowed.

Where nothing blocks the copies they cancel exactly, so no surface is lit twice. Where he blocks the positive
one, the key's light is removed with a crisper edge than the soft key gives everyone else: faint side by side
with Asha, not a cut-out.
- **Cost:** the positive copy is one more shadowed directional light, so it shares the directional shadow atlas
  with the key while the tell is engaged.
- **Spots don't work:** distant spot lights standing in for the key were tried first. In Godot 4.6.3 a spot 200 m
  out shadowed the light's side of the caster too, and at 60 m it showed acne and black tiles. The probe numbers
  are in the task's result.

## Limits

- **Low** has no SSR (`WATER_SSR_STEPS 0`), so it shows no reflection of anyone. Medium and up have the tell.
- **Close shots:** CutsceneKeyLight moves a close shot's cast onto layer 19, which removes the still layer while it's
  engaged. In those shots his shadow is the sun's soft one; the reflection tell is unaffected.
- The capsule is a cylinder around his whole AABB (arms out: wide). The background inside it is still marched
  rippled, because only hits on him take the flat reflection.

## Shots

`revenant_tells_reflection` / `_off` and `revenant_tells_shadow` / `_off` (`game/levels/_tests/revenant/`): Sefir
beside Asha on the Sefir stage, over 3 cm of rippled water and on the dry floor, with the tells on and off.
