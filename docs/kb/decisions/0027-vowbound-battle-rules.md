# 0027 — Vowbound battle rules: the call stands the party down and costs the caller's rank

- **Status:** accepted with amendments A1–A3 (review-sweep-P, Design, 2026-10-24; see "Acceptance" below)
- **Date:** 2026-10-24
- **Roles affected:** Combat, UI, Narrative, the m2-slice track (the Drownbell)
- **Author role:** Combat (M2-CMB-04)

## Context
SPEC §6.3: a summoned Vowbound replaces the whole party on the field, with its own HP, abilities and Swell, and grows with Asha's stats. The SPEC does not say what the call costs, when the party comes back, or what happens when the Vowbound falls. formulas.md listed "Vowbound stat scaling from Asha" as not yet specified. The slice needs Ilun for the Drownbell's phase 2 (vertical_slice.md §5). ADR 0024/0026 (the first-playable stand-in, *Call Ilun*) waits on this system.

A scratch probe on the sandbox (1000 seeds; battle_ctb.md § Vowbound) showed that a free call is a large swing even with a 1 HP Vowbound: a masher went from 8.7% to 28.7% wins. The call soaks an enemy turn and costs the party nothing.

## Options
1. **A free call** (the Vowbound takes the turn; the caller gets its turn back when the party returns). This is simple, but the call is a free action, worth 20 masher points by itself.
2. **The call costs the caller's rank** (`call_rank` per row). The Vowbound still takes the turn at once, but when the party returns the caller waits a rank-`call_rank` delay, as if it had acted. Everyone else keeps the ticks they had left.
3. **The call costs MP or a full Swell gauge.** This hits careful players (Asha's MP is her heals), not mashers, and it adds a second gauge rule.

## Decision
Option 2, with `call_rank` 3 for Ilun.
- **The call.** The Vowbound acts at once. When the party returns, the caller pays the call's rank and the others keep their ticks.
- **Dismissal** is the Vowbound's action. It spends its turn, then the next turn begins.
- **A fallen Vowbound** (KO or stone) is no defeat. The party returns at once, and that Vowbound cannot be called again this battle.
- **Victory while it is out** hands the field back to the party before the battle ends, so XP and vitals see the party.
- **Refused while it is out:** swap, escape and items.
- **Its gauge** fills only from HP it loses: `swell_gain` at its row's rate (amended by A1: absorbed HP fills it too). The finisher has no input.
- **Its stats:** `vowbound_stat(base, caller_stat, scale_pct) = base + caller_stat × scale_pct ÷ 100`, at the caller's level. Ilun at Asha level 5 has 360 HP.
- **The data field is `caller`.** The class word for one who summons is on the banned list, so it is not used.

## Consequences
- **The probe.** A 1 HP call is worth 8 masher points, down from 20. The shipped Ilun lifts a sandbox masher with no gear to 38.9%. That is above the 25% starting-gear line for the Swell masher. **This is a deliberate proposal for review**: a Vowbound is one HP pool per battle, not a gauge that comes back every fight. The proposed Vowbound masher line is 40% with no gear. The sandbox is pre-Ilun content, so this is a stress test, not a band. If the review wants Ilun weaker, the levers are his HP scale and `call_rank` (the table in battle_ctb.md § Vowbound).
- **Pillar 4.** The UI must show the call's cost: a timeline preview with the caller's delay (M2-UI-05).
- **The Drownbell.** The real call replaces `call_ilun` on claude/m2-slice. Its bands must be re-run.
- **Not decided here:** carrying a Vowbound's HP, MP and gauge between battles; summon cinematics; and growth from item-taught abilities (SPEC §6.3).

## Acceptance (review-sweep-P, Design, 2026-10-24)
**Accepted: Option 2, the turn rules, the stat formula, Silence blocking the call, and the `caller` field.**
- **The call's rank, not MP or a gauge.** It taxes the policy that abuses a free action (the masher) and not the careful player. The probe isolates this well: a 1 HP call drops from 20 points to 8.
- **Silence blocks the call.** The call is a verse (story/vowbound.md: each Vowbound teaches one), and Silence has a counter on sale before the Drownbell. Pillar 4: the greyed command must name the reason (M2-UI-05).
- **The 40% Vowbound masher line is accepted as a provisional ceiling.** It holds for the sandbox with no gear, a masher calling at once. It is not a band. The binding per-encounter line is set once the simulator models the call (M2-CMB-05). The basis: Ilun falls in 99.6% of those runs, so he rescues and does not replace.
- **Wording.** "Once-a-battle rescue" should read "**one HP pool per battle**". A dismissed Vowbound can be called again as it left; only a fallen one cannot.

**Amendments.** They are binding, and M2-CMB-05 implements them. They were found by checking Ilun against the fight he exists for, the Drownbell's flood phase:
- The bell and its polyps absorb water, so Brine Lash and Floodnet heal them, and Ilun's Attack (STR 7) barely scratches DEF 30.
- Every flood-phase attack but Hood Slam is water, and Ilun absorbs water.
- His gauge filled only from HP lost.

So a called Ilun was immortal and harmless, Floodnet never came, the flood never cleared, and the party could wait out the phase out of reach.

- **A1. Absorbed HP fills the Vowbound's gauge.** It fills at the same `swell.rate`, through `Formulas.swell_gain` on the HP restored by an `absorb` hit. This replaces "fills only from HP it loses". Ilun drinks the tide and turns it into the net: calling him into the flood is the answer, not a hiding place.
- **A2. Floodnet is non-elemental and carries `clears_field: flood`.** The net binds; it is not a wave. Brine Lash stays water, so Read teaches the player not to lash an absorber.
- **A3. The call runs the caller's end of turn at the moment of the call.** That means Poison and Regen, the status countdown, Doom, `turns_taken` and `turn_ended`. Only the caller's `next_time` waits for the party's return, at the `call_rank` delay. Before this, every call skipped one tick of Doom or Poison.

The Drownbell's bands must then include a policy that calls Ilun when the flood rises and stays out (M2-FP-17).

## Implementation note (M2-CMB-05, Combat, 2026-10-24)
A1–A3 are in the engine. The wording above now reads "one HP pool per battle", as the acceptance asked; nothing else in the decision changed. Three details the amendments left open:
- **A1 counts the rolled absorb, not the HP actually restored.** The hit records `absorbed`, the amount before the max-HP cap, and the gauge takes `swell_gain` of that. Ilun is called at full HP, so a gauge fed only by restored HP filled nothing in the flood. A scratch probe of the Drownbell with the real call showed it: Floodnet never came, the flood never cleared, and role_answer and smart won 0.0% (most fights timed out). With the rolled absorb they win 72.0% and 87.0% (300 seeds). This is the amendment's stated intent ("calling him into the flood is the answer, not a hiding place"), and Design should confirm it.
- **A Swell finisher with `clears_field` is never refused while that field is down.** Floodnet stays Ilun's finisher in every fight and clears nothing there.
- **The simulator's call rule.** `naive_swell` calls at once and stays out. `role_answer` and `smart` call while a field is up and dismiss Ilun on his first turn after the field is gone.

The provisional 40% line is the `sandbox_reef_vowbound` suite, measured as the probe was: no gear and no hero Swell. There the masher calling at once wins 38.9%, which reproduces the probe. With the heroes' Swell played at `good`, the same masher wins 46.2%, above the line (balance_targets.md § Vowbound masher line). The per-encounter line is M2-FP-17's.
