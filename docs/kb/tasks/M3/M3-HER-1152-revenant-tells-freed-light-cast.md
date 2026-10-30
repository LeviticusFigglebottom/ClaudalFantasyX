---
id: M3-HER-1152
title: "RevenantTells casts a stored light before its is_instance_valid check (a 'Trying to cast a freed object' on teardown)"
role: rendering
status: review
owner_session: "pc-gpu (gpu/m3-her-1152-1124-freed-casts)"
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
In `game/vfx/revenant/revenant_tells.gd:162`, `var light := p[0] as DirectionalLight3D` runs before
`if not is_instance_valid(light)`. A paired light that was freed while it's still listed (a zone torn down by the
router's swap into a fight) is a script error on the cast, which is the human's "Trying to cast a freed object". The
twins at `p[2]`/`p[3]` are cast without any check.

## Acceptance criteria
- [x] Check `p[0]` (and the twins) with `is_instance_valid` before casting them.
- [x] Remove this task's KNOWN row from `tools/freed_cast_lint.py` (`python3 tools/freed_cast_lint.py` shows 0 hits for the file).

## Notes
Found by integration-qa's freed-cast lint. The same bug in HeroFieldParty.should_hide reproduced the human's message
exactly, in `test_qa_party_spawns::test_a_freed_sequencer_is_not_cast`. Filed rather than fixed because
`game/vfx/revenant/**` is Rendering's.

## Review log

- pc-gpu (2026-10-30), gpu/m3-her-1152-1124-freed-casts: `--filter=_thread` 40/0 with no "Error calling deferred method", `--filter=revenant` 8/0, `--filter=underwater` 8/0. freed_cast_lint has no revenant_tells hit. Its one remaining hit, ebbing_motes.gd:168, is env-art-b's (M3-HER-1161, fixed on claude/env-art-b @ e884cb93), so test_freed_cast_lint stays red on the integration branch until that lands.
