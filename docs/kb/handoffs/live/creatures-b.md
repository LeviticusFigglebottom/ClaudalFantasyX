# Live log: creatures-b environment

Feature track for **the Act I bosses and the Act I Vowbound at final quality** (ADR 0041), branch `claude/creatures-b`,
started 2026-10-28 from `origin/claude/undertow-lead-handoff-ze8rrn` bd3ab5b. **This environment owns this file**
(CLAUDE.md §7a). Regular enemies and wildlife stay with the creatures track (`creatures.md`); the shared creature kit,
CreatureActor and the validator are theirs too (kit or tool changes go to them as request tasks).

## Scope (from game/data, 2026-10-28)
- **Bosses** (enemies.json rows with phases, or a choreo.json `boss_intro` row): `hullgnaw` (Ch1), `drownbell`
  (the slice, Ch3), `bottle_hermit` and `spar_wraith` (Ch4), `cinder_matron` (Ch5), `undertows_reach` (Ch8).
  `stillguard_inquisitor` (Moll, Ch6) is a person: the characters track builds him (M3-CHR-507, on claude/characters).
  The Lamp Engine is Ch11 (Act II, paused by ADR 0041). Ch7 has no foes and Ch9 no fight.
- **Vowbound met in Act I:** `ilun` (Ch3), `kahre` (Ch5), `virel` (Ch8). The creatures track built all three
  (M3-CRE-638/640/641) on claude/creatures; they are not on the integration branch yet, which is why Ilun still reads as
  a capsule there.
- `docs/kb/qa/act1_final_inventory.md` does not exist yet (integration-qa); these rows come from my own audit until it
  lands.

## Base
- **claude/creatures @ 851c4136 is merged into this branch** (813677a4): every model above is there, and the
  integration branch is not. **Lead: merge claude/creatures before (or with) claude/creatures-b.**

## NEW ACCOUNT (from 2026-10-25)
- 2026-10-28: branch made, binding docs read, ownership claimed (339557e6), toolchain set up.
- **Audit done (M3-CRB-001, 2a4a9db1):** all nine self-rendered on the review stage and viewed; the table is in the
  task file. Primitive (full rework): hullgnaw, undertows_reach, bottle_hermit, ilun, kahre, virel. Medium:
  spar_wraith. Light: drownbell, cinder_matron (and the Matron needs a small closed spawn_wound mark, ADR 0151).
  Every boss lacks `ready` and `intro` clips; nothing has VFX anchor bones yet.
- **Hooks (the contract, no data key):** every boss GLB gains an `intro` clip and unweighted bones `vfx_wound`,
  `vfx_core`, `vfx_phase`; every Vowbound `vfx_core` and `vfx_keepsake`. Requests filed: **M3-CRB-009** (combat /
  battle-presentation: BattleBossIntro plays `intro`; intro and phase VFX start at the anchors) and **M3-CRB-010**
  (creatures: CreatureActor.vfx_anchor, M3-CRE-651, resolves a bone named `vfx_<name>`).
- **In progress (worktree agents):** M3-CRB-002 hullgnaw, M3-CRB-004 bottle_hermit, M3-CRB-008 ilun. Next wave:
  spar_wraith, kahre, undertows_reach, then virel, drownbell, cinder_matron.
