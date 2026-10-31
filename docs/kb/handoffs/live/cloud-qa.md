# Live log: cloud-qa (lavapipe stand-in for the PC)

This environment owns this file (CLAUDE.md §7a). Branch `qa/cloud-pass6`. The Lead is `session_01Bg3iP7cPGyjbX4CyniBahc`;
the integration branch is `claude/new-session-mj8c3c`.

**What it is:** the PC (pc-gpu) is offline, so this cloud session runs its QA passes headless and on Mesa lavapipe
(llvmpipe, 4 vCPU, no GPU). Lavapipe's lighting, shadows and shading differ from the RX 9070 XT, so every pass-6 note
judges only what lavapipe can show: framing, geometry, cameras, presence and motion. Timings are CPU-side and on a
contended 4-vCPU box: compare them with each other and across merges, not with the PC's numbers.

**Methods and tools (all on this branch):**
- The PC's QA doc and walk tools were brought over from `gpu/act1-qa-5` (tools only): `docs/kb/qa/act1_gpu_qa.md`,
  `tools/gpu_bench/slice_sweep.gd`, `act1_walk*.json`, `capture_preset.gd`.
- Manifest shots: `tools/screenshots/capture.sh --shots <ids> --out <dir>` (one process per shot, lavapipe).
- Row walk: `godot-render ... res://tools/gpu_bench/slice_sweep.tscn -- --walk=res://tools/gpu_bench/act1_walk_pass6.json
  --preset=high --res=960x540 --stills=<dir>`.
- Playtest probes (new, headless):
  - (a) `tools/gpu_bench/return_probe.tscn`: the victory exit → field timing;
  - (b) `tools/gpu_bench/dock_probe.tscn` + `dock_overlaps.py`: Oruvel's boat/dock AABBs and every deck edge walked;
  - (c) `tools/gpu_bench/run_cycle_probe.tscn` (lavapipe): a clip at even phases from the stage's cameras;
  - (d) `tools/gpu_bench/encounter_gap_probe.tscn`: each zone's live FieldEncounters meter, its gaps and the run speed.
- Stills: `docs/kb/qa/cloud/pass6/` (small JPG sheets).

## PASS 6 @ 2026-10-30 (big22, integration @ 19e7f01c)

QA-DONE pass6 @ 19e7f01c (big22), with the playtest checks (a), (b) and (d) re-run on big23 @ 8fe3644b.
The row notes ("pass 6 (cloud, lavapipe, 19e7f01c)") and the new rows 74–78 are in `docs/kb/qa/act1_gpu_qa.md` on this
branch. That file isn't on the integration branch yet; this copy is the PC's gpu/act1-qa-5 copy plus pass 6.

### Rows by verdict and owner (lavapipe judges framing, geometry, cameras, presence and motion only)
- **Fixed on lavapipe (6), GPU to confirm:**
  - 34 (act1-chapters, env-art-b): ridge skippers on the shoals' beach vs Shoal Skippers;
  - 38 (hero-integration, env-art-b): the Coilspire spawns frame Rhen. The "Encounter looks at open sea" is a walk
    artefact: that spawn is the world origin until a random fight records a return point (greybox_zone.gd:106);
  - 46 (characters): no shadow line down Moll's face;
  - 47 (env-art): FerryAft frames the hero whole in the cabin;
  - 51 (env-art-b): the field camera shows the graves as sand mounds;
  - 59 (env-art): the o10 gull is in frame on its post.
- **Partly fixed (8):**
  - 17 (rendering): the dense rings are gone; a few thin arcs remain;
  - 24 (env-art): DockShore is no longer inside Rhen, but a half-faded hero stands at the lens; DockEnd has no hero;
  - 37 (hero-integration): Toma's shield still fills the right third at AfterHarrier;
  - 54 (characters): Sefir's gown is pleated; her hair is still a cap with floating strands;
  - 55 (characters): Sabe's and Fenn's white hair is still a flecked cap;
  - 58 (slice-polish, act1-chapters): o07 is reframed and net_pen reads; the Hullgnaw is a small dark shape;
  - 61 (battle-presentation, creatures-b): the Surge is smaller now, but its head is cropped at the top edge;
  - 66 (hero-integration, env-art): no frame inside a wall; about 5 stills low against a wall and post, then under an
    eave.
- **Still open (6):**
  - 21 (hero-integration): not reachable here (see the row);
  - 39 (act1-chapters): Rhen is alone in Ch9;
  - 56 (characters): Asha's run skirt is unchanged since big19;
  - 62 (env-art-b): the weir (the material is a GPU check);
  - 63 (env-art-b): the flat panel behind the Matron;
  - 64 (battle-presentation): one 78–234 ms CPU frame at each boss fight's reveal, still there on big23.
- **New playtest rows:** 74 integration-qa (open), 75 env-art (partly), 76 env-art and integration-qa (fixed on big23),
  77 characters (open), 78 act1-chapters (fixed on big23).

### HUMAN PLAYTEST checks (2026-10-30), headless

