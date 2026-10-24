# Live log: m2-slice environment

Feature track for the M2 vertical slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`, started from `claude/first-playable` 67984ce. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Now
- **Done:** the slice playthrough pass (Lead item f, the last). PLAYTEST.md is updated: step 7 sent testers the wrong way, and the night, Osu and the field menu are now described. Filed friction tasks **M2-FP-20** (the causeway head is silent before the first save) and **M2-FP-21** (nothing signposts that the causeway head ends Haluna's day). Handoff cinematics-7. **The standing queue and the top-up are both done; everything is in review. Lead: please queue more.**
- **Done, in review:** M2-FP-19 (Lead item e). The field menu already works in Haluna through UI-04's FieldController hook. Asha and Toma now join after Cutscene A (`party_ids` written from data), so its Heroes page lists the real party.
- **Done, in review:** M2-ENV-02, Haluna at night: a moon, a star sky, sea-glow 0.12, oil lanterns under every house eave, and the new `haluna_h10_dock_night` shot with a baseline. B11 now uses it, so the FP-15 stand-in is gone. **Also fixed a foliage shader bug:** every omni light lit all foliage at 35% at any distance. All five noon shots still pass. **PC: please measure the night's GPU cost at H10.** Handoff environment-2.
- **Done, in review:** M2-ENV-01. The Haluna world moved out of `_tests/` into `game/levels/ch02/haluna/haluna_dressing.tscn`, and the mood test is now a thin wrapper that adds the cameras. The five haluna shots are byte-identical. **PC/Rendering: `haluna_noon_environment.tres` is now at `game/levels/ch02/haluna/`.** Handoff environment-1.
- **Done, in review:** M2-FP-14, B04 "Pila's Granddaughter": Osu at the causeway head on a greybox stand-in wake-shell wall, because the real piece is out of reach (filed **M2-ENV-04**). Also the B02 bag insert and the H03 lintel-gull look-at. Handoff cinematics-6.
- **Done, in review:** M2-FP-10, the dialogue key light. The PC's GPU check passed. Its two follow-ups are done: H05/H06 `key_pitch_deg` 30, and the key layer moved 20 → 19 (20 is `UndertowHalfRes.BODY_LAYER`), with a guard test.
- **Done, in review:** M2-FP-15, B11 "The dock at night" (the Drownbell victory → Haluna at night under a stand-in light → B11 → the end card; night blessings for the barks). It doesn't wait for M2-ENV-02 any more: its criteria allow the stand-in.
- **Done, in review:** M2-FP-18, Cutscene A/B facial animation (seeded blinks, a blink on each expression change, text-driven visemes on Asha's viseme shapes; checked on lavapipe).
- **Done, in review:** M2-CMB-05 (ADR 0027 A1–A3, the sim call rule, the `sandbox_vowbound` masher band of ≤40%, measured 37.0%) and M2-FP-17 (the Drownbell's bands now use the real Ilun call; the bell answers a lone absorber with Hood Slam; `flood_call` wins 38.7% with no timeouts). Handoff combat-12. The live game keeps `call_ilun` until M2-UI-05's Call command.
- **Done, in review:** M2-FP-16, the Shell Shrine trial (B07). The puzzle rules are headless and data-driven; the room is a greybox built from JSON. The thread now runs the causeway head → low tide → the trial → Cutscene B. Filed M2-ENV-03 (the shrine kit) and M2-AUD-01 (the trial audio).
- **Done, in review:** M2-FP-13, Haluna by day (B02 Neme's table after the tideline win, B03's four fragments overheard on walk-past, B05 Low tide). Filed M2-FP-14, M2-FP-15, M2-ENV-02 and M2-UI-06.
- **Done, in review:** M2-FP-11 (the integration branch's task: zone suns back to bias 1.0, FlowRouting serving waiters in turn). I took it because it lives in my scenes and pairs with FP-10. The file is taken verbatim from the integration branch, so it should merge clean, apart from my status and notes.
- **Done, in review:** M1-UI-10, the Graphics settings page (title → Settings). **`boot_title` baseline re-approved** for the new row; no other shot drifts.
- **Done, in review:** M2-FP-12, the Drownbell at slice quality (`BattleBossStatus` read-out, toll chip text, retry test). Reviewer ui, because of the one-line `timeline_chip.gd` change.
- **In progress:** nothing.
- **Un-pushed state:** none.
- **Integration merge:** merged `origin/claude/undertow-lead-handoff-423ixt` at cae2e16 (which carries the first-playable merge, M2-CMB-04 Vowbound and review-sweep-P) into this branch. Conflicts: the FP-10 and FP-11 task files (took this branch's copies; the integration side was unchanged) and `strings.csv` (`merge_union.py`, no duplicate keys). Renumbered on the merge: my shop/inn request **M2-UI-05 → M2-UI-06** (the integration branch's UI-05 is the Vowbound HUD), and my Drownbell handoff **combat-9 → combat-11**. Gates on the merged tree: lint and format, coverage over the full suite (1305 tests; battle 99.95%, progression 96.52%), `sim.py --check` passing every band, tools unittest OK.

## For the Lead (send_message to the Lead is refused: elevated_session_untrusted_device, so this file is the report)
- **2026-10-24 ~03:10: your six messages from 00:00–00:40 reached me only now.** Everything in them is done (merges, renumbers, FP-11, and the first Vowbound as CMB-05/FP-17). Working through your top-up now: ENV-01 is done (review); ENV-02, FP-19 and the playthrough pass are all done. The queue is empty.
- **I CLAIMED M2-CMB-05 (Combat's ADR 0027 amendments A1–A3 and the sim call rule) on this branch.** It was unclaimed and blocks M2-FP-17 (this track's Drownbell) and UI-05. If you've given it to someone else, tell me through this file's history or the task file and I'll stop.
- **Two queue items remain after Haluna** (5, the Shell Shrine trial; 6, the first Vowbound and Cutscene A/B facial animation). Please queue more when you can. New requests for other roles: M2-ENV-02 (Haluna night light, which blocks B11) and M2-UI-06 (shop and inn).
- **Task-id note:** my Drownbell task was renumbered FP-11 → **FP-12**, because the integration branch's FP-11 came first.
- **M2-FP-12 is review-ready** (see its task file). Also: **c818bc8 and ef563ee carry a test leak** (a key-light test didn't free its zone, failing 7 field/Haluna/save tests in a full run). The FP-12 push (09db8b2) fixes it, so merge the branch head, never c818bc8 alone.
- **M2-FP-10 is review-ready at c818bc8.** Please ask the PC GPU session to check Cutscene A (H05/H06): nose and mouth-corner shadows with the key on, the key's cost (a second shadowed directional light shares the directional atlas), and whether Haluna's `face_key_shadow_normal_bias` 3.0 on the zone sun can return to 1.0 (RND-20 S1).

## Exact next step
**The standing queue is done.** Every item is in review.
- M2-CMB-05 and M2-FP-17 are in review. When M2-UI-05 (the Call command) lands, remove `call_ilun` from Asha and from the `ch03_drownbell` loadout's `retire_skills`, then re-run `sim.py --check`.
- M2-FP-14 is in review. When M2-ENV-04 lands, swap the stand-in wall for the real piece (handoff cinematics-6).
- M2-FP-15 (B11) is done with the stand-in night; swap in M2-ENV-02's light when it lands.
Lead: please queue more slice work.

## Queue
1. ~~M2-FP-10 dialogue key light~~ (review)
2. ~~Drownbell follow-ups (M2-FP-06)~~ → M2-FP-12 (review)
3. ~~M2-FP-05 and M1-ARC-15 follow-ups; M1-UI-10~~: FP-05 and ARC-15 had no open review items (their known gaps are documented). M1-UI-10 is done (review).
4. ~~Haluna at vertical-slice quality~~: M2-FP-13, M2-FP-14 (B04) and M2-FP-15 (B11) in review
5. ~~Shell Shrine temple trial~~: M2-FP-16 (review)
6. ~~First Vowbound~~ → M2-CMB-05 and M2-FP-17 (review); Cutscene A/B faces → M2-FP-18 (review)

## Setup notes
- `fetch_godot.py` doesn't put Godot on PATH: `ln -s /root/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`).
- `pip install -r tools/requirements.txt` for gdlint/gdformat.

## History
- 2026-10-24: playthrough pass done (headless thread green; PLAYTEST.md fixed; FP-20 and FP-21 filed). Gates: validate_data, taskboard --check (docs and tasks only after FP-19's full run).
- 2026-10-24: M2-FP-19 done. Gates: lint and format, validate_data, taskboard --check, the full Godot suite (1366 green).
- 2026-10-24: M2-ENV-02 done. Gates: lint and format, validate_data, taskboard --check, the full Godot suite (1363 green), tools unittest (488 OK), and the six haluna shots (noon passes against its baselines; H10 approved as new).
- 2026-10-24: merged the integration branch (a514c06, RND-23/24): clean, 1359 green. M2-ENV-01 done; gates: lint and format, validate_data, taskboard --check, the full Godot suite (1359 green), and the five haluna shots byte-identical before and after.
- 2026-10-24: M2-FP-14 done (B04, the B02 insert, H03). Gates: lint and format, dlgc --check, validate_data, taskboard --check, the full Godot suite (1355 green). I checked four lavapipe renders by eye. No coverage (no battle code), no shots (none render this scene).
- 2026-10-24: merged the integration branch (e7270ca: RND-01 undertow compute, the GPU key-light check, the Lead's merge of this branch). Clean, no conflicts. Gates on the merged tree: validate_data, taskboard --check, lint and format, the full Godot suite (1347 green).
- 2026-10-24: M2-CMB-05 and M2-FP-17 done. Gates: lint and format, validate_data, taskboard --check, the full Godot suite under coverage (1337 tests; battle 99.95%, progression 96.52%), `sim.py --check` passing every band, tools unittest 483 OK. No shots (none cover a boss fight).
- 2026-10-24: M2-FP-15 done (B11). Gates: dlgc and `--check`, validate_data, lint and format, the full Godot suite (1316 green). I checked a lavapipe render of the night stand-in by eye.
- 2026-10-24: merged the integration branch (763faeb), then finished the PC's FP-10 follow-ups (pitch 30 on H05/H06; key layer 19 with a guard test). Godot key_light 9, test_haluna_zone 6.
- 2026-10-24: M2-FP-18 done (faces). Gates: lint and format, the full Godot suite (1311 green), validate_data, taskboard --check. I checked five lavapipe renders of Asha's face by eye.
- 2026-10-24: M2-FP-16 done (the Shell Shrine trial). Gates: dlgc, validate_data, lint and format, Godot shell_shrine 11, fp_ 22 and haluna 13, plus the full Godot suite (1280 green) and tools unittest (452 OK). I checked three lavapipe renders by eye.
- 2026-10-24: M2-FP-13 done. Gates: dlgc and `--check`; validate_data; lint and format; the full Godot suite, 1269 green. Filed FP-14, FP-15, ENV-02 and UI-05.
- 2026-10-24: M2-FP-11 done (bias and FlowRouting). Gates: lint and format; Godot flow_routing 4, fp_ 22, haluna 8. Renumbered the Drownbell task to FP-12.
- 2026-10-24: M1-UI-10 done. Gates: gdlint and gdformat; the full Godot suite, 1263 green; tools unittest 448 OK; validate_data and taskboard --check clean; `HYMN_SHOTS=boot_title` captured and re-approved after a side-by-side view. No coverage step (no battle or progression code since the last run).
- 2026-10-24: M2-FP-12 done. Gates: gdlint and gdformat over game and tests; the full Godot suite under coverage (1257 tests; battle 99.95%, progression 96.52%, within baseline); `sim.py --check` passes every band; validate_data and taskboard --check are clean. I checked two lavapipe renders by eye; no manifest shot covers a boss fight.
- 2026-10-23: setup; claimed and finished M2-FP-10. Gates: gdlint/gdformat, `--filter=cutscene` (26), `--filter=key_light` (8), `--filter=haluna` (8), validate_data, taskboard --check. No game/battle or progression code touched (no coverage step), no skills or encounters (no sim), no screenshot covers cutscenes (no shots).
