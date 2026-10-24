---
id: M3-C01-03
title: Ch1 design rulings (Kick Off, the solo bands, the shutter, the economy, the tin, the pre-boss rest)
role: combat
status: todo
owner_session: ""
depends_on: [M3-C01-02]
milestone: M3
request-from: cinematics
---
## Goal
M3-C01-02 built Ch1 on first values and placeholders where act1_ch01.md §9 left the call to Design and Combat. Rule on each one, and change the data (not the code) where the answer differs:
1. **Kick Off.** Hullgnaw lends `kick_off` for that fight only (encounter `party_skills`, ADR 0034). Should Ch1 grant Rhen's Lattice node `rh_03` outright instead, so he keeps it? That's also the sheet's "the Lattice's first use" question (§9 Design 4).
2. **The bands (ADR 0034).**
   - Hullgnaw keeps the Ch1–Ch3 boss band, with `role_answer` report only: the policy never uses items, and nobody can swap in a solo fight.
   - The Underway's fights, scripted and random, take a tutorial band (`naive` 80–100%).
   - Confirm or replace both. The numbers are in balance_report.md (2026-10-24, Ch1).
3. **The shutter** (`game/data/flow/ch01_field.json` `lantern`): light radius 4 m narrow and 10 m open, and encounter rate ×1.0 and ×2.5.
4. **The economy:**
   - the gauge-wheel sells for 40 lume, 50 if he haggles;
   - the diver's kit at C1-01 is 2 Salt Tonic and 1 Brine Eyewash;
   - the old tin holds 2 Salt Tonic and 1 Brine Eyewash.
5. **The tin's accessory.** The sheet asks for one, but equipment has only weapon and armor slots. Name one when an accessory slot exists, or drop it.
6. **The pre-boss rest.** The flow fully heals Rhen before Hullgnaw, because the fight is tuned for full HP and the scuttler fight comes just before it. Keep the rest, or re-tune Hullgnaw against carried damage.
7. **No save in Ch1.** Today the only safety net is Fight again. The chapter autosave arrives with the shared `{"chapter": 1}` step (M2-FP-25). Is that enough for a 30-minute chapter? The sheet's fallback is a save at the scale-hull.

## Acceptance criteria
- [ ] Each item answered in Notes, with any data change and a `sim.py --check` rerun.

## Notes

## Review log