**(a) Victory exit → field (owner integration-qa; target ≤ 1 s of black).** `return_probe`: the F8 chapter start, the
location, the fight asked for as the zone asks it, foes held at 1 HP, Return pressed 1 s after the result panel shows (t0).
From t0 it holds the stick and records the router's fade. CPU-side, on a 4-vCPU box with a lavapipe job beside it, so the
absolute numbers run slower than a PC; they are for comparing merges. Milliseconds from t0, 19e7f01c → big23 (8fe3644b):

| Fight → return | black (fade ≥ 0.99) | field scene in | fade clear | hero moves | input live | instantiate | worst hidden frame |
|---|---|---|---|---|---|---|---|
| tideline → Haluna BattleReturn | 5905 → 6130 | 5375 → 5310 | 6601 → 6679 | 5574 → 5520 | 18417 → 18524 (the post-fight lines) | 1815 → 1883 | 3100 → 2944 |
| causeway shore → Encounter | 4046 → 3744 | 4356 → 4067 | 4737 → 4432 | 4380 → 4081 | 4737 → 4438 | 90 → 106 | 3881 → 3569 |
| the Drownbell → Haluna DockNight | 17012 → 14752 (B11, the chapter card, Ch4 inside the 60 s) | 5815 → 4371 | 6791 → 5638 | 6271 → 4829 | never in 60 s (B11 → Ch4) | — | — |
| Oruvel scuttlers → AfterScuttlers | 2797 → 2795 | 3102 → 3085 | 3495 → 3471 | 3115 → 3103 | 3495 → 3471 | 1277 → 1198 | 1444 → 1498 |
| Ch4 ferry (derelict leeches) → Encounter | 5554 → 5497 | 5557 → 5471 | 6223 → 6158 | 5832 → 5767 | 6229 → 6162 | 909 → 817 | 4252 → 4268 |
| Ch6 ridge skippers → Encounter | 11263 → 11354 | 10893 → 10841 | 11815 → 11907 | 11150 → 11114 | 11834 → 11914 | 3815 → 2677 | 6683 → 7769 |

- **Every return is far over 1 s of black, and big23 doesn't change it.** The black is the zone's whole reload under the
  fade: one hidden frame of 1.4–7.8 s (the zone's instance and first draw), then the reveal wait. The battle has freed the
  field, so each return is a cold zone entry.
- **The hero takes the stick 0.3–1.1 s before the fade clears** (moves < fade clear on every return): he can walk blind.
- The tideline's post-fight lines hold input until ~18.5 s (story, by design). The Drownbell goes on through B11 and the
  chapter card into Ch4.
- **Suggestion for integration-qa:** start the return zone's threaded load when the victory shows (the result panel is
  ≥ 1 s of reading), or keep the field zone resident under the battle, so Return only fades.

**(b) Oruvel moorings (owner env-art; the guard integration-qa).** `dock_probe` + `dock_overlaps.py`.
- **Boats vs docks (mesh AABBs overlapping > 5 cm on every axis):** 19e7f01c 13 pairs → **big23 10 pairs** (7fbb9319
  moved the cookboat clear). Still overlapping on big23:
  - scale_hull × the raft deck under it: 1.93 × 2.08 × 7.27 m;
  - keel_hull × two tucked raft decks: 10.45 × 2.17 × 0.43 m each;
  - terrace_hull × a tucked raft deck: 0.25 × 2.14 × 10.50 m;
  - hull_outrigger × a small tucked deck: 0.59 × 1.14 × 0.34 m; the second outrigger × two plank bridges: 0.61 and
    2.76 m wide;
  - dive_raft × two plank bridges and the gull post (likely intended: the bridges land on the raft, the post stands on it).
  AABBs only flag candidates: view them in the GPU stills before acting.
- **Dock edges:** every walkable deck box's edges, every 2 m, the hero driven straight off with the field controller.
  - **19e7f01c: 215 of 260 pushes walk off into the water**, onto the solid Sea block at y = −1.0, and the hero **can't
    climb back** (216 of 216 tries stuck 1 m below the deck): a soft-lock at every open edge of every mooring, bridge and
    plank.
  - **big23: 0 of 260** (28b005ad's edge walls). Fixed.

**(c) Rhen's default run (owner characters).** `run_cycle_probe`, rhen_stage at 12 even phases of the `run` clip
(0.667 s), side and front, on lavapipe: `docs/kb/qa/cloud/pass6/playtest_c_rhen_run_side_front.jpg`.
- Side: a full alternating stride, the feet plant, the torso upright: grounded.
- **Front: the hands swing up to shoulder and face height with open, splayed fingers** (left hand at t0–t1, right at
  t5–t8). It reads as a wave, not a run's arm swing. The forearms stay folded up through the whole cycle.

**(d) Breather between field encounters (owner act1-chapters; target 30–45 s).** `encounter_gap_probe` reads each zone's
live meter and draws its first 8 gaps with the zone's own `_draw()`, plus the grace, at the 3.6 m/s run (the measured push
reaches 3.59–3.66 m/s on open ground).

