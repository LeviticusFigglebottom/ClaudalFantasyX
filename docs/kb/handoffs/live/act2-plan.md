# Live log: act2-plan

Branch `claude/act2-plan`, cut from the integration branch `claude/new-session-mj8c3c` @ 57ba06b2 (2026-10-30).
Lead: `session_01Bg3iP7cPGyjbX4CyniBahc`. Mandate: ADR 0203 §"Preparation now" (a planning session; **docs only**:
no game content, scene, asset, data table or test changes while ADR 0041 stands).

## Scope
- `docs/kb/plan/act2_plan.md`: the Act II work list (Ch10–Ch16), the inventory summary, the critical path, the risks, the task index.
- `docs/kb/plan/act2_inventory.md`: the branch-by-branch evidence for the inventory.
- `docs/kb/plan/act2_tracks.md`: the **proposed** track split, ownership globs and SESSION-BRIEFS rows (the Lead applies them).
- `docs/kb/tasks/M4/M4-A2P-*.md`: 67 gap tasks, `status: blocked`, `blocked-by: ADR 0203`.
- **Id block:** `M4-A2P-001`…`M4-A2P-199` (no other branch uses the `A2P` prefix).

## NEW ACCOUNT (from 2026-10-25)
- 2026-10-30: plan and track-split drafts committed.
- 2026-10-30: inventory (every `origin/claude/*` branch), 67 tasks, critical path and risks done. See MERGE-READY below.

### LEAD-ASKs (each has a default the plan already uses; overrule any)
- LEAD-ASK: **The gate's flip list** (act2_plan §3): 58 ADR-0041 tasks go to `todo`, 18 Act III ones stay blocked, and 3 close (M3-AUD-804/805 superseded; M4-AUD-1001 already satisfied). M3-CRE-649 is split (Kesh's sheet is Act II, now M4-A2P-057). M3-AUD-837 is tooling. Confirm the list?
- LEAD-ASK: **Merge the three Act II commits** that are only on track branches (`e1db6170` kirru_roost determinism; the rim_crawler rebuild `2224e784`/`c3f61ea6`; `6b399185` grounding), in the gate's first batch, before anything is rebuilt. Default: yes.
- LEAD-ASK: **The tracks** (act2_tracks.md): add a **story** track (the seven beat sheets and scripts are the long pole); rename slice-polish → **cinematics**; fold combat into chapters and progression into chapters plus ui-menus; start eight tracks on day 1. Apply the ownership rows and narrow act1-chapters' `ch1[0-9]` glob?
- LEAD-ASK: **Beat sheets out of order:** the story track writes Ch10 first, then **Ch14 and Ch15** (the wedding and the reveal: M4's named set piece and the characters track's longest lead), then Ch11–13 and Ch16. The chained `depends_on` in M4-C1x-01 stays; the Lead waives it for Ch14/15. Default: yes.
- LEAD-ASK: **Design defaults** (Narrative and Combat confirm):
  - (a) Lowlight's sanctum is walked to a ledge and seen underwater, not swum;
  - (b) the wedding trap is a step-hold set-piece battle on the water-steps (ADR 0100's schema) before the barge escape;
  - (c) after the heresy, Order shrines go dark and refuse, and Saltwright and Kirru places keep working;
  - (d) the flat-engine is a breakable part with a timeline entry row, not its own combatant;
  - (e) the storm's waking at the Choir is a `scripted_escape` set piece.
- LEAD-ASK: **Human item (environment):** `lfs.github.com` is denied, and `assets/audio/music/act2/**` is LFS. Act II's 14 unwritten cues can't be pushed as specified. Can the human allow the host? Default meanwhile: files under 5 MB go as plain blobs outside the LFS paths (TRACK-RULES), bigger ones wait in PC-QUEUE.
- LEAD-ASK: **Human item (scope, SPEC §10.2):** should the cut list be put to the human for Act II now (Keth Pass folds into Quellan first, per act_outline's Cut Notes), or only if Act I's velocity data says so? Default: no cuts; revisit after Ch12.
- LEAD-ASK: M4-A2P-100 (`placeholder_audit.py --act 2`) is tools work that ADR 0203 allows **before** the gate. Hand it to integration-qa now as `todo`? It's filed `blocked` like the rest.

### MERGE-READY
