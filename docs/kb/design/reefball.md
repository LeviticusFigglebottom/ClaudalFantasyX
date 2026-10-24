# Reefball: Rules Engine (M3-RBL-01)

Owner: Combat/Systems. Code: `game/minigames/reefball/`. Data: `game/data/reefball/`. Tests:
`tests/unit/test_reefball_*.gd`, `tools/tests/test_reefball_validate.py`. Balance:
`tools/balance/reefball_sim.py`.

SPEC §6.10 asks for a turn-paused, tactical team sport played in suspended water, with a simplified
version for the Act I story match (M3) and a deeper league later (M6, "extended Reefball"). This is the
rules core for that story match: headless, deterministic, data-driven, and with no UI and no scene. The
UI track and the arena look build on its API and signals.

## Story constraints it serves

- **Ch7 "The Tidecup"** ([act_outline.md](../story/beats/act_outline.md), [ADR 0017](../decisions/0017-act-one-restaging.md)):
  Rhen dives for **Oruvel's side** under its captain **Tavi Orse**. Toma doesn't play. Nothing interrupts
  the match, so the engine has no interruption hook, and none should be added for Ch7.
- **The result never branches the story** ([ADR 0020](../decisions/0020-kerrid-restaging.md) (h)): win or
  lose, it only picks a reward. `ReefballMatch.outcome` is `win`, `loss` or `draw` from the player's side;
  the flow layer maps it to a reward and nothing else.
- **N-12, the arena** ([decisions_log.md](../story/decisions_log.md)): Reefball began as a Low Reaches
  drowning-rescue drill. The ball is a woven **float**, and a score is **bringing it up** through a single
  **ring at the top of the drop**, never a net at the side. The rules below are built on that.

## How it plays

**The drop.** The water hanging in the Tamsule Bell is modelled as five depth **bands**, from the top:
the **ring** (0, at the surface), high water, mid water, low water, and the **weep** (4, the lowest point,
where the drop weeps its column into the catch-pool). There is no left or right and no halves of a pitch:
position is depth only.

**One ring, one float.** Both sides score through the same ring. Whoever holds the float is attacking.

**The fetch rule** (from the rescue drill: you can't bring up someone you didn't go down for). A side may
only score a float it has **fetched**: carried, dived or passed to `fetch_depth` (low water) or deeper
during its possession. A float won high up has to go back down before it can come up. A kickoff float
starts at the weep, so it is already fetched.

**Contacts.** Play is turn-paused. Each contact, the diver holding the float takes one action:

| Action | What it does | Odds | Clock | Breath |
|---|---|---|---|---|
| **Rise** | Swim up one band with the float. Rising into the ring scores (fetched floats only). | Contested by the opponents in the carrier's band and the band above. Open water is sure. | 2 strokes | 2 |
| **Dive** | Swim down one band with the float. | Always sure. | 1 | 0 |
| **Pass** | Hand the float to a teammate in any band below the ring (nobody receives at the ring: a diver there is breathing). | Marked by the opponents in the receiver's band. An open pass of one band or less is sure; longer open passes lose odds per band. | 1 | 0 |
| **Loft** | Throw the fetched float up through the ring from high or mid water. | Contested by the opponents waiting at the ring (wardens) and those in the carrier's band. | 1 | 1 |

**Turnovers.** A missed action gives the float to a named opponent, shown before the action is taken:
a missed rise goes to the best stripper among the contesters, a missed pass to the opponent nearest the
receiver's band, and a missed loft to the best warden at the ring (else the best presser, else whoever is
nearest the ring). Nobody can hold the float at the ring, so a diver who takes it there sinks one band
with it, and the float is unfetched for their side.

**Breath.** Every contact, each diver below the ring loses `drain` breath and each diver at the ring gets
`ring_recover` back. Actions cost the actor breath too. A diver at or below `winded_at` is **winded**:
their own actions lose `winded_penalty` odds, and off the float they swim up to the ring to rest until they
are back to `rested_pct` of their breath. The carrier never leaves the float to breathe, so a carrier
who keeps it too long gets worse at everything. Passing to a fresh diver is the answer.

**Swimming.** After each contact every diver but the carrier swims toward the band their **role** wants,
one band a contact (two for a stroke of `fast_stroke` or more). Roles are data: each has an attack band
(while its side holds a fetched float), a fetch band (while the float still has to be fetched) and a defend
band, each either fixed (`{"band": n}`) or relative to the carrier (`{"rel": n}`). The shipped roles:

| Role | Attacking | Fetching | Defending |
|---|---|---|---|
| Lifter | two bands above the carrier | high water | one band above the carrier |
| Anchor | beside the carrier | low water | the carrier's band |
| Presser | one band above the carrier | one band below the carrier | the carrier's band |
| Ringward | high water | high water | the ring |