| Zone | 19e7f01c gaps (s) | big23 gaps (s) |
|---|---|---|
| Ch1 Underway | 6.5–11.6 | 31.0–48.7 |
| Ch3 causeway (after the harrier) | 25.4–29.6 | 39.0–52.0 |
| Ch4 derelict | 8.2–13.7 | 32.3–50.1 |
| Ch5 Ashcrown stair | 11.7–17.1 | 35.4–52.0 |
| Ch6 Brine Shoals | 10.0–13.2 | 38.4–48.3 |
| Ch8 Coilspire path | 9.5–14.5 | 33.6–50.9 |

- **big23 fixes it** (a1e49de9, b7d03f81: a 95–145 m gap, grace 15 m and 12 s). About a third of the draws land 46–52 s,
  a little over the 45 s target: fine for a breather; say if 45 s is a hard cap.
- Oruvel, Haluna, the Shell Shrine, the wake, Pemakar, Tamsule and Corrow have no random encounters, only scripted fights.
- With the longer gaps, the main routes (straight-line spawn-to-spawn: 13–197 m) now hold 0–1 random fights each. The
  Coilspire path (102 m) and the derelict (13 m) hold none.

## STATUS (01:05): big35 (6df68f059) chapter-start pieces started
- **big34 fresh run (9317c6b6c), stopped for big35:** New Game → Ch4's Brightwater ferry in 1175 s with **0 ERROR
  lines**. The only stop was the Shell Shrine basin puzzle, which the probe skips (PLAY_SKIP), as on earlier runs.
- **Now, in order, on big35:** F8 Ch6 → end card (the Coilspire door after the beacon scene, and the binding), then a
  fresh New Game → Ch6. Both count ERROR lines against a target of 0.

## STATUS (01:10): big33 Ch6 → end card, the binding hang; big34 fresh run started
- **big33 (5695a69ce), F8 Ch6 → end card, second try.**
  - Ch6 and Ch7 play by objective. Ch8 plays Corrow, Ivo, the path fight, the door (576.6 s), both flue-moth fights
    and the flue tiers.
  - With the probe's landing fix, the crown binding fires (`ch08_virel_bound` at 855.9 s). The flue puzzle itself is
    still skipped by the probe (PLAY_SKIP).
  - **Then the run stops inside the binding scene. This is a game bug, M3-C08-1400 (act1-chapters, high).**
    `ch08_binding.dlg:26` `@mark virel virel_gone` walks Virel about 2,500 m to the off-stage park at 1 m/s.
    `CutsceneSequencer._finish` plays every walk out, so the player has no control for about 42 minutes after Asha's
    last line. A debug script saw `_awaiting` = wait with `wait_left` 2483 s, counting down in real time.
  - Holding ui_cancel (skip) gets out; tapping ui_accept doesn't. No other `.dlg` has a `@mark` more than 200 m off.
  - The same task asks for the missing objective row (crown → binding).
- **Probe:** past 90 s stuck in a cutscene, it now holds ui_cancel (PLAY_SKIP_SCENE), as a stuck player would. It lands
  on a floor point inside a trigger that spans a void (the crown's trigger spans the spire's well).
- **Now:** big34 (9317c6b6c), one continuous fresh-profile run New Game → end card (`--secs=12000`, detached).
  ERROR lines will be counted against a target of 0.
- **Queued:** Ch8's Coilspire door after big35 merges (the touch-beat fix), then the Act II smoke, Ch10 → Ch13.

## STATUS (23:35): objectives preview on 7a37c3d53, then big33 and the Lead's 23:06 ask
- **Preview on act1-chapters' 7a37c3d53 (F8 Ch6 → end card).** With the new rows, the probe plays Ch6 and Ch7 by
  objective. In Ch8 it plays Corrow and Ivo, the Coilspire path fight, and the Coilspire door
  (`ch08_entered_coilspire` at 577.6 s; this was blocked on big28).
- **The flue puzzle** ("Lead the flame up the flues to the crown") was skipped by the probe (PLAY_SKIP raised
  `ch08_flame_at_crown`). That's a limit of the probe, not of the game.
- **Then a soft-lock at 939 s.** The HUD reads "No errand calls just now" at (309.4, 81.3, 157.8).
  - **Objective gap, owner act1-chapters.** The Coilspire rows are q_door (until entered), q_crown (until
    `ch08_flame_at_crown`) and q_beacon (requires `ch08_virel_bound`). No row covers flame_at_crown → virel_bound,
    which is the crown binding beat (trigger `crown`, y 74.3). A player who reaches the crown sees "No errand calls
    just now" until they find the trigger on their own.
  - The probe's whole-zone sweep stepped onto `crown` over and over without firing it. Its landing ray started 40 m up
    and took the gallery floor above the crown. The probe now rays from 2 m above each trigger
    (`playthrough_probe.gd`, TRIGGER_RAY_M). Ch5 wasn't reached in this preview.
  - ERROR lines in this run: 39. Of those, 32 are the known UiAudio `used` reconnect on resident returns (audio and
    integration-qa; big34 should fix it). The rest are 3 × `material` null, 2 × uninitialized RID, 1 × `mem` null and
    1 × wrong RID, all rendering-server noise in headless mode.
