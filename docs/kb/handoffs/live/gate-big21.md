# Gate session live log: big21

The cloud gate session (`session_01UPFyEAXofxWazWNnRTzFGJ`), on the Lead's rolling cadence (ADR 0205). It never writes
or approves baselines. One log per batch.

## big21

GATE-BUILT big21 @ e3e7deb1 (branch `lead/gate-big21`), from `lead/gate-big20` @ 597f7bf7. big20 is not merged yet (its two
batch reds wait on the Lead), so big21 carries big20 and its resolutions, plus:
1. claude/new-session-mj8c3c @ 3a5759ad: clean (the Lead's big19 approvals).
2. claude/env-art @ f3898456: **env-art and env-art-b both did M4-A2P-043 (Ansedra's dressing).** act2_tracks.md gives
   Ch13–16 dressing to env-art-b, so ours (env-art-b's dressing, environment, generator, its test and the task's
   `review` state) was kept over env-art's "in progress" version. env-art's other new kit pieces came in.
3. claude/env-art-b @ c46d29e4: the Haluna `kit_manifest.json` key-merged again (no clash, sorted); ownership.md both.
   shots.json: `slice_end_card_voice` stays removed (m2-slice's M3-CIN-1233 dropped the mid-Act I card).
4. claude/characters @ 7fbe446f, claude/creatures @ 4f53a834: clean.
5. claude/creatures-b @ 10490ad9: `game/data/import/creatures.json`'s `assets` list merged as a 3-way set (51); ours'
   `lods` and `_about` changes kept.
6. claude/battle-presentation @ 27dbad77: union only.
7. claude/act1-chapters @ 03b3d90c: `enemies.json` block-merged. **The four Act II bosses' stats and phases take
   act1-chapters' numbers** (the Lead, 05:51: chapters tunes the numbers on Combat's definition; act2_tracks.md gives
   chapters the boss tables). `creatures.json`: the vowbound_pending keys dropped (act1-chapters' 45faae4e: the rows exist).
8. claude/ui @ 391059f3: `codex.json`: ui's `keth`, `conclave`, `malcor_venn` and `heresy` (ui owns the codex) replace the
   story track's `conclave` and `malcor_venn`.
9. claude/hero-integration @ e7af4147: M3-CIN-1251's task took theirs (done by integration-qa, `review`).
10. claude/audio @ 6e3530f0: union only.
11. claude/act2-plan @ a766bdc2: `codex.json` held `farewell_tide` and `name_shells` twice. Kept act2-plan's (unlocked by
    `ch10_tide_witnessed`, set by three Ch10 dialogues); the other copy unlocked on `ch10_farewell_tide_seen`, which
    nothing sets. `test_codex.gd`'s pinned world total is the merged codex's 19 (ours said 17, theirs 16).
- Not merged: claude/m2-slice (nothing new since big20's seabed fix), claude/menus, the stale branches.

Merge fallout fixes:
- 17cd2bea: ENEMY_ and LORE_ for the Mangrove Drowner, Lamp Engine, Avalanche Ram and Wakefin were in strings.csv (the
  Lead's PROVISIONAL rows, 1dbfed6d) and in ch10/11/12/15.csv (act2-plan's bestiary pass M4-A2P-009); the story track's
  rows stay. PROVENANCE: avalanche_ram's and rime_urchin's `ice.tres` rows (deleted files, ADR 0015) out.
- e3e7deb1: kesh's `vowbound_pending` dropped (validate_data: vowbound.json has its row).

Checks at the build: validate_data 0/0; taskboard ok; dlgc 0/0; gdlint and gdformat clean; no duplicate loc keys, codex
ids, PROVENANCE rows or shot ids (669 shots); no conflict markers.
