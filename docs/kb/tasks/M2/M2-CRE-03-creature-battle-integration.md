---
id: M2-CRE-03
title: "Battle integration: enemies.json model field, the creature actor on the stage, validator and tests"
role: character
status: doing
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-02]
milestone: M2
request-from: lead
---
## Goal
An enemies.json `model` field that the battle stage turns into the actor scene (built on M2-UI-07's FighterStandIn "scene" hook), with clips played on attack, cast, hit, KO and phase change, falling back to the primitive. BattleVfx/BattleBossVfx anchors still land on the rim, polyps and toll. validate_data.py checks the field. Tests.

## Acceptance criteria
- [ ] See Goal; notes below record what shipped.

## Notes

## Review log
