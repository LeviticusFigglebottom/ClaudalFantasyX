# Live log: creatures-b environment

Feature track for **the Act I bosses and the Act I Vowbound at final quality** (ADR 0041), branch `claude/creatures-b`,
started 2026-10-28 from `origin/claude/undertow-lead-handoff-ze8rrn` bd3ab5b. **This environment owns this file**
(CLAUDE.md §7a). Regular enemies and wildlife stay with the creatures track (`creatures.md`); the shared creature kit,
CreatureActor and the validator are theirs too (kit or tool changes go to them as request tasks).

## LEAD: READ FIRST (2026-10-28 09:20) — Ilun is NOT a capsule; your queue items are done
- **Ilun has a real procedural body, rig and clips** (assets_src/creatures/ilun/build_ilun.py → assets/creatures/ilun/ilun.glb,
  wired through creatures.json `ilun` `vowbound: true` → CreatureModels / BattleStage.stand_in_spec). Clips: idle,
  ready, **rise** (the call), **dismiss**, attack, cast, hit, hit_b, defend, ko, victory, special, release, idle_b.
- **SELF-RENDERED @ 7305540a (this branch's head), viewed: battle_vowbound_out and battle_choreo_vowbound_rise both show
  the manta, no capsule.** The big14 gate's own out PNG (gpu/gate-big14-shots:
  docs/kb/qa/gate-runs/big14/out/battle_vowbound_out.png) shows the manta too.
- **The capsule you see is the OLD BASELINE** `tests/screenshots/baselines/battle_vowbound_out.png` (and
  `battle_choreo_vowbound_rise.png`), from big13. Those two shots are **drift to re-approve after viewing**; I never
  write baselines (TRACK-RULES).
- **Portrait:** `assets/ui/portraits/creatures/ilun.png` is committed (e0300c83) with its PROVENANCE row; so are kahre,
  virel and the three held forms; the six bosses are re-baked. test_creature_portraits now fails only on Act II's
  nhoa, hesk, ethren (+ held), the creatures track's, paused.
- **Every other Act I boss and Vowbound row is done** (MERGE-READY lines below). Open, not mine: M3-CRB-009 and
  M3-CRB-011 (battle-presentation: intro clip playback, the boss seat at the default camera), Ilun's blank turn-order
  icon (ui).

- **09:45, why the inventory still says "Vowbound … drawn as a primitive" (M3-HER-1143): an audit false positive.**
  `tools/placeholder_audit.py` only reads battle_sandbox.json `stand_ins.<id>.scene`; the game resolves a Vowbound
  through its creatures.json `vowbound: true` row. **M3-CRB-012** (qa) carries a tested 4-line patch: with it the ilun,
  kahre and virel rows go and the audit's tests stay OK. M3-HER-1143 is in review with the row-by-row status; the
  Moll row is the characters track's (M3-CHR-507).
- **The battle-distance arena pass is done** (the 04:57 entry below; scratch fixture on the big14 tree, chapter parties,
  real arenas): hullgnaw, drownbell and bottle_hermit read whole and well scaled; the Wraith, the Matron and the Reach
  are cropped by the stage's lone-boss seat (EnemySlots/Slot0), filed as **M3-CRB-011**. Idle motion was checked clip
  by clip in each model pass.

- **11:40, the Lead's 10:55 queue:**
  1. **M3-CRB-011 fixed (052d69a2), MERGE-READY:** `boss_seats` in battle_sandbox.json + `BattleStage._seat_lone_boss`
     (a lone boss stands on its mark at spawn, before the line-up). Reach [-2.6,0,-2.4], Matron [-2.6,0,-1.2],
     Spar-wraith [-2.0,0,-1.4]. SELF-RENDERED (scratch default-camera fixture, never committed; plus
     battle_boss_intro_wraith/_matron/_reach), viewed: the Reach's hand grips the wall-head and reads; the Matron is
     whole, hood clear, intro unoccluded; the Wraith's body and shroud are in frame but its mast tops still leave the
     frame. Further-back Wraith seats broke test_battle_boss_camera (its big-move shots), so the rest is a home-camera
     fit for a tall boss: noted on M3-CRB-011 for battle-presentation. New test_battle_boss_seat 2/0.
  2. **Arena pass:** hullgnaw, drownbell, bottle_hermit read whole and well scaled at the default camera (no seat
     needed); the three above are fixed as far as a seat can. Phase-change motion was checked per model in each pass.
  3. **Clips the choreo calls:** none missing. `dodge` is declared but never played; `item` and `read` are hero menu
     actions (the Vowbound menu has neither); `victory` plays on the party side (the Vowbound have it); creature strikes
     resolve through clip_by_skill/clip_by_kind. Pinned: test_creature_bosses_act1 now checks every Act I Vowbound
     skill and Swell finisher resolves to a clip its model has (5/0).
  - **Checks:** validate_data 0/0; gdlint, gdformat; Godot boss 75/0, choreo 58/0, battle_lineup 5/0, vowbound 87/0,
    creature_bosses 5/0, battle_boss_seat 2/0; the full battle filter is running. **Pre-existing, not mine:**
    test_battle_act1_ability_vfx fails on tannin_archer, root_crab and fen_leech (Act II creatures; it fails without my
    change too).

