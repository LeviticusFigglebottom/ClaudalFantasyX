---
id: M2-NIT-03
title: Review-sweep-M follow-ups (balance risk, import LOD ranges, override layering, test hygiene)
role: combat
status: done
owner_session: "agent-a14a20707d2ef004e"
depends_on: [M2-CMB-01, M1-ART-02, M1-NIT-02]
milestone: M2
request-from: "progression"
reviewer: progression
---
## Acceptance criteria
- [x] **Balance risk:** add a report-only `naive_swell` policy to the sim. A masher who opens Swell wins 37.5% against the 5-15% band, mostly via Shallows Verse (power 12 to every ally for no MP). Propose and apply a fix (power, cost or gauge fill), with the bands re-checked; pin the new technique powers in test_formulas.gd. Tether's unlock count of 12 is now too low with four heroes counting hits: retune it
- [x] **role_answer artefact:** a ready technique respects the policy's focus foe (sim_policy.gd ~:63-99)
- [x] **Import rules:** no visibility range on meshes that have no LOD behind them (asset_import_rules.gd ~:169-183); asset_import.md ~:16 matches the code; the stale comment at test_post_import.gd ~:156 is fixed; the convex shape transform is asserted
- [x] **Overrides:** a push during a scene swap does not layer on a pending pop's base settings (graphics_settings.gd ~:398-447); the cached settings are returned read-only or as a copy
- [x] **Test hygiene:** test_weathering_tide asserts the written value and restores the global
- [x] **Swell saves:** an escape-path test; the swell.json-broken path refuses gauge recording consistently with the unlock record (game.gd ~:161 vs ~:174)
- [x] **CharacterShaderTiers:** the overlay and next_pass limitation is documented

## Notes
- 2026-10-23 combat (agent-a14a20707d2ef004e): ready for **progression** review (SPEC §12.3). Handoff: docs/kb/handoffs/2026-10-23-combat-6.md.
  - **Balance.**
    - `naive_swell` is report only in every suite, with decision lines at 35% (starting gear) and 50% (tier-1).
    - Shallows Verse power 12 → 4. The masher's rate goes 37.9 → 32.1% on starting gear and 49.5 → 47.7% on tier-1. Every band holds at miss, good and perfect.
    - The reasoning and sweeps are in balance_report.md ("2026-10-23 M2-NIT-03") and battle_ctb.md § Swell. Power was the lever because the Ballast rate is a cliff, costs every hero's Swell, and is undone by carried gauges.
    - 32.1% is above "about 30%" by a deliberate decision. The residual is the second-life loop, and only a structural change removes it (handoff, Known issues).
    - Tether's unlock count 12 → 40, measured at 6 to 7 counted hits per fight with four heroes, against 2 when only Rhen counted.
    - test_formulas.gd pins every technique's power at good and perfect against skills.json. formulas.gd is unchanged.
  - **role_answer.** `swell_focus` sends a ready technique to the answered foe, and a free swap to the answer comes first. The ~3-point loss came from the swap pre-emption, not the target choice.
  - **The other criteria.** Import LOD ranges (chains only) and the convex transform, the override re-base and stored copy, the tide spy and restore, the Swell escape test and the broken-table refusal, and the CharacterShaderTiers limits are done as listed.
  - **Also done.** The bestiary assert, M1-NIT-02's reviewer field, and the M2-UI-03 notes (Brace lead-in, landing before the slice).
  - **Edits outside Combat paths.** game/core/import, graphics_settings.gd, game.gd, the haluna_mood tide script and CharacterShaderTiers are .gd and .md only, under this task's scope. No scene, resource or asset changed.
  - **First-playable footprint.** The battle data edits are the two Swell rows only. battle_controller.gd is untouched.
  - **Gates.** See the handoff.

## Review log
- 2026-10-24 review-sweep-O (progression): **approve.** All seven criteria hold in the code.
  - **Balance:** the Shallows Verse power 4 and Tether 40 choices stand. M2-CMB-02 then removed the residual loop structurally, and my 1000-seed re-run (`sim.py --check`, rc 0) shows every band holding on today's data: `naive_swell` 23.8% and 39.1%, against this task's 32.1% and 47.7% before CMB-02. test_formulas.gd pins every technique power against skills.json.
  - **What I read:**
    - 5ee5dc0: `push_override` re-bases when only deferred pops remain (`_older_owners_left`), and stores `base.copy()`; `same_as` compares the warning by value.
    - 724e749: `lod_chains` gives ranges to authored chains only, and the convex shape child gets `body.transform.affine_inverse()`.
    - a190b98: the tide test asserts the written value and restores the global.
    - 053587e: with swell.json broken, `record_party` keeps the saved gauge and mode, which matches `record_swell`; there is an escape-path test.
    - c31a878: the CharacterShaderTiers limits are documented.
  - **Checks:** Godot `--filter=` graphics_override 15/0 failed, graphics_settings 24/0, post_import 17/0, weathering 2/0, save 186/0, swell 124/0, battle 307/0. gdlint and gdformat are clean.
  - **Nit (no task):** `_older_owners_left` treats an owner briefly outside the tree mid-reparent as departed. A push in exactly that window would re-base. It's harmless in practice, because reparents are rare during cutscene swaps.
