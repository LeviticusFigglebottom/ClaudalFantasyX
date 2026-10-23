---
id: M1-CHR-08
title: Import the cloth band-id map without mipmaps
role: character
status: todo
owner_session: ""
depends_on: [M1-RND-09]
milestone: M1
request-from: "rendering"
---
## Goal
`assets/characters/shader_test/sleeve_bandid.png.import` has `mipmaps/generate=true`. Since M1-RND-09 the cloth shader samples `tex_band_id` with `filter_nearest` (no mipmap filtering), so the mips are never read: there is no bleed any more, only wasted VRAM. The contract now exempts id maps from the "mipmaps on" rule (docs/kb/tech/character_shading.md, "Every map" and the `asha_sleeve_bandid` row).

## Acceptance criteria
- [ ] `sleeve_bandid.png.import`: `mipmaps/generate=false` (and the same for the production `asha_sleeve_bandid` when it lands)
- [ ] The texture build script writes id maps with each band region at least 2 texels wide (contract row)

## Notes
Owner of `assets/characters/**` is Character, so Rendering did not edit the import. Expect `char_cloth_gold` to stay within its threshold (the shader already ignores the mips).

## Review log
