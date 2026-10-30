# Live log: battle-presentation environment

**Session:** `session_014EcW9e5tEmjDi5S2HmCECd` (cloud) · **Branch:** `claude/battle-presentation` (from `claude/undertow-lead-handoff-423ixt` 499f074) · **Role:** combat · **Lead:** `session_019iimsngAgPLEram1wcbLpE`

The gap (the human's playtest note): battles had no action animation. This track adds a listen-only presentation layer: choreography, a clip contract, a camera director, the specials, the intro and outro. Docs: `docs/kb/tech/battle_presentation.md`.

### 2026-10-30 ~21:40: the Lead's 20:26 and 21:25 (Act I readability pass, pillar 4, on 46d8a067 merged in at 39486b66)
**In progress. The first fix is MERGE-READY @ d58eb032.**
- **The tool:** tools/vfx/readability_sheet (15d1b779, ec07c623). Every Act I fight at 1920x1080 per text scale:
  - stills of the target pick (the cursor, the rings, the action's cost on the timeline) and of the hit;
  - checks for HUD labels that overflow, and for floats drawn over the timeline or the party panel.
  - VFX draw under the HUD's layers, so none can cover the turn order.
- **Found and fixed:** at 130% text, the current timeline chip's "Acting now" ran past its bottom border (d58eb032,
  viewed; timeline 30/0).
- **Checked, not a defect:** the party panel's numbers at 130% sit above their gauges (ui-menus' own fix). My first
  run had set the scale on a private UiSettings and missed it.
- **Tideline at 1.0 and 1.3:** turn order, cost, target ring and damage number all read. No overflow, no float over
  the timeline or the party panel.
