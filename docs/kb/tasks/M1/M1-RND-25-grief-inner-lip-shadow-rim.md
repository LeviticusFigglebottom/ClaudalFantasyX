---
id: M1-RND-25
title: Grief mouth's black rim is the lip shadow on the inner-lip skin, which gets no cavity bounce (QA-08 fault A)
role: rendering
status: todo
owner_session: ""
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

## Review log