- **Now: F8 Ch6 → end card on big33 (5695a69ce),** with the fixed probe.
- **Next, from the Lead's 23:06 ask:** once big34 merges, one continuous fresh-profile run from New Game to the end card
  (or the chapter-start pieces again), counting ERROR lines against a target of 0. Then the Act II smoke, Ch10 → Ch13,
  the same way.

## STATUS for the Lead (23:05): the Act I end-card playthrough
- **Done on big28 (c646c3a8): the Act I end card is reached, with no game soft-lock.** The run is pieced together:
  fresh New Game → Ch6, then F8 Ch6 → Ch8, then F8 Ch9 → end_card. Details are in the big28 section below.
- **The probe did stall where Ch6 and Ch8 had no objectives.** It got through Ch6 and Corrow by sweeping their story
  triggers, but it couldn't play the Coilspire interior.
- **Now:** re-running Ch6 → end card and Ch5 (the new Ashcrown stair rows) on act1-chapters' 7a37c3d53, which has the
  objectives. That commit contains big28 but not big32. When big33 merges I'll re-run Ch6 and Ch8 there.

## RE-RUN after "Merge lead/gate-big32" (integration @ 8889542f6): playtest (a) and (b)
Same probes and box. Milliseconds from Return, big28 → big32:

| Fight | black | field in | fade clear | resident | Verdict (≤ 1 s of black) |
|---|---|---|---|---|---|
| tideline | 426 → **161** | 469 → 445 | 1086 → 838 | yes | PASS |
| Oruvel scuttlers | 57 → 71 | 387 → 392 | 735 → 740 | yes | PASS |
| the Drownbell (→ Haluna DockNight) | to the field: 5032 → **2533** | 1987 → 2062 | 5032 → 2533 | no (another zone) | **FAIL, better:** about 2.5 s of black before Haluna shows (was 5.0) |
| causeway / Ch4 ferry / Ch6 (random) | 54 / 69 / 83 → 57 / 69 / 72 | ~390 | ~740–754 | yes | PASS |

- **(a): 5 of 6 pass.** The Drownbell's cross-zone return has improved to 2.5 s but is still over 1 s (integration-qa). The
  hero moves only after the fade clears.
- **(b) Oruvel boats: PASS.** 4 AABB pairs: the dive raft's three (intended) and the second outrigger against the net
  pen (0.35 × 1.14 × 6.77 m). Viewed on lavapipe (`docs/kb/qa/cloud/pass6/row75_outrigger_big32.jpg`): the canoe now
  lies in open water alongside the pen's outer walkway, its booms resting over the walkway edge. It reads as moored;
  no hull runs through a deck. M3-ENV-1391 can close. **Edges: PASS** (0 of 260).