Attackers never wait at the ring. Movement is deterministic (no roll), so the positions after a contact
follow from the positions before it.

**Clock.** The match lasts `match_strokes` strokes. Each action spends its strokes, and every action costs
at least one (the validator checks), so a match always ends. A tie when the strokes run out goes to an
overtime period of `overtime_strokes`, where the next float up wins at once; after `overtime_periods`
periods it is a draw.

**Kickoff.** The match opens with `first_float`'s kickoff diver holding the float at the weep, both sides
in their roles' kickoff bands. After a score, the side that was scored on kicks off.

## Odds (`ReefballFormulas`)

Every coefficient is in `rules.json`; the formulas themselves hold no tuning numbers. Contested odds are
clamped to `[odds_min, odds_max]` (0.05 to 0.95), so only an uncontested action is ever sure.

- **Rise:** `base + edge_k × ((stroke + grip) / 2 − best contester strip) − crowd_k × (contesters − 1)`.
- **Pass:** `base + skill_k × (passer reach + receiver grip) / 2 − dist_k × max(0, bands − 1)`, then
  `− mark_k × best marker strip − crowd_k × (markers − 1)` when marked.
- **Loft:** `base + skill_k × loft − depth_k × (depth − 1) − press_k × pressers − ward_k × best warden ward`.
- **Winded actor:** `− winded_penalty` on any of the above.

## Tactical clarity (pillar 4)

The player always knows who acts next (the float holder) and what each action costs:
`legal_actions()` returns every legal action with its **exact** odds, its stroke and breath cost, who
takes the float on a miss (`fail_to`), whether a success scores, and the band it ends in.
`preview()` and `perform()` call the same functions, and `perform()` rolls one number against the
previewed odds (`roll < odds`). A test checks the two agree over many seeds.

## API for the UI and the arena

`ReefballMatch` (RefCounted, Node-free):

| Call | Use |
|---|---|
| `setup(db, match_id, seed) -> bool` | Builds the match from `ReefballDB`. False for an unknown match or side. |
| `begin()` | Starts the clock and kicks off. |
| `is_player_contact() -> bool` | The player's side holds the float: show the action menu. |
| `legal_actions() -> Array[Dictionary]` | The menu, each entry as `preview()` returns it. |
| `preview(action, target = &"") -> Dictionary` | `{action, actor, target, odds, strokes, breath, scores, fail_to, to_depth}`, or `{}` when illegal. |
| `perform(action, target = &"") -> Dictionary` | Resolves it: the preview fields plus `{ok, roll, success, holder, scored, strokes_left}`. Illegal actions return `{ok: false, error}` with no roll and no change. |
| `play_ai_contact(ai = null) -> Dictionary` | The AI decides the current contact (the match's opposing profile by default). The UI calls it on the opponents' contacts. |
| `snapshot() -> Dictionary` | Plain data for the HUD, debug overlays and tests: score, clock, holder, fetched, and each diver's band, breath and resting state. |

Signals, in this order after each contact: `action_resolved(result)`, then `float_scored(side, score)`
(on a score), then `divers_moved(moves)` (`[{id, from, to}]`, swims or the kickoff reset), then either
`contact_started(holder_id, side)` or `match_finished(outcome, score)`. `begin()` emits `divers_moved`
and `contact_started`. The UI and the arena only listen and call; they never write match state.

Other classes: `ReefballDB` (loads and indexes the tables; `from_tables()` for fixtures), `ReefballDiver`
(runtime state), `ReefballFormulas` (static odds), `ReefballAI` (the opposing side), and `ReefballSim`
(the balance runner).

**Determinism:** all randomness goes through `ReefballMatch.rng`, seeded in `setup()`. Each `perform()`
draws exactly one roll; the AI draws one more only when its profile's `whim_pct` is above 0. The same
seed and the same decisions always play the same match.

## Data (`game/data/reefball/`)

- `rules.json`: bands, `fetch_depth`, the stat and odds ranges, the clock, action costs, formula
  coefficients, breath, swimming, roles and AI profiles.
- `sides.json`: each side's divers (role, and the seven stats breath, stroke, reach, grip, strip, loft,
  ward, in `stat_min..stat_max`), its captain and its kickoff diver.
- `matches.json`: the two sides, `player_side`, `first_float` and the opposing `ai_profile`.

`tools/validate_data.py` checks all three (the M3-RBL-01 section): shapes, ranges, unique ids across
sides, known roles and profiles, captains and kickoff divers on their own side, every action costing a
stroke, and that every `*_key` has a loc row (in `strings.csv`).

**Provisional names, for Narrative to confirm:** the opposing side is the **Pemakar Terraces** (the story
names only "their opening round"), and Oruvel's two other divers are **Noa** and **Old Ama**. They are
loc rows only (`RBL_SIDE_PEMAKAR`, `RBL_DIVER_*`), so renaming them doesn't touch the rules or the ids.

