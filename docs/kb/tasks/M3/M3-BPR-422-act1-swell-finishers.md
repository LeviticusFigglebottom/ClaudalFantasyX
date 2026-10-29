---
id: M3-BPR-422
title: Swell finishers for every Act I party member (Kerrid's weighted swing, Liss's reel-stop)
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-BPR-420]
milestone: M3
reviewer: rendering
request-from: lead
---
## Goal
The Lead's 02:14 item 4 (ADR 0041): every Act I party member's Swell plays a finisher of its own, with its own motion,
camera and VFX.

## State
- Rhen (Lamp Dive), Asha (Shallows Verse), Toma (Return Tide) and Ysolde (Written Light) already have theirs: the dive,
  verse, brace and glyph styles, their camera framing, and their effects.
- Kerrid and Liss join in Act I (Ch5 and Ch6), but their Swell techniques are combat's to write (M3-C05-06, M3-C06-05),
  so their finishers are staged ahead and play as soon as a technique lands:
  - `choreo.json` styles `swing` and `reel`, and `swell_style_by_hero` (`kerrid: swing`, `liss: reel`), used for any
    skill marked `"swell"` with no `style_by_skill` row.
    - `swing` follows kerrid.md's finisher clip: he closes in, holds the cleaver coiled through a long strike, then
      hauls it through flat and low. It is never overhead, so it reads apart from Toma's blow.
    - `reel` follows Liss's finisher clip: she winds at the hip and throws the gadget down onto the foe from a step
      out. It is not a run.
  - `camera.by_style`: `swing` plays finisher, then target; `reel` plays cast, then target.
  - `effects.json` `map.swell_by_hero` maps Kerrid to `swell_weighted_swing` (a flat, low sweep of iron with wet
    sand, plus heavy debris) and Liss to `swell_reel_stop` (a brass ring locking, then a salt-glass flash in bound
    glimmer).
    - BattleVfx plays them for a "swell" skill with no `map.skills` row.
    - They are prebuilt only when that hero is in the party.
    - `tools/vfx/gen_act1_ability_vfx.py` writes them; their sounds borrow `hit_none` and `status_apply` until audio
      (M3-BPR-421) gives them their own.
- Combat needs to do nothing beyond adding the technique (its `"swell": true` skill row and swell.json row). A
  `style_by_skill` or `map.skills` row of its own would override these.

## Acceptance criteria
- [x] Every Act I hero's Swell resolves to a finisher style with the finisher clip, its camera framing and an effect
  of its own (`test_battle_swell_finishers`, with a stand-in technique for Kerrid and Liss).
- [x] The swing stays low and holds longer than the finisher; the reel is thrown, not run.
- [x] A finisher is prebuilt only when its hero fights.
- [x] `validate_choreo` checks `swell_style_by_hero` names real styles.
- [ ] Viewed in a self-render once the technique and the heroes' battle actors are in a fight (no Kerrid or Liss
  battle actor scene is wired into battle_sandbox.json yet).

## Review log