- **12:40, the Lead's 12:11 rows (act1_gpu_qa.md on gpu/act1-qa-2), MERGE-READY @ 066cc8b9:**
  - **Row 12 (Moll a grey capsule): fixed.** His actor (characters' M3-CHR-507) is wired as a battle_sandbox.json
    stand-in `scene` (enemies.json `model` only takes creature scenes), yaw 90, height 1.86; the Ch6 intro row gets
    `fit_margin` 1.1 so the party stays clear of the HUD. SELF-RENDERED battle_boss_intro_inquisitor and
    battle_arena_camp — viewed: Moll and the hound facing the party, no capsule. M3-CHR-523 to review.
  - **Row 30 (capsules in drowned_choir_ring, iskarra_spire_crown, undertow_cage, undertow_heart(_letting),
    keth_seep_terrace): record only.** No encounter at all uses those arenas yet (later acts, paused by ADR 0041).
  - **The placeholder audit now lists nothing for creatures-b.** Ilun, Kahre and Virel also carry their actor scenes
    as battle_sandbox.json stand-in `scene` keys (redundant with creatures.json; the audit reads only those), so the
    false positive is gone without touching qa's tool; M3-CRB-012 stays as the proper fix.
  - **Checks:** validate_data 0/0; gdlint, gdformat; Godot boss 76/0, creature_bosses 6/0 (new: every Act I boss,
    Moll included, and Vowbound draws a real body), ch06 5/0, vowbound 87/0.

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
- **MERGE-READY @ (this merge): M3-CRB-008 polish, Kahre** (worktree agent 6150705d, viewed by me): the hammer's
  handle sunk 16° into the casque with layered keratin growth and a crack round it, the head lying along the crest
  (`vfx_keepsake` moved with it); forearm plates laid on the arm with a worn raised lip and a dark seam. Last Strike's
  hip drop 0.31 → 0.245 m so the lower hammer face stays on the water (contact time unchanged). 17.8k triangles; rest
  height 3.25 m (stand-in 3.3 kept). Checks: Blender verify identical; tools tests 48 OK; validate_data; Godot kahre
  6/0, vowbound 83/0. SELF-RENDERED @ 6150705d: creature_kahre, creature_kahre_held — viewed: the hammer reads as part
  of the casque. Left: the wrist seam is ragged up close.
- **MERGE-READY @ (this push): M3-CRB-003, the Drownbell to final quality** (worktree agent 66d6f5c0, viewed by me),
  **and the contract test.**
  - The Drownbell: double beads, an invented-script inscription band, waves under eleven cast fan-shells, the shrine
    sigil roundel; a bright strike seat, a riveted old mend, dents, pitting, verdigris and a tide line; open rim seams
    with torn bright lips branching up (the rim stays the weak point; `RimBroken` loses 105° of lip round the biggest
    wound and its light goes out); cast crown lugs (one snapped) with a chain stub; three-strand hemp rope; jointed
    plated legs with hooked tips, feet at 1.1 m. Relaid so the biggest wound faces the battle cameras (they see it
    from about −20°). 23.8k triangles, 22 bones. New `ready`, `intro` (2.8 s); `vfx_wound`, `vfx_core`, `vfx_phase`.
    Contacts and the flood offset unchanged.
  - **tests/unit/test_creature_bosses_act1.gd (new):** every Act I boss has idle, ready, intro (1.5–3.5 s), attack,
    cast, hit, hit_b, ko and unweighted `vfx_wound`/`vfx_core`/`vfx_phase`; every Act I Vowbound has its clips and
    unweighted `vfx_core`/`vfx_keepsake` (weights read from the vertex arrays). 4/0.
  - **Checks run:** Blender verify identical (drownbell); validate_data; tools tests 48 OK; gdlint/gdformat; Godot
    creature 79/1 on the combined tree (the known portraits), drownbell 6/0, boss 57/0, creature_bosses 4/0.
  - SELF-RENDERED @ 66d6f5c0: creature_drownbell, creature_drownbell_toll, creature_drownbell_rim_broken,
    battle_boss_intro_drownbell, drownbell_flood — drift (new model); viewed: a finished, doomed bell; the glowing
    seams face the intro camera at sunset.
- **All nine Act I bosses and Vowbound have had their final pass.** In progress: the Reach's close-range facets and the
  hermit's gloss (polish agent).
- **MERGE-READY @ ac2fc33b: polish (M3-CRB-007, M3-CRB-004)** (worktree agent d65ad59e, 85784455, viewed by me): the Reach's
  digit crust plates smooth-shaded and domed with a crisp rim, matte salted shell (crust roughness up, specular down;
  23,978 tris, bounds not grown); the Bottle hermit's chitin matte and mottled, dry above and damp below, salt at the
  joints (geometry unchanged). SELF-RENDERED @ d65ad59e/85784455: creature_undertows_reach, battle_boss_intro_reach,
  creature_bottle_hermit, battle_boss_intro_hermit (+ a scratch default-camera Reach view) — viewed: the facets and
  the toy sheen are gone.
- **Combined-tree checks @ ac2fc33b:** validate_data 0 errors; taskboard; tools test_creatures + test_blender_builds OK;
  Godot creature 79/1 (test_creature_portraits: unbaked portrait PNGs only), boss 61/0, vowbound 83/0. Blender verify
  identical for every job changed (each agent ran its own). **Skipped:** coverage (no game/battle or
  game/progression change), the full manifest (Lead's).
- **Shots that change** (for the Lead's gate; I wrote no baselines): creature_hullgnaw, creature_drownbell,
  creature_drownbell_toll, creature_drownbell_rim_broken, creature_bottle_hermit, creature_spar_wraith,
  creature_cinder_matron, creature_undertows_reach, creature_ilun, creature_kahre, creature_virel, creature_ilun_held,
  creature_kahre_held, creature_virel_held, battle_boss_intro_hullgnaw, battle_boss_intro_hermit,
  battle_boss_intro_wraith, battle_boss_intro_matron, battle_boss_intro_drownbell, battle_boss_intro_reach,
  drownbell_flood, battle_vowbound_out, battle_choreo_vowbound_rise, battle_choreo_summon, battle_vowbound_call,
  creature_portraits, and any battle shot that seats these models.
- **MERGE-READY @ 397f0da8: polish 2** (worktree agent fdf0b665, fb334ace, b89d95a9, 5587e970; viewed by me): the
  Hullgnaw's neck dull and folded (carapace roughness_dry 0.35 → 0.62; wet glints only in slime streaks); the
  Matron's five biggest front slag cells bubbled, pitted and cracked (24,988 tris); Ilun's net cords thin toward the
  wing tip and the membrane darkens to the trailing edge, so the near wing reads as net over dark diamonds; Kahre's
  wrists get a cuff of hide folds (17,990 tris). Bones, clips, contacts and anchors unchanged. Blender verify
  identical (×4); tools tests 48 OK; validate_data; Godot creature 79/1 (known portraits), boss 61/0, vowbound 83/0,
  creature_bosses 4/0. SELF-RENDERED: creature_hullgnaw, battle_boss_intro_hullgnaw, creature_cinder_matron,
  battle_boss_intro_matron, creature_ilun, battle_vowbound_out, battle_choreo_vowbound_rise, creature_kahre — viewed.
- **BACKLOG EMPTY (this track's Act I scope):** all six Act I bosses and three Act I Vowbound are at final quality with
  the hook contract pinned. What remains is other tracks': M3-CRB-009 (battle-presentation), M3-CRB-010 (creatures),
  the portraits (ui-menus), Moll (characters, M3-CHR-507), the Ch5 arena edge (env-art). Next for me: merge the
  integration branch when the Lead lands creatures + creatures-b, and check the intro clips once M3-CRB-009 lands.
- **Lead's 04:44 message, answered:**
  1. **Ilun is not a capsule on big14.** Rendered battle_vowbound_out and battle_choreo_vowbound_rise on a worktree
     of lead/gate-big14 @ 8707ff90 (fresh import): both show the manta model (net wings, plumes, float). His
     call/dismiss/idle clips are `rise`, `dismiss`, `idle` (plus ready, attack, cast, hit, defend, ko, victory, special,
     release). A capsule in your view must come from older baselines (big13's) or a tree without claude/creatures.
     Polish 2 (b4ee2492: Ilun's net reads further out on the near wing) is after big14's cut.
     **Seen there, for ui:** Ilun's turn-order and party-panel icon is a blank tile (no portrait yet).
  2. **Every Act I boss and Vowbound on my rows** (hullgnaw, drownbell, bottle_hermit, spar_wraith, cinder_matron,
     undertows_reach, ilun, kahre, virel) is at final quality; nothing else is on my inventory.
  3. **Arena pass at the default battle camera, done** (scratch fixture, big14 tree, chapter parties, real arenas):
     hullgnaw, drownbell and bottle_hermit read whole and well scaled against the party; idle motion was checked
     clip by clip in each pass (no new idle needed). **The Spar-wraith (mostly out of frame), the Matron (hood
     under the phase label) and the Reach (fills the camera)** are cropped by the stage, not the models: a lone boss
     sits on EnemySlots/Slot0 (-2.4, 0, 0.9), close and to the left. **Filed M3-CRB-011** (combat /
     battle-presentation): a boss mark further back and central, or the intro's bounds fit applied to the home
     camera. Not done model-side on purpose: moving a model inside its scene would pull it off its ring and VFX
     anchors. I re-render the six when it lands.
- **Lead's 08:59 message, done @ b7ff479a (merged origin/gpu/gate-big14-shots first, at 4583d3fc):**
  1. **Ilun is a real model in big14 itself.** The gate's own render
     `docs/kb/qa/gate-runs/big14/out/battle_vowbound_out.png` (on gpu/gate-big14-shots) shows the manta; the
     **capsule is only in the old baseline** `tests/screenshots/baselines/battle_vowbound_out.png` (big13), which the
     out PNG is compared against. Same for battle_choreo_vowbound_rise. **Lead: those two are drift to re-approve
     after viewing, not a missing model.** His clips: idle, ready, rise (the call), dismiss, attack, cast, hit, hit_b,
     defend, ko, victory, special, release.
  2. **Portraits baked** with ui-menus' tool (tools/portraits/render.sh, at your request): **ilun, kahre, virel,
     ilun_held, kahre_held, virel_held new** (PROVENANCE rows added), and the six Act I bosses **re-baked** on the
     final models (their old PNGs showed the primitive first passes). Ilun and ilun_held got a portrait framing
     (yaw 45, pitch 32, margin 0.95: the net wings read). All viewed as a contact sheet.
     test_creature_portraits now fails only on **nhoa, hesk, ethren and their held forms** (Act II, creatures',
     paused by ADR 0041); `tools/portraits/render.sh --only nhoa,hesk,ethren,nhoa_held,hesk_held,ethren_held` turns
     it green if you want it baked anyway.
  3. Every other Act I boss and Vowbound: done (see above); the default-camera framing of the Wraith, the Matron and
     the Reach waits on **M3-CRB-011** (battle-presentation).
  - **Checks:** validate_data 0/0; Godot creature_portraits 4/1 (the six Act II PNGs only), creature_bosses 4/0,
    vowbound 87/0.
- **Housekeeping @ 00c836b6:** added `docs/kb/qa/gate-runs/.gdignore` (the big14 merge brought ~390 gate PNGs and JPGs that Godot otherwise imports into .import files; same as docs/kb/qa/gpu/.gdignore; QA's path, flagged here for the Lead), and committed six .uid sidecars Godot generated for other tracks' new scripts.
- **BACKLOG EMPTY (12:50):** every creatures-b row is closed — the six Act I bosses, Moll's battle wiring and the three
  Act I Vowbound are at final quality and draw real bodies; the placeholder audit lists nothing for creatures-b; GPU QA
  rows 12 (fixed) and 30 (later-act arenas, record only) are answered. Open items are other tracks': M3-CRB-009 (intro
  clip playback), the Spar-wraith's home-camera fit (M3-CRB-011 note), M3-CRB-010, M3-CRB-012, and the Act II Vowbound
  portraits (creatures, paused). The one full battle run on 052d69a2 showed only the pre-existing Act II
  test_battle_act1_ability_vfx failures.

## 2026-10-29: the new Lead's brief (integration `claude/new-session-mj8c3c` merged at 1d0f272b, then lead/gate-big17 at its head)
- **Merges:** integration (one conflict, pc-gpu.md, not mine: took theirs), then `origin/lead/gate-big17` (the
  Lead's "newest everything"; same pc-gpu.md conflict, same resolution). This branch now holds big17 + the below.
- **Rows 12 and 35 (Moll a grey capsule in his fight): verified fixed on big17.** Pass B (lead/gate-ft-beach @
  93d0741e, 07:06) predates the fix (066cc8b9, 12:31, his battle_sandbox.json stand-in `scene`). On big17, Moll
  draws his actor in ch06_inquisitor at the default camera, with the hound (scratch fixture, viewed).
  **New test** `test_every_act1_boss_encounter_seats_real_bodies_not_capsules` (test_creature_bosses_act1): for every
  encounter that fields an Act I boss, Moll included, it builds each boss's FighterStandIn as the battle does and
  fails if it falls back to the primitive. Shown live: with Moll's `scene` removed it fails.
- **Row 36 (the Reach's arm over the party): fixed model-side, a654ccc5.** At the old seat the digits reached x
  1.2-1.7, between Asha and Toma. Its boss seat [-2.6,0,-2.4] -> [-5.0,0,-2.4] (out along the arm's own axis): the
  hand still grips the wall-head and reads, with a clear gap before the party, in every clip (idle, the phase idles,
  attacks, casts, hits, intro: bones below 4 m stay at x <= -1.25; Asha's body starts at -0.1). Test
  `test_the_reach_keeps_its_arm_out_of_the_party_lane` (test_battle_boss_seat) fails at the old seat.
  **For battle-presentation:** rendered with your M3-BPR-425 `rest_by_enemy` row (4 m back, 2 m up) in place; the
  hand stays in frame at the left. With the arm now clear of the lane you may want less pull-back; your call.
  The intro frame is unchanged.
- **Row 30 (capsules in drowned_choir_ring, iskarra_spire_crown, undertow_cage, undertow_heart(_letting),
  keth_seep_terrace): still record only.** On big17 no encounter uses any of them (arenas.json only): later acts,
  paused by ADR 0041.
- **Primitive-at-battle-distance sweep** (all seven Act I boss fights at the default camera, big17 tree, scratch
  fixture, viewed as a contact sheet): Hullgnaw, Bottle hermit, Matron, Moll, Drownbell read well. **The Spar-wraith
  read as ship's rigging:** the camera saw its A-frame edge-on (one mast, the body behind it). **Fixed, d4d52043:**
  creatures.json `spar_wraith.stand_in.yaw_deg` 45 (stormgull and squall_wing already use 60); the frame, hanging
  body and glowing seam now read. Its intro still reads.
- **Clips battle-presentation's choreography asks for:** their log (claude/battle-presentation, 10-29) asks nothing
  of creatures-b; the earlier check (every Act I Vowbound skill and finisher has its clip) still passes.
- **Checks:** validate_data 0/0; gdlint, gdformat; tools test_creatures OK; Godot boss 86/0, creature_bosses 7/0,
  ch08 25/0, ch04 13/1 (**pre-existing on big17, not mine:** test_ch04_zones `test_the_wakes_field_camera_is_halunas`,
  10 volumes vs 8; it fails the same on an untouched big17 worktree). **Skipped:** Blender (no source touched),
  coverage (no game/battle or game/progression code), the tools suite (no tools/ change).
- SELF-RENDERED @ d4d52043 (scratch default-camera fixture for all seven fights, never committed; plus
  battle_boss_intro_reach and battle_boss_intro_wraith): viewed. Intro shots are drift against their old baselines
  (which predate the models), not a regression: battle_boss_intro_reach rendered the same at the old and new seat.
- **MERGE-READY @ d4d52043** (+ this log commit): a654ccc5 (rows 35/36 and both tests), d4d52043 (the Spar-wraith's
  yaw). Shots that can move: battle_boss_intro_reach, battle_boss_intro_wraith, any battle shot fielding the Reach
  or the Spar-wraith.

### PC-QUEUE
- GPU QA rows 12/35 (Moll) and 36 (the Reach, now seat + battle-presentation's rest frame): re-check on the RX 9070 XT.
- The Spar-wraith's 45° turn: check in live play on the derelict deck at night.

- **BACKLOG EMPTY (2026-10-29):** rows 12/35/36 fixed and pinned by tests, row 30 is later-act (record only), no clip
  is asked of this track, and the boss sweep's one weak read (the Spar-wraith) is fixed. What's left is real-GPU only
  (PC-QUEUE).