- **Queue after this (the Lead's 21:56, ADR 0207):** the Act I readability pass, then the Act II one, then the
  paused Act I sweep (Ch6, Ch8). After that: Act III production (battle VFX, boss intros, the finale camera; ids
  M5-A3P-1900..1949), or an offer to slice-polish's Act II cutscene staging by request task.
- **Running:** every Act I fight at 1.3 (the sweep covered 1.0). The Ch6 encounter sweep is paused so this pass has
  the CPU. Then the same pass for Act II.

### 2026-10-30 ~19:30: the Lead's 18:45 (The Seven out of frame, creatures-b 5e3492af)
**MERGE-READY @ 004f4dae.** A tall called Vowbound gets its own rest frame (9999f3e1, tuned 004f4dae).
- **The problem:** on the middle party slot, right before the camera, Kesh's head was cut at rest. In The Seven
  the director takes no lead or contact shot (both come back empty), so as she rises her head and raised arms left
  the frame.
- **The fix:** `camera.rest_by_vowbound` (as rest_by_enemy, applied after it) moves the rest frame while one is
  out, and the fight's own frame comes back when it leaves. Kesh: 3 m back, 1.4 m up, fov 52.
- **SELF-RENDERED** (a probe calls Kesh on the tideline as Asha): rest, and The Seven's lead, contact and +0.8 s.
  Kesh is whole with headroom, and the foes read. vowbound 117/0.
  - Ethren's row (2.6 m back, 1 m up, fov 52) is NOT viewed yet. Next.
- camera: 73 run, 1 failed, test_qa_field_camera (lowlight's field camera). It fails without this change too; not
  mine.
- **Sweep, ch04_derelict_leeches:** Ilun "under the timeline" at his Brine Lash and attack is the contact shot's
  over-the-shoulder: the target leech reads clearly, and Ilun's net reaches past the right edge. Judged as framing,
  not a defect. 55e54edd (his seat) does not change it and is harmless. ch04_derelict_glass is clean.

LEAD-ASK (18:30): Not idle and not blocked. Everything you asked at 17:04, 18:04 and 18:2x has been MERGE-READY on
`origin/claude/battle-presentation` since 17:30, as logged right below and in the CURRENT STATUS table. If these
updates aren't reaching you, please read this file on this branch, not the integration copy.
- **MERGE-READY @ 064c9e46:** the crawler's 3 effects and the Vowbound's 19.
- **test_battle_act1_ability_vfx:** green.
- **MERGE-READY @ bdc5ef22:** the Act II boss intros.
- **MERGE-READY @ 5aa9f169:** the branch head, everything.
- Since then: the Act I encounter sweep only.

## 2026-10-30 ~17:30: the Lead's 17:04 (big25 merged in at 9795b3f3)
**MERGE-READY @ 064c9e46.** The conduit crawler's 3 and the four Vowbound's 19 battle effects are generated, now that
their rows are on integration (06a51e5c). Checks on the merged tree: `--filter=vfx` 46/0, `--filter=vowbound` 117/0,
`--filter=act2` 78/0, validate_data clean, both generators' `--check` clean.
- **test_battle_act1_ability_vfx (red on integration since the Vowbound rows landed):** it needs every Swell technique
  to have its own effect, and the_seven, farewell_tide, pass_cord and still_water had none. Fixed by 06a51e5c.
  `--filter=act1_ability_vfx` 5/0 at 19f9abe6.
- **Act II boss intros on big25 (bdc5ef22), SELF-RENDERED and viewed:**
  - Drowner and Lamp Engine: they read, and the crawlers stay out of the intro.
  - Avalanche Ram: its hero shot saw the new model's rump, its low head behind the card. Its row takes the fitted
    boss shot: the Ram head-on above the card. boss_intro 24/0.
  - The Lamp Engine's moves sheet (on its fight with the crawlers) is clean.
  - **MERGE-READY @ bdc5ef22.**
- Also in this range: a called Vowbound kept clear of the timeline (55e54edd, the sweep's ch04_derelict_leeches;
  screen_spread 3/0).
- Next: the Ch10–Ch13 boss intros. On integration that is the Drowner, the Lamp Engine (now with two conduit
  crawlers) and the Avalanche Ram; Ch13 has none. Re-rendering them and the Lamp Engine's moves.

## CURRENT STATUS (2026-10-30 18:10). Branch head is MERGE-READY. Act II task ids: M4-A2P-1900..1949 (the Lead, 18:04)
| Item (the Lead's 17:04 and 18:04) | State | Commit | Check |
|---|---|---|---|
| The conduit crawler's 3 skill effects | **MERGE-READY** | 06a51e5c | big25 merged in (9795b3f3); vfx 46/0, act2 78/0 |
| The four Vowbound's 19 effects (15 skills, 4 finishers) | **MERGE-READY** | 06a51e5c | vowbound 117/0 |
| test_battle_act1_ability_vfx (red on integration: the Vowbound finishers had no effects) | **green**, 5/0 | 06a51e5c | |
| Act II boss intros, Ch10–Ch13 (Drowner, Lamp Engine with its crawlers, Avalanche Ram; Ch13 has no boss yet) | **MERGE-READY**, all viewed | bdc5ef22 (the Ram: hero shot off) | boss_intro 24/0 |
| Earlier: rank overlap and the menu safe area, rows 61 and 64, the glimmer hit, a Vowbound clear of the timeline | in big25 | aa227a57, ef997f3d, 7c3307df, 4c4a3dd3, 55e54edd | battle 826/0 |
- In flight: the Act I encounter sweep (Derelict Leeches and Glass, Ch6 ridge), then Ch6 and Ch8.

## NEW ACCOUNT (from 2026-10-25)
Session `session_015hKkhtpX67kS4yZeA8AAhv`. Integration branch `claude/undertow-lead-handoff-ze8rrn` merged in
(c6a960ab).

### 2026-10-29: the new Lead's brief (integration branch `claude/new-session-mj8c3c`, merged in at b3f092f8)
- **Merge:** one conflict, `pc-gpu.md` (not mine): took the integration branch's side.
- **1. The stair meter on env-art-b's Fisher Stair:** nothing new has landed. The integration branch has no new stair
  commit, and env-art-b's branch has no new prop. The hook from M3-BPR-1325 (the Corrow kit's `fisher_stair` and the
  `StairHead_ward` / `CameraHints/the_stair_head` marks in all three seawall arenas) still stands. Re-checked:
  `--filter=stair_marks` 5/0.
- **2. act1_gpu_qa rows** (read from `gpu/act1-qa-2` @ 59a41402):
  - Row 36 (the Reach's arm over the party) is mine. It was fixed in M3-BPR-425 (camera.rest_by_enemy) and viewed,
    and it waits on the PC (PC-QUEUE below).
  - Rows 12 and 35 (Moll a capsule in battle): the battle side was closed by M3-CHR-523 (his stand-in).
  - **Row 34 (ch06_ridge_skippers on the sandbox's set and foes) is not a battle bug.** The encounter row is right.
    The three foes are `sandbox_reef`, which `FieldBattle` plays when it takes no request. `BattleRequest.submit` has
    no guard against a second submit while the first is still awaiting its stinger, and the QA walk starts fights
    from outside the zone while brine_shoals' random encounters can still fire. Diagnosis and proposed fix are in
    request **M3-BPR-427** (to slice-polish, who own `game/flow/**`). I did not edit their file.
  - Inventory: `placeholder_audit.py --static-only` lists nothing for combat or battle-presentation (19 items: audio,
    creatures-b, env-art). `battle_vfx_coverage.py`: 0 unexplained gaps. Every Act I foe's skill has its own effect,
    except the Drownbell's toll and toll_gather, which are its set piece (BattleBossVfx and BattleTelegraph).
- **3. M3-BPR-406's last open question** (asked of act1-chapters on 10-27, never answered; I decided it per ADR 0042):
  - The Breach's gather turns stay on the home frame, with the push-in only.
  - Wave 3's Kirru cuts to the hoist arena's `CameraHints/along_the_walk` (the movers in front, the party behind
    them) the **first** time Pell sounds Storm-Call (`storm_call_sound`). I rendered and viewed five hints;
    `the_storm_wall` showed only Toma's back, and `party_side` hid the foes.
    His later calls, and Storm-Call itself (the withdrawal), stay on the home frame, where the player sees which
    spawn leaves.
  - This needed a per-role `skills` filter and a `once` list on choreo.json `camera.moments.entry`
    (BattleEntryCamera). Test: test_the_kirrus_first_call_cuts_along_the_walk. `boss_camera_sheet --entry` now also
    renders the Kirru's cut.

- **MERGE-READY @ e205c3e0** (+ this log commit): M3-BPR-406 (the Kirru's cut, now in review), request
  M3-BPR-427, and the integration-branch merge b3f092f8.
  - SELF-RENDERED @ e205c3e0 with `boss_camera_sheet --entry` (not a manifest shot). Viewed: the Kirru's cut along the
    wall-walk shows the crawlers and polyp in front and Asha, Toma and Rhen behind with the hoist; the Climb's cut is
    unchanged. No manifest shot can move: entry cuts play only mid-fight, and no shot freezes one.
  - Checks run: Godot `--filter=` set_piece 48/0, ch08 23/0, boss_camera 7/0, stair_marks 5/0; gdlint, gdformat,
    validate_data 0/0, taskboard --check.
  - Checks skipped: the screenshot manifest (no shot can move), Blender (none touched), coverage (no game/battle core
    change), and the tools suite (no tools/*.py touched).
- **BACKLOG EMPTY (2026-10-29 18:xx):** the brief's three items are done or waiting on others:
  - the stair has no new prop;
  - row 34 waits on slice-polish (M3-BPR-427);
  - row 36 waits on the PC;
  - VFX coverage and the inventory have nothing left for this track.
  Next: merge big17 when the Lead announces it, then any new rows.

### 2026-10-29 evening: the Lead's 17:59 message (Kerrid's and Liss's Swell techniques, then the Act I VFX sweep)
- **Claimed** M3-C05-06 and M3-C06-05 (2b-claim commit, pushed).
- **The techniques** (80e565ea):
  - Kerrid: **The Long Hold**, physical 14, one foe (Return Tide's band).
  - Liss: **Three-Reel Charge**, physical 9, every foe, a 1-rank push (Written Light's band less one for the push).
  - Their inputs are data rows on the existing kinds. The weighted swing is a one-blow `brace` (hold while the
    cleaver coils, let go on the count). The reel-stop is a three-beat `timing_ring`. Both give +45% at good and +90%
    perfect.
  - formulas.md and test_formulas.gd list both. No formula or constant changed.
- **Viewed with self-rendered stills** in their own fights: `tools/vfx/swell_finisher_sheet.gd` plays each technique
  through BattleSwell.perform.
  - Liss on the Ch8 hoist reads: the gadget bursts over all four foes.
  - Kerrid on the Matron showed only the chest hit at first. His low sweep spawned inside her 2.9 m bulk.
- **Fix (0c84c54b):** new near-face low anchors, `ground` and `knee` (feet stays centred, for rings).
  - Kerrid's sweep uses knee; Anchor Fall, Return Tide and Lamp Dive use ground.
  - Re-rendered: the sweep's sand now shows low on her near side, apart from the chest hit.
- **Sweep, Act I foe and boss actions:** every AI-picked skill of every Act I foe has its own effect (the Drownbell's
  toll is its BattleBossVfx set piece). The one hidden effect found was the Matron's recrust ring (0.75 m, inside her
  bulk). It is now 1.6 m (5b5d42d8). Re-rendered: ember motes ring her base.
- **Off the tree (the Lead's 19:24, ui-menus' error sweep), e7aaf8cd:** BattleVfx play, play_at, anchor, entry_mark and
  _half_depth, and BattleBossVfx's deferred polyp light, no longer read or set global transforms once the fight has
  left the tree. New test test_battle_vfx_off_tree (2).
- **test_battle_act1_ability_vfx:** after merging origin/claude/new-session-mj8c3c (cf2ffc15) it passes, 5/0.
  - Its failure was the one I hit and fixed in 0c84c54b: the Swell techniques had no map.skills row of their own.
  - A tree with 80e565ea but not 0c84c54b fails it.
- **MERGE-READY @ 8da23b91** (+ this log commit): M3-C05-06 and M3-C06-05, the Swell part only (to review: combat),
  the ground/knee anchors, the recrust ring, and the off-tree guards. The integration branch is merged in.
  - **Checks run on the merged head:**
    - Godot `--filter=` battle 812/0, swell 151/0, formulas 39/0, off_tree 2/0, vfx 28/0.
    - `sim.py --check` on the 18 Ch5, Ch6 and Ch8 suites with Kerrid or Liss: exit 0, all 77 policy rows in band.
    - validate_data 0/0, taskboard --check, gdlint, gdformat, `gen_act1_ability_vfx --check`.
  - **Coverage:** the full gate exits 2 (the run failed, not a drop), and none of the failures are from this branch.
    - Under instrumentation the whole suite fails 11 tests outside battle, then segfaults in
      test_villager_routines.gd:434 (a freed instance).
    - The 11 are: test_creature_portraits (nhoa, hesk, ethren portraits missing), test_field_audio,
      test_hero_field_snaps (haluna_wake, drowned_choir), test_villager_routines (3), test_act1_cutscene_walks
      (haluna_wake), test_fp_prologue (Liss's vigil), test_qa_capsules (Haluna villagers, Act II foes) and
      test_qa_save_shrines (haluna_wake).
    - These are the integration branch's reds. The Lead routes them.
    - `--filter=battle` report: game/battle 96.57% (2588/2680). The files under baseline there are the ones tests
      outside the filter cover (battle_swell, bestiary and others). This branch changes no game/battle/*.gd.
  - **Skipped:** the screenshot manifest (no shot freezes a Swell or the low anchors; finisher stills viewed with the
    new tool instead), Blender (none touched), and the tools suite (only tools/vfx scripts touched;
    `gen_act1_ability_vfx --check` passes).
- **Sweep, done:** every AI-picked skill of every Act I foe and boss has its own effect, timing and camera. The hidden
  ones I found are fixed: Kerrid's sweep, Anchor Fall, Return Tide, Lamp Dive and the Matron's recrust.
- **BACKLOG EMPTY (2026-10-29 ~21:xx):** the Lead's 17:59 and 19:24 items are done.
  - Left open and not this pass: the rest of M3-C05-06 and M3-C06-05 (gear, Lattice, Liss's steal and gadgets,
    Kahre, the shop tier).
  - The integration branch's coverage reds.

**MERGE-READY @ afe59523** (+ this log commit): the Act II creature bosses' PROVISIONAL rows and staging, and two Act I
sweep fixes.
- **LEAD-ANSWERED (03:44): the Act II boss rows, PROVISIONAL (1dbfed6d).**
  - enemies.json:
    - mangrove_drowner: Ch10, L9, 5200 HP; phase uprooted at 50%;
    - lamp_engine: Ch11, L10, 5600 HP; opened at 50%;
    - avalanche_ram: Ch12, L11, 6200 HP; torn_fleece at 40%;
    - wakefin: Ch15, L13, 7000 HP; close_circle at 40%.
  - Each row has its creatures.json model and phases, lore, and `"provisional": true`. 15 skills come from
    creatures-b's sheets, and none of them use ice (ADR 0204).
  - encounters.json: ch10_mangrove_drowner, ch11_lamp_engine, ch12_avalanche_ram and ch15_wakefin, on M3-BPR-419's
    arenas. **Not yet placed in zones** (that is chapters' job).
  - **For act1-chapters (the chapters' combat seat):** tune these with the sim against the Act II boss band
    (balance_targets.md: naive ≤ 3%, role_answer 55–80%, smart 70–90%). No suite exists for them yet.
  - Request **M3-BPR-428**: an evasion-up status for Sound Dive (ADR 0204 #3), and the Ram's snow field.
  - Their skills' effects are in gen_act2_ability_vfx.py (23 Act II skills), and test_battle_act2_ability_vfx
    covers phase skills.
- **On stage (26db1af3, afe59523):**
  - The Wakefin's seat is in the water past the barge's back rail (boss_seats; its blade had stood out of the deck
    planks), and its blows stay in place (style_by_actor).
  - The Drowner has a seat and a fitted rest frame. Its root cage had filled the frame and its top was cut off.
  - The whole-party sweeps (ram_bellow, wake_breach, wake_wheel) play in place.
  - SELF-RENDERED and viewed the four bosses' arena previews:
    - the Wakefin's black fin cuts the dark water beyond the rail;
    - the whole Drowner stands beside a readable party;
    - the Lamp Engine and the Ram read whole (no change).
- **For the Lead at merge:** on big18, creatures-b moved the Reach's seat to [-5.0, 0, -2.4] (a654ccc5, GPU QA rows 35
  and 36), and this branch's boss_seats line adds the Wakefin and the Drowner. Keep their Reach value plus this
  branch's two new rows (the scratch merge does exactly that).
- **Act I sweep fix (21ef24f9 + 26db1af3):** the tallest foes are seated farthest from the camera (spacing.tall_to_back).
  - On the causeway the Lantern Eel had hidden the Gull Harrier at rest, and in the harrier fight the gull hid the
    crab. Foes of equal height keep their own slots.
  - Test test_battle_seat_order fails without it.
  - **Multi-foe battle shots move (their seating): the gate views them.**
- **Checks run:**
  - Godot `--filter=battle` **819 run, 0 failed** (fresh user dir, on 26db1af3);
  - on afe59523 (data only): `--filter=` boss_camera 8/0, act2_bosses 5/0, arena 18/0, seat_order 2/0;
  - earlier: ability_vfx 6/0, act2 6/0, encounter 1/0, boss 85/0, set_piece_shots 4/0, party_kits 4/0;
  - validate_data 0/0, taskboard --check, gdlint, gdformat, and gen_act1/2 --check.
- **Skipped:** the full manifest (ADR 0205; the gate views the moved battle shots and the four boss arena previews),
  Blender (none touched), coverage (no game/battle core .gd change).

**The Act I encounter sweep, batch 2** (on big18 + this branch at e9d38ec4): ch03_causeway_shore, ch03_causeway_harrier,
ch01_wickfry, ch01_oil_slug, ch01_shaft_limpet and ch01_scuttlers.
- Every automatic check is clean: the arena is right, every landed hit and status has its effect, and no framing
  issue.
- Contact sheets viewed:
  - The causeway's eel-over-gull was fixed by the seat order.
  - The Underway fights read in their dark arena.
  - wickfry and oil_slug end in one action, so they have few stills.
- ch01_hullgnaw hit the batch cap after its opening (viewed: it reads), so it leads batch 3.
- Batch 3 is running: hullgnaw, the two Underway fights, and Ch4's leeches, Hermit and Spar-Wraith.

**MERGE-READY @ ac34fe8b** (+ this log commit; integration merged in at 1060a593):
- The items:
  - drownbell_flood (9524f9f0);
  - GPU QA rows 57 and 61 (921e5fec);
  - the encounter sweep's fixes: the bystander-hidden contact (75b2ebea, ab7c9925), the smaller hit cores and the
    floats in the safe frame (339ddd43);
  - M4-A2P-060 part 1, the Act II regulars' VFX (65ea933e).
- **Checks run:**
  - Godot `--filter=battle` **817 run, 0 failed** (fresh user dir);
  - `--filter=` camera 60/0, summon 23/0, vowbound 89/0, arena 18/0, boss 84/0, ability_vfx 6/0;
  - validate_data 0/0, taskboard --check, gdlint, gdformat, and `gen_act1/2_ability_vfx --check`.
- **Shots self-rendered and viewed:** drownbell_flood, battle_boss_intro_drownbell, battle_choreo_summon,
  battle_arena_seawall_stairhead_surge, battle_arena_bridal_barge_night.
- **Shots the gate should view** (the hit cores, the floats and the summon shot can move them): those five, plus any
  battle_choreo_* or battle_boss_* frame that freezes a contact.
- **Skipped:** the full manifest (ADR 0205), Blender (none touched), coverage (no game/battle core .gd change).
- An earlier run showed 4 reds (battle_result_motion, battle_stings). They came from merging the integration branch
  while the run was going: each file passes 5/0 on the merged tree, and the clean run above is 817/0.

### 2026-10-30 14:50: for the Lead's 14:48. Every item is pushed, MERGE-READY, branch head @ 7973fb7a
- **All five items are MERGE-READY** (the table below, committed at e32568c2 and 7973fb7a). The overlap and
  command-menu fix landed at aa227a57: full `--filter=battle` 826/0.
- **The split with creatures-b** (proposed; creatures-b, please confirm in your log):
  - **battle-presentation:** the effects data. The three conduit-crawler skills and the four Vowbound's 19 are
    written in tools/vfx/gen_act2_ability_vfx.py. I run the generator on the first integration merge that carries
    their skill rows (big22/23).
  - **creatures-b:** once those rows are in, view each Vowbound's and the crawler's effects on its own model (the
    anchors and sizes fit the bodies you built). File any misfit to me as a task. I fix the data the same day.
- **In flight:** sweep batch 5 (the last four Ch4–5 encounters, the Hermit re-run, the stair re-check with the
  spread), then Ch6 and Ch8.

### 2026-10-30 ~14:10: status for the Lead's 14:09 (for big24)
| Item | State | Commits |
|---|---|---|
| Glimmer element hit | **MERGE-READY**, verified on big21 | 4c4a3dd3 |
| Row 61 (the Reach's rest frame) | **MERGE-READY**, viewed | ef997f3d |
| Row 64 (the camera search behind the fade) | **MERGE-READY**: reveal frame 1.2–2.6 ms headless | 7c3307df (+ 65e776af, the particle variants) |
| Act II foe-skill effects | **MERGE-READY**: the Act II regulars and bosses (65ea933e, 8d0fe783..f2bbb673); act1-chapters' 3 new conduit-crawler skills and the Vowbound's 19 are written as their rows land | 6f3608a7, 97e22896 |
| Rank overlap and the command-menu safe area | **MERGE-READY @ aa227a57**: full `--filter=battle` 826/0 | c552664f, 3d65ec00, aa227a57 |

- **Act II effects:** act1-chapters' and gate-big22's skills.json hold 3 Act II foe skills with no effect (brush_jab,
  crawler_mend, crawler_tend). Those are in FOES_PENDING. On gate-big22's data, gen_act2_ability_vfx writes them
  with the Vowbound's 19, and `--check` is clean. **After big22/big23 merge, run `python3 tools/vfx/gen_act2_ability_vfx.py`
  (or I will on my next integration merge).**
  - I found 3 such skills, not 6. The only other candidates (drowning_grasp, tide_gather) are on older branches.
- **Rank overlap (BattleScreenSpread):**
  - At spawn, on the fight's rest frame, foes whose boxes share more than 20% of the smaller step apart. The left
    foe steps away from the party, and the right foe steps back. A foe on the command menu steps back or right.
  - No step lands a foe in another's footprint, on the menu or in a melee lane. A lone foe keeps its seat.
  - Viewed: tideline, the stair's tortoises, the flats' crabs, both underway fights and the fen's root crabs.
  - Allowance: the causeway's and the flats' Crabs are boxed in by the Eel and the Gull. Their leg tips may reach
    56 px over the menu's top edge (`spacing.screen.menu_edge_px`), but never their bodies.
  - Baseline drift: the opening line-up moves in any multi-foe fight, so the gate re-renders the battle shots.

### 2026-10-30 ~11:xx: the Lead's 10:47 item (row 64 is the camera search, after creatures-b's trace)
**MERGE-READY @ 7c3307df** (+ this log commit). Rows 61 (ef997f3d) and the glimmer hit (4c4a3dd3) were done before.
- **Row 64's cause** (creatures-b's trace of pc-gpu's big21 capture): BattleBossHeroShot.search ran on the first
  uncovered frame. There were no pipeline compiles. 65e776af (the particle variants) stays as a harmless guard.
- **The fix:**
  - BattleBossIntro frames its boss at the first turn, while the fade covers the screen, and keeps that pose for
    the reveal.
  - The arena's occluders are built once per battle.
  - Meshes shorter than `boss_intro.hero.occluder_min_h_m` (0.5) are no longer occluders. The Drownbell drops from
    935 occluders to 217 (its saltgrass).
- **Verified headless** (shared CPU, so the absolute numbers run high):
  - The reveal frame is 1.2–2.6 ms in the Drownbell, Hermit, Inquisitor (Moll), Matron and Hullgnaw fights.
  - The search, 27–343 ms, now runs behind the fade, inside ADR 0029's 1 s limit for hidden frames.
  - Every fight's chosen pose is unchanged with the filter, so no baseline moves.
  - Tests test_the_boss_is_framed_behind_the_fade and test_short_arena_meshes_are_not_occluders. boss 88/0,
    camera 65/0.
- **Still open, mid-fight:** the phase and fall camera moments run the same search after an action, uncovered: about
  100 ms on the Drownbell headless. The filter and the cache help. If PC-QUEUE shows them over 50 ms, the next step
  is to search once at the action's start, in the time the action plays.
- **PC-QUEUE:** re-measure row 64 (the 60 frames after the fade) at tideline, the causeway, the Drownbell, the Hermit
  and Moll.

### 2026-10-30 ~10:xx: the Lead's 10:07 item (PC pass 5 rows 61 and 64)
**MERGE-READY @ ef997f3d** (+ this log commit). The glimmer swatch is in 4c4a3dd3 (below).
- **Row 64 (65e776af): a 73-119 ms frame in the 60 after the fade, in five fights.**
  - Cause: a ParticleProcessMaterial compiles one shader per feature set. Every battle effect sets a color ramp, and
    most motes add turbulence. prewarm_materials.json warmed only the bare base spark material, so the first effect
    after the fade compiled its variant.
  - Fix: the registry now stages the ramped variant and the ramped turbulent one for the battle scenes
    (battle_spark_process_ramp{,_turb}.tres).
  - Test test_battle_vfx_prewarm: every effect layer, as BattleVfx builds it (reduced motion too), matches a warmed
    variant. It fails without the two rows. `--filter=prewarm` 23/0.
  - **PC-QUEUE:** re-measure the 60 frames after the fade at tideline, causeway, the Drownbell, the Hermit and Moll.
    This is the likely cause, but only the GPU can confirm it. If a frame stays over the bar, the next suspect is
    the runtime actor scenes (boss rigs), which the scene harvest can't see.
- **Row 61 (ef997f3d):** the Reach's rest frame (rest_by_enemy) is now 6 m back and 1.6 m up at 56° (was 4, 2, 48).
  - SELF-RENDERED battle_arena_seawall_stairhead_surge, three tries, viewed. Its hand grips the wall beside the
    party, the arm takes about a fifth of the frame, and the party and the sea read.
  - Tests: camera 65/0, boss 86/0, arena 18/0.

### 2026-10-30 ~09:xx: the Lead's 09:00 item (the glimmer element's hit)
**MERGE-READY @ 4c4a3dd3** (+ this log commit): `hit_glimmer` and `map.elements.glimmer` for act1-chapters' glimmer
element (voice_glimmer, level_hand, still_water).
- The effect: a soft pale-gold core, then motes rising off the target. It is released glimmer (color_script rule 1:
  glimmer_lift brightening to glimmer_lift_hi, rising, never the held cyan).
- Its sound stands in on hit_holy (battle_sfx.json vfx row) until audio writes its own.
- **Verified on origin/lead/gate-big21 with this branch merged** (scratch worktree, imported): `--filter=battle_vfx`
  10/0, and validate_data is clean.
- Merge note: tests/screenshots/shots.json conflicts with big18+ (both sides append at the end). Keep both.
- **A big21 red that isn't mine:** `test_battle_vowbound_model::test_a_real_vowbound_lands_each_action_on_its_clip_contact`
  fails for every Kesh action (voice_* and the_seven: no clip of its own, no contact time). It fails the same on
  big21 without this branch. BattleClips.action_clip reads Kesh's creatures.json row (clip_for), which maps none of
  his skills. That row belongs to the creatures lane (Kesh's model and clips).
  - The rest of that suite passes on big21 + this branch: `--filter=vowbound` 116 run, that 1 failed; `--filter=vfx`
    45/0.
- **M4-A2P-061 claimed:** the four Act II Vowbound's VFX and finishers are in gen_act2_ability_vfx.py (97e22896).
  Each is written once its skill row lands (big21), and all 19 are checked there.
- **Rows 57 and 61, verified on big21 + this branch (SELF-RENDERED, viewed):**
  - battle_choreo_summon: the side-on frame keeps Ilun clear of the foes and the gull clear of the eel.
  - battle_arena_seawall_stairhead_surge: the Reach is on its mark, its arm over the wall, with the party on the
    wall-walk beside it.
- Also MERGE-READY in this range: the Act II boss intros (c3e45bb0), the Act II boss moves fixed and viewed
  (8d0fe783..f2bbb673; M4-A2P-062 Sound Dive verified in live play: sea-glow at the fin's crest beside the Breach
  telegraph), and the Hullgnaw fall frame (8b0e12c2, viewed in a re-run of the sweep).

### 2026-10-30 ~03:xx: GPU QA pass 3 rows 57 and 61 (fixed, 921e5fec), and Act II begins (ADR 0205)
- **Row 57 (battle_choreo_summon), fixed.** Nobody overlapped on the floor. The summon shot sat 4.2 m behind Ilun
  on the battle axis, so Ilun covered the foes and the gull read through the eel.
  - It now looks in from the side (back 1.2, side 6.2, up 1.3, fov 54). Ilun is clear of the foes, and the gull is
    clear of the eel.
  - SELF-RENDERED and viewed.
- **Row 61 (battle_arena_seawall_stairhead_surge), fixed.** The preview put the Reach on Slot0 under the authored
  camera, which is not what its fight shows.
  - The preview now seats it on its boss_seats mark and takes the fight's rest_by_enemy fit
    (BattleCameraDirector.rest_fit, now static and shared). The Reach's arm and head read over the wall, with the
    party beside them.
  - **env-art please note:** game/levels/_tests/battle_arenas/battle_arena_preview.gd gets one call, and
    BattleArenaLayout gains `enemy_slots`.
- Tests `--filter=` camera 60/0, summon 23/0, vowbound 89/0, arena 18/0, boss 84/0.
- **No open Act I row is left for this track,** so Act II starts (ADR 0205).
  - Claimed M4-A2P-060 (Act II battle VFX) and M4-A2P-062 (the Wakefin in the dark).
  - **M4-A2P-060, part 1 (65ea933e):** tools/vfx/gen_act2_ability_vfx.py gives the eight Act II regulars' skills
    their own effects (Ch10 to Ch16), with ADR 0204's no-ice rule for Ch12 to Ch15. Test
    test_battle_act2_ability_vfx. Ownership row added.
  - **M4-A2P-062, viewed:** the battle_arena_bridal_barge_night preview is dark and readable (the party lit, the sea
    at night). **But the Wakefin is a capsule there, because it has no enemy row with a `model`.**
- **LEAD-ANSWERED (03:44, take the default):** the four Act II creature bosses (mangrove_drowner, lamp_engine, avalanche_ram, wakefin) have
  creatures.json models and full battle staging (M3-BPR-408/418), but no enemies.json or encounters.json rows. So
  their intros, cameras, the darkness fight and their skills' VFX can't go live or be viewed.
  - M3-BPR-419 (the request, with the staged ids) is now `todo`.
  - Who writes those rows: the chapters' combat seat?
  - Default if no answer: battle-presentation writes PROVISIONAL rows (model, arena, phases from creatures.json, and
    stats copied from the Act II boss curve with a `_note`) so the presentation can be built and viewed. The combat
    seat then owns the numbers.
- **Act II boss intros (c3e45bb0), SELF-RENDERED and viewed:** battle_boss_intro_drowner, _lamp_engine, _ram and
  _wakefin, on the PROVISIONAL encounters.
  - The Drowner, the Lamp Engine and the Ram take their hero shots under their cards.
  - The Wakefin's did not: no low lens was clear of the barge, and the fitted fallback framed its mostly-submerged
    bounds from 17 m behind the hull, so it was not in shot. Its row now takes `camera.shots.boss_over_rail` (hero
    and fit off): the fin above the card, with the rail leading to it.
  - New baselines for the gate: those four shots (never written by this track).
- **Act II boss moves, viewed** on tools/vfx/boss_camera_sheet (now covering the four Act II creature bosses):
  - **The Wakefin in the dark (M4-A2P-062):**
    - Each hit's white core was a flash in the night. effects.json `dark_arenas` now scales every layer's energy in
      bridal_barge_night by 0.35, except the sea-glow's (BattleVfx.dark_scale). 8d0fe783.
    - Sound Dive's ring played on the fin's near face against the hull, hidden by the barge. It now centres on the
      fin, and sea-glow motes climb the fin over the rail. A tried over-rail cut framed mostly deck and was
      withdrawn. 8d0fe783, 5d16499d.
  - **The Avalanche Ram:** Toma's shield stood across the Ram and its head left the frame in its charge_side shot.
    1.0 m up and 7.2 m out keep both. Viewed. 5dc0eb00.
  - **The Lamp Engine:** its canopy left the top of the rest frame (rest_by_enemy lamp_engine). Viewed. fdc92fbe.
  - **The Mangrove Drowner:** Root Stamp throws splinters and fen mud. The teal over it was Rising Water's,
    left on the sheet, which now waits out each move. 3ae3896c, 5d16499d.
- **Act I sweep, Hullgnaw (batch 3):**
  - Checks clean: the arena, impacts, framing, and no dead time.
  - But the victory frame put the fall moment behind the raft's rail and a post. With Rhen alone, the intro's hero
    shot is a low 30° lens from across the raft. The fall now searches its own higher lenses (moments.fall.hero).
    8b0e12c2, test test_the_fall_looks_down_from_above_the_intros_lens.
- **Not mine, for the Lead:** test_cutscene_vfx_hosts fails to parse on this branch with or without my changes. It
  uses `CutsceneMotes`, which 93c1aa2d removed.
- **The Act I encounter sweep (the Lead's 23:10)**, so far:
  - Done: ch02_tideline clean (arena, impacts, framing). The Drownbell's 8 stills were viewed and are clean after
    the hit-core and float fixes.
  - The tool runs about 50 min per boss fight on lavapipe, so the caps dropped to 10 actions and 2 min.
  - The remaining 31 run in background batches between Act II items, and findings go here.
- **The wedding-trap step-hold (ADR 0204 / act2_plan Ch14):** needs the court-steps encounter (combat) and the
  `ansedra_lacquer_court` arena, which has no arena scene in arenas.json yet (env-art).
  - Presentation is ready by role: the ward entry ("Merel's knife") uses BattleEntryCamera and the StairHead_ward
    mark, as the Fisher Stair does.
  - The arena needs `StairHead_ward` and `CameraHints/the_stair_head` marks. A request follows when the encounter
    is drafted.

### 2026-10-30 ~01:xx: the big17 gate's drownbell_flood regression (the Lead's 00:47), fixed @ 9524f9f0
- **Cause, mine:** M3-BPR-426's phase moment.
  - The fixture forces the Flood (BossMechanics.check_phases). That now eases the camera onto the bell, and the
    capture froze it mid push-in, so the party was out of shot.
  - The fixture now ends the moment (BattleCameraDirector.end_moment).
- **A real-play bug behind it:** that moment's lens sat at the risen waterline (y 0.6, the flood's 0.6), so the water
  was edge-on and invisible.
  - Camera moments now keep the lens camera.water_clear_m (0.5) above the flood's target height. It is checked each
    step, because the rise is set after the moment starts.
  - Test: test_the_floods_phase_moment_stays_above_the_water. `--filter=camera` 60/0.
- Not creatures-b's: the Drownbell model is fine.
- **SELF-RENDERED @ 9524f9f0:** drownbell_flood and battle_boss_intro_drownbell, both viewed.
  - drownbell_flood: the party waist-deep in the teal flood, the bell and the glowing polyp, as the baseline.
  - battle_boss_intro_drownbell: the bell on the causeway disc under its title card.
- **Drift for the gate:** drownbell_flood (the new bell model and the arena, against the old baseline). Plus the
  battle shots my 339ddd43 can move: the element hit cores are smaller, and damage floats start inside the safe
  frame.

### 2026-10-30: the Lead's 23:10 item, the Act I encounter sweep (in progress)
- **The tool:** `tools/vfx/encounter_sweep.gd` (75b2ebea, ab7c9925). It plays every Act I encounter (33: ch01..ch09,
  the Drownbell and the Reach) on the real stage at real pacing.
  - **Stills:** the opening, each party action type (attack, skill, item, Swell, Vowbound call), each foe or entry
    skill, and the victory.
  - **checks.json:**
    - the arena shown against the encounter's;
    - every landed hit and added status with an effect on its target;
    - at each contact, the actor and target on screen and clear of the HUD panels, and the target not hidden
      behind a bystander;
    - the longest stretch with nothing animating.
- **It runs** in a scratch worktree of origin/lead/gate-big18 @ d00d3284, with this branch merged on top (8 files).
- **First finding, fixed:**
  - On ch02_tideline, Toma's shield hid the Reef Crab at the contact of Rhen's Lamp Dive, Asha's Ember Pot and
    Rhen's Quick Hit.
  - The director now drops a contact shot when a bystander crosses the sight line to the target. If the held lead
    hides it too, it comes home for the contact. Test: test_a_bystander_across_the_sight_line_keeps_the_default.
  - Re-rendered: the crab shows at every contact.
- **Next:** view each encounter's contact sheet, fix, file and log. BACKLOG EMPTY only when every encounter is clean.
- **Batch 3 (10-30), on big21 + this branch:**
  - Clean (checks clean, stills viewed): ch01_underway_shoals, ch01_underway_limpet, ch04_sail_leeches.
  - ch01_hullgnaw: checks clean, but the fall moment's frame was behind the rail. Fixed in 8b0e12c2 and viewed.
  - **ch04_bottle_hermit: a sweep artifact, fixed in the tool.** The red "119" at the screen's corner was Ysolde's.
    After Ilun's return, the sweep's sim policy swapped her in through BattleEngine.swap, which seats no one on the
    stage. In play the game swaps through swap_members, which does. She fought, was hit by Glass Flare and fell with
    no body on the stage. The sweep now syncs the stage after a policy swap. Re-run queued with batch 5.
  - ch04_spar_wraith: clean (checks clean, stills viewed). At rest the Wraith is small and dark against the night
    sky; that is the arena's light.

### PC-QUEUE
- Row 64 re-measure (7c3307df, the search behind the fade): the 60 frames after the fade at tideline, causeway, the Drownbell, the Hermit and Moll; and the Drownbell's phase and fall moments.
- GPU QA row 36 (the Reach): re-check in live play on the RX 9070 XT (M3-BPR-425's rest frame).
- GPU QA row 34: re-check once M3-BPR-427 lands (and hold the zone's random encounters in the walk).

**MERGE-READY @ 1daa0fa7 (04:45): M3-BPR-423 boss-intro hero shots.** The Hullgnaw rail and the Drownbell framing are
both fixed and pushed. The branch head also carries:
- M3-BPR-420/422: the boss big-move camera, Kerrid's and Liss's Swell finishers, the Act I creatures' stand-in
  heights, hits on a big body's near face, and the trimmed KO flash.
- Checks run:
  - Tests: `--filter=boss_intro` 21/0, `--filter=battle` 776 with 2 fails (both fixed since: the boss-camera refit and
    the swing/reel sound rows), plus vfx 18/0, act1_ability_vfx 5/0, boss_camera 1/0, swell_finishers 3/0,
    audio_live 12/0, swell 151/0, camera 52/0 and choreo 56/0.
  - Static checks: gdlint, gdformat, validate_data, taskboard --check and `gen_act1_ability_vfx --check`, all clean.
  - Tools: test_choreo_validate OK. test_screenshots fails only on my three battle_ch08_* baselines (the gate's to
    write). test_iskarra fails on a clean tree too (not mine).
- **Not yet run: the full Godot suite on the head.** Two runs were stopped because I edited under them. It runs once
  my arena renders finish, and I will log the result here.
- Shots the gate should re-approve:
  - the six moved battle_boss_intro_* (viewed above);
  - any battle shot with an Act I creature, since the heights and the near-face anchor move its effects. I am
    self-rendering those next.

**BACKLOG EMPTY (2026-10-28 19:xx), MERGE-READY @ the branch head: the Lead's 18:37 item (the Fisher Stair).**
- **Merged origin/claude/env-art-b** (its marks and camera hint). The Ch8 arena ids agree on both sides.
- **M3-BPR-1325:** the Climb anchors on `StairHead_ward`. The stair-aimed skills have their own effects there, and the
  Climb's turn cuts to `the_stair_head`.
  - SELF-RENDERED and viewed: battle_ch08_stair_hold (no capsule), battle_ch08_intercept, and the Climb's cut.
- **The prop mesh is not missing:** the Corrow kit's `fisher_stair` stands in all three seawall arenas. So there is no
  LEAD-ASK.
- **Shots for the gate:** battle_ch08_stair_hold and battle_ch08_intercept move (the storm sky and the marks), plus the
  earlier list.
- **What is left is not mine:** combat's design tasks (Kerrid's and Liss's techniques), creatures-b's vfx_anchors rows
  and Hullgnaw's intro clip, and the gate's baselines.

**BACKLOG EMPTY (2026-10-28 16:xx, MERGE-READY @ the branch head):** the Lead's 13:25 list and the combat-owned
presentation tasks are done, self-rendered and viewed:
- M3-BPR-411 (VFX coverage closed);
- M3-CHR-523 (Moll in battle);
- M3-BPR-1305 (Ch5 on Ashcrown);
- M3-ENV-737 (greybox arenas retired);
- M3-CRB-009 (boss intro clips, anchor bones);
- M3-ENV-714 (Ch8 seawall states);
- M3-CRE-639 (Ilun's rise and dismiss): SELF-RENDERED battle_choreo_summon and _vowbound_rise, Ilun unfurling up.

What is left is not mine:
- **combat's game design:** M3-C01-03, C04-06, C05-06, C06-05, C09-07, RBL-1208. Kerrid's and Liss's techniques wait
  there (their finishers are staged).
- **env-art-b:** the Fisher Stair prop (LEAD-ANSWERED above).
- **creatures-b:** Hullgnaw's intro clip turns its head away (noted on M3-CRB-009); vfx_anchors rows.
- **The gate:** re-approve the moved baselines (boss intros, the Vowbound and summon shots, battle_ch08_stair_hold,
  battle_arena_camp) and write the three battle_ch08_*.

**MERGE-READY @ the branch head (15:xx).**
- **M3-ENV-714:** the Ch8 wall-head fights play on their seawall states (stair hold 1 on storm, 2 and 3 on hoist, the
  Reach on surge).
  - SELF-RENDERED and viewed: battle_ch08_stair_hold, battle_boss_intro_reach, and the Reach's fight frame on surge.
- **Fix for a regression I introduced** (M3-BPR-426's camera moments): at instant pacing a moment could start that
  nothing advanced, and the turn waited on it, which test_ch08_thread caught.
  - Moments now play only while the choreography animates. Bisected to 29eef908 and fixed at 93de03c3, with a test.
  - ch08_thread 6/0, boss_camera 7/0.
- Shots for the gate: battle_ch08_stair_hold also moves (the storm state).

**MERGE-READY @ the branch head (14:xx): the Lead's 13:25 list.**
- **M3-BPR-411 closed.** Battle VFX coverage has 0 unexplained gaps; the 5 left are kept on purpose (`INTENDED`).
- **M3-CHR-523:** the Inquisitor stands in as Moll's battle actor (battle_sandbox.json `stand_ins`).
  `enemies.json` `model` is reserved for creature scenes, and he is a person. His intro is now a hero shot.
  - SELF-RENDERED and viewed: battle_boss_intro_inquisitor (Moll with the hound, the card under him) and
    battle_arena_camp (Moll and the hound face the party). Closes GPU QA row 35's battle side.
- **M3-BPR-1305:** Ch5's stair fights play on ashcrown_forecourt_day and the Matron on ashcrown_anvil_court.
  battle_boss_intro_matron is viewed on the court.
- **M3-ENV-737:** the 10 greybox arenas are retired. `--filter=battle` 802/0.
- **M3-CRB-009:** the boss model's `intro` clip plays (6 bosses have one), and set pieces play at the model's anchor
  bones when they are named.
  - SELF-RENDERED: the Reach's hand rises over the wall; the Hermit emerges.
  - Hullgnaw's clip turns its head away from the camera; noted to creatures-b on the task.
- **Shots for the gate to re-approve:** battle_boss_intro_* (all seven move: clips, Moll, the court) and
  battle_arena_camp.
LEAD-ANSWERED (14:27): the Lead gave the Fisher Stair prop to env-art-b directly. When it lands, hook the stair meter
and the push VFX to its marks.

**BACKLOG EMPTY (2026-10-28 13:xx, @ the branch head, MERGE-READY):** the Lead's 09:35, 10:55, 11:46, 12:11 and
12:37 lists:
- **The boss-fight camera on the real models:** done, self-rendered and viewed (entry below).
  - Intro: the hero shots, refit to big14's actors and dressing.
  - Phase change and fall: the new moments.
  - Big moves: unchanged and green on the seats.
  - Home frames: per fight on creatures-b's seats.
- **GPU QA row 36** (the Reach): fixed and viewed. It waits on the PC's GPU re-check.
- **Status ticks for every Act I fighter** (M3-BPR-424): done and viewed on the Ch5 terrace.
- **Ilun's call and dismissal on the new actor:** done and viewed.
- **Swell finishers: blocked on combat.** Kerrid's and Liss's finishers are staged (M3-BPR-422) and play as soon as a
  `"swell": true` technique exists. combat has not written the techniques yet (M3-C05-06, M3-C06-05, still todo).
  Rhen, Asha, Toma and Ysolde have theirs.
- **Waiting on others:**
  - The gate: re-approve the moved baselines (the seven battle_boss_intro_*, the Vowbound and summon shots) and
    write the three battle_ch08_*.
  - Fix `merge_union.py`'s silent revert of the other side's shot edits (it cost big13 and big14).
  - Audio (M3-BPR-421): sounds for the new effects and ticks.
  - characters/creatures-b: the Inquisitor's battle model (GPU QA row 35); then drop his intro row's `hero: false`.
- **Next step for whoever resumes:** merge the integration branch once the gate takes this, then the next Lead list.

**MERGE-READY @ the branch head (13:xx): boss-fight camera choreography on the real models, with creatures-b's seats.**
- **Merged origin/claude/creatures-b** (M3-CRB-011 boss_seats; clean). The seats move the Reach, the Matron and the
  Spar-Wraith when each fights alone.
- **Home frame per fight** (`camera.rest_by_enemy`, M3-BPR-425), retuned on the seats. Each SELF-RENDERED in its own
  arena and viewed:
  - The Reach: 4 m back and 2 m up. The hand grips the wall beside the party, and the party and the sea read. This
    is GPU QA row 36; **the PC should re-check it.** The earlier 8 m would have stacked on the seat.
  - The Spar-Wraith: 3 m back and 1.5 m up. Its masts had left the top of the frame, which is the item creatures-b
    left me.
  - The Matron: the seat alone is enough.
  - The big-move shots (test_battle_boss_camera) still pass on the seats.
- **Phase change and fall** (`BattleBossCamera`, M3-BPR-426): once the action is done, the camera holds on the boss
  as its intro frames it (the hero shot). The next turn waits, and there is no moment under reduced motion.
  - SELF-RENDERED (`boss_camera_sheet --moment=phase|fall`): seven boss fights, both moments, all viewed. The Matron
    has the party around her; the Wraith's whole A-frame shows with Rhen and Asha in front; the Reach towers over
    the wall-head; Hullgnaw arches over the raft; the Drownbell fills the frame.
  - Test: test_battle_boss_camera_moments 3/0.
- **Checks on the head:** boss_camera 6/0, boss_seat 2/0, boss_intro 21/0, camera_director 47/0, choreo 58/0;
  gdlint, gdformat, validate_data and validate_choreo clean.
- **Not rerun:** the full suite since the last account (3167/12, every failure accounted for in the entry below).
  The changes since are in the battle camera, and its filters are green.

**12:xx: GPU QA row 36 (the Reach's arm over the party) and the full suite.**
- **Row 36 (mine, with creatures-b):** the Reach's fight now rests farther back and higher (`camera.rest_by_enemy`,
  M3-BPR-425, 4078fc0f).
  - SELF-RENDERED on the seawall hoist arena: the hand takes the left-centre third, reaching toward the party, with
    the parapet and the party readable. Before, it covered half the frame or more.
  - Test: test_battle_boss_camera 3/0.
  - **PC: please re-check row 36 on the GPU.** creatures-b's `boss_seats` (M3-CRB-011) also moves the Reach. I'm
    merging it now and will retune so the two don't compound (next entry).
- **Full Godot suite on the head before the Reach change:** 3167 run, 12 failed.
  - 11 of the failures are in files already red on the big14 gate list, so not this branch's: act1_cutscene_walks,
    creature_portraits, field_audio, fp_prologue, hero_field_snaps, qa_capsules, qa_save_shrines and
    villager_routines.
  - The 12th, test_battle_boss_intro, was the suite loading the test mid-edit. On the head it is 21/0.

**2026-10-28 11:xx: big14 gate fixes, and the Lead's 09:35/10:55 list.**
- **Merged origin/gpu/gate-big14-shots** at 94da590d.
  - battle_sandbox.json takes Kerrid's and Liss's landed actors.
  - `merge_union.py` dropped big14's `boot_title` 72 again, and `battle_victory`'s 90; both restored.
  - **Lead: that tool keeps "ours" for a shot both sides list, and silently reverts the other side's edit. It has now
    cost two gates.**
- **My gate failures, fixed** (0875dc95):
  - test_battle_act1_ability_vfx now walks Act I foes only. Act II's Ch10+ creatures are out of scope (ADR 0041).
  - test_battle_party_stand_ins: Liss's tint is her landed row's #7A8C5A.
  - test_battle_result_motion: battle_victory settles 90 frames again.
- **Status ticks (M3-BPR-424):** poison, regen, a Doom count, Doom falling, and a turn lost to Sleep or Stop now show
  on their fighter (BattleVfx on turn_ended/turn_lost; six generated effects).
  - SELF-RENDERED: the six ticks on the Ch5 terrace at night. All read.
  - Fixed after the first look: the Doom ticks vanished in the dark (pale motes now fall with them), and Stop's ring
    hid under a wide shell.
  - Test: test_battle_status_tick_vfx 3/0.
- **Ilun's call and dismissal on the new actor (5.1 x 3.2 m):** the ring and motes were sized for a capsule, so they
  hid under its middle. They are widened for the real bodies.
  - SELF-RENDERED: battle_vowbound_call, _out, battle_choreo_summon and _vowbound_rise. Viewed: the bound light now
    rings Ilun's body.
  - The teal plume above its back in the summon shot is not my effect; it looks like the model's own (creatures-b).
- **Boss intros on big14's actors and dressing:**
  - The hero shot judged heroes by their meshes' bounds. Toma's spear and shield span 1.8 m, so the Matron's and the
    Drownbell's intros fell back to wide shots. Heroes are now judged by their bodies, and may stand at the frame's
    foot.
  - The occlusion test used bounds. big14's raft and deck are merged meshes whose bounds take in the boss, so they
    were skipped, and the rail (Hullgnaw), the deck's edge (the Wraith) and Toma's shield (the Matron) came back.
    - Sight lines now test the surfaces (a cached TriangleMesh per mesh).
    - The lens needs 4 m of headroom.
    - Sight lines also cross the boss's body, not only its middle.
    - A near wall may not fill the frame's foot (9 rays, at most a third).
  - SELF-RENDERED @ the head, all viewed:
    - Hullgnaw: the rail now only crosses the bottom quarter under the card; the boss is clear.
    - Spar-Wraith: on its lit deck with the party.
    - Cinder Matron: Toma's shield at the side, she is clear.
    - Drownbell: fills the frame.
    - Hermit and Reach: as before.
    - Inquisitor: the fitted wide shot (no model yet).
    - **Gate: re-approve the seven battle_boss_intro_*.**
  - Test: test_battle_boss_intro 21/0, now also checking headroom and the foreground.
- **Boss camera and Swell finishers:** unchanged since the BACKLOG EMPTY entry below.
  - Kerrid and Liss have actors now, but their Swell techniques are still combat's to write (M3-C05-06, M3-C06-05).
  - Their finishers play the moment a `"swell": true` skill exists.

**BACKLOG EMPTY (2026-10-28, @ 7f4fea7f, MERGE-READY):** every item on the Lead's lists (02:14, 03:41, 04:44) is
done, self-rendered and viewed:
1. M3-HER-1148's five set-piece rows.
2. The hit, death and status VFX on the dressed arenas, with the fixes listed above.
3. The boss big-move camera.
4. The Swell finishers.
5. The boss-intro hero shots.

What remains waits on other tracks:
- **The gate:** re-approve the moved baselines and write the three new battle_ch08_* ones (lists above). Fixing
  `merge_union.py`'s silent revert of the other side's shot edits is suggested.
- **Combat** (M3-C05-06, M3-C06-05): Kerrid's and Liss's Swell techniques. Their finishers (swing, reel) play as soon as
  a `"swell": true` skill row exists, with nothing more needed from me. I'll view them in a fight once the techniques
  and a Kerrid or Liss battle actor are in the sandbox.
- **Characters:** the Inquisitor's model. Then drop his row's `hero: false` and re-view his intro.
- **Audio** (M3-BPR-421): their own sounds for the Act I effects and the swing/reel styles (stand-ins for now).
- **After the env-art merge:** apply docs/kb/tasks/M3/M3-BPR-407-seawall-repoint.patch, then view the Reach's staging
  in the default frame (it fills the left third there).
- **Known reds, not this branch's:** test_hero_field_snaps and test_zone_map are red on big13 too;
  test_creature_portraits is Act II, which is paused.

Next step for whoever resumes: merge the integration branch once the gate takes this, then take any new Lead list.

**08:xx: the boss-camera sheet viewed; the Reach's big moves fixed.** See M3-BPR-420's review log.
- SELF-RENDERED (tool, scratch worktree): `boss_camera_sheet`, all 13 big moves at the lead and the contact.
  - Ten read well: Hullgnaw, the Wraith, the Matron, the Inquisitor and the Drownbell.
  - The Reach's lunge hid the party behind its arm. The director now drops a foe shot whose body blocks the targets,
    and the Reach keeps the default frame.
- The four foe-action shots are unchanged (rmse 0).
- **This entry is MERGE-READY at the branch head.** The branch carries everything listed under MERGE-READY @ 98aa030d
  below, plus this.

**MERGE-READY @ 98aa030d (07:xx), the branch head.** It carries M3-BPR-420/422/423 and the big13 merge, plus a merge
fix.
- **Full Godot suite on 4a19f707: 2997 run, 5 failed.** Now accounted for:
  - test_battle_set_piece_shots: mine, fixed at 98aa030d (the riposte effect steps to the attacker's near face).
  - test_title_reveal: **a merge loss**, fixed at 98aa030d.
    - `tools/dev/merge_union.py` keeps *our* copy of a shot both sides list, so big13's `boot_title` settle_frames
      change was dropped. I rebuilt shots.json from the merge base; only boot_title differed. baselines.json lost
      nothing.
    - **Lead: the tool silently reverts the other side's edits to shared shots. Worth a fix: take the side that
      changed against the base.**
  - test_hero_field_snaps and test_zone_map (ch08/corrow, coilspire): **red on clean big13 90ecee18 too** (checked
    in a scratch checkout). Not this branch's.
  - test_creature_portraits: the Act II creature portraits, a known red (Act II is paused, ADR 0041).
- Re-run since the fixes: set_piece_shots 4/0 and title_reveal 3/0. test_screenshots (tools) fails only on my three
  un-baselined battle_ch08_* shots.
- Shots for the gate to re-approve after viewing (all viewed here; drifts listed below):
  - the six battle_boss_intro_*;
  - battle_choreo_hit, _ko, _toll, _support and _summon, battle_heroes_hit and battle_vowbound_call;
  - new: battle_ch08_intercept, _counter and _withdraw.

**2026-10-28 06:xx: the Lead's items 2–4 (VFX on the real arenas, boss camera, Swell finishers), self-rendered @ 4a19f707.**
- SELF-RENDERED (tool, scratch worktree with env-art and env-art-b merged plus the seawall patch; never pushed):
  `act1_vfx_sheet --enemy_set` on 14 Act I arenas. Viewed: ch01 oil slug and Hullgnaw, ch02 tideline, ch03 causeway,
  Drownbell, ch04 Spar-Wraith, ch05 Matron and stair tortoise, ch06 ridge gulls and Inquisitor, ch08 stair hold,
  headland crabs and flue moths, and the Reach.
  - **Found and fixed:**
    - 21 Act I creatures had no height, so hits floated over small ones and struck big ones' shins. They now have
      measured height rows.
    - Hits on big bodies spawned inside the mesh. They now land on the near face.
    - Oil Slap vanished on the dark tower; it now carries lamp glints.
    - Lure Glow was faint on the beaches; it is now larger and brighter.
    - The KO flash (a 2 m core) bleached the fighters beside it; the core is now about 1 m.
  - **Read fine after the fixes:** every hit, status and KO, and each foe's own skills, on every arena.
  - **Noted, not mine to change:**
    - With the seawall repoint (unmerged), the Reach fills the left third of the default battle frame. That is
      staging for when the repoint lands.
    - The flue moths are grounded by design (creatures M3-CRE-631/632).
    - The hound stands half-behind the Inquisitor's capsule until his model lands.
- SELF-RENDERED @ 4a19f707, 15 shots (the ones the heights and the near face can move):
  - **Pass:** melee, cast, lamp_dive, stair_hold, statuses.
  - **Drift, viewed, intended:**
    - battle_choreo_hit 0.023: Undertow Cut's spray on the crab's near face;
    - battle_choreo_ko 0.019: the smaller KO flash, just in front of the falling gull;
    - battle_choreo_toll 0.018: the dust on Toma's near side;
    - battle_choreo_support 0.017: Mend over Asha;
    - battle_choreo_summon 0.014, battle_heroes_hit 0.013 and battle_vowbound_call 0.013: small shifts in the
      effects.
  - The three battle_ch08_* shots are new, with no baselines yet (viewed). **Baselines are the gate's.**
- The boss-camera sheet (`tools/vfx/boss_camera_sheet.tscn`) failed on a typed array, fixed at 4a19f707. It reruns
  after the full suite.

**2026-10-28 04:3x: big13 (90ecee18) merged in at 5baf9952. M3-BPR-423 boss-intro hero shots @ 59edc9b9 (the Lead's
03:41 items, ahead of the rest of the queue).**
- **Merge notes:**
  - Shared files resolved by union.
  - Baselines take the gate's.
  - `battle_choreo.gd` keeps BattlePhaseLooks; the barks are now attached by the controller (ui's).
  - `battle_sandbox.json` keeps Ysolde's actor plus Kerrid's and Liss's rows.
- **Hero shots (`BattleBossHeroShot`, choreo.json `boss_intro.hero`):** a low lens on the viewer's side looks up at
  the boss, at the biggest fill that holds.
  - The upper body stays clear of the card; the feet may pass behind it.
  - Nothing may stand between the lens and the boss: no arena mesh, which fixes Hullgnaw's rail, and no hero.
  - Heroes are off frame or small, and clear of the timeline.
  - The old corner test let a hero filling the lens pass as "off screen". The hero shot tests the projected rectangle
    instead.
  - The Inquisitor keeps the fitted shot (`hero: false`) until his model lands.
- SELF-RENDERED @ 59edc9b9: the seven battle_boss_intro_* shots, all viewed. Nothing reads wrong.
  - Hullgnaw: arched above the card, Rhen on the deck, no rail. rmse 0.298.
  - Drownbell: the bell fills the frame. 0.202.
  - Matron: three-quarter profile with the party at the right. 0.118.
  - Hermit: close and low. 0.038.
  - Reach: towering over a tiny party on the wall-head. 0.089.
  - Wraith: centred above the card, still thin and dark on its night deck. 0.046.
  - Inquisitor: PASS at 0.003 (unchanged).
  - **For the gate: re-approve the six moved baselines.**
- Checks: `--filter=boss_intro` 21/0 (3 tests updated to the hero contract, 1 new), gdlint, gdformat, validate_data
  and taskboard clean.

**FAST-TRACK MERGE-READY @ 4e89c967: M3-BPR-404 boss-intro framing (the human's "Hullgnaw framed too close").**
- **Cherry-pick exactly these two commits, in order:** `269054a3 4e89c967`. They touch only
  battle_boss_intro.gd, choreo.json (boss_intro), test_battle_boss_intro.gd, the 404 task file, one doc section and
  the six baselines. Verified: the pair cherry-picks cleanly onto `-ze8rrn` c6a960ab, and `--filter=boss_intro`
  gives 17 run, 0 failed there.
- **What changed:** the camera fits the boss model's bounds, and the feet must clear the title card. The search
  aims lower first, then widens. The Inquisitor's fit_margin 1.6 is gone, because it sank his capsule behind the
  card.
- **Shots that move (all six viewed and re-approved, captured on integration + 404 only):**
  battle_boss_intro_hullgnaw (rmse 0.253), battle_boss_intro_matron (0.109), battle_boss_intro_drownbell (0.104),
  battle_boss_intro_inquisitor (0.053), battle_boss_intro_hermit (0.039), battle_boss_intro_wraith (0.039).
- **Checks run:** gdlint, gdformat, validate_data 0/0, taskboard --check, `--filter=boss_intro` 17/0, and the six
  shots captured and compared.
- **Checks skipped:** the full manifest (only boss-intro shots can move), Blender (none touched), coverage (no
  battle-core change).

**MERGE-READY @ a9f8d67b: M3-BPR-401 battle feel + M3-BPR-402 melee spacing** (with M2-BPR-11 follow-ups e03f04ba,
d5d4edfd and the test fix 9369e8c0). Merge the branch head; it includes 404, the integration branch -ze8rrn 492651da
is merged in, and big10's bpr pick a3e489bb is an ancestor.
- **New since the handover:**
  - c3b01d7f/e5a1d3e6: a **Screen shake setting** (Full / Half / Off; accessibility.json row `screen_shake`,
    loc SET_SCREEN_SHAKE*). Reduced motion now drops every battle shake, BattleFloats' too.
  - The audio hooks: BattleImpact `landed(target, strength, stop_sec)` and `slowmo_planned`. Request
    **M3-BPR-405** (role audio) asks for an impact weight layer and a KO swell on them.
  - A 402 fix (the melee_approach commit): a body *beside* the path turns the run instead of stopping it short.
    Rhen had struck the air 2.9 m from the reef crab, because the gull harrier's wing footprint blocked the path.
  - 9369e8c0: test_battle_ko_once takes the wickfry's new model away for its primitive case. **It fails on -ze8rrn
    and big10 as well**, because the wickfry gained a model; cherry-pick 9369e8c0 if needed.
- **Shots that move (viewed, re-approved):**
  - battle_choreo_melee (rmse 0.069): Rhen no longer inside the gull harrier.
  - battle_choreo_hit (0.091): Rhen meets the crab, with the flash and the scaled recoil.
  - battle_choreo_ko (0.034): the impact flash under the falling harrier.
  - battle_choreo_toll (0.062): Ysolde's heavier recoil at 13 HP.
  - Every other battle_*, arena and drownbell shot passes (43 + 12 compared). The boss intros are 404's six.
- **Checks run:** Godot `--filter=battle` 634 run, 0 failed; gdlint, gdformat, validate_data 0/0, taskboard --check.
- **Checks skipped:** the full manifest (only battle shots can move), Blender (none touched), and tools tests (no
  tools change).
- **Coverage:** not run. game/battle core is untouched; every change is under game/battle/scene.

**In progress:** M3-BPR-403, the opening line-up spaced by footprint (BattleLineup), on a local worktree. Its tests
pass (lineup 4/0; it fails with the spread off), and the battle filter gives 638/0. It moves every sandbox_reef shot,
so a full battle-shot capture comes next.

### Render requests
RENDER-REQUEST (WITHDRAWN 2026-10-28: the greyboxes are removed in favour of env-art's final Act II kits) @ HEAD: battle_arena_fen_roots_dusk,battle_arena_lowlight_engine_hall,battle_arena_keth_terrace_wall,battle_arena_night_sea_barge; why: M3-BPR-418's greybox Act II boss arenas (new, no baselines), each in its chapter's colour-script grade, with the sandbox fight standing in.
RENDER-REQUEST @ HEAD (see `git log -1 origin/claude/battle-presentation`): battle_ch08_intercept,battle_ch08_counter,battle_ch08_withdraw,battle_ch08_stair_hold; why: M3-BPR-406's set-piece freeze-frames (new, no baselines yet): Toma taking the crawler's grip for the stair, Rhen's riposte landing, a crawler withdrawing half-way. Also stair_hold: Kerrid (in the reserve) and Liss now have their own stand-ins and timeline tints. Batch it with the 3-shot HEAD request below if that one hasn't run yet.
RENDER-REQUEST @ HEAD (see `git log -1 origin/claude/battle-presentation`): battle_boss_intro_reach,battle_arena_wall_head,drownbell_flood; why: (1) reach and wall_head: big12's baselines were rendered without this branch's arena rework (5a5b4fe isn't in the integration branch), and the 5a5b4fe render predates big12's stair HUD. Only a render of this branch's HEAD shows both. (2) drownbell_flood: settle_actors now ends the summoned polyps' entrance (1284fdec); the ed3a458 render caught them mid-rise.
(21:2x: the PC is paused. The Lead's cloud container serves these requests, and results land on `lead/gate-render-battle-presentation-<sha7>`. Requests are kept small.)
RENDER-REQUEST (DONE 21:4x: cloud render 60cbb21 viewed and approved) @ 60cbb212: battle_boss_intro_hullgnaw; why: FAST-TRACK M3-BPR-404. At c1d1e3e the party rule (party_max_h 0.3) widened Hullgnaw's camera past the raft's rope rail, which cut across the serpent. At 0.36 it keeps its approved 10.6 m frame (Rhen 0.35 tall at its side); the Drownbell, Matron and Wraith frames don't change.
RENDER-REQUEST (DONE 22:3x: cloud render ed3a458 viewed; superseded, see below) @ ed3a458e: battle_choreo_melee,battle_choreo_hit,battle_choreo_ko,drownbell_flood; why: M3-BPR-416 (trimmed 21:3x for the Lead's cloud renderer). The reef crab's Brine Spit now stays in place, a timeline push staggers its target, and summoned polyps walk onto their marks. These four shots can move. The reach and wall_head shots are no longer needed: big12 baselined them.
RENDER-REQUEST @ 25dcea24: battle_boss_intro_hullgnaw,battle_boss_intro_inquisitor,battle_boss_intro_matron,battle_boss_intro_hermit,battle_boss_intro_wraith,battle_boss_intro_drownbell; why: FAST-TRACK M3-BPR-404, the Hullgnaw boss intro framed too close (the human's playtest). The camera fits the boss model and clears the title card. All six move.
RENDER-REQUEST (CLOSED 21:3x: superseded by the big11/big12 approvals; render db0819b viewed, nothing copied) @ 25dcea24: battle_hud_preview,battle_swap_menu,battle_victory,battle_statuses,battle_swell_ring,battle_read_panel,battle_opening_banner,battle_swell_modes,battle_vowbound_call,battle_vowbound_out,battle_choreo_melee,battle_choreo_hit,battle_choreo_cast,battle_choreo_support,battle_choreo_read,battle_choreo_ko,battle_choreo_swap,battle_arena_tideline,battle_arena_causeway,battle_choreo_lamp_dive,battle_choreo_toll,battle_choreo_vowbound_rise,battle_choreo_summon,drownbell_flood,battle_swell_chant,battle_swell_brace,battle_swell_glyph,battle_statuses_colorblind,battle_pause,battle_arena_raft,battle_arena_underway,battle_arena_route,battle_arena_derelict,battle_arena_terrace,battle_arena_tideline_dawn,battle_arena_causeway_disc_sunset,battle_arena_causeway_route_afternoon,battle_arena_derelict_deck_night,battle_arena_ash_terrace_lanternfall,battle_arena_oruvel_raft_morning,battle_arena_underway_tower,battle_arena_shoals,battle_arena_camp,battle_hud_21x9,battle_hud_16x10; why: M3-BPR-401 battle feel (flash, recoil, shake by damage, KO slow-mo, the hit-stop hold fix) + M3-BPR-402 melee spacing and detour + M3-BPR-403 opening line-up spread sideways by footprint, now on the big9 real heroes. Expect the choreo_* and every sandbox_reef shot to move; arenas may move where 403 spreads a line-up.

RENDER-REQUEST @ 680cd88e: battle_boss_intro_reach,battle_choreo_melee,battle_choreo_hit,battle_choreo_ko,battle_choreo_toll; why: M3-BPR-406 Ch8 set pieces. The new Reach boss intro (no baseline yet: test_screenshots' baselined check is red until it is approved), and the hit-stop hold fix plus the counter planning re-checked on the choreo shots.

RENDER-REQUEST @ 60b62678: battle_arena_wall_head,battle_boss_intro_reach; why: M3-BPR-406 greybox wall_head_storm arena for Ch8 (new shot, no baseline yet); the Reach intro now stands on it. Supersedes the reach id in the 680cd88e line.

### 2026-10-28 02:3x: the Lead's 02:14 list
1. **M3-HER-1148, this track's five inventory rows: done.**
   - Hullgnaw, the Spar-Wraith, the Cinder Matron, the Inquisitor and the Reach have set-piece rows in boss_vfx.json
     (kind `set_piece`): a gather each turn of a charge, a moment per phase, and the fall.
   - The new `BattleBossSetPiece` plays them. The Drownbell's rig is unchanged.
   - Their phase skills, and the Drownbell's Flood Surge and Undertow Surge, have their own effects too.
   - integration-qa's `check_vfx` reads `bosses` keys, so it should list nothing for this track once merged.
   - **For integration-qa:** close M3-HER-1148 on your branch after the merge.

### 2026-10-28 01:xx: ADR 0041, Act I at final quality first (the Lead's 01:12 refocus)
- **Act II paused:** M3-BPR-408, 418 and 419 are `status: blocked`, `blocked-by: ADR 0041`. Nothing reverted.
- **Self-render rule (TRACK-RULES cd23f612):** this track now renders its own shots; open render requests are retired.
- **M3-BPR-420, every Act I ability's own VFX:**
  - **The list:** before this, `map.skills` had 3 specials, and every other Act I ability played only its element's
    generic hit. Supports, stances, gathers, summons and items played nothing.
  - **Fill:** `tools/vfx/gen_act1_ability_vfx.py` (palette-only, `--check`) writes 85 effects: 77 skills and 8 items.
    That covers every party kit skill, the Ch8 set-piece skills, the 5 other Swells, the 4 Vowbound skills, and every
    Act I creature skill and gather.
    - Exceptions: the ward-aimed skills (the stair has no fighter; the push reaction is their motion) and the
      Drownbell's toll (its boss view).
  - **Sounds:** each effect borrows an existing sound row (validate_data needs one per effect). Request **M3-BPR-421**
    to audio for their own.
  - **Entry cost:** `BattleVfx.prebuild()` now builds only the effects of abilities in the current battle. Headless,
    178 emitters took 66 ms; the sandbox fight builds 72.
  - **Found by viewing:**
    - effects on fliers landed on the sand below them; `BattleVfx.anchor` now adds the stand-in's hover;
    - a second impact core stacked on the element hit read as a blob, so the cores are dropped;
    - three pale ones got darker swatches.
  - Ownership row appended (rendering is paused with the PC).
- **M3-BPR-406 fixes found by self-rendering battle_ch08_counter:**
  - a counter's attacker now stays where it struck until the riposte lands;
  - a freeze-frame's `seek()` poses the frame before its beats fire. The riposte's VFX had landed on the attacker's
    empty mark.
- **SELF-RENDERED (lavapipe, viewed):**
  - SELF-RENDERED @ 5537f553: battle_ch08_intercept, battle_ch08_counter, battle_ch08_withdraw — new, viewed. The grip
    lands on Toma; Rhen's riposte now meets the crawler beside him; the crawler is half-way back.
  - SELF-RENDERED @ 5537f553: battle_choreo_melee, _cast, _support, _read, _ko, _swap, _lamp_dive — pass
    (rmse 0.000, so the seek change moves nothing else); battle_choreo_toll pass (0.001); battle_choreo_hit drifts
    0.012 (the same frame).
  - SELF-RENDERED @ c128eb55: drownbell_flood — pass (the polyp-settle fix brings it back); battle_boss_intro_reach,
    battle_arena_wall_head, battle_ch08_stair_hold — drift, all intended: the arena rework, Liss's tint, the dark
    storm banks.
  - SELF-RENDERED (tool) @ a2770dd8: `tools/vfx/act1_vfx_sheet.tscn`, all 85 Act I ability effects on the battle stage
    in 15 sheets, at 0.12 s and again at 0.5 s for the slow ones. Each is distinct and on its target. Known limit: the
    palest (Tidewash Salve, Climb Up) read softly on the noon beach.
- **Merged the integration branch** at 8bb52fec: clean, re-imported, validate_data 0/0.
- SELF-RENDERED @ 8bb52fec (integration merged, M3-BPR-420 VFX): 15 shots, viewed side by side with their baselines.
  - battle_choreo_melee, _cast and _lamp_dive pass (the cast freezes before contact). drownbell_flood passes (0.005).
  - **Drift, all intended:**
    - battle_choreo_support (0.011): Mend's teal motes rise around Asha;
    - battle_choreo_hit (0.013): Undertow Cut's teal spray, faint;
    - battle_choreo_ko (0.018): the gull's KO dust now on the gull, not on the sand under it (the hover fix);
    - battle_choreo_summon (0.009): bound motes over Ilun;
    - battle_choreo_toll (0.017): a light dust at Toma;
    - the reach, wall_head and stair_hold drifts as before.
  - The three new battle_ch08_* shots are as viewed above. Nothing reads wrong. Baselines are the Lead's gate's.
- **Vowbound summons (the Lead's list):** a call, a dismissal and a fall now play their own VFX in bound light
  (`vowbound_call`, `vowbound_dismiss`, `vowbound_fell`; never rising gold). The sounds are audio's own Vowbound rows.
  Tested (6db94e85).
- **Boss intros (the Lead's list):** every scripted Act I boss fight has one: Hullgnaw, the Bottle Hermit, the
  Spar-Wraith, the Cinder Matron, the Inquisitor, the Drownbell and the Reach. ch04_derelict_glass is a random roll
  that reuses the Hermit as an ordinary foe (no intro, by design).

### 2026-10-28 00:3x: the Lead's 00:13 list
- **Ch10–12 fights:** act1-chapters' a4410fd9 / d0ec6878 has the Act II field greyboxes and flows, but no enemies.json
  or encounters.json rows for Ch10–16 (checked both files on their branch). There are no fights to stage yet; their
  tasks put the encounters after the beat sheets. Everything battle-side is keyed and waiting (M3-BPR-408/418,
  request M3-BPR-419).
- **Act II arenas: env-art has built the final kits** (`ossa_fen_roots`, `lowlight_engine_hall`, `keth_seep_terrace`,
  `bridal_barge_night`, on claude/env-art). I withdrew my four greybox duplicates (19b4706d). One id and its shot would
  have collided with env-art's. M3-BPR-419 names env-art's ids.
- **Ch8 stair fights repointed to env-art's `seawall_stairhead_*`:** a patch, because the arenas live on claude/env-art
  and aren't on the integration branch yet.
  - **For the Lead at merge:** after claude/env-art, run `git am docs/kb/tasks/M3/M3-BPR-407-seawall-repoint.patch`
    (data only). Verified on a local merge (see M3-BPR-407's review log), then re-render the Ch8 shots it lists.
- **Fixed, found on the way:** test_set_piece_hud failed on this branch since 5a5b4fed. My entries line in
  `_build_hud` dropped the entry flag that ui-menus' set-piece HUD gives the Climb and the Surge. Fixed at bcdf7170.
  - Lesson: `--filter=battle` misses test_set_piece_hud. This branch's gate now runs the full Godot suite: **2865 run,
    2 failed** at bcdf7170. Both are the big12 gate's known reds, owned elsewhere with fixes in flight
    (test_creature_portraits, test_footsteps_slice_zones::causeway). Nothing else is red.
- **Boss intros:** the Mangrove Drowner has one (418). **Kahre is not fought anywhere:** it's the Ch5 Vowbound, with no
  enemies.json row in any branch, and its first call has the C10 cinematic (414). If a Kahre fight is planned, its
  enemy row is design's, and its intro is one by_enemy row.

### 2026-10-28 00:0x: the Lead's 23:52 list
- **Act II bosses' specials and telegraphs:**
  - The Lamp Engine (`opened`), the Ram (charge gather plus pressure) and the Drowner (`uprooted`) were already
    staged.
  - **The Wakefin** now has its own: its blade sinks under while it gathers (no light; it fights in the dark), and the
    camera closes in. Tested.
  - "Kahre" is the Ch5 Vowbound, not an Act II boss; its first-call cinematic was done in M3-BPR-414.
- **Boss intros:** all four Act II bosses have one (M3-BPR-408/418).
- **The battle side of act1-chapters' Ch10–12:**
  - Their branch (d0ec6878) has the field greyboxes and flows for Ch10–16, but no encounters or enemies yet; their
    tasks say the encounters come after the beat sheets.
  - Request **M3-BPR-419** asks them to use the staged enemy, phase and arena ids, so everything is live the day the
    encounters land. Their Keth Pass RamArena matches `keth_terrace_wall`.

**BACKLOG EMPTY (2026-10-27, after 8c302fa3):** every step of TRACK-RULES' list is done or waits on another track.
1. **Renders:** none open for this track. The three requests above (the HEAD 3-shot set, the Ch8 freeze-frames, the
   Act II arenas) wait on the Lead's cloud renderer.
2. **Combat TODOs:** each waits on another track's input (the C01..C09 rulings, Reefball, Pell's kit).
   - Mine in review: 401..418, M2-BPR-100, M2-HER-1114.
   - 406's last open item is the question to act1-chapters about per-wave beats.
   - 408 and 418's shots wait for their encounters.
3. **Requests to me:** none open.
4. **Primitive audit:** what's left is owned elsewhere:
   - Ysolde's battle actor: hero-integration M2-HER-1115;
   - Ilun: creatures M3-CRE-638, ready to merge;
   - the Inquisitor: M3-CRE-625;
   - Kerrid's and Liss's models: M3-BPR-412;
   - the wall_head kit: env-art, M3-BPR-407.
5. **Act II:**
   - All four Act II bosses with creature scenes have intros, moments and greybox arenas.
   - What's left needs their enemies and encounters (design/combat, act-two chapters). Remaining Act II creatures
     with no scene yet: creatures' M3-CRE-620.
   - The Ch14 Warden fight is the characters track's.
**Next, as soon as any lands:** view the renders; wire the Act II encounters' `arena` keys and boss shots; re-render
Ilun's four summon shots after creatures merges.

### 2026-10-27 23:xx: the self-directed backlog (TRACK-RULES)
5. **The next act (M3-BPR-418):** the Mangrove Drowner (Ch10) and the Wakefin (Ch15) get intro rows by enemy id. The
   Drowner's `uprooted` phase (its creature's phase id) gets its own moment, like the Lamp Engine's `opened`. Tested;
   the shots wait for their encounters.
   - Greybox arenas for the four Act II boss fights (fen roots, Lowlight's engine hall, the Keth terrace wall, the
     night-sea barge) in their chapters' grades. Tested; render requested.
- **Checks:** full `--filter=battle` at 1bf51636: **764 run, 0 failed**. Then, after the arena commit, `--filter=arena`
  20/0 and act2_arenas 2/0; gdlint, gdformat, validate_data and taskboard clean. **MERGE-READY @ f1162b31** (plus
  docs). Known red: test_screenshots, only for the new unbaselined shots in the render requests above.
1. **Render branches:** all viewed (none open).
2. **Task board (combat):**
   - **M3-BPR-406 (Ch8 set pieces), every acceptance box now done:**
     - phase looks: the untargetable Reach fades (BattlePhaseLooks), and a blow on a damage-immune foe plays the new
       `immune` reaction;
     - freeze-frames battle_ch08_intercept, _counter and _withdraw on the real wave (render requested);
     - the reduced-motion box checked against its tests.
     - Still open: the question to act1-chapters about per-wave beats.
   - **Moved to review, the work having been done before:**
     - M3-BPR-403 (line-up; every shot was viewed via the big11/big12 approvals and db0819b);
     - M2-BPR-100 (the Drownbell intro's hero in frame, which M3-BPR-404 fixed, all six approved);
     - M2-HER-1114 (the placeholder clip fixes at 56921688).
   - The other combat TODOs wait on other tracks (C01..C09 rulings, Reefball).
3. **Found and fixed:** shots.json pointed battle_arena_wall_head at a shot scene the Lead moved in big12. My big12
   merge had kept the old path, so the screenshot manifest test failed on a missing scene. It now points at
   `game/levels/_tests/battle_arenas/arena_wall_head.tscn`, as on the integration branch.
- **Known red until the renders are viewed:** test_screenshots has no baselines yet for the three new Ch8 shots (the
  first baselines come from the request above).
4. **"Parts look primitive" audit:**
   - **Kerrid and Liss had no stand-in rows.** Both fell back to the shared default capsule and the default grey
     timeline tint. They now have stand-ins sized from their sheets (Kerrid 1.82 m and heavy, Liss 1.56 m) in their
     garment colours.
   - Their timeline tints are their own: Kerrid's iron grey #8E9296 (his sheet: the only colour on him is a red cord,
     and red reads as foe/danger here) and Liss's launcher copper #A0603A.
   - **ui-menus:** these tints are provisional. Change them if the timeline has an identity palette.
   - New test `test_every_hero_has_its_own_stand_in_and_tint`.
   - **Still capsules, owned elsewhere:** Ysolde's battle actor (hero-integration M2-HER-1115, in flight on its
     branch), Ilun (creatures M3-CRE-638, built and waiting to merge), the Inquisitor (creatures M3-CRE-625), and the
     wall_head greybox (env-art, M3-BPR-407).

### 2026-10-27 22:3x: cloud renders 5a5b4fe and ed3a458 viewed; Ilun on the real model
- **ed3a458, 4 drifts (melee, hit, ko, drownbell_flood):** viewed side by side with HEAD's baselines.
  - melee, hit and ko are within 0.008 to 0.015 of HEAD's big12 approvals, with the same frames, so none copied.
  - **drownbell_flood: not approved.** M3-BPR-416's new entrance caught the polyp mid-rise (dim, small, no glow).
    Fixed: `settle_actors` (which the capture calls) now ends every entrance in progress. Tested.
- **5a5b4fe, 2 new (reach, wall_head): not approved.** big12 baselined both from integration code without this
  branch's arena rework, and the 5a5b4fe render lacks big12's stair HUD. Neither matches HEAD, so I re-requested both
  at HEAD (one 3-shot request with drownbell_flood).
- **Found in the big12 wall_head baseline:** the stair meter is drawn over the help line's second line. That's
  ui-menus' M3-UI-100, with combat as reviewer, so the finding is in its review log. I didn't change their files.
- **Ilun on the real model** (creatures' M3-CRE-638, claude/creatures a41ab41c):
  - I tested it in a local worktree that merged their branch into mine. It was never pushed and has been removed.
  - All of Ilun's actions play on the model, each landing on its clip's own contact: Attack and Brine Lash (`attack`,
    0.55 s), Tidal Ward (`cast`, 0.80 s), and Floodnet (`special`, 1.45 s, Swell style chant).
  - Their test_ilun_summon_path passes (2/0), and so do my summon_cinematic (8/0) and vowbound (58/0) filters.
  - New test `test_a_real_vowbound_lands_each_action_on_its_clip_contact`: it checks every Vowbound that has a real
    actor. Here it checks Ilun's 4 actions; on this branch, which has no model yet, it skips.
  - **For the Lead at merge:** creatures' `CreatureModels.vowbound_creature` and this branch's
    `BattleStage.vowbound_model` now use the same rule (a row with `vowbound` true and a `scene`). Theirs answers
    first; mine is a stopgap the second merger can delete.
- **Checks:** full `--filter=battle` on 47327ca6: **757 run, 0 failed**; gdlint and gdformat clean. MERGE-READY
  stands at the branch head. test_screenshots stays red only for reach, wall_head and drownbell_flood until the HEAD
  render is viewed.
  - Ilun's four summon shots (battle_vowbound_call, battle_vowbound_out, battle_choreo_vowbound_rise,
    battle_choreo_summon) need a render **after** creatures merges. On this branch Ilun is still the capsule.

### 2026-10-27 21:4x: Hullgnaw approved
- I viewed the cloud render lead/gate-render-battle-presentation-60cbb21. The serpent is whole above the card with
  no rail across it, and Rhen stands at its side, clear of the timeline. Re-approved. **M3-BPR-404 is complete:** all
  six boss intros are approved on this branch.

### 2026-10-27 21:3x: PC render gpu/render-battle-presentation-db0819b viewed (all 27 drifts): superseded, none copied
- I viewed every drift side by side with the baseline on this branch's HEAD, which carries the integration's big11
  and big12 approvals.
- All 27 show the same composition as HEAD's baselines. Their RMSE against HEAD is 0 to 0.03.
  - The three Vowbound shots (summon, rise, out) are identical to HEAD.
  - The shoals arena differs most (0.13): this render shows the old greybox blocks, and HEAD's baseline has env-art's
    wreck dressing.
- **Decision: none copied.** HEAD's baselines are later, viewed approvals of the same shots. Copying this older render
  would regress them, the shoals arena included. The 25dcea24 consolidated request is closed by them.
- **Still open:** the ed3a458e request (M3-BPR-416 moves the choreo shots and drownbell_flood) and the 60cbb212
  Hullgnaw request.
- **The staging audit, re-checked against the other tracks' heads (21:3x):**
  - claude/creatures aa762dee has no `ilun` creatures.json row or scene yet, so Ilun's summon stays on the M3-BPR-417
    hook until it lands.
  - Sefir has character assets (claude/characters 2ec366e9) but no characters.json battle row on any branch, so the
    kit is still blocked on design data.
  - Every other entry is unchanged: see the 20:50 table.

### 2026-10-27 21:xx: big12 merged in; the FAST-TRACK render viewed; Ilun's model ready
- **Merged big12** (integration e930595c) at 6d57bdff:
  - the four battle_choreo baselines and shots.json taken from the integration branch (it carries the reach and
    wall_head shots);
  - ownership.md, flags.tres and strings.csv unioned;
  - validate_data 0/0.
- **PC render gpu/render-battle-presentation-c1d1e3e, all four drifts viewed:**
  - **drownbell, approved:** the bell is whole above the card, and the party stands small at the right, clear of the
    timeline (the big11 fix works).
  - **matron and wraith, approved:** the same compositions as their baselines, now with the real heroes (big11).
  - **hullgnaw, NOT approved.** The party rule at 0.3 rejected Rhen at the serpent's side (0.35 of the screen, inside
    the safe frame). The camera widened from 10.6 to 11.7 m, past the raft's rope rail, and the rail and a post cut
    across Hullgnaw's head.
    - Fixed: `party_max_h` is now 0.36, and Hullgnaw keeps the frame it has with no party rule at all.
    - The Drownbell keeps the +45° orbit just approved, and the Matron and Wraith don't move.
    - New test `test_the_party_rule_widens_a_shot_only_when_the_party_crowds_it` (it fails at 0.3).
    - Re-requested at 60cbb212.
  - inquisitor and hermit pass unchanged.
  - Approvals: 7aa31b6f.
- **Ilun's model (M3-BPR-417):** a creatures.json row keyed by a Vowbound's id with a `scene` now replaces the
  capsule. Before, only enemies.json `model` reached the stage, so Ilun would have stayed a capsule.
  - Tested on a borrowed creature scene: the call, the C10 rise, and the head for the frame.
  - **creatures:** what Ilun's row needs is in docs/kb/tasks/M3/M3-BPR-417 (row id `ilun`, the scene, stand_in yaw,
    attack and cast clips with contact times).
- **Checks:** boss_intro 20/0, vowbound_model 2/0; gdlint and gdformat clean. Full `--filter=battle` on 657aab1a
  (big12 + 404 + 417): **754 run, 0 failed**.

**FAST-TRACK MERGE-READY @ the branch head (M3-BPR-404 + big12 + 411-417):** the Drownbell crowding fix with
three re-approved intros (7aa31b6f) and the Hullgnaw fix (60cbb212). Known red until the PC renders are viewed and
approved: test_screenshots for battle_boss_intro_hullgnaw (the 60cbb212 request) and the ed3a458e set.
- **Checks skipped:** coverage (no battle-core change), Blender (none touched).

### 2026-10-27 20:50: the audit list, entry by entry (answering the Lead's 20:47)
The list is empty except for blocked entries. Each one below has its staging, its test and its render request, or
the reason it's blocked.
| Entry | State | Test | Render |
|---|---|---|---|
| Ysolde's kit (ember, frost, slow_hex, read, attack) | staged: cast, support, read, melee | test_battle_party_kits, test_battle_ysolde | 25dcea24 line |
| Kerrid's kit | staged: melee, finisher on anchor_fall | test_battle_party_kits | needs his model (below) |
| Liss's kit | staged: reel_shot cast from range (item), flash_housing support | test_battle_party_kits | needs her model (below) |
| Every Swell (7) | staged: dive, verse, brace, glyph, chant, cast | test_battle_party_kits (audit) | 25dcea24 line |
| Ilun's, Kahre's and Virel's first calls and signatures | C10 cinematic for all three, reduced-motion variants, timeline kept | test_battle_summon_cinematic, test_battle_clarity | battle_vowbound_call, battle_choreo_summon |
| Act I creature specials (28 foes) | every skill has a style; ranged and sweeping blows stay in place; heavy blows play the finisher | test_battle_party_kits (both audits) | ed3a458e line |
| Telegraphs | every charge gathers on stage | test_battle_telegraph | 25dcea24 line |
| Timeline pushes and summons | push reaction, summoned foes walk in | test_battle_push_reaction, test_battle_summoned_entrance | ed3a458e line |
| **Not an Act I kit: Sefir** | Sefir is High Warden Sefir Aurane, the antagonist, not a party member. M3-CHR-02: "the final boss's battle actor is Act III work." There's no hero kit to stage; his boss intro and specials come with Act III | — | — |
| **Blocked: Act II creatures and bosses (6)** | no enemies.json rows yet; tracked by creatures' M3-CRE-620 (roster, then design sheets, then builds) and M3-CRE-623/624 (Lamp Engine, Avalanche Ram, whose boss intro and charge rows are already keyed by id, M3-BPR-408) | the foe audits cover them once the rows land | — |
| **Blocked: Kerrid's and Liss's real clips** | M3-BPR-412 to characters (Kerrid: M3-CHR-505) | placeholder clips meanwhile | — |
| **Blocked: VFX particles for 17 skills and 8 items** | effects.json is rendering's; map proposed in M3-BPR-411 | coverage tool test (each gap has a stage answer) | — |
| **Blocked: a foe dive or sweep style, and the charge style** | need audio choreo_sfx rows (M3-BPR-410) | — | — |
Nothing else is open on this track until one of those lands or a PC render comes back to view.

### 2026-10-27 night: filling the audit (M3-BPR-416, the Lead's 20:26)
- **Filled, each with a test that fails without it:**
  - Foes stage their blows by their reach. Ranged or whole-party blows stay in place: Brine Spit, Shroud Sweep and
    Undertow Pull no longer run at one hero. The heaviest blows (Gnaw, Ladle Swing, Pounce) play the finisher.
  - A new `reaction.push`: a hit that only pushes its target down the timeline (Rope Dive, Grip the Stair and Hand
    Closes on the ward; the Drag Net) staggers the target back. Before, it played nothing.
  - Summoned foes (the flood's polyps, Rouse Polyp, the Reach's surges) walk onto their marks instead of appearing.
  - The VFX audit names each gap's stage answer, and a tool test requires one. All 17 skills and 8 items have one.
- **The audit list is now empty apart from these blocked entries:**
  - **The VFX particles:** `game/data/vfx/battle/**` is rendering's. Request M3-BPR-411 carries the proposed map.
  - **Sefir:** there's no characters.json row (Act II).
  - **The 6 Act II creatures and bosses:** no enemies.json rows.
  - **Kerrid's and Liss's real clips:** request M3-BPR-412 to characters.
  - **A dedicated foe dive or sweep style:** it needs an audio choreo_sfx row (the `dive` row plays Rhen's Swell
    accent), as with M3-BPR-410.
- **Checks:** the new tests (party_kits 3/0, push_reaction 2/0, summoned_entrance 2/0); audio_live 12/0, creature 29/0, choreo_audio 15/0; tools coverage and choreo_validate OK; gdlint and gdformat clean. Full `--filter=battle` on ed3a458e: **751 run, 0 failed**.
- **Checks skipped:** coverage (no battle-core change), Blender (none touched), and cloud shots (rendering is on the PC).

### 2026-10-27 night: the Lead's 19:35 queue (items 1-5)
Status of each item. "Blocked" names the reason and what unblocks it.
1. **Act I party kits (M3-BPR-412): done, with one gap blocked.**
   - Every kit skill of Rhen, Asha, Toma, Ysolde, Kerrid and Liss resolves to a real style with a contract clip and
     camera shots. Reel Shot casts from range, and Anchor Fall plays the finisher.
   - Every Swell technique resolves through the real `style_id_for`: lamp_dive → dive, shallows_verse → verse,
     return_tide → brace, written_light → glyph, floodnet → chant, last_strike and flare_line → cast.
   - Tests: `test_battle_party_kits` (2 tests, 2/0). The second checks every Swell, every Vowbound and every enemy skill.
   - **Blocked: Sefir.** There's no `sefir` row in characters.json (an Act II hero; there's no kit to stage). This
     unblocks when design or characters add the row; the test then covers the kit automatically.
   - **Blocked: real clips for Kerrid and Liss.** Request **M3-BPR-412** goes to characters. The placeholder clips
     stand in until then.
2. **Creature specials and telegraphs (M3-BPR-413): done for Act I, Act II blocked.**
   - Every foe's gathering charge reads on stage through BattleTelegraph and `telegraph.gather`. A boss whose
     row owns the charge (the Drownbell) keeps its own gather.
   - All 28 enemies' skills resolve to a real style with a clip and camera shots (the audit above).
   - **Blocked: the 6 Act II creatures and bosses.** They have no enemies.json rows yet, apart from the Avalanche
     Ram's intro and charge rows, which are already keyed by id (M3-BPR-408). This unblocks when design adds the
     rows; the audit then covers them.
3. **Act I Vowbound cinematics (M3-BPR-414): done.**
   - Ilun, Kahre and Virel each get the C10 first-call cinematic (the seen-flags are declared in flags.tres).
     Reduced-motion variants and turn-order visibility are covered by test_battle_summon_cinematic and
     test_battle_clarity.
   - Signatures resolve as follows: brine_lash → finisher, tidal_ward → chant, forge_bolt → cast, kite_flare → cast.
4. **Victory and result handoff (M3-BPR-415): done.** The result panel waits for the real heroes' victory pose
   (`clip_sec`). A scripted escape walks the party off. ui-menus owns the panel itself.
5. **VFX coverage gaps (M3-BPR-411): audit done, fill blocked.**
   - `python3 tools/battle_vfx_coverage.py` lists every skill and battle item that plays no effect, and proposes an
     existing library effect for each one.
   - **Blocked:** effects.json belongs to rendering. The map is proposed in request **M3-BPR-411**.
- **Charge sound:** request **M3-BPR-410** to audio. The `charge` style comes back once audio's choreo_sfx row exists.
- **Checks run:** full `--filter=battle` **745 run, 0 failed** at 5cd7cad5; party_kits 2/0 after the new audit;
  gdlint and gdformat clean.
- **Checks skipped:** coverage (no battle-core change), Blender (none touched), and shots (no scene or visual change
  since the requests above).

**MERGE-READY @ the branch head (see `git log -1 origin/claude/battle-presentation`):** M3-BPR-404 (the
FAST-TRACK, with the big11 crowding fix c1d1e3e6), 406, 407 (requested), 408, 409, 411, 412, 413, 414, 415, and
everything in the 2d988e27 MERGE-READY below.
- test_screenshots stays red until the PC renders are approved: the boss intros at c1d1e3e6, plus wall_head and reach.

### 2026-10-27 evening
- **Merged big10** (integration 792ee805) at 19172f4c. Conflicts:
  - the three boss-intro PNGs: took theirs; my 404 render request supersedes them;
  - encounters.json: took theirs, which has the new Ch8 encounters, and re-added `arena: wall_head_storm` on the
    four set pieces.
  - My final 404 (the card clearance, with no Inquisitor fit_margin) is what the branch carries now; big10 had the
    WIP fit.
  - Battle filter: **716 run, 0 failed**.
- **M2-HER-1114 done @ 56921688** (hero-integration's request):
  - `_install` stops a playing player before the library swap (the segfault);
  - rotation keys stay on one hemisphere, with slerped keys between any pair more than 60° apart
    (`placeholder_clips.max_key_deg`);
  - the new test fails without the fix (148.7° on the attack).
  - **hero-integration:** drop your KNOWN `ysolde ready -> finisher` entry once this reaches you, and mark the task
    done on your branch.
  - Shots: interpolation for a single clip is unchanged, so no baseline should move. Ysolde's shots are in the
    25dcea24 render line anyway.
- Refactor a03c6cd3: the reaction pose moved to BattleChoreoPlan; battle_choreo.gd is now 969 lines.
- M3-BPR-405 is fulfilled by audio's M3-AUD-816. Audio drops `pending` when this branch merges.

**MERGE-READY @ 2d988e27:** M3-BPR-401 (incl. the hit-stop hold fix f8cd9269), 402, 403, M2-HER-1114, M3-BPR-406
(Ch8 so far), M3-BPR-408 (Act II intros by enemy id), and M3-C08-100's barks.
- Merge the branch head; it carries big10.
- **Checks run:** gdlint, gdformat, validate_data 0/0, taskboard --check, and Godot `--filter=battle` 716/0 at 19172f4c
  plus the scoped filters after (boss 58/0, set_piece_stage 5/0, placeholder 8/0); full `--filter=battle` at 2d988e27: 719/0.
- **Checks skipped:** coverage (no battle-core change), Blender (none touched).
- **Known red until the PC render is approved:** tools test_screenshots, which has no baseline yet for
  battle_boss_intro_reach and battle_arena_wall_head.
- **Shots:** every one that can move is in the render requests above. None is approved yet: approval needs the PC
  renders.
- **Pillar 4 check:** the boss intro and the C10 summon both keep the timeline and party panel visible, so who acts
  next stays on screen. Every new impact or motion respects reduced motion and the shake setting (tested): no
  shake, no withdrawal motion, no Breach push-in, and a dimmer flash.

RENDER-REQUEST @ dcc68922: battle_hud_preview,battle_choreo_toll,drownbell_flood,battle_swell_ring,battle_read_panel; why: M3-BPR-409. The target ring now draws over ground VFX (render_priority 10); view the ring over the toll's wave and the flood.

### 2026-10-27 late: the Lead's queue items 3–7
- **Battle filter after items 3–7 and the 408 fix-up: 726 run, 0 failed.** An earlier run caught two failures, now
  fixed:
  - the Ram's new `charge` style had no sound row in audio's choreo_sfx.json, so the style is withdrawn and asked of
    audio as M3-BPR-410; its framing moved to camera.enemy_by_actor;
  - the specials test assumed every boss row names an existing enemy.


- **3, M3-BPR-408 (a433b3b3): the Act II bosses' camera language, by enemy id.**
  - The Lamp Engine opens: a phase moment where the core rises and the party steadies in turn.
  - The Avalanche Ram's physical moves play a low, side-on `charge` run (style_by_actor, enemy_by_style).
  - Any charge the Ram gathers paws the ground and closes the camera in (pressure.by_enemy).
  - Intros come from by_enemy rows.
  - The Ch10–11 regulars need nothing bespoke: the model fit, the footprint spacing and the line-up all work from
    their models.
  - Tests: act2_bosses 3/0; tools test_choreo_validate 21/0.
  - **Ask** whoever writes the Act II enemies: keep the ids `lamp_engine`, `avalanche_ram` and the phase `opened`.
- **4, Ysolde (a433b3b3):** `test_battle_ysolde` puts characters' ysolde_battle.tscn on her stand-in.
  - Every contract clip plays (placeholders) and her footprint is sane.
  - Ember and Read play to the end (2/0).
  - Her shots wait on ui-menus' repoint (M2-HER-1108).
- **5, M3-BPR-409 (71ec1234): the Pillar 4 pass.**
  - The timeline and party panel stay on screen through the boss intro and the C10 summon (tested).
  - The target ring now draws over ground VFX.
  - Reduced motion and the shake setting cover every new impact or motion (tested).
- **6, the Ch8 staging:**
  - the greybox wall_head_storm arena with EntryMarker_ward;
  - the intercept staged by geometry (the stair is behind the party line);
  - withdrawals, counters, barks, the Breach push-in and the Reach intro.
  - M3-BPR-407 now points env-art at the corrow seawall kit and act1-chapters' corrow_frame for the final arena.
- **7, the board:** the combat `todo` tasks are engine and design rulings (M3-C01-03 … M3-C09-07), not presentation.
  I took M3-C08-100's barks; the needle is an item, so not mine.

**FAST-TRACK MERGE-READY @ 89ffba3c: M3-BPR-404, viewed on the PC render.**
- Render: gpu/render-battle-presentation-25dcea2. Four drifts, all viewed and re-approved:
  - Hullgnaw: the whole serpent and its ribs above the card, with the real Rhen beside it;
  - the Matron and the Drownbell: clear of the card;
  - the Wraith: a little wider.
- Inquisitor and Hermit pass unchanged.
- **To pick onto the integration branch:**
  1. `git am docs/kb/tasks/M3/M3-BPR-404-boss-intro-fit.patch` (the code).
  2. Then copy these four PNGs from `89ffba3c`: `git checkout 89ffba3c -- tests/screenshots/baselines/battle_boss_intro_{hullgnaw,matron,drownbell,wraith}.png`.
- Note: in the Drownbell's frame the real Toma stands large in the right foreground, near the timeline. The boss and
  the card are clear. I'll look at moving the boss_tall shot's side later.

RENDER-REQUEST @ c1d1e3e6: battle_boss_intro_hullgnaw,battle_boss_intro_inquisitor,battle_boss_intro_matron,battle_boss_intro_hermit,battle_boss_intro_wraith,battle_boss_intro_drownbell; why: FAST-TRACK M3-BPR-404, the big11 regression. The real Toma stood huge over the timeline in the Drownbell's intro; the intro now keeps the party clear. Expect the Drownbell to move and the other five to be unchanged.

**FAST-TRACK @ c1d1e3e6: big11 merged in (5fbbdb2d); the Drownbell party-crowding fix.**
- **The fix:** `_party_clear`, plus an orbit in `_fit_search`.
- **Checks:** boss_intro 19/0. The new test fails without the orbit, and only on the Drownbell. validate_data shows
  0 errors and 1 warning (env-art's missing offering_step.glb row, not mine). gdlint and gdformat are clean.
- **For the Lead's pick:** the code is in commit c1d1e3e6 (battle_boss_intro.gd, choreo.json boss_intro.fit, the test,
  the task). Take the baselines from the PC render of the line above once I've viewed it.

RENDER-REQUEST @ db0819b2: battle_hud_preview,battle_swap_menu,battle_victory,battle_statuses,battle_swell_ring,battle_read_panel,battle_opening_banner,battle_swell_modes,battle_vowbound_call,battle_vowbound_out,battle_choreo_melee,battle_choreo_hit,battle_choreo_cast,battle_choreo_support,battle_choreo_read,battle_choreo_ko,battle_choreo_swap,battle_arena_tideline,battle_arena_causeway,battle_choreo_lamp_dive,battle_choreo_toll,battle_choreo_vowbound_rise,battle_choreo_summon,drownbell_flood,battle_swell_chant,battle_swell_brace,battle_swell_glyph,battle_statuses_colorblind,battle_pause,battle_arena_raft,battle_arena_underway,battle_arena_route,battle_arena_derelict,battle_arena_terrace,battle_arena_tideline_dawn,battle_arena_causeway_disc_sunset,battle_arena_causeway_route_afternoon,battle_arena_derelict_deck_night,battle_arena_ash_terrace_lanternfall,battle_arena_oruvel_raft_morning,battle_arena_underway_tower,battle_arena_shoals,battle_arena_camp,battle_arena_wall_head,battle_hud_21x9,battle_hud_16x10,battle_boss_intro_reach; why: one consolidated battle set at the post-big11 head. It covers M3-BPR-401/402/403 (impact, spacing, the sideways line-up), 406 (the Ch8 arena and the Reach intro, both new with no baseline yet), 408 and 409 (the ring over VFX). It **supersedes** the 25dcea24 (second line), 680cd88e, 60b62678 and dcc68922 lines. The boss intros stay on their own FAST-TRACK line (c1d1e3e6).

**MERGE-READY @ e1077bbe** (post-big11), carrying:
- M3-BPR-401 and 402: the hold fix, the detour, the screen shake setting;
- M3-BPR-403: the sideways line-up;
- M3-BPR-404: the card clearance plus the big11 party-clear fix, FAST-TRACK;
- M3-BPR-406: Ch8 (withdrawals, counters, the arena, the Reach intro, the Breach push-in);
- M3-BPR-408: the Act II bosses by enemy id;
- M3-BPR-409: the ring over VFX;
- M3-C08-100's barks and M2-HER-1114.

**Checks run:** Godot `--filter=battle` 731/0, validate_data 0 errors, taskboard --check, gdlint, gdformat, tools
test_choreo_validate 21/0.
**Checks skipped:** coverage (no game/battle core change), Blender.
**Red until the PC render is approved:** tools test_screenshots, which has no baseline yet for battle_boss_intro_reach
and battle_arena_wall_head (both in the consolidated request above).
**Baselines:** 404's four are approved at 89ffba3c. The rest wait on the two open requests (c1d1e3e6 FAST-TRACK, and
the consolidated one).

RENDER-REQUEST @ 5a5b4fed: battle_arena_wall_head,battle_boss_intro_reach; why: M3-BPR-406, the Ch8 arena reworked after viewing 60b6267 (the Reach's wide intro showed the greybox's edges; the storm read as grey pillars) and the timeline naming the entries. Both are new shots with no baseline yet. This supersedes those two ids in the consolidated line.

**gpu/render-battle-presentation-60b6267 viewed, NOT approved** (the two new shots):
- the Reach intro pulled back far enough to show the greybox wall-walk as a small slab floating over grey;
- the arena's "storm" read as near grey pillars;
- the timeline showed `the_climb` and `the_surge` (BattleController._build_hud skipped entries; fixed).

The arena is reworked (60 m walk, a sea plane, the low town, far storm banks), and the generator is committed
(tools/arenas/gen_wall_head_storm.py).

**2026-10-27 night (the Lead's items a–e):**
- (a) test_battle_ysolde covers her whole kit, on hero-integration's wrapper once it lands.
- (b) Ch8 staging: wall_head_storm travel 0.85; the timeline names the entries. The per-wave beats are asked of
  act1-chapters (M3-BPR-406).
- (c) test_battle_reduced_motion_audit.
- (d) test_battle_clarity: the order stays on screen mid-toll, mid-C10, at a hero's contact and through boss intros.
- (e) No presentation todo is on the board.
- Battle filter at the head: **738 run, 0 failed**.

**Renders viewed, 2026-10-27 evening:**
- gpu/render-battle-presentation-25dcea2: four re-approved at 89ffba3c (above).
- **gpu/render-battle-presentation-680cd88: viewed, NOT approved.** The renders are fine (Rhen meets the crab with the
  flash and recoil; the KO flash; the toll). But they are from 680cd88e, before big11, whose PC-approved battle_choreo
  baselines are now on this branch, and before my later changes (the line-up spread, the ring priority, the Act II
  rows). Approving them would put older pictures over newer approved ones, so the consolidated request above replaces
  them. Notes for the next view:
  - battle_choreo_melee catches Rhen mid-run, because the real clips moved the contact;
  - in battle_choreo_toll Ysolde is still a capsule (ui-menus' repoint M2-HER-1108).
- Battle filter at the post-big11 head with the Drownbell fix: **731 run, 0 failed**.

### FAST-TRACK M3-BPR-404 on the post-big9 integration branch (updated 2026-10-27)
- **Cherry-picking 269054a3 and 4e89c967 now conflicts on the six baseline PNGs.** big9 re-approved them with the
  real heroes, and the PNGs in my commits were rendered with primitive heroes.
- **Use the code-only mbox instead:** `git am docs/kb/tasks/M3/M3-BPR-404-boss-intro-fit.patch` (from this branch).
  It holds the same two commits without the PNGs. Verified on -ze8rrn 7cccb551: it applies cleanly,
  `--filter=boss_intro` gives 17 run, 0 failed, and validate_data is 0/0.
- **Then:** take the six baselines from the PC's render of the first request line above. That render is at this
  branch's head, which differs from integration + 404 only by 403's party line-up spread. If you want a pixel-exact
  pick, push the git-am result to a lead/gate branch and request the six there.

**Also merged and fixed (2026-10-27, pushed):**
- The integration branch with big9 is merged in (7708d572). Conflicts were the baselines (theirs), strings
  (union, no duplicate keys), test_battle_choreo (theirs), and test_battle_ko_once (mine: it no longer needs any
  model-less foe).
- **f8cd9269, the BattleImpact hold bug** (creatures' M3-CRE-617 report): the struck target's clip now stays held
  through the hit-stop. Regression test included; it fails without the fix.
- 4a525046: the reduced-motion run test measures against the real approach. Big9's real heroes have real
  footprints.
- **M3-BPR-403** (BattleLineup, merged from my worktree): the opening line-up spreads sideways on screen by
  footprint, each fighter at most 0.6 m off its mark. Tests: lineup 5/0.
- Battle filter after all of it: **711 run, 0 failed**. gdlint, gdformat and validate_data are clean.
- Cloud captures stopped, per the human's directive: only my wt403 PIDs, checked by their cwd.
- **creatures, please note:** your M3-CRE-617 last box (the target's clip held through the hit-stop) is fixed at
  f8cd9269.
- **M3-BPR-406 (doing), Ch8 set pieces on stage:**
  - all four Ch8 encounters play to their result panel at full pacing (new test);
  - **withdrawn foes used to stay standing** on stage; they now back away and are hidden;
  - counters show the hero's riposte;
  - the Reach has a boss intro.
  - Battle filter: 714 run, 0 failed.
  - Open: the intercept step-in (it needs a stair marker on the Ch8 arena), the breach push-in and the phase looks.

## STATE AT HANDOVER (2026-10-25)

**HANDOVER DONE @ e4b36a0d.**

**Branch:** `claude/battle-presentation` @ 269054a3 (plus this docs commit). Integration branch
`claude/undertow-lead-handoff-423ixt` merged in up to big8 (6c6e5514). No subagents or worktrees running; nothing
un-pushed.

### Already on the integration branch
- M2-BPR-01..10 (big7/big8) and the KO fix M2-BPR-11 (fast-tracked at be807afe; the Lead dropped its `c.yielded`
  clause there; this branch keeps it).

### Merge-ready on this branch (not yet merged)
- **M2-BPR-11 follow-ups** (e03f04ba, d5d4edfd): hero-integration's review (the tests take the clip path for real
  heroes, no KO sink for a model with a ko clip, staggered victory clips) and the optional `revive` clip.
  M2-BPR-10 is done (characters approved). Battle tests were green (550/0) at d5d4edfd.

### In progress (code pushed, gate not finished)
- **M3-BPR-401 battle feel** (c2598a43): BattleImpact: hit-stop, shake by damage, impact flash, recoil by damage,
  KO slow-mo; choreo.json `impact`; validator `impact_errors`; tests `test_battle_impact` (12/0).
- **M3-BPR-402 melee spacing** (c2598a43, 6ba9bd5d): BattleChoreoPlan.melee_gap and footprint (from the real
  models); overlap test. Battle tests 603/0 at 6ba9bd5d.
- **M3-BPR-404 boss-intro framing** (269054a3, WIP): the Lead's Hullgnaw bug. The camera fits the boss's model
  bounds (choreo.json `boss_intro.fit`, row `fit_margin`). boss_intro tests 14/0. Viewed and good: Hullgnaw,
  Matron, Hermit (min_m 2.2), Wraith, Drownbell. **The Inquisitor with fit_margin 1.6 is captured but not viewed.**
  There's no task file yet; write `docs/kb/tasks/M3/M3-BPR-404-boss-intro-fit.md`.
- **Screenshot baselines are NOT re-approved** for any of the above. 401/402 move the battle_choreo_* contact
  frames (the flash, the scaled recoil, shorter runs) and probably arena and other battle shots; 404 moves all six
  battle_boss_intro_*.

### Exact next steps
1. Merge the integration branch again. Then `python3 tools/validate_data.py`, gdlint/gdformat, and
   `godot --headless --path . res://tests/run_tests.tscn -- --filter=battle` (expect 0 failed).
2. Capture every `battle_*` and `drownbell_*` shot, with your own TMPDIR/XDG_DATA_HOME. It's about 80 minutes on
   lavapipe now that the final arenas are heavy, so split it into batches.
   Run `tools/screenshots/capture.sh --shots <ids> --out <dir>`, then `compare.py --out <dir> --shots <ids>`.
   View every FAIL side by side. Approve only the intended changes: the flash, the recoil, the spacing, the boss
   framing, and env-art's final arenas. Use `compare.py --out <dir> --update-baselines <ids>`.
3. View battle_boss_intro_inquisitor (fit_margin 1.6). Tune it if the capsule still crowds the card.
4. Then write MERGE-READY in this log for 401/402/404, with checks and shas.
5. Next queue: M3-BPR-403, which spaces the line-up slots by real footprints (BattleStage). Real creature models
   overlap on their marks (the reef crab and gull harrier in sandbox_reef). Re-check the camera safe frames after it.
6. Bring in hero-integration's real heroes (claude/hero-integration, M2-HER-1103) when the Lead merges them. View a
   melee freeze-frame per hero, and check the footprints read.

### Open questions / requests out
- **M3-CHR-01** (characters): 32 Asha/Toma clips that the Act I dialogue calls. `test_hero_clips` fails on any
  branch with m2-slice + big7 until it's done.
- **M3-AUD-13** (audio): placeholder voice rows for 23 speakers.
- creatures: `creature_actor.gd` got two of our fixes (set_frozen idempotent; the KO fade hides a foe). Please
  review them.
- audio: `audio_director.gd:486` loop var Object→Variant (freed keys in multi-shot captures).
- env-art: their "owner inconsistent" warning was not reproduced here. Ask for the exact log line.

### Known bugs / gotchas
- `battle_choreo.gd` is 967/1000 lines (gdlint cap). New logic goes in helpers: BattleChoreoPlan (static),
  BattleImpact, BattleOutro and the like.
- `battle_controller.gd` is 995/1000. Edit in place only.
- `BattleChoreo._flat()` NORMALISES the vector. Use `_flat_len` or zero `.y` yourself for distances.
- A seek (freeze-frame) clears any hit-stop. The impact flash follows the choreography clock when `live` is false,
  which keeps captures deterministic.
- The KO path must stay idempotent. BattleStage.refresh_ko re-applies stone and KO to every fighter after every
  action.
- The tools tests take about 19 minutes under plain unittest (audio loudness, rig integrity). Use
  `python3 tools/run_tool_tests.py -j 4`.
- `capture.sh` logs to `$TMPDIR/hymn_capture.log`. Always set TMPDIR to your own scratch folder.
- Never kill processes by pattern, and never with a pattern that also matches your own shell.

## Queue (tasks M2-BPR-01..08, role combat; all built, all `review`, reviewer lead)
| Task | State |
|---|---|
| M2-BPR-01 BattleChoreo sequencer | review. Beats from choreo.json; floats/VFX/Read panel land on contact; KO collapse; hand-off waits `BattleStage.hold_after` (controller still 995 lines). |
| M2-BPR-02 clip contract | review. `BattleClips`; creature actors (claude/creatures) strike with their own clip on their contact frame (agreed with creatures). |
| M2-BPR-03 camera director + battle_speed / battle_animations settings | review. |
| M2-BPR-04 specials | review. Swell finishers (dive/verse/brace/glyph), Drownbell toll wave + gather/rim/flood beats (BattleBossVfx lands on contact), Vowbound call/rise/dismiss/fall. |
| M2-BPR-05 stinger, banner timing, victory pose, escape, lead-in bark hook | review. Bark line: Narrative, M2-NAR-01. |
| M2-BPR-06 freeze-frame shots | review. 11 freeze-frames + 2 arenas, all viewed, run-to-run RMSE 0. |
| M2-BPR-07 per-encounter arenas | review. encounters.json `arena`; contract agreed with env-art; greybox tideline_dawn / causeway_disc_sunset; env-art M2-ENV-11 (their task). |
| M2-BPR-08 C10 Ilun first call | review. Full on first live call (flag ch03_ilun_first_call_seen), Short setting, skippable. |

## Pillar-4 fixes found in the freeze-frames
- While an action plays the order has already moved on: the timeline head now reads **"Next"** (not "Acting now") and the help line names the action ("Rhen: Attack") until the sequence ends.
- The Read panel opens on the Read's contact beat, not before the reader moves.

## After MERGE-READY (Lead's queue, 15:22)
- The Lead took d717cb3 into batch big7 (with ui, menus, characters, creatures, combat and the PC's rendering).
- **Mouse parity (Lead item 1): covered by the UI track.** Their M2-UI-26 `BattlePointer` gives battle mouse targeting and Swell play; the command menus took the mouse already. I removed my duplicate picker (M2-BPR-09 closed as superseded, 64a293c) so there's one mouse path.
- **summon_cinematic aligned with UI's M2-UI-23 row** (same id, options, default and text): Short (default) = full the first time, Full = always, Off = no rise. Keep one copy of that row and of the SET_BATTLE_SPEED* rows at merge.
- **Merged claude/m2-slice (MERGE-READY a30b664) into this branch** (66011333) to unblock the Act I arenas and boss intros (append-only conflicts only). Full Godot suite after the merge: **1664 run, 0 failed**.
- **Done this round (all review):**
  - **M2-BPR-10 placeholder hero clips:** a hero actor with a skeleton but no contract clip gets a generated pose clip (bone rotations in choreo.json `placeholder_clips`, MPFB2 DEF-* names); a real clip of the same name always wins, so M2-CHR-07 replaces them with no code change. Also: a hero's own `ko` clip now plays and holds. Not yet seen on a real hero (the actors aren't on this branch): reviewer character.
  - **M3-BPR-01 Act I arenas (greybox):** oruvel_raft_morning, underway_tower, causeway_route_afternoon, derelict_deck_night, ash_terrace_lanternfall, all 19 Act I encounters mapped (ch01_wickfry/oil_slug go to the Underway, per act1_ch01.md). Per-arena staging (underway: shorter, slower). 5 shots viewed and approved. Open: the derelict and Ashcrown fights are morning/day in the beats but graded night (as agreed with env-art); Art may add sub-frames.
  - **M3-BPR-02 boss intros:** Hullgnaw, Bottle Hermit, Spar Wraith, Cinder Matron, the Drownbell: the camera finds the boss, a title card (name, epithet), home; skippable; after the opening banner; once per battle. Shot battle_boss_intro_hullgnaw. Epithets are short and sincere; Narrative may want to own them. No audio sting yet.
  - **M3-BPR-03 Ch6 (review, b1db8fa):** greybox brine_shoals_afternoon (ridges/flats) and salvage_camp_burning (the Inquisitor), Ch6 haze grade, fog-safe lamps; the Inquisitor's intro ("Inquisitor Hadric Moll / A tired officer who still believes the Edict"; Narrative may refine); shots battle_arena_shoals, battle_arena_camp, battle_boss_intro_inquisitor viewed and approved. Toma's first-turn bark still shows after the intro (tested). Known quirk (BattleBossHud, not this track's): one pending prompt slot, so if Toma ever had the first turn his bark would replace TUT_CH06_HOUND.
  - **Follow-ups (17:3x):** BattleBossHud's turn prompt no longer replaces an unshown opening prompt (m2-slice's file, one condition; test_battle_boss_prompts). The Cinder Matron's intro has its own `boss_skyward` shot (she was small behind a party fighter; now clear above the card with the terraces and Ashcrown's cone). Every boss intro has a viewed shot: battle_boss_intro_{hullgnaw,inquisitor,matron,hermit,wraith,drownbell}.
  - **Hero clips (characters' M2-CHR-07):** strikes now land on each clip's `contact` marker (BattleClips.contact_sec); a revive returns a hero to idle. Answered characters.
  - battle_choreo.gd hit the 1000-line cap; the plan moved to BattleChoreoPlan (930 → 936 now).
- **M3-BPR-01 Act I battle arenas: greybox in progress (agent); env-art took M3-ENV-06** (78916415 on claude/env-art) with the same five ids; three are being built now. Starts when big7 brings m2-slice's Act I encounters.
- Hero battle clips: characters' M2-CHR-07 is in progress (reviewer: combat). I'll review and wire it when it lands.
- Review fixes from the big7 gate: none yet.

## MERGE-READY

**MERGE-READY (KO fix) @ 329ce604 (+ this log commit; the integration branch merged in at 07781cba):** M2-BPR-11, the human's playtest bug.
- **+ e03f04ba (hero-integration's review, M2-HER-1103):** applied their proposed patch's test hunks and the stand-in sink fix (a model with a `ko` clip is not sunk through the floor); their sandbox repoint to `game/hero_motion/battle/*` stays on their branch. BattleOutro now starts each hero's victory clip `stagger_sec * i` apart like the hops (new test). Contract doc: a KO pose may kneel or slump; strike blends belong to the model's player. `--filter=battle_` **549 run, 0 failed**. No shot can move (no hero model on this branch; primitives unchanged). **To hero-integration:** done as proposed, thanks; the four tests now take the clip path when a hero has the clip.
- **+ d5d4edfd:** characters approved M2-BPR-10 (logged, task done). A revived hero plays the optional `revive` clip (characters' ~0.8 s clip, coming) before idle. `--filter=battle_` **550 run, 0 failed**.
- **Root cause:** `BattleStage.refresh_ko` re-applies every fighter's stone state after every action, and `CreatureActor.set_frozen(false)` called `AnimationPlayer.play()` whenever the player was idle: that restarts a finished KO clip, so every later move replayed each fallen creature's death. Fixed in set_frozen (a repeat does nothing; it resumes only a clip Petrify paused). Creature models only; primitives and heroes never replayed.
- **Fallen foes now fade out and are hidden** (`battle_sandbox.json` `foe_ko_alpha` 0, shadow gone); the party keeps `ko_alpha` 0.35 to be revived; a revive shows it again.
- **Regression test** `tests/unit/test_battle_ko_once.gd` (5): fell one foe, three more actions, KO clip started exactly once and the foe hidden, for a creature model (sandbox_reef) and a primitive (ch01_underway_shoals); revive and Petrify still work. Without the fix it fails (2 KO starts).
- **"Enemies act twice", presentation side:** no path plays one action twice (one plan per `action_resolved`, VFX hook the contact beat or `action_resolved` never both, placeholder clips skip creatures, no creature has a `ready` clip). The replayed KO (a dead foe moving every turn) is the likely cause of that report; the engine side is the Lead's combat agent's.
- **Checks:** Godot `--filter=battle` **584 run, 0 failed**, `--filter=creature` **13 run, 0 failed**; all 42 battle_* and drownbell shots captured and compared: **0 failed, no baseline changed**; validate_data, taskboard, gdlint, gdformat clean. Skipped: full Godot suite (no change outside battle/creatures; ran both areas), full manifest, Blender.
- Touched creatures' `creature_actor.gd` (set_frozen, the fade's hide): **creatures track please note**.

**MERGE-READY @ HEAD (batch 2 for big8; big7 d6a0886d merged in at 046e8409, latest 9531191c):** M2-BPR-10 placeholder hero clips, M3-BPR-01 Act I arenas + staging, M3-BPR-02 boss intros (all six with viewed shots), M3-BPR-03 Ch6 arenas + the Inquisitor, the BattleBossHud prompt fix, the audio hooks.
- **big7 merge resolutions:** C10 follows `UiSettings.summon_cinematic_cut` (Lead's call); Off's `none` cut still plays `off_entry` (no rise; tested). Seven new arena shot fixtures moved to `game/levels/_tests/battle_arenas/` with their script path. strings/flags/shots/provenance/docs unioned; 19 duplicate loc keys dropped. My handoff renumbered combat-18. **17 m2-slice speakers** (boatman … wright) got placeholder voice rows like the Lead's six (noted on M3-AUD-13) so validate_data stays 0/0.
- **Checks run:** full Godot suite **2032 run, 0 failed**; validate_data 0/0, taskboard --check, gdlint, gdformat clean. tools/tests **704 run, 2 failed (7 skipped)**: both `test_hero_clips` (below). Shots: 9 arenas, 11 choreo, 6 boss intros compared. Re-approved after viewing: battle_arena_{raft,underway,route,derelict,terrace,shoals,camp} and battle_boss_intro_drownbell (only changes: the creatures track's models in place of stand-ins and UI's new panel corners); all others PASS.
- **Known red, not this track's:** `test_hero_clips` (characters' test from big7) fails because m2-slice's Ch4–Ch9 dialogue calls 32 Asha/Toma clips hero_clips.py lacks. Same on any branch with both. Request **M3-CHR-01** lists every clip and its scene. No test was skipped or loosened.
- **env-art's report (19:5x):** (1) `AudioDirector.attach_battle` assigned freed listener keys to an `Object` loop var: now `Variant` like the prune loop above it (audio's file, one token; **audio track please note**). (2) The WorldEnvironment owner warning: `BattleArena.apply` already clears the owner of every moved node (battle_arena.gd:63); not reproduced here on the greybox (single run nor the 10-shot capture). Env-art: send the exact log line and shot if it persists.
- **Skipped:** full screenshot manifest (only battle shots can move), Blender (none touched), coverage (no game/battle core change).

**MERGE-READY @ HEAD (see `git log -1 origin/claude/battle-presentation`; the integration branch merged in at 35d3a35, m2-slice MERGE-READY a30b664 merged in at 6601133):** M2-BPR-10 placeholder hero clips, M3-BPR-01 Act I greybox arenas + staging, M3-BPR-02 Act I boss intros, the audio hooks (battle_stinger / battle_bark / boss_intro), M2-BPR-08's alignment with UI's summon_cinematic row, M2-BPR-09 closed (superseded by UI's BattlePointer).
- **Checks run (on 35d3a35 + the two small fixes after):** full Godot suite **1707 run, 1 failed** (below); tools/tests **561 OK (3 skipped)**; validate_data, taskboard --check, gdlint, gdformat clean; battle_controller.gd 995, battle_choreo.gd 936 lines. Shots: all 30 battle_* plus drownbell_flood captured and compared: all PASS after the drownbell rig fix (new and viewed: battle_arena_raft/underway/route/derelict/terrace, battle_boss_intro_hullgnaw).
- **RESOLVED 16:5x:** m2-slice reverted its 17 resident flags (dc044b48) and I merged it again; `test_scene_router_swap` passes here (16/0, twice). **Full Godot suite on 1311c99: 1739 run, 0 failed.** Since then only 0f-level additions: the hero contact-marker fix (choreo 40/0, placeholder 7/0, specials 13/0) and task files. Background, kept for the record: **`test_scene_router_swap` (boot.tscn and battle_sandbox swap frames 160–190 ms ≥ 40 ms).** It passes on the integration branch alone and on this branch before the 35d3a35 merge; it fails once **m2-slice's M2-ENV-05 `"resident": true` flags in prewarm_materials.json** meet **the integration branch's new boot card / shader_prewarm / scene_router (M2-ARC-05/08)**. Removing the resident flags makes it pass (verified). The Lead will hit the same when merging m2-slice: needs the m2-slice / architect owners (resident warm-up has to stay out of the swap frames). I didn't change either.
- **Skipped (Lead's rules):** full screenshot manifest (only battle shots and drownbell_flood can move), Blender (none touched), coverage (game/battle/scene excluded; no core change).


**MERGE-READY @ d717cb3** (`claude/battle-presentation`; the integration branch at its 14:3x head merged in at 9fee881, docs-only commits after it): M2-BPR-01 choreography, -02 clip contract (with creature actors), -03 camera director + battle speed / battle animations settings, -04 specials (Swell finishers, Drownbell toll/rim/flood, Vowbound call/rise/dismiss/fall), -05 tide-line stinger + banner timing + victory/escape + lead-in bark hook, -06 freeze-frame shots, -07 per-encounter arenas, -08 C10 first-call cinematic.
- **Checks run (on 9fee881):** full Godot suite **1528 run, 0 failed**; tools/tests **511 OK (3 skipped)**; gdlint, gdformat --check, validate_data, taskboard --check clean; battle_controller.gd 995 lines. Shots captured and viewed: all 17 battle_* plus drownbell_flood (new: 11 battle_choreo_*, battle_arena_tideline, battle_arena_causeway; re-approved after viewing: drownbell_flood (sunset causeway arena + the party's flood brace), battle_choreo_vowbound_rise (help line); every other battle shot unchanged; run-to-run RMSE 0 for all new shots).
- **Skipped (Lead's gate rules):** the full screenshot manifest (only battle shots and drownbell_flood can move: no other scene or shader touched besides the stinger's new shader, which no shot captures), Blender (no Blender sources), coverage (no game/battle core or game/progression change; game/battle/scene is excluded).
- **For the Lead at merge:** (1) shared-file appends: strings.csv, flags.tres (ch03_ilun_first_call_seen), accessibility.json (3 rows), validate_data.py (check_choreo), prewarm_materials.json (the stinger shader, one row); (2) PC's game/vfx/battle files got two one-`if` hooks (BattleVfx, BattleBossVfx land on BattleChoreo.contact); (3) creatures merge: delete BattleActorMotion's action/hit calls; (4) env-art merge: repoint arenas.json and re-approve the three arena-dependent shots; (5) battle_vowbound_call sits at RMSE 0.00798 / 0.008 on lavapipe here, the same on base 499f074.

## Notes from env-art (17:10)
- The raft's rope rails are at x ±6.3 and the derelict's bulwarks at ±7.2: runs stay within ~±4 m (fine; underway travel is 0.6x anyway).
- underway_tower's `Underwater` child (ArenaUnderwater over the UnderwaterRig) must come after the moved WorldEnvironment and Sun: BattleArena already moves those first. **Follow-up:** when Rhen's fighter carries a lamp node (hero actor), re-target `Arena/Underwater.lantern_target` to it (today a bare marker at party slot 0's hand). Its look under the battle camera: Rendering's M3-RND-25.
- **Lead rule:** lights near a dense FogVolume set `light_volumetric_fog_energy = 0`. Done for every OmniLight in this track's greybox arenas and the C10 summon light (shots unchanged, RMSE 0). **PC GPU:** BattleBossVfx's glow and net_light OmniLights need the same (your file).

## Requests filed for other tracks
- Arena kits: env-art's own **M2-ENV-11** (docs/kb/tasks/M2/M2-ENV-11-battle-arenas.md on claude/env-art, in review); my duplicate task file was removed. Final scenes: assets/environments/arenas/{tideline_dawn,causeway_disc_sunset}/<id>.tscn (root: WorldEnvironment, Sun, Sea, dressing, CameraHints, BossAnchor, FloodAnchor; their root script is BattleArenaRoot, no name clash). **After the Lead merges both branches:** repoint the arena paths in game/data/battle/arenas.json (M2: tideline_dawn, causeway_disc_sunset; M3-ENV-06, all five at 169445e9: causeway_route_afternoon, derelict_deck_night, ash_terrace_lanternfall, oruvel_raft_morning, underway_tower) to assets/environments/arenas/<id>/<id>.tscn, then view and re-approve every battle_arena_* shot, drownbell_flood and battle_boss_intro_hullgnaw (raft). Env-art notes: the derelict deck's bulwarks are at x ±7.2 (runs stay within ~±4 m: fine); the terrace's plume is above the default frame (a tilted boss shot for the Cinder Matron could show it: a follow-up for the boss_tall shot). Whoever merges second (Lead or this track) does it.
- M2-NAR-01 (narrative): the tideline lead-in bark line.
- At the creatures merge: delete the action/hit calls in BattleActorMotion._on_action_resolved (agreed; whoever merges second).

## Exact next step
**KO fix: done and MERGE-READY @ 329ce604 (see MERGE-READY above).** Id rule (Lead, 21:00, CONSOLIDATED §4): this track's new task ids are 400–499 (e.g. M3-BPR-410), ADRs 0130–0139, handoffs `<date>-<role>-bpr-<n>.md`; M2-BPR-11 and M3-CHR-01 predate the rule and keep their ids.
MERGE-READY for big8 (above). After big8: take env-art's arenas.json repoint (74c6dc0e on claude/env-art) if the Lead hasn't, re-view arena shots. Then: review fixes; M3-CHR-01 clips when characters land them.

Older: Next: review fixes as they come, the creatures/env-art follow-ups after the Lead merges, then M3 battle presentation (hero clips as the characters track lands them; per-encounter arenas for Act I fights).

## Log
- 2026-10-24: merged the stinger agent (04417ea); freeze-frame capture states (b6..); BattleOutro (4e052f8). Specials agent spawned. **Two queue items remain after camera + specials: BPR-06 baselines and the pre-merge full gate.**
- 2026-10-24: branch created and pushed; tasks claimed (b-claim commit). BattleChoreo core pushed (0cfa455). Two worktree agents running (BPR-05 stinger/banner, BPR-03 camera).
