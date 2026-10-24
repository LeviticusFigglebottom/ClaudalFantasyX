---
id: M2-AUD-13
title: B06 causeway route ambience: saltgrass wind and tidepools
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-05]
milestone: M2
request-from: lead
---
## Goal
The route's beds (vertical_slice.md B06: a tidal causeway of saltgrass and coral boulders, exposed at low tide, tidepools and wind).

## Acceptance criteria
- [x] Seamless beds at −26 LUFS: causeway_wind (saltgrass hiss, gusts), tidepools (trickles, small pops, a far surf line); ambience.json rows; PROVENANCE; loudness targets.

## Notes
- Done in a worktree agent (claude/audio). Source `assets_src/sfx/causeway_ambience.py` (render_all job kind
  `ambience_loop`, with its own 1.2 MiB size budget: `AMBIENCE_JOB_BUDGETS`, because the M2-AUD-05 field beds already
  fill their 2.5 MiB). Periodic by construction (circular noise, whole-cycle modulators, wrapped events, steady-state
  bus processing), so there is no end crossfade.
- `ambience/causeway_wind.ogg`, a 52 s loop: the wind's low body breathing in gusts (the lead, 0 LU), saltgrass hiss −3,
  blade flutter −8 (its rate rises in the gusts and its phase is whole-cycle), grass swishes −9, a boulder whistle at
  gust peaks −15. Decoded −25.85 LUFS, TP −13.4 dBTP, 0.50 MiB, seam flux ×1.36.
- `ambience/tidepools.ogg`, a 46 s loop: trickles (Minnaert bubble streams, the lead, 0 LU), far surf line −3, drips
  −7, gurgles −8, pops −9, breeze −9. Decoded −26.21 LUFS, TP −5.26 dBTP, 0.50 MiB, seam flux ×1.53.
- Both are q1 with a −6 dBFS ceiling. Bus levels were measured (`bus_lufs`), set and re-measured on plan within 0.1 LU.
  `--determinism`: identical. Each has an `ambience.json` row; neither has a zone row (the causeway scene doesn't exist
  yet; M2-AUD-12 asks m2-slice). Suggested use: `causeway_wind` along the route, plus `tidepools` near C03. The
  `.import` files are committed with the loop settings synced. PROVENANCE rows are in place, and the listening notes
  are in "M3: Oruvel, the living funeral, the causeway beds".

## Review log
