# Live log: m2-slice environment

Feature track for the M2 vertical slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`, started from `claude/first-playable` 67984ce. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Now
- **Done, in review:** M2-FP-10, the dialogue key light. The PC's GPU check passed. Its two follow-ups are done: H05/H06 `key_pitch_deg` 30, and the key layer moved 20 → 19 (20 is `UndertowHalfRes.BODY_LAYER`), with a guard test.
- **Done, in review:** M2-FP-15, B11 "The dock at night" (the Drownbell victory → Haluna at night under a stand-in light → B11 → the end card; night blessings for the barks). It doesn't wait for M2-ENV-02 any more: its criteria allow the stand-in.
- **Done, in review:** M2-FP-18, Cutscene A/B facial animation (seeded blinks, a blink on each expression change, text-driven visemes on Asha's viseme shapes; checked on lavapipe).
- **Waiting:** M2-FP-17 (the Drownbell with the real Vowbound call, filed by the Lead for this track) depends on M2-CMB-05, which is still todo on the integration branch.
- **Done, in review:** M2-FP-16, the Shell Shrine trial (B07). The puzzle rules are headless and data-driven; the room is a greybox built from JSON. The thread now runs the causeway head → low tide → the trial → Cutscene B. Filed M2-ENV-03 (the shrine kit) and M2-AUD-01 (the trial audio).
- **Done, in review:** M2-FP-13, Haluna by day (B02 Neme's table after the tideline win, B03's four fragments overheard on walk-past, B05 Low tide). Filed M2-FP-14, M2-FP-15, M2-ENV-02 and M2-UI-06.
- **Done, in review:** M2-FP-11 (the integration branch's task: zone suns back to bias 1.0, FlowRouting serving waiters in turn). I took it because it lives in my scenes and pairs with FP-10. The file is taken verbatim from the integration branch, so it should merge clean, apart from my status and notes.
- **Done, in review:** M1-UI-10, the Graphics settings page (title → Settings). **`boot_title` baseline re-approved** for the new row; no other shot drifts.
- **Done, in review:** M2-FP-12, the Drownbell at slice quality (`BattleBossStatus` read-out, toll chip text, retry test). Reviewer ui, because of the one-line `timeline_chip.gd` change.
- **In progress:** nothing.
- **Un-pushed state:** none.
- **Integration merge:** merged `origin/claude/undertow-lead-handoff-423ixt` at cae2e16 (which carries the first-playable merge, M2-CMB-04 Vowbound and review-sweep-P) into this branch. Conflicts: the FP-10 and FP-11 task files (took this branch's copies; the integration side was unchanged) and `strings.csv` (`merge_union.py`, no duplicate keys). Renumbered on the merge: my shop/inn request **M2-UI-05 → M2-UI-06** (the integration branch's UI-05 is the Vowbound HUD), and my Drownbell handoff **combat-9 → combat-11**. Gates on the merged tree: lint and format, coverage over the full suite (1305 tests; battle 99.95%, progression 96.52%), `sim.py --check` passing every band, tools unittest OK.

## For the Lead (send_message to the Lead is refused: elevated_session_untrusted_device, so this file is the report)
- **I CLAIMED M2-CMB-05 (Combat's ADR 0027 amendments A1–A3 and the sim call rule) on this branch.** It was unclaimed and blocks M2-FP-17 (this track's Drownbell) and UI-05. If you've given it to someone else, tell me through this file's history or the task file and I'll stop.
- **Two queue items remain after Haluna** (5, the Shell Shrine trial; 6, the first Vowbound and Cutscene A/B facial animation). Please queue more when you can. New requests for other roles: M2-ENV-02 (Haluna night light, which blocks B11) and M2-UI-06 (shop and inn).
- **Task-id note:** my Drownbell task was renumbered FP-11 → **FP-12**, because the integration branch's FP-11 came first.
- **M2-FP-12 is review-ready** (see its task file). Also: **c818bc8 and ef563ee carry a test leak** (a key-light test didn't free its zone, failing 7 field/Haluna/save tests in a full run). The FP-12 push (09db8b2) fixes it, so merge the branch head, never c818bc8 alone.
- **M2-FP-10 is review-ready at c818bc8.** Please ask the PC GPU session to check Cutscene A (H05/H06): nose and mouth-corner shadows with the key on, the key's cost (a second shadowed directional light shares the directional atlas), and whether Haluna's `face_key_shadow_normal_bias` 3.0 on the zone sun can return to 1.0 (RND-20 S1).

## Exact next step
**The standing queue is done apart from blocked items.**
- M2-FP-17 waits on M2-CMB-05. When CMB-05 merges: merge the integration branch, replace `call_ilun` with `engine.summon(&"ilun")`, add the "call into the flood" sim policy, and re-band.
- M2-FP-14 (B04) waits on the wake-shell wall being reachable.
- M2-FP-15 (B11) is done with the stand-in night; swap in M2-ENV-02's light when it lands.
Lead: please queue more slice work.

## Queue
1. ~~M2-FP-10 dialogue key light~~ (review)
2. ~~Drownbell follow-ups (M2-FP-06)~~ → M2-FP-12 (review)
3. ~~M2-FP-05 and M1-ARC-15 follow-ups; M1-UI-10~~: FP-05 and ARC-15 had no open review items (their known gaps are documented). M1-UI-10 is done (review).
4. Haluna at vertical-slice quality: M2-FP-13 in review; M2-FP-14 (B04) next, M2-FP-15 (B11) in review (stand-in night)
5. ~~Shell Shrine temple trial~~: M2-FP-16 (review)
6. First Vowbound → M2-FP-17 (blocked on M2-CMB-05; the engine side is Combat's M2-CMB-04/05, ADR 0027); Cutscene A/B faces → M2-FP-18 (review)

## Setup notes
- `fetch_godot.py` doesn't put Godot on PATH: `ln -s /root/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`).
- `pip install -r tools/requirements.txt` for gdlint/gdformat.

## History
- 2026-10-24: M2-FP-15 done (B11). Gates: dlgc and `--check`, validate_data, lint and format, the full Godot suite (1316 green). I checked a lavapipe render of the night stand-in by eye.
- 2026-10-24: merged the integration branch (763faeb), then finished the PC's FP-10 follow-ups (pitch 30 on H05/H06; key layer 19 with a guard test). Godot key_light 9, test_haluna_zone 6.
- 2026-10-24: M2-FP-18 done (faces). Gates: lint and format, the full Godot suite (1311 green), validate_data, taskboard --check. I checked five lavapipe renders of Asha's face by eye.
- 2026-10-24: M2-FP-16 done (the Shell Shrine trial). Gates: dlgc, validate_data, lint and format, Godot shell_shrine 11, fp_ 22 and haluna 13, plus the full Godot suite (1280 green) and tools unittest (452 OK). I checked three lavapipe renders by eye.
- 2026-10-24: M2-FP-13 done. Gates: dlgc and `--check`; validate_data; lint and format; the full Godot suite, 1269 green. Filed FP-14, FP-15, ENV-02 and UI-05.
- 2026-10-24: M2-FP-11 done (bias and FlowRouting). Gates: lint and format; Godot flow_routing 4, fp_ 22, haluna 8. Renumbered the Drownbell task to FP-12.
- 2026-10-24: M1-UI-10 done. Gates: gdlint and gdformat; the full Godot suite, 1263 green; tools unittest 448 OK; validate_data and taskboard --check clean; `HYMN_SHOTS=boot_title` captured and re-approved after a side-by-side view. No coverage step (no battle or progression code since the last run).
- 2026-10-24: M2-FP-12 done. Gates: gdlint and gdformat over game and tests; the full Godot suite under coverage (1257 tests; battle 99.95%, progression 96.52%, within baseline); `sim.py --check` passes every band; validate_data and taskboard --check are clean. I checked two lavapipe renders by eye; no manifest shot covers a boss fight.
- 2026-10-23: setup; claimed and finished M2-FP-10. Gates: gdlint/gdformat, `--filter=cutscene` (26), `--filter=key_light` (8), `--filter=haluna` (8), validate_data, taskboard --check. No game/battle or progression code touched (no coverage step), no skills or encounters (no sim), no screenshot covers cutscenes (no shots).
