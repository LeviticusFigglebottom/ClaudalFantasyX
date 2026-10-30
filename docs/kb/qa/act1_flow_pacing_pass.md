# Act I flow and pacing pass (act1-chapters, 2026-10-29)

The Lead's brief (10-29 23:10), run on `lead/gate-big18` @ d00d3284 in a scratch worktree, with the same checks on
`claude/act1-chapters`.

## 1. The critical path: dead ends, soft-locks, backtracking, long stretches
- **Tool:** `tools/act1/flow_audit.py`, guarded by `tools.tests.test_act1_flow_audit`. It runs a fixed point from a new
  game over every Ch1–Ch9 flow group, beat and trigger, and follows the zone hand-offs. Code-set flags (trial and
  binding flags, Interactables' `sets_flag`) count as available, and beats a zone's code runs (`*_beat` config keys)
  are seeded.
  - Result: every arrive row, beat and trigger can run; every Act I zone is reached.
  - Two first-run findings were the tool's blind spots, not the game's: the Shell Shrine's net-float charm
    (`ch03_found_net_float`, set by an Interactable) and Coilspire's `stuck_key` (run by the trial's `seized_beat`).
- **The played path broke twice: request M3-CIN-1233 (slice-polish; the Lead approved the switch on 10-29).**
  - `first_playable.json` sent the Prologue to `ch02/haluna`, so Ch1 was skipped.
  - The slice's end card returned to the title, so Ch4–Ch9 were reachable only from the debug chapter select.
  - One `end_card` block also serves Ch9's act break, so each card needs its own next stop.
  - act1-chapters reviews the change: the `_thread` tests, plus stills of the Ch1 Drop and Ch4 NemeDoor arrivals.
- **Zone chain:**
  - `ch01/oruvel_underway` → `ch01/oruvel` → (slice) → `ch04/haluna_wake` → `ch04/brightwater_ferry`;
  - → `ch05/pemakar` ⇄ `ch05/ashcrown` → `ch06/brine_shoals` → `ch07/tamsule` ⇄ the Bell (the Tidecup);
  - → `ch08/corrow` ⇄ `ch08/coilspire` → `ch09/corrow_night` (strand → road) → the end card.
  - Every return trip has a new beat at its end (Pemakar after Ashcrown, Tamsule after the match, Corrow's storm after
    Coilspire).
- **Walking between beats:** straight-line legs between story triggers, × 1.5 detour, at the field run speed (3.6 m/s).
  - No leg is over ~75 s; the longest is the Ch4 wake's crossing of Haluna at night, which has barks along the way.
  - No visit walks more than ~3 minutes in total.
  - The long stretches are the trials (Ashcrown, Coilspire) and the random-fight roads, all content, so none goes
    5 minutes without a beat, a fight or a discovery.

## 2. Encounter density and difficulty
- **Random-fight density** (expected fights on each zone's critical route, the table's gaps plus a 12 m grace):
  - Brine Shoals ~4, Ashcrown's causeway ~3, Coilspire's headland 2–3, the derelict 1–2.
  - **Ch1's dive: ~4–5 (6 at most) on a 130 m route.** That's too dense for the opening. Request M3-CIN-1234
    (slice-polish) proposes 32–52 m gaps, about 3 fights.
- **Difficulty:** `tools/balance/sim.py` over every Act I suite (33; `ch02_tideline`, the slice tutorial, has none).
  - Every policy is inside its band (138/138).
  - Naive win rates step down through the act: Ch1 regulars 100% (tutorial), Ch3 ~70%, Ch4 ~48%, Ch5 27–52%,
    Ch6–Ch8 regulars 40–58%.
  - Every boss stops the naive policy (0–4%) and lets the smart one through: the Hullgnaw 86%, the Drownbell 84%, the
    spar wraith 100%, the Cinder Matron 100%, the Inquisitor 100%, the stair holds 100%, Undertow's Reach 86% (the act's
    climax).
  - No wall (smart ≥ 84% everywhere), and no walkover past the tutorial (naive ≤ 58% from Ch4 on).

## 3. Optional scenes and side spots
- Every side trigger is reachable (§1).
- Flags that optional scenes set and Act I never reads are later payoffs, per the beat sheets:
  - `ch09_heard_stair_clear` (log only; the Ending's E3);
  - `ch09_rhen_answered_toma` (Ch15).
- The only unplayed scenes are the Reefball match barks (`ch07_reefball_barks` and its nodes), filed as M3-RBL-1208
  (combat, todo).

## 4. Flag hygiene
- Every flag Act I reads is set somewhere: flow `when`, trigger `requires_flag`, layout states and variants, and
  dialogue `<<if>>`. Code reads go through those data rows.
- None is read in a chapter before the one that sets it.
