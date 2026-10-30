---
id: M5-A3P-1700
title: "Act III UI: the closing credits roll (act3_ending CR): timed to credits_suite, the beach-rite vignette, faster on hold, skip once seen"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: cinematics
milestone: M5
request-from: lead
---
## Goal
ADR 0207: the Act III UI, starting with the closing credits (act3_ending CR: 7 min under `credits_suite`, the beach
rite as an in-engine vignette, then E7's post-credits lamp).

## Acceptance criteria
- [x] **CreditsRoll** (`game/ui/credits/`) and **CreditsRollModel**, Node-free; data in `game/data/ui/credits.json`.
  - Black; the sections climb the centre column over `roll_sec`, with a lead-in and an end hold.
  - A vignette (`beach_rite` at 62%) stops the roll, fades it and its black out, and emits `vignette_started(id)` for
    Cinematics to play it. Then the roll fades back in. It plays once.
  - Holding Confirm runs the roll 4x faster (keys and pad, from input events), never through a vignette.
  - Once the credits have been seen in full (`credits_seen`, declared in flags.tres), holding Cancel skips them. The
    hint at the foot names both, filled for the device in use.
  - At the end: `credits_seen` is set, and `next_scene` opens (the post-credits scene when Cinematics names it;
    empty: the title).
- [x] **tests/unit/test_credits_roll.gd (4/0):** timing, the vignette once, fast and skip rules, the view's climb and
      end, and a held pad button.
- [x] **Shot `credits_roll`** (pending_baseline), viewed.
- [x] **Sound hook:** a ui_sfx.json row (the end turns the page; nothing sounds under the music). The audio audit is
      clean.

## Notes
- **Content is facts only for now:** the title, original music, and the engine, font and MPFB2 licences.
  **LEAD-ASK** (log): who and what the credits should name. The human's credit, the tracks' roles, and the music's
  and voices' credits are the human's call, and nothing is invented here. Until then the 7-minute roll is sparse.
- **For Cinematics:**
  - **The vignette:** play `beach_rite` on `vignette_started` (it runs `hold_sec` 20 s; `ch18_haluna_lifted` picks
    its opening line).
  - **The post-credits scene:** set `next_scene` to E7's scene when it exists.
  - **The music:** match `roll_sec` to `credits_suite`'s length once audio renders it.

## Review log
