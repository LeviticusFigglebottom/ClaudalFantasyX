---
id: M4-A2P-1005
title: "Request: two Ch1 story prompts are lost before they show; the Ch3 trial hint holds too briefly"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To slice-polish (`game/levels/ch01/**`, `game/levels/ch03/**`). This comes from the Lead's Act I tutorial clarity pass.
Story has fixed the prompts' wording (commit on claude/act2-plan): the tether no longer offers "climb back up", and the
shutter now says what opening it does.

| # | Sev | Where | Problem | Suggested fix |
|---|---|---|---|---|
| F2 | **high** | `game/levels/ch01/ch01_zone.gd:60-70`; `oruvel_underway_layout.json:50,70` | The **tether prompt is usually lost.** The movement prompt reveals for about 2.1 s and holds 3.5 s. The tether trigger is 9 m from the `Drop` spawn (about 2.7 s at a run). `prompt()` marks the prompt seen, then drops it when another line is showing ("the flag is spent") | Queue a prompt that arrives while another plays; don't mark it seen and drop it |
| F3 | **high** | `oruvel_underway_layout.json:76-77` | The **shutter prompt is cut off by the wickfry fight.** The fight trigger is 2 m beyond the hint trigger, both span the gallery, and the fight frees the zone mid-line. The prompt is already marked seen | Move `shutter_hint` to just after `GalleryAfter`, or have the wickfry beat wait for the hint to finish |
| F7 | low | `game/levels/ch03/shell_shrine/shell_shrine_level.gd:130-134` | The trial's only hint ("Start at the spring. Follow the water, not the stone.") plays once, with the default 1.5 s hold (about 2.8 s on screen). The Ch1, Ch5 and Ch8 hints hold 3.5 s | Set `auto_advance_hold_sec` from data to 3.5 s |

## Acceptance criteria
- [ ] F2 and F3: both prompts show on a straight run through the Underway.
- [ ] F7 fixed, or answered here with a reason.

## Review log