- **MERGE-READY @ 2f37abe7: M3-CRB-008 part 1, Ilun to final quality** (worktree agent, viewed by me).
  - A thick-bodied manta (0.42 m disc, spine ridge, broad head, gill slits, scroll lobes), a continuous knotted net
    of glimmer_bound light along the wing's span and chord, three long plumes, a whip tail and the glass float in a
    cord net. Wingspan 5.1 m: the biggest thing on the field at battle distance, inside the safe frame at rest.
    15.6k triangles, 20 bones (`vfx_core`, `vfx_keepsake` added, unweighted). Clips and contact times unchanged.
  - **Checks run:** Blender verify identical (creature_ilun); tools test_creatures and test_blender_builds 48 OK;
    validate_data 0 errors; Godot ilun 6/0, vowbound 83/0, creature 74/1 (test_creature_portraits: the ~26 unbaked
    portrait PNGs, known on claude/creatures, not this change). **Skipped:** gdlint/gdformat (no .gd), coverage.
  - SELF-RENDERED @ d5101f4f: creature_ilun, battle_vowbound_out, battle_choreo_summon, battle_choreo_vowbound_rise —
    drift (the new model, intended); viewed: reads as a vast luminous manta with net, crest and float. Open polish:
    the near wing is pale at the battle camera's grazing angle; a true see-through look needs a spectral material in
    the kit (creatures').
- **In progress:** M3-CRB-002 hullgnaw, M3-CRB-004 bottle_hermit, M3-CRB-008 kahre (worktree agents).
- **MERGE-READY @ efdcef1f: M3-CRB-002, the Hullgnaw to final quality** (worktree agent 8323726d, viewed by me).
  - Eel anatomy (flattened section, slate belly, torn dorsal fin and crest, lateral line, folds, welts, barnacles,
    a weed and foam collar), six recessed open wound seams (spawn_wound) between squared adzed oak frames with
    treenails, rusting spikes, splintered salt-pale ends, weed and plank stubs; a real skull with brows, gill slits,
    lips, a too-wide jaw and nail teeth. 15.8k triangles (sheet budget raised to ≤16k). New clips `ready` and `intro`
    (2.6 s: rears out, jaw wide, settles); bones `vfx_wound`, `vfx_core`, `vfx_phase`. Contacts unchanged.
  - **Checks run:** Blender verify identical; validate_data 0 errors; taskboard; tools test_creatures and
    test_blender_builds 48 OK; Godot creature 74/1 (the known unbaked portraits), ch01_battles 5/0.
  - SELF-RENDERED @ 8323726d: creature_hullgnaw, battle_boss_intro_hullgnaw — drift (the new model); viewed at battle
    distance: a black arch caged in broken ship's timbers with cyan seams. Mild: the neck is a little glossy in sun.
  - **For ui-menus:** the hullgnaw bestiary portrait is stale (re-bake `tools/portraits/render.sh --only hullgnaw`).
- **In progress:** bottle_hermit, kahre, spar_wraith (worktree agents).
- **MERGE-READY @ c5774622: M3-CRB-004, the Bottle hermit to final quality** (worktree agent 0bd7293a, viewed by me).
  - Scaled to a boss: 1.2 m to the antennae (creatures.json stand_in height 1.2, radius 0.75). A thick, chipped,
    salt-frosted deck-lantern chimney with barnacles, draped weed, a riveted green-bronze band and bail ring, lit
    from inside (sea_glow) round a backlit banded abdomen; a granular-shelled crab with segmented spined legs,
    compound eyes, antennae and a heavy lumpy claw; one small closed spawn_wound mark on the abdomen (ADR 0151).
    15.2k triangles. New clips `ready` (loop) and `intro` (2.6 s); bones `vfx_wound`, `vfx_core`, `vfx_phase`.
  - **Checks run:** Blender verify identical; validate_data 0 errors; tools tests 48 OK; Godot creature 74/1 (the
    known portraits), boss_intro 17/0, ch04_battles 5/0; taskboard.
  - SELF-RENDERED @ 0bd7293a: creature_bottle_hermit, battle_boss_intro_hermit — drift (new model); viewed at battle
    distance: a giant hermit in a glowing old lamp glass. Polish note: the crab's shell is still a little glossy.
  - **For ui-menus:** re-bake the bottle_hermit portrait.
- **In progress:** kahre, spar_wraith, undertows_reach (worktree agents).
- **MERGE-READY @ 2a36f12e: M3-CRB-008 part 2, Kahre to final quality** (worktree agent 6c7e72a3, viewed by me).
  - Real anatomy (hump, shoulder masses, ribs, tendoned forearms, curled digits and claws, scaled hind feet), a
    charcoal-to-ash stone hide with ember-warm creases and cracks (no teal), 24 keratin back plates, the anvil as his
    sternum (striking face, hardy and pritchel holes, hammer scars), a bigger grooved casque, a 0.65 m cross-peen
    hammer, a 240-filament bound-light mane. 17.7k triangles; `vfx_core`, `vfx_keepsake`. Last Strike dips the hips
    0.31 m (was 0.4) so the new horn stays above the water; contact time unchanged.
  - **Checks run:** Blender verify identical; validate_data; tools tests 48 OK; Godot kahre 6/0, vowbound 83/0,
    creature 74/1 (the known portraits).
  - SELF-RENDERED @ 6c7e72a3: creature_kahre, creature_kahre_held — drift (new model); viewed: a hulking stone beast
    with a hornbill casque, hammer and anvil chest. **Follow-up polish (mine, queued):** the hammer reads as perched
    on the casque on a thin handle, not grown into it; the forearm plates' front edges are ragged up close.
- **In progress:** spar_wraith, undertows_reach, virel (worktree agents).
- **MERGE-READY @ 2b6b5f8b: M3-CRB-007, the Undertow's Reach to final quality** (worktree agent f2a641cc, viewed by me).
  - The forearm a rope of six twisting water strands with foam-crested surge folds and flow streaks, narrowing into
    a storm spout; wreckage (two banded masts, chain, a lashed cross-spar and a drowned lantern, half a ship's wheel,
    nailed planks, rope); two half-swallowed spawn shells (segments, spines, dead eyes, mandibles); two door-sized
    recessed wounds with torn lips facing the party; six jointed digits with serrated crust plates, barnacles and
    hooked claws. 24.0k triangles (budget 24k), 28 bones; `water` slot wet_darken 0.2 → 0.55 so the colour shows.
    New `ready` and `intro` (2.8 s: comes down from 11 m and slams onto the wall-head); `vfx_wound`, `vfx_core`,
    `vfx_phase`. Contacts and phase data unchanged. The spout is capped at 19.2 m: taller fails
    test_every_boss_stands_clear_of_the_title_card.
  - **Checks run:** Blender verify identical; validate_data; tools tests 48 OK; Godot creature 74/1 (known
    portraits), ch08 19/0, boss_intro 17/0.
  - SELF-RENDERED @ f2a641cc: creature_undertows_reach, battle_boss_intro_reach — drift (new model); viewed: the
    intro reads as the storm's limb of water and wreck on the wall-head.
  - **Seen at the default battle camera (a scratch render):** the hand crowds the camera beside the party, and its
    plates show hard facets that close. Facets: my follow-up. Framing, and **a white capsule for "The Fisher Stair"**
    (a set-piece target, a placeholder in Act I): added to M3-CRB-009 for battle-presentation.
- **In progress:** spar_wraith, virel, drownbell (worktree agents). Then cinder_matron, then my polish queue
  (Kahre's hammer and forearm plates, the Reach's close-range facets, the hermit's glossy shell).
- **MERGE-READY @ 04db1e70: M3-CRB-005, the Spar-wraith to final quality** (worktree agent f92f50d8, viewed by me).
  - Hewn eight-sided spars (salt-silvered, tarred low, iron bands, cleats, a fid hole, splintered tops, a lashed
    broken yard); three-strand rigging of varied thickness with sag, deadeyes, ratlines, a stay and a block-and-
    tackle; three monkey's-fist element knots; eight telescoping chitin plates with jointed hooked limbs; four open
    spawn_wound seams; an eyeless split mask with a glowing mouth-seam; a torn two-sided shroud with seams, grommets
    and reef points; the Sheath follows the plates. 18.0k triangles (sheet budget raised to ≤18k). New `ready`
    (loop; added to the row's `loop`) and `intro` (2.8 s); `vfx_wound`, `vfx_core`, `vfx_phase`. Contacts unchanged.
  - **Checks run:** Blender verify identical; validate_data 0 errors; tools tests 48 OK (incl. grounding: the KO head
    was 12 cm under the deck, fixed); Godot creature 74/1 (known portraits), ch04 11/0; taskboard.
  - SELF-RENDERED @ f92f50d8: creature_spar_wraith, battle_boss_intro_wraith — drift (new model); viewed: at night a
    broken A-frame of masts with a hanging plated body, pale knots and a glowing seam. Mild: plates a little clean at
    noon close range.
- **In progress:** virel, drownbell, cinder_matron (worktree agents).
- **MERGE-READY @ (this merge): M3-CRB-006, the Cinder Matron to final quality** (worktree agent 387af0af, viewed by me).
  - Slag crust as irregular cooled runs (pumice tops, glassy downhill lips, drips; a third of the cracks glow);
    plated riveted arms with hinged elbows and a piston linkage, heat-blue and soot; a scorched stitched leather apron
    with burn holes and a buckled strap (new `leather` slot); the hood's heat rainbow and soot. **Weak point (ADR
    0151):** a cracked, sealed sight-glass on her right flank, beside the firebox (new `wound` slot, spawn_wound),
    distinct from the glimmer_bound heart. 24.8k triangles (budget 25k). New `ready` (loop) and `intro` (2.6 s, the
    anvil's ring wakes her); `vfx_wound`, `vfx_core` (firebox), `vfx_phase` (behind the heart port). Two PROVENANCE
    rows added (leather.tres, wound.tres). Contacts and the Crust/recrust cue unchanged.
  - **Checks run:** Blender verify identical; validate_data 0 errors; tools tests 48 OK; taskboard; Godot creature
    74/1 (known portraits), ch05 4/0, part_cues 6/0, boss_intro 17/0.
  - SELF-RENDERED @ 387af0af: creature_cinder_matron, battle_boss_intro_matron — drift (new model); viewed: a plated
    forge-machine, the sight-glass a clear teal point in the intro. Mild: the biggest belly cells are smooth up close.
  - **For env-art / battle-presentation (seen in battle_boss_intro_matron):** the Ch5 terrace arena's front edge
    shows stretched vertical texture streaks (orange stripes) across the lower third of the frame.
- **MERGE-READY @ (this merge): M3-CRB-008 part 3, Virel to final quality** (worktree agent bfd23910, viewed by me).
  - An open S in flight (head raised toward the foes, a kite-tail of bows and a tassel), never a closed loop;
    15 varied trapezoid sail panels on a cane spine and battens with lashings, hems, grommets, stains and Saltwright
    patches; each seam a sewn raised line with a narrow bound-light core, a charred ring and scorched cloth, with
    small frozen flame tongues; a framed cloth kite-dragon head (cane ridge, open glowing jaw, lantern-eyes, cord
    whiskers, pennant); a 0.37 m brass tuning key. 17.8k triangles; body 4.85 m (was 5.5) so the S fits the safe
    frame; her test's Flare Line length check 5.0 → 4.5 m (the line reaches 4.75). creatures.json: `virel` and
    `virel_held` get stand_in height 2.6 / radius 0.8 (as ui's note asked: effect anchors land on her).
  - **Colour decision (documented in virel.md):** her light stays glimmer_bound; ember_orange is for flames and
    fire VFX (palette.json), the held swap requires bound slots, so the fire reads through scorch and flame shapes and
    her battle VFX carries the flame colour. **For battle VFX:** Kite Flare and Flare Line should add the fire.
  - **Checks run:** Blender verify identical; validate_data 0 errors; tools tests 48 OK; gdlint/gdformat on her test;
    Godot virel 6/0, vowbound 83/0, creature 74/1 (known portraits).
  - SELF-RENDERED @ bfd23910: creature_virel, creature_virel_held — drift (new model); viewed: a kite-serpent riding
    the wind. Mild: from the held shot's near front-on view the S is nearly edge-on.