- The UiAudio reconnect ERROR is still there on big32 (60 lines in the return probe's six fights).

## RE-RUN after "Merge lead/gate-big28" (integration @ c646c3a8, the scripted-fight resident return)
Same probes and box. Milliseconds from Return, big27 → big28:

| Fight | black | field in | fade clear | hero moves | resident | Verdict (≤ 1 s of black) |
|---|---|---|---|---|---|---|
| tideline (scripted) | 5098 → **426** | 4098 → 469 | 5649 → 1086 | 4277 → 14512 (the post-fight lines first) | yes | **PASS** |
| Oruvel scuttlers (scripted) | 2893 → **57** | 3192 → 387 | 3582 → 735 | 3207 → 397 | yes | **PASS** |
| the Drownbell (scripted, Shell Shrine → Haluna DockNight) | 14868 → 11086 (B11 and the chapter card on to Ch4) | 4079 → **1987** | 5542 → **5032** | 4478 → 2381 | no (another zone) | **FAIL:** Haluna is in by 2.0 s, but the screen stays black until 5.0 s |
| causeway (random) | 75 → 54 | 409 → 387 | 767 → 740 | 450 → 837 | yes | PASS |
| Ch4 ferry (random) | 62 → 69 | 389 → 394 | 753 → 759 | 449 → 850 | yes | PASS |
| Ch6 ridge skippers (random) | 93 → 83 | 414 → 394 | 780 → 750 | 456 → 841 | yes | PASS |

- **5 of 6 returns pass.** The Drownbell's is a cross-zone return (Shell Shrine → Haluna), so it can't stay resident. It
  still holds about 5 s of black, about 2 s of load and then about 3 s more under the fade before B11 shows. Owner
  integration-qa (with slice-polish for B11's opening fade). Row 74 is now partly fixed: only the Drownbell is left.
- On the field-to-field returns the hero now moves only after the fade clears (837–850 ms against 740–759 ms): the
  "walk blind" note is fixed.
- **(b) Oruvel: edges PASS** (0 of 260 off the deck). **Boats: FAIL (partly):** still 5 pairs, unchanged from big27.
  The second outrigger lies under the two plank bridges (0.61 and 2.76 m), a real clip, M3-ENV-1391's last box; the
  dive raft's three are intended.
- **New ERROR on big28 (not on big25), owner audio with integration-qa:** after each resident return, Godot prints
  `ERROR: Signal 'used' is already connected to given callable 'Node(UiAudio)::request'`, from `UiAudio.watch`
  (game/audio/ui_audio.gd:90, via audio_director.gd:569). That's 97 lines in one Act I run, first after the first
  Underway fight's return. The re-attached zone's Interactables are watched again: the "already watched" guard misses
  them, so `watch` connects a second time. No crash and no doubled sound (the second connect fails), but it's an engine
  ERROR on every return, and qa_threads-style guards count those. Make `watch` skip a node it's already connected to
  (`is_connected`), or forget/re-watch on detach.
- **The fresh-profile playthrough to the Act I end card on c646c3a8.**
  `playthrough_probe.tscn` uses guided hops toward the objective marker, so it skips a puzzle or climb it can't play by
  raising that objective's flag (PLAY_SKIP).
  - **New Game → Ch6 Brine Shoals: no game soft-lock in 2350 s, 0 SCRIPT ERROR.**
  - Played: the Prologue → Ch1 (Underway, Oruvel, 4 fights) → Ch2 Haluna (beach, tideline, Nemes, the save shrine) →
    Ch3 (the causeway, the harrier, the Shell Shrine, the Drownbell, B11, the chapter card) → Ch4 (the wake feast, the
    shell set, the dock; the ferry, Ysolde joins, the derelict: leeches, the Spar-Wraith) → Ch5 (Pemakar, Kerrid, then
    Pemakar again, ch05_done) → Ch6 arrival.
  - **Steps the probe skipped (not played; each checked as probe limits, not game bugs):**
    - Ch3 the Shell Shrine's basin puzzle (`ch03_shrine_door_open`).
    - Ch4 the bottle-hermit (`ch04_hermit_won`). A headless stick walk confirms the hermit fight fires when you walk
      round the hold hatch at x −7. Straight at the hatch corner the hero catches on its 0.42 m lip (minor collision
      feel, env-art).
    - Ch5 the Ashcrown stair and trial (`ch05_trial_begun`, `ch05_strike_landed`). The objective's target height (y 0)
      sits between the stair foot (−81) and the crown (+36), so the probe's jumps land on the wrong level.
  - **Real finding, owner ui-menus + act1-chapters: Ch6 Brine Shoals and Ch8 (Corrow, the Coilspire) have no objective
    rows in `objectives.json`.** On arriving in Ch6 the objective line reads "No errand calls just now. The road will
    keep." with no marker. Every other Act I zone has 1–7 rows (ch09/corrow_night has 4).
  - **Ch6 → the end card, on c646c3a8: REACHED.** Pieced together from F8 chapter starts once the fresh run reached Ch6:
    - **Ch6 (F8 start), then on through Ch7 into Ch8 in one run, played.** The midday, Liss sheltered, the Inquisitor
      fight (Moll yields), on to Tamsule, the bell galleries, the Tidecup match, Tavi withdrawn, then Ch8: Corrow, Ivo,
      the save shrine, the stair, the Coilspire path fight, feeding the beacon.
    - **The Coilspire door: not passed by the probe.** Its touch beat fires when the hero is placed on it fresh
      (headless check), but not in the probe's flow after the beacon scene. Inside is the flue-key puzzle and the two
      moth fights, which guided hops can't play anyway. Ch8's interior, the crown binding and the beacon opening are
      unplayed by this smoke.
    - **Ch9 (F8 start) → the Act I end card, played: 216 s, 59 flags.** The Ebbing dance (two "hold to raise the
      staff" prompts held), Asha, Pell joins and is named, Kerrid on the road, ch09_act_one_complete, then
      end_card.tscn.
  - **No game soft-lock anywhere it played.** Every stop was a probe limit, each checked headlessly:
    - Ch4: the hold-hatch lip;
    - Ch5: the Ashcrown heights;
    - Ch6: Toma's refused Attack;
    - Ch8: the door, after the beacon scene;
    - Ch9: the hold prompt, which needs a hold, not a tap;
    - plus a shop menu and a freed trigger in the probe itself.
  - **Real findings from the run:**
    - **No objective rows in Ch6 or Ch8** (above): the player gets "No errand calls just now" all through Brine Shoals,
      Corrow and the Coilspire (ui-menus, act1-chapters).
    - **The UiAudio reconnect ERROR** after each resident return (above): 134 in Ch1–Ch6, 11 to 21 per later run
      (audio, integration-qa).
    - **New ERROR, owner audio:** `Amount of unbind() arguments must be 1 or greater` at `game/audio/ashcrown_audio.gd:53`
      (`_connect`, from `attach`, `audio_director.gd:663 attach_ashcrown`), twice on entering Ashcrown. A signal with
      no arguments goes through `unbind(0)`; it wants a plain callable when argc is 0 (as ui_audio.gd does).
    - Minor (act1-chapters, env-art): a touch beat entered while another scene plays is dropped until the hero steps
      out and back in. The Ch4 hold hatch's 0.42 m lip catches a hero walking into its corner. The Ch9 objective marker
      at the landing (−27.1, 29.9) sits past a ledge: a straight walk stops 3.5 m short at (−30.6, 29.4), though the
      way round works.
  - Logs (scratchpad only): play_full_ch1_ch6.log, play_ch06_to_ch08.log, play_ch08.log, play_ch09.log.

## RE-RUN after "Merge lead/gate-big27" (integration @ 9572c4129): playtest (a) and (b)
Same probes and box. The deltas against big25:
- **(a) Scripted-fight returns: still FAIL, unchanged.** Black from Return: tideline 5507 → 5098 ms, Oruvel scuttlers
  2808 → 2893, the Drownbell 4031 → 4079 ms until the field scene is in (then B11 and the chapter card, by design).
  Random-fight returns still pass: causeway 63 → 75 ms, ferry 60 → 62, Ch6 69 → 93; fade clear by 753–780 ms. Row 74
  stays partly fixed (integration-qa: the resident return for scripted fights).
- **(b) Oruvel boats: 10 → 5 AABB pairs.** The scale, keel and terrace hulls and the first outrigger are clear now.
  Left: the second outrigger under the two plank bridges (0.61 and 2.76 m wide, unchanged; a real clip, M3-ENV-1391's
  fourth box) and the dive raft's three (intended). Edges: 0 of 260 off the deck (still a pass).

## THE LEAD'S ASK (17:24): playthrough smoke, the rows on the newest merge, re-runs per merge
**Newest merge:** big25 @ 4b198810. No later "Merge lead/gate-bigN" yet; (a) and (b) on big25 are in the section below.

**(3) Fresh-profile Act I playthrough smoke, headless, on big25: PASS (New Game → Ch2 Haluna in 417 s, 25 flags).**
`tools/gpu_bench/playthrough_probe.tscn`, with an empty XDG_DATA_HOME:
- It presses the title's New Game and taps ui_accept whenever the field isn't taking input.
- In the field it hops the hero toward the objective line's own target (ObjectiveHud.target_position) and interacts.
- It wins fights live (foes held at 1 HP) and presses Return.
- The route it played: the Prologue (8.9–41.9 s) → the Underway: bell room, wickfry and Oil Slug fights, the gauge wheel →
  Oruvel: the sale at the scale hull, Kell's wick, the gulls, the scuttlers fight, the lashings, the children safe, the
  Hullgnaw → "going under" → Ch2 Haluna: the beach, Asha met, the objective tutorial.
- **No soft-lock, no stuck dialogue, no missing transition; 0 SCRIPT ERROR and 0 ERROR lines.** The only warnings are
  load-budget warnings (this box is slow).
- **Probe limits worth knowing:**
  - Hops move in straight lines. Where big25's FieldShore stops them at a dock edge, the probe jumps beside the target
    (PLAY_TELEPORT). That's a probe limit, not a game soft-lock.
  - Two beats sit on touch triggers on the way, not at the objective's target. Kell's wick fires on her bridge at (23, −6),
    not at Kell at (29, −7); the scuttlers fire on their own trigger. The probe finds them by stepping onto the triggers near
    the target (PLAY_SWEEP).
- **Minor fragility (low priority; owner act1-chapters, with tech for greybox_zone.gd):** the touch-trigger boxes start
  exactly at deck height (y 0 to 3 m). A hero who lands on a deck from above (a teleport, a fall) rests at y −0.0004, and
  `contains_point` is false, so Kell's beat didn't fire until the probe dropped him in from 0.3 m. Walking in from the
  commons (around the net frame) he stands at +0.0009 and it fires: checked by stick in a headless test. Suggest starting
  each touch box a few cm below its `at` height.
- **Minor note (act1-chapters):** the o_kell objective points at Kell herself, but interacting with her does nothing.
  The beat is the touch on her bridge, so a player who comes at her another way gets no response from her.
- The 19e7f01c attempts that "soft-locked" at Oruvel were the probe's hops, not the game.

**(2) Pass-6 rows on big25 (lavapipe, the 15 row shots against 19e7f01c):**
- **63, the Matron: fixed on lavapipe.** The flat bright panel behind her is now a lattice window
  (`big25_rows63_58_62_vs_19e7.jpg`).
- **58, hullgnaw_rises: better.** The Hullgnaw rises lit and larger out of the water beside the pen. net_pen is reframed
  closer, with the children larger. Still partly: o07 has no Sadi.
- **56, Asha's run:** the pose changed a little (a foot shows), but the skirt is still a cone. Still open.
- **54, Sefir's face:** the floating strands are thinner, but it's still a cap. Partly.
- Unchanged since 19e7f01c: 17, 46, 55 (Sabe and Fenn), 59, 61, 62 and 51's shot.
- **37: fixed on lavapipe.** At AfterHarrier the whole party is in frame; the shield no longer fills a third.
- **39: fixed on lavapipe.** Ch9's followers walk with Rhen at Strand and RoadGate.
- **24: unchanged.** DockShore has a half-faded party member at the lens; DockEnd has no hero in frame.
  (`big25_rows37_39_24_spawns.jpg`)
- **Tally on big25:**
  - fixed on lavapipe: 34, 37, 38, 39, 46, 47, 51, 59, 63;
  - partly fixed: 17, 24, 54, 55, 58, 61, 66 (not re-walked);
  - open: 21 (not reachable here), 56, 62, 64 (big25 still has the boss-intro spike; see row 64).

## THE LEAD'S ASKS (14:09–16:26), answered on big25 @ 4b198810 (it contains big23 8fe3644b and big24 efe7fb10)
Pass or fail per check, each against the playtest fix:
- **(a) Battle return: PASS for random fights, FAIL for scripted fights.** The causeway, ferry and Ch6 returns (random)
  have 60–69 ms of black, with the fade clear by 738–766 ms; before (19e7f01c) they had 3.7–11.4 s. The scripted fights
  still reload cold: tideline 5.5 s, Oruvel scuttlers 2.8 s, and the Drownbell 4.0 s to Haluna. Row 74 is now partly
  fixed (integration-qa).
- **(b) Oruvel edges: PASS** on big23 and big25 (0 of 260 pushes off the deck; before, 215). **Oruvel boats: FAIL
  (partly).** 10 AABB pairs remain, and I viewed each one on lavapipe (`docs/kb/qa/cloud/pass6/row75_oruvel_overlap_views_big25.jpg`).
  Real clips: scale_hull × its deck, keel_hull and terrace_hull × their tucked decks, and the second outrigger under the
  two plank bridges. The first outrigger's boom rests on a deck edge (check it). The dive raft's are intended. Filed to
  env-art as **M3-ENV-1391** (on this branch).
- **(c) Rhen's run: PASS.** Before (19e7f01c, run 0.667 s), the front view swung open hands to face height. After (the
  jog, 0.733 s), the hands stay at waist to chest height and the stride and footplants hold. Before/after sheet:
  `docs/kb/qa/cloud/pass6/playtest_c_rhen_run_before_after_big25.jpg`.
- **(d) Encounter spacing: PASS** (31.0–52.0 s on big23 and big25; before, 6–30 s). About a third of the draws run 46–52 s.
- **New Game → the Prologue first: PASS.** From a fresh profile (an empty XDG_DATA_HOME, headless,
  `tools/gpu_bench/newgame_probe.tscn`), the title's New Game goes to prologue.tscn at 9.2 s, then
  ch01/oruvel_underway at 42.0 s, tapping through.
- The row walk had already run one job at a time (spawn_stills) before these asks arrived, and the suite remainder ran
  file by file. Both results are above.

## RE-RUN after "Merge lead/gate-big25" (integration @ 4b198810): playtest (a), (b) and (d)
Same probes and box, in a worktree of 4b198810 (LFS pulled, imported). The deltas against big23:
- **(a) Victory exit → field** (ms from Return; big23 → big25):

  | Fight | black | field in | fade clear | input live |
  |---|---|---|---|---|
  | causeway shore (random) | 3744 → **63** | 4067 → 397 | 4432 → **752** | 4438 → 755 |
  | Ch4 ferry (random) | 5497 → **60** | 5471 → 388 | 6158 → **738** | 6162 → 738 |
  | Ch6 ridge skippers (random) | 11354 → **69** | 10841 → 391 | 11907 → **766** | 11914 → 766 |
  | tideline (scripted) | 6130 → 5507 | 5310 → 4408 | 6679 → 6058 | 18524 → 17892 (the lines) |
  | Oruvel scuttlers (scripted) | 2795 → 2808 | 3085 → 3104 | 3471 → 3495 | 3471 → 3495 |
  | the Drownbell (scripted) | 14752 → 15361 | 4371 → 4031 | 5638 → 5513 | B11 → Ch4 |

  **Random fights now meet the ≤ 1 s target** (99989c2b keeps the field resident). **Scripted fights still reload the
  zone cold: 2.8–5.5 s of black.** Row 74 is now partly fixed (owner integration-qa: extend the resident return to
  scripted fights, at least the tideline and the scuttlers). The hero still moves about 0.3 s before the fade clears.
- **(b) Oruvel:** edges 0 of 260 off the deck (unchanged, fixed); boat/dock AABB overlaps 10 pairs (unchanged).
- **(d) Encounter breather:** unchanged from big23 (31.0–52.0 s).

MERGE-READY @ the head of qa/cloud-pass6: QA docs and tools only (act1_gpu_qa.md with pass 6 and rows 74–78, the cloud-qa
log, the probes, docs/kb/qa/cloud/pass6). Checks: validate_data and taskboard ok; gdlint/gdformat on the probes clean; the
tools suite was partial (see above). No game code or baselines.

### Full Godot suite on 19e7f01c (non-blocking), with godot_failures
`godot --headless --path . res://tests/run_tests.tscn`, one pass on 19e7f01c. The box's memory cgroup OOM-killed it at about
3430 tests, in test_qa_threads' Act II report. The 12 files it hadn't reached were run one by one with `--filter`, all green
except test_battle_lineup. This container first had LFS pointers for the 193 .ogg files: `git lfs pull` works here, the
host is reachable. So the audio reds were re-run on big23 with LFS content.

godot_failures (8 files red on 19e7f01c):
| Test | Red on 19e7f01c | big23 | Class | Owner |
|---|---|---|---|---|
| test_battle_act1_ability_vfx::test_every_act_one_skill_has_its_own_effect (swell the_seven, farewell_tide…) | yes | red | known since big21 | battle-presentation, act1-chapters |
| test_battle_act2_ability_vfx::test_every_act_two_foe_skill_has_its_own_effect (conduit_crawler brush_jab, crawler_mend…) | yes | red | known (big22 branch content) | act1-chapters, battle-presentation |
| test_qa_threads::test_every_thread_plays_through_clean | yes | not re-run | known (big22: the Act II objectives vs the Ch10–13 threads) | ui, act1-chapters |
| test_battle_audio::test_a_fire_hit_plays_the_fire_sound | yes | **green with LFS** | environment: LFS pointers | — |
| test_battle_stings::test_every_row_resolves_and_imports | yes | **green with LFS** | environment: LFS pointers | — |
| test_music_transitions::test_every_act1_cue_has_a_beat_grid_or_is_free | yes | **green with LFS** | environment: LFS pointers | — |
| test_post_import::test_every_glb_import_runs_its_category_script | yes | red | **new** | env-art-b: 40 `assets/environments/kits/haluna/*.glb.import` files (the Act II kit pieces from M4-A2P-043 9b2f4e2f and later: archive_*, sanctum_*, court_*, hm_*, bridal_barge_*…) have an empty `import_script/path` (they want haluna_kit_post_import.gd). slice-polish / env-art: `assets/cutscene/ch01/oruvel_seabed.glb` belongs to no import category. |
| test_battle_lineup::test_no_encounter_opens_with_overlapping_fighters | yes | red | **new** | creatures-b, act1-chapters: ch11_lamp_engine opens with lamp_engine_1 2.49 and 2.55 m from conduit_crawler_2 and _3; it needs 2.74 m |

### Checks on this branch
- **Ran:**
  - validate_data: 0 errors, 0 warnings;
  - taskboard --check: ok;
  - gdlint and gdformat on the new probes: clean;
  - the banned-terms grep over the diff: 0 hits.
- **Partly ran:** the tools suite (`run_tool_tests.py -j 4`) hit my 15-minute cap at 44 of about 200 units, all 44 green.
  test_rig_integrity alone is 454 s here. No tools test covers `tools/gpu_bench`.
- **Skipped:** the screenshot gate. QA renders aren't baselines, and no game code changed.

### LEAD-ASKs
- LEAD-ASK: act1_gpu_qa.md isn't on the integration branch, only on gpu/act1-qa-5 and now qa/cloud-pass6, which carries
  the pass-6 notes and rows 74–78. Merge it from here when the PC is back? Its copy has nothing newer.
- LEAD-ASK: route the two new suite reds (test_post_import → env-art-b and slice-polish; test_battle_lineup →
  creatures-b and act1-chapters) and the five playtest rows (74–78) to their owners.
- LEAD-ASK: the encounter breather on big23 runs 31–52 s; about a third of the draws are over 45 s. Is 45 s a hard cap?

### PC-QUEUE (real-GPU only)
- The GPU look of the rows lavapipe calls fixed (34, 38, 46, 47, 51, 59), and the material and light rows (17's arcs, 62,
  63, 71).
- Row 64 re-timed on big23 at High: whether visible frame 1's spike shows under the lifting fade.
- Row 21 by hand.

### Gotchas (this box)
- 4 vCPU, a 15 GB memory cgroup: the suite grows to about 5 GB, a lavapipe slice_sweep walk to 5–7 GB, and an import is
  about 1 GB. Run one heavy job at a time, or the OOM killer takes them.
- slice_sweep's dwell needs at least 60 frames, and at lavapipe's ~2 s per frame that's 2 minutes a spawn. A row
  `still_every` at or under a frame's time never ends the dwell, because a still's frame isn't counted. Use spawn_stills.
- slice_sweep hangs headless: its dwell awaits frame_post_draw.
- In 4.6.3 an AnimationPlayer paused after a seek ignores later seeks (run_cycle_probe samples the tracks itself).

### Exact next step
After the next "Merge lead/gate-bigN" on claude/new-session-mj8c3c, run these in a worktree of it, with the probes copied
in and `git lfs pull` plus an import first:
- (a) `return_probe.tscn`;
- (b) `dock_probe.tscn -- --out=<dir>`, then `dock_overlaps.py <dir>/meshes.json`;
- (d) `encounter_gap_probe.tscn`.

Then report the deltas against the big32 numbers above (the latest re-run). The playthrough smoke: `tools/gpu_bench/playthrough_probe.tscn` from an empty XDG_DATA_HOME.

Files touched: `tools/gpu_bench/{return_probe,dock_probe,run_cycle_probe,encounter_gap_probe,spawn_stills,fight_entry_probe}.gd/.tscn`,
`tools/gpu_bench/dock_overlaps.py` and `act1_walk_pass6.json`/`act1_walk_row21.json`. Brought from gpu/act1-qa-5:
`docs/kb/qa/act1_gpu_qa.md` and the `tools/gpu_bench` walk tools. Also `docs/kb/qa/cloud/pass6/*.jpg` and this log.
