---
id: M1-QA-06
title: Capture setup and Blender gate hardening (review-sweep-I)
role: qa
status: todo
owner_session: ""
depends_on: [M1-QA-04, M1-QA-02]
milestone: M1
request-from: "character"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [ ] Held capture values win over Tweens (apply after the tween step, or pause tweens) (capture_setup.gd ~:103-120)
- [ ] Globals restore to the previous live value where possible, or the limitation is documented in the shot schema
- [ ] A known-failure job still fails on a NEW failure signature (verify_blender_builds.py ~:371-386)
- [ ] A new .glb or Blender script not covered by any job fails the gate
- [ ] Asha's texture chain is covered or explicitly listed as out of scope

## Review log
