---
id: M3-HER-1124
title: "UnderwaterRig's deferred refresh_bounce_passes gets a freed scene root (request to the PC / rendering)"
role: rendering
status: review
owner_session: "pc-gpu (gpu/m3-her-1152-1124-freed-casts)"
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
`game/world/water/underwater/underwater_rig.gd` `_build_lantern` queues
`CharacterShaderTiers.refresh_bounce_passes.call_deferred(root)`. When the zone is freed in the same frame (a zone
change, or a test that frees its zone), the deferred call gets a freed object: "Error calling deferred method:
'GDScript::refresh_bounce_passes': Cannot convert argument 1 from Object to Object", twice per thread-suite run.

## Acceptance criteria
- [x] Defer a call that checks the root first, e.g.
      `(func() -> void: if is_instance_valid(root): CharacterShaderTiers.refresh_bounce_passes(root)).call_deferred()`.
- [ ] `--filter=_thread` ends with no "Error calling deferred method".

## Review log