## AI (`ReefballAI`)

The AI scores each legal action from its previewed odds: `odds × gain − (1 − odds) × turnover_cost`.
A success is worth `score_value` when it brings the float up, `advance_value` per band toward the ring
(toward the weep while the float is unfetched), `fetch_value` when it fetches the float, and
`fresh_value` × the breath a pass hands on. A loft below `loft_min_odds` is never taken. `whim_pct` is the
chance it takes its second-best action instead. The Tidecup opponent (`story_opponent`) is the same
brain with no fear of turnovers, an eagerness to loft, and a 40% whim: a good side that makes mistakes.

## Balance

`tools/balance/reefball_sim.py` plays the match for N seeds with the player's side under each policy in
`tools/balance/reefball_targets.json`, and the other side under `story_opponent`:

- **naive**: the masher. It carries the float itself: dive until it's fetched, then rise. It never
  passes or lofts.
- **smart**: the `smart` AI profile, a player who reads the odds on the menu.
- **story_opponent**: the opponent's own brain on the player's side (report only: is the opponent's
  side stronger than Oruvel?).

Bands: **naive 10–30%** wins (a masher should sometimes win, never usually), **smart 55–80%** (winnable,
not trivial), with smart's draws at most 15%. `tests/unit/test_reefball_sim.gd` checks the same bands at
200 seeds with 7 points of slack.

<!-- reefball-balance:start -->
Measured 2026-10-24, 2000 seeds, match `tidecup_opening` (`python3 tools/balance/reefball_sim.py --report`).

| Policy | Band | Win % | Draw % | Goals for | Goals against | Contacts | Turnovers | In band |
|---|---|---|---|---|---|---|---|---|
| naive | 10–30% | 18.4 | 12.3 | 0.58 | 1.36 | 38.1 | 10.6 | yes |
| smart | 55–80% | 66.8 | 4.0 | 2.22 | 1.42 | 41.2 | 11.4 | yes |
| story_opponent | report only | 55.2 | 5.5 | 1.83 | 1.55 | 45.0 | 12.9 | yes |
<!-- reefball-balance:end -->

### Tuning log
- 2026-10-24 (M3-RBL-01, first pass). The first draft scored about one float a side and the masher
  never won: every rise was contested by three defenders who always kept up, and a stolen float had to be
  fetched from the weep. Changes: rise base 0.6 → 0.8 with crowd_k 0.1 (a crowded rise is still bad, a
  lone presser isn't); loft base 0.3 → 0.4; passing costs no breath and rising costs 2 (carrying it alone
  should tire you; passing is the answer); the clock 40 → 48 strokes; up to three overtime periods of 8
  (draws were 15–25%); the opponent's AI lost its fear of turnovers and gained a 40% whim; and every
  Pemakar diver lost a point in every stat but breath. A sweep of the smart profile's weights showed the
  greedy AI tops out near 63–68% against this opponent whatever its weights, so the smart band is set
  from that ceiling.

## For M6 ("extended Reefball")

The core is built to grow without changes to the story match's rules:
- **More sides and a league:** more rows in `sides.json` and `matches.json`. Recruitment would write
  divers' stats from save data into a side row before `setup()`.
- **Techniques:** a new action is a row in `rules.json` `actions`, a formula in `ReefballFormulas`, and a
  branch in `preview()` and `_apply_success()`. Keep each one previewable.
- **Defensive decisions:** today the defending side only swims by role. A defensive contact (who presses,
  who wards) would be a second decision type on the same `contact_started` signal.
- **Rhen's stats from his party growth:** the side row is plain data, so the flow layer can fill Rhen's
  row from his level before the match.
- **The Weir** (N-12's alternative arena, if the human changes the form) needs no rule change: the bands
  are depth below the surface, and the ring is the surface gate.

## Originality (CLAUDE.md §2)

The inspiring game's sport is a horizontal pitch inside a water sphere, with two goals at the sides, a
keeper, two halves on a running timer, six-a-side teams, a stamina stat that tackles wear down, and
named special shots. Ours shares only what SPEC §6.10 mandates (a team sport in held water, decided at
contact moments). It differs in:
- **Geometry and goal:** depth bands instead of a pitch, and **one shared ring at the surface** instead
  of two side goals. Scoring means bringing the float up.
- **The fetch rule:** a float has to be taken deep before it can score, from the rescue drill.
- **Breath** is the resource, and it comes back only at the ring, so divers leave play to breathe.
- **No keeper:** anyone at the ring wards.
- **Four a side, one period** measured in strokes per action, with golden overtime.
- **No named shots.** The four actions are plain verbs.

The sport's terms and its named shots are on `tools/banned_terms.txt` (the M3-RBL-01 block), so a
near-miss in data, code or story fails the validator.
