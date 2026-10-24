# 0027 — Vowbound battle rules: the call stands the party down and costs the caller's rank

- **Status:** proposed (Design or Lead to accept in the M2-CMB-04 review)
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
- **Its gauge** fills only from HP it loses: `swell_gain` at its row's rate. The finisher has no input.
- **Its stats:** `vowbound_stat(base, caller_stat, scale_pct) = base + caller_stat × scale_pct ÷ 100`, at the caller's level. Ilun at Asha level 5 has 360 HP.
- **The data field is `caller`.** The class word for one who summons is on the banned list, so it is not used.

## Consequences
- **The probe.** A 1 HP call is worth 8 masher points, down from 20. The shipped Ilun lifts a sandbox masher with no gear to 38.9%. That is above the 25% starting-gear line for the Swell masher. **This is a deliberate proposal for review**: a Vowbound is a once-a-battle rescue, not a gauge that comes back every fight. The proposed Vowbound masher line is 40% with no gear. The sandbox is pre-Ilun content, so this is a stress test, not a band. If the review wants Ilun weaker, the levers are his HP scale and `call_rank` (the table in battle_ctb.md § Vowbound).
- **Pillar 4.** The UI must show the call's cost: a timeline preview with the caller's delay (M2-UI-05).
- **The Drownbell.** The real call replaces `call_ilun` on claude/m2-slice. Its bands must be re-run.
- **Not decided here:** carrying a Vowbound's HP, MP and gauge between battles; summon cinematics; and growth from item-taught abilities (SPEC §6.3).
