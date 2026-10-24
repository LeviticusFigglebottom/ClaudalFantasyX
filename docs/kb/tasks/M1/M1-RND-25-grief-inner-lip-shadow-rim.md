---
id: M1-RND-25
title: Grief mouth's black rim is the lip shadow on the inner-lip skin, which gets no cavity bounce (QA-08 fault A)
role: rendering
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: character
depends_on: [M1-RND-24]
milestone: M1
request-from: "rendering"
---
## Goal
QA-08 fault A (docs/kb/qa/gpu/2026-10-24-qa-08-asha.md) is a hard black rim around the open grief mouth. QA put it
down to the asset or texture and asked for a key-shadow-off check first. M1-RND-24 ran that check on lavapipe (High,
2×, `qa08/crop_grief_rim_shadow_off.png`):

- **With the key and rim shadows off, the rim disappears entirely**, and the interior lights up. So it's the lips'
  shadow, not a bake.
- **The rim isn't on the mouth-family surfaces.** With the mouth bag, teeth and tongue painted green, the dark band is
  outside the green: it's `skin_head`, the inner roll of the lips. That skin is in the lips' shadow and, unlike the
  mouth family, gets no cavity bounce. The skin shader has none.
- M1-RND-24 doesn't change it. Both Asha stage lights are directional, and their bounce was already unshadowed.

## Acceptance criteria
- [ ] Choose and document one of these, with Character:
  - (a) Character assigns the inner-lip roll's faces to the `mouth` material, so it gets the bounce. That's an asset
        change in `assets_src/characters/asha/` (Character-owned): file it as a request.
  - (b) A masked cavity-bounce term in the skin family, keyed to a mouth-rim mask that the head bake provides
        (vertex colour or an ORM channel).
- [ ] lavapipe and GPU: the rim is gone or softened in `asha_face_grief` at High and Low. Closed-mouth shots are
      unchanged. List the drift and RMSE for the Lead.

## Delivery (2026-10-24, characters: option (a), the Character fix, as the Lead asked)
- The lips' inner roll moves to the `mouth` material (the mouth family, with the cavity bounce):
  `build_asha.inner_lip_vertices` picks skin vertices within 5 mm of the contact line, inside 0.85 of the mouth's
  half-width, whose normal does not face forward (depth behind the contact picked up the lower lip's front at the
  corners); `head_materials` assigns faces whose corners are all on it. Asha, Rhen and Toma use the same helper.
- The `mouth` material now samples the head atlas (`tex_albedo`, white tint): asha_textures paints the bag its old flat
  colour (#471A17, `MOUTH_BAG`) and the inner-lip faces (the `INNERLIP` bake term) as mucosa. Toma's mouth family moved
  from StandardMaterial3D to character_mouth too.
- **Result (lavapipe):** the grief rim is softened: the lower lip's inner edge reads red instead of black. The upper
  edge stays darker (the upper lip's own shadow on the teeth and its inner roll). Closed-mouth shots: only a thin sliver
  along the seam changes material. GPU check (High and Low) goes to the PC.
- Asha's GLB 4.65 MB (+0.04), Rhen 4.41, Toma 4.90 MB (all under 5 MB; Toma's is tight).

## Review log
