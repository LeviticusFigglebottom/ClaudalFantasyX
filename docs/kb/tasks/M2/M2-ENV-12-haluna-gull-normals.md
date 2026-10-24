---
id: M2-ENV-12
title: "Haluna lintel-gulls render dark: village.lintel_gull builds its body inside-out"
role: environment
status: doing
owner_session: "env-art"
depends_on: [M2-ENV-06]
milestone: M2
request-from: environment
reviewer: rendering
---
## Goal
Found by the M3-ENV-07 (Oruvel) worker: `assets_src/environments/kits/haluna/village.py` `lintel_gull` winds its
body's faces inward, so every Haluna gull shades dark. The Oruvel kit fixed its own copy only. Fix the Haluna
generator.

## Acceptance criteria
- [ ] Wind the gull body's faces outward in `village.lintel_gull`. Rebuild the `haluna_kit` job and check
      `verify_blender_builds` is identical apart from the gull pieces.
- [ ] Re-capture every Haluna shot that shows a gull (the lintel-gulls at H03 and others), view them, and
      re-approve only the drifted ones.
- [ ] Check the Brightwater ferry's "stem-gull" (it reuses the Haluna gull, M3-ENV-08) and re-approve its shots
      if they move.

## Review log
