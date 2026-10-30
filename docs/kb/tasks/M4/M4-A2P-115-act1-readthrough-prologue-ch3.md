---
id: M4-A2P-115
title: "Request: Act I read-through fixes, the Prologue to Ch3 (as played on integration @ 4b1988109)"
role: cinematics
status: review
owner_session: slice-polish → cinematics (claude/m2-slice)
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To slice-polish (m2-slice), the owners of `game/levels/ch01–ch03/**`, `game/data/dialogue/ch01–ch03/**` and the slice
flow. The Lead asked story for a read-through of the as-played script order from New Game through Ch9, looking for
scenes that play out of order, repeat, or refer to something the player hasn't seen yet.
`tools/act1/flow_audit.py` is clean at the flag level, so these are content findings. Each was traced through the
flows, layouts and scenes, and the dialogue ones were re-read line by line. The layout ones (A2, A4–A6) are traced from
trigger coordinates and flags: check the walk in-engine.

| # | Kind | Sev | Where | What the player gets | Suggested fix |
|---|---|---|---|---|---|
| A1 | unseen | **high** | `dialogue/ch03/ch03_dock_at_night.dlg:29` "You leave the day after tomorrow." | Rhen states Asha's departure as fact, and his guardian request rests on it, but no line on any path tells him. The overheard "Two days…" fragments are optional and never answered (vertical_slice B03: he "misses what they add up to") | Rhen asks instead ("You're leaving, aren't you? The bag at Neme's."), or Asha tells him earlier (B05) |
| A2 | order | med-high | `levels/ch01/oruvel_underway/oruvel_underway_layout.json`, triggers `low_lights` / `oil_slug` | The gallery opens onto the gauge room before z −32, so C1-05 "the low lights" (the first held light; act1_ch01 "never cut") can be skipped, or seen after the gauge wheel | `requires_flag: ch01_saw_low_lights` on `oil_slug`, or widen `low_lights` across the gauge-room mouth |
| A3 | order | med | `dialogue/ch02/ch02_low_tide.dlg:9-11` vs `:15-18` | "Go now / Not yet" is offered before Asha's "Come and see it, Rhen" and Toma's "He is not sworn to anything", so Rhen agrees before he is invited | Move the tide explanation and the invitation above the choice; keep Toma's objection and "I'm already walking" after "Go now" |
| A4 | order | med | `levels/ch02/haluna/haluna.tscn`: `OverhearDock`, the dock `Talk`, Osu's `Talk`, `CausewayHeadUnsaved` | Reachable at dawn, before Neme's table (B02): B03 fragments, Pila's Granddaughter ("She'll be waiting at the causeway") and Toma's causeway rule before any causeway walk is proposed | `requires_flag = &"ch02_ate_at_nemes"` on those four |
| A5 | repeat | med | `haluna.tscn`: each `Overhear*` and its villager's `Talk` use the same scene, about 2 m apart | Every "Cantor" fragment plays twice, word for word (overheard, then again on Listen) | Give each `Talk` its own follow-up bark; keep the fragment overheard-only |
| A6 | repeat | low-med | `haluna.tscn` `Overhear*` (`once = true`, no `sets_flag`) | A fragment re-fires after any reload of Haluna (the tideline battle's return, a shrine load) | `sets_flag` per fragment (`ch02_overheard_market/_chapel/_dock/_lane`; declare them) |
| A7 | repeat | low | `flow/chapters/ch01.json:111` barks map, `ch01_bark_roof_dive.dlg` | The roof dive replays in full on every later Listen; act1_ch01 has it as a one-off | Set `ch01_roof_dived` in the dive; map to a short after-bark once set |
| A8 | continuity | low | loc `FLOW_END_CARD_VOICE` "a girl I'd known for two days." | Plays the night of the day they met (vertical_slice §0: dawn to night) | "a girl I'd known for a day" (Narrative wording) |

## Acceptance criteria
- [x] A1–A8 fixed (5a935953), each below.

## Review log
- 2026-10-30 cinematics (slice-polish): all eight fixed at 5a935953.
  - A1: Rhen asks "You're leaving, aren't you? The bag at Neme's." (he saw it in B02's insert), and Asha gives the day.
  - A2: `oil_slug` requires `ch01_saw_low_lights`; `low_lights` now spans z −22..−34, the gauge room's whole mouth.
    test_ch01_thread asserts both (fails on the old layout).
  - A3: the tide and the invitation precede the choice; Toma's objection and "I'm already walking" follow "Go now".
  - A4: the four `Overhear*`, the four villager `Talk`s, Osu and `CausewayHeadUnsaved` require `ch02_ate_at_nemes`; a
    dawn test asserts none plays. The first-playable thread now talks to the villagers after B02.
  - A5: each `Talk` plays its own follow-up (`ch02_bark_<x>_listen`, new lines, still no "Cantor"); their night
    variants follow. The fragment stays overheard-only.
  - A6: each fragment sets and is blocked by `ch02_overheard_<x>` (declared in flags.tres).
  - A7: the dive sets `ch01_roof_dived`; later Listens map to `ch01_bark_roof_after` (two lines).
  - A8: "a girl I'd known for a day".
  - Checks: haluna 66, ch01 20, ch01_thread 2, _thread 40, dialogue 86, fp_ 30, all 0 failed. Narrative: please review
    the four Listen follow-ups and the roof after-bark (new lines).
