---
id: M2-NIT-03
title: Review-sweep-M follow-ups (balance risk, import LOD ranges, override layering, test hygiene)
role: combat
status: todo
owner_session: ""
depends_on: [M2-CMB-01, M1-ART-02, M1-NIT-02]
milestone: M2
request-from: "progression"
---
## Acceptance criteria
- [ ] **Balance risk:** add a report-only `naive_swell` policy to the sim. A masher who opens Swell wins 37.5% against the 5-15% band, mostly via Shallows Verse (power 12 to every ally for no MP). Propose and apply a fix (power, cost or gauge fill), with the bands re-checked; pin the new technique powers in test_formulas.gd. Tether's unlock count of 12 is now too low with four heroes counting hits: retune it
- [ ] **role_answer artefact:** a ready technique respects the policy's focus foe (sim_policy.gd ~:63-99)
- [ ] **Import rules:** no visibility range on meshes that have no LOD behind them (asset_import_rules.gd ~:169-183); asset_import.md ~:16 matches the code; the stale comment at test_post_import.gd ~:156 is fixed; the convex shape transform is asserted
- [ ] **Overrides:** a push during a scene swap does not layer on a pending pop's base settings (graphics_settings.gd ~:398-447); the cached settings are returned read-only or as a copy
- [ ] **Test hygiene:** test_weathering_tide asserts the written value and restores the global
- [ ] **Swell saves:** an escape-path test; the swell.json-broken path refuses gauge recording consistently with the unlock record (game.gd ~:161 vs ~:174)
- [ ] **CharacterShaderTiers:** the overlay and next_pass limitation is documented

## Review log
