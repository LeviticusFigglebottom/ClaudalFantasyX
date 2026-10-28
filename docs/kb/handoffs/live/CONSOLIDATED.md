# CONSOLIDATED HANDOFF: start here

**Handover snapshot:** 2026-10-25, written by the outgoing Lead (cloud `session_019iimsngAgPLEram1wcbLpE`) for a **new account with no prior knowledge**. The previous version is `CONSOLIDATED-history-2026-10-24.md`; older history is in git.

> **2026-10-25 (new Lead, `session_018aiGwGLGkxsnMnu8VfCu1m`): the integration branch is now `claude/undertow-lead-handoff-ze8rrn`** (fast-forwarded from `claude/undertow-lead-handoff-423ixt` @ 73a4c3fa, which is now frozen history). Every merge, gate base and track sync uses the new branch. Read "integration branch" below as `-ze8rrn`.

**Fetch every branch first** (`git fetch origin`). Each environment's newest live log is on its own branch: `docs/kb/handoffs/live/<env>.md`, under the "STATE AT HANDOVER (2026-10-25)" section.

## 0. Read these, in this order
1. [`CLAUDE.md`](../../../CLAUDE.md): the binding rules. They cover pillars, IP guardrails, coding standards, gate scope, claiming work, ownership, live logs and shared-machine etiquette.
2. [`SPEC.md`](../../../SPEC.md) **v1.4**: the brief. Only the Lead edits it, and every change needs an ADR plus a version note.
3. This file, then [`lead-cloud.md`](lead-cloud.md), then each environment's live log on its branch.
4. [`docs/kb/STATUS.md`](../../STATUS.md), and `python3 tools/taskboard.py` for the task board.
5. ADR titles in [`docs/kb/decisions/`](../../decisions/) (0001–0038). These matter most:
   - 0009: lavapipe baselines.
   - 0029 and 0037: hitch budgets, including the cold first-launch exception.
   - 0032: port to Godot 4.7.2 after the M2 review.
   - 0034–0036.
   - 0038: the timeline predicts each foe's real tempo.

## 1. The project and where it stands
- **What it is:** *Hymn of the Undertow*, an original, cinematic CTB (conditional turn-based) RPG in **Godot 4.6.3**:
  - Forward+ renderer, typed GDScript, data-driven JSON under game/data/;
  - a headless, deterministic battle engine;
  - every asset reproducible from source (Blender scripts under assets_src/).
- **IP guardrail:** it's inspired in tone only by a classic 2001 JRPG. Keep the strictness: the banned terms in `tools/banned_terms.txt` are grepped, and there are no pixel-copied UI, names, music or spell-tier suffixes.
- **M1, the prototypes:** effectively done. The M1 review waits on the human: their music listen and the Asha face direction.
- **M2, the vertical slice:** feature-complete on the integration branch, being polished from the human's playtests. The M2 review is a **blocking human review** (SPEC §16 Q7). Reviews never block work, so M3 runs in parallel.
- **M3, Act I:** under way:
  - Ch1 and Ch4–Ch9 as **greybox** chapters (m2-slice);
  - 27 Act I creatures;
  - Act I kits (env-art);
  - the Reefball engine (M3-RBL-01) and its look (PC).
- **The intro thread the human plays:** title → prologue → Haluna beach (the cutscene) → playable Haluna → B06 Saltgrass Causeway → Shell Shrine trial → the Drownbell boss → B12 end card.
  - Act I sits behind `first_playable.json` switches (`prologue.next_location`, `end_card.next_location`), left EMPTY (back to the title) until the human signs off M2.
  - The F8 debug chapter select reaches Act I.

## 2. Branches (repo `LeviticusFigglebottom/ClaudalFantasyX`)
| Branch | State at handover |
|---|---|
| **`claude/undertow-lead-handoff-423ixt`** | **The integration branch, i.e. the real "main".** Head ≈ 6c6e5514 plus doc commits. Every merge lands here, behind a passing gate. |
| `main` | **Stale** since the old account. Fast-forward it to the integration branch only with the human's explicit permission. |
| **`lead/gate-big9`** (ae4666e0) | **The next batch, merged but NOT yet gated.** It is big8 plus the integration head plus: m2-slice's newest (the prologue colour fix for "everyone is still here", CutsceneMotion eased turns and walks M2-FP-29, Ch8), **hero-integration** (the real heroes in field and battle), and the newest battle-presentation, characters, creatures, menus, ui, env-art and audio. Last local `ci_local.sh` run: passed (the Godot suite, coverage including reefball 100%, the boot smoke, sim --check). An earlier tool-test run failed `test_hero_clips`, so re-check it. **FIRST JOB for the new Lead: gate it on the PC runner, view the drifted shots, merge.** |
| `claude/m2-slice`, `claude/ui`, `claude/menus`, `claude/battle-presentation`, `claude/characters`, `claude/creatures`, `claude/env-art`, `claude/audio`, `claude/hero-integration` | The track branches. Each has a "STATE AT HANDOVER" section in its live log. Each has moved since big9 was cut, so a big10 pass merges their heads. |
| `gpu/*` | The PC's branches, one per item. Merged: everything up to RND-19, 910, NIT-05, 901 and 902 (the runner), M3-RND-01/04/05. Check `pc-gpu.md` for any unmerged. |
| `claude/gate-runner-a`, `claude/gate-runner-b` | Old cloud screenshot-shard runners; reports only. Superseded by the PC runner. |
| `claude/first-playable`, `claude/new-session-mj8c3c` | Frozen history; don't merge into them. |
| `lead/*` (other), `worktree-agent-*` | Local to the old Lead's container. Everything of value is merged or pushed. |

## 3. Environments at handover, with recommendations for the new account
| Old env | Branch | Did | Recommendation |
|---|---|---|---|
| Lead (cloud) | integration | Orchestration, merges, gates, decisions, local agents | Keep. The new Lead takes the role. |
| **pc-gpu** (Remote Control on the human's PC) | `gpu/*` | GPU perf and look-dev, hardware QA, and the **gate runner** (WSL2) | Keep, as the new empty Remote Control session the human provides. It is THE gate runner: about 16 min for tests, about 27 min for screenshots (2 shards), about 12 min for Blender `--all`, against 2–3 h on a 4-CPU cloud container. |
| m2-slice | `claude/m2-slice` | Story flow, zones, cutscenes, encounters; the M2 slice plus M3 Act I greybox (Ch1, Ch4–Ch9) | **The bottleneck: split it into two.** (a) **slice-polish**: the M2 slice the human plays, the prologue and cutscenes, encounters, playtest fixes. (b) **act1-chapters**: the Act I chapters (Ch8 and Ch9 onward), the greybox-to-final swaps with env-art. |
| ui | `claude/ui` | The HUD, objectives and map, prompts, title, tips, dialogue box, settings, input parity, pseudo-loc, resolutions | **Merge menus into it**: one "ui-menus" track. They share the field-menu shell and constantly merge each other. |
| menus | `claude/menus` | Lattice, Equip, Items, Status, Formation, portraits | → folded into ui-menus. |
| battle-presentation | `claude/battle-presentation` | Choreography, camera, specials, arenas wiring, KO, boss intros, battle feel | Keep. |
| characters | `claude/characters` | Hero and villager models, faces, clips (Blender) | Keep. Its focus is hero battle and locomotion clips plus M2-CHR-11. |
| **hero-integration** | `claude/hero-integration` | The real heroes in field and battle: locomotion blend, eased turns, followers | Keep until heroes and villagers are alive everywhere, then fold into characters. |
| creatures | `claude/creatures` | 27+ creature models, clips, villager life, wildlife | Keep while Act I creature, battle polish and villager life remain. It often idles, so give it long queues. |
| env-art | `claude/env-art` | Final kits (Haluna, causeway, shrine, arenas, Act I zones) | Keep. Heavy and productive. |
| audio | `claude/audio` | Synthesised original music and SFX, voices (blips), mix | Keep, but it idles often: always give it a long queue. |
| gate-runner-a/b (cloud) | n/a | Screenshot shards | **Retire.** The PC runner replaces them; spin up cloud shard runners only if the PC is busy benchmarking. |

**Recommended setup for the new account:** Lead (cloud) + pc-gpu (the empty Remote Control session) + slice-polish + act1-chapters + ui-menus + battle-presentation + characters + hero-integration + creatures + env-art + audio. That's 10 sessions plus the Lead. The usage limits were hit several times at this scale; if limits bite, pause creatures and audio first, then act1-chapters.

## 2-FOCUS. ACT I AT FINAL QUALITY FIRST (ADR 0041, the human's directive, 10-28 01:10)
- Every track works only on the game as played, from the title through Ch9, at final quality: no greybox, no stand-ins, no placeholders. Act II and later are paused, with their tasks blocked by ADR 0041.
- The work list is `docs/kb/qa/act1_final_inventory.md` plus `tools/placeholder_audit.py` (integration-qa).
- **New sessions (10-28):**
  - env-art-b `session_01F3vrUNt6trAMrjeYavaDNC` (claude/env-art-b): the Ch5–Ch9 zones and their arenas;
  - creatures-b `session_01F3vrUMszfxGn5bonYsSJxK` (claude/creatures-b): the Act I bosses and the Vowbound.
  - env-art keeps the Prologue–Ch4 zones and the shared kits; creatures keeps the regular enemies and the wildlife.
- **Ownership under ADR 0041 (Lead decision, 10-28 02:40):**
  - Act I dressing (the generated dressing, collision and layout json and their tools/act1 scripts): env-art for the Prologue–Ch4, env-art-b for Ch5–Ch9.
  - act1-chapters: encounters, NPC and trigger placement, cutscene staging and flow only. Its parallel Ch5–Ch9 dressing is dropped in favour of env-art-b's; act1-chapters merges env-art-b and keeps Ch4 plus its dressing test.
  - Inventory capsules: party → integration-qa; generic villagers → creatures (a villager generator); named NPCs → characters.
  - integration-qa runs an hourly TRIAL MERGE of every track branch and logs the conflicts.
- The account's seven-day usage is at its warning level, so no more sessions unless one is clearly the bottleneck.

## 2a. Merge state (new account)
- **10-27: big9 MERGED** (integration 3b7cbf5e). PC gate: Godot 2561/0, coverage and boot OK, Blender 40 identical + 11 M2-CHR-11 DIFFs (rhen, toma, 9 villagers), 281 shots with 48 re-approved after the Lead viewed them. The results are on `gpu/gate-big9-shots`.
- **10-27: big10 MERGED** (integration f5ec3bda). PC gate: Godot 2637/0, coverage and boot OK, Blender 20 identical + rhen/toma, 292 shots with 51 re-approved (37 identical to big9's; 14 viewed). It includes M3-BPR-404: the Hullgnaw, Drownbell and Matron intros now fit the boss.
- **10-27 ~21:15: big12 MERGED** (integration e930595c): 111 shots approved after viewing; Blender 28/28 identical; the PC's shrine GI rebake folded in. Open from viewing:
  - Iskarra (the prologue) reads greybox → env-art, FAST-TRACK;
  - Ilun (the Vowbound) is a teal capsule → creatures;
  - Asha's staff is missing in static views and her skirt holds a stiff bell → characters;
  - Ch9 road capsule and the dark strand → act1-chapters;
  - the dialogue box covers speakers on the beach, and the harrier view is mostly sky → slice-polish;
  - the Ch8 wall arena and Reach backdrop are plain → env-art;
  - the life_audio freed-object error → audio.
- (was) **big12** `lead/gate-big12` @ 8a28be17 (big11 + every track head as of 10-27 ~18:00) is gating on the PC, full manifest, 341 shots. Cloud: Godot 2820/2, both owned by tracks: creature portraits (creatures) and the footsteps causeway test (audio). Tools: 41 new shots without baselines, the shrine GI bake (PC), test_iskarra (env-art).
- **To fold into the big12 merge:** `gpu/shrine-gi-big12` @ a748e599 (the Shell Shrine GI rebaked on big12's tree; fixes test_shrine_gi_bake).
- **Unmerged PC branches to merge with a later batch:**
  - `gpu/m2-nit-903-runner-renders`;
  - `gpu/m2-nit-904-import-exit-check` @ 5d5b65d1 (the import retry now needs exit 0 plus DONE);
  - `gpu/m3-rnd-03-sefir-tells` @ 02d1fa52 (review);
  - `gpu/m1-qa-09-heroes` (the QA report).
- **ADR 0040:** no accessory slot. The Float is a key item, the needle a Customize material, Reefball stock is Reefball-only gear.
- **M2-CHR-11 VERIFIED on AVX2** (PC, claude/characters @ 3723f3eb): base_body, rhen, toma and the 9 villagers, 12/12 identical. Blender rebuilds now match the cloud; it lands with big12.
- **M1-QA-09 hardware results** (`gpu/m1-qa-09-heroes` @ c50f039f): Asha's staff and Toma's spear aren't gripped (they float); the staff goes through the skirt when kneeling; the underskirt is a rigid tube in offer_hand. Rhen and the braid are clean. This is now characters' top item.
- **10-27 18:45: big11 MERGED** (integration 3cbcff9e): 43 baselines re-approved after viewing; Godot 2738/0, Blender 13/13 identical. Opened: the Drownbell intro crowds Toma into the frame (bpr FAST-TRACK); Ch6 capsule NPCs (act1-chapters); the shutdown freed-object error (creatures).
- (was) **big11** `lead/gate-big11` @ 23ea8c6f (every track head as of 10-27 ~15:30 + integration f5ec3bda) is gating on the PC with the full manifest. Cloud: Godot 2738/0. Known tools failures, owned by the tracks: test_audio_loudness (audio) and test_shrine_gi_bake (the stale shrine bake; slice-polish M3-ENV-704). Open: the duplicate Haluna villager systems (creatures' VillagerLayer vs slice-polish's HalunaVillagers); one owner to be picked.
- **Open from viewing big9:**
  - Ysolde is still a capsule in battle → hero-integration (FAST-TRACK).
  - Inquisitor Hadric Moll is a capsule (battle_arena_camp, battle_boss_intro_inquisitor) → characters (a human foe).
  - No manifest shot covers the prologue's "everyone is still here" colour → slice-polish.

## 2b. Rendering is PC-only (human directive, 10-27)
No cloud session captures screenshots. Tracks post `RENDER-REQUEST @ sha: ids` lines in their live logs, and the PC renders them and pushes `gpu/render-<track>-<sha7>`. The protocol is in TRACK-RULES.md. Gates stay on the PC as before.

## 2b''. The PC is RESUMED (10-28 ~03:30, the human: "use it however is most impactful")
- In priority order:
  1. batch gates from big14 on, on lavapipe as before (`gpu/gate-bigN-shots`);
  2. Act I real-GPU QA along the critical path, logged in `docs/kb/qa/act1_gpu_qa.md` with owners, contact sheets on `gpu/act1-qa-<n>`, plus a per-zone frame-time budget;
  3. heavy Blender verifies of the characters, creatures and creatures-b builds.
- Its old 13-request render queue is retired. Cloud tracks keep self-rendering their own small sets.

## 2b'. (history) The PC was PAUSED (10-27 ~21:30, the human's instruction)
- **pc-gpu PAUSED at 10-27 21:29 UTC** (clean; nothing running in WSL). The resume point is pc-gpu.md on `gpu/pc-gpu-paused-1027` @ 1dffdb31. Ready to run on resume: the slice --budget re-sweep (prepared in `hymn_budget`) and the Act I playthrough. Open render requests were handed to the Lead's cloud render server.
- **Meanwhile the Lead's container takes over** the render requests (`lead/gate-render-*` branches) and the batch gates (big13 and on): the full Godot suite plus the full manifest on cloud lavapipe, about 2–3 h per full gate.
- **10-28 01:00: tracks self-render (TRACK-RULES).** The shared cloud render queue left six tracks idle, so it is retired. Each track renders its own changed shots in its own container (HYMN_SHOTS ≤15, never baselines) and views them. The Lead's container only runs the batch gates, which re-render everything and approve baselines.
- **LFS routes** (ADR 0039) also cover `assets/audio/sfx/act3/**` (10e3a7a5, the Kite foley).
- Deferred until the PC resumes:
  - GPU benchmarks and hardware QA (M1-QA-09 follow-up, the --budget re-sweep, the Act I playthrough);
  - M3-RND-02;
  - Blender verify on AVX2.

## 2c. Lead decisions (10-27)
- ADR 0171 (audio 72 MiB for Act I) accepted.
- Act II audio storage (Git LFS or a build-time render) goes to the human. Audio prototypes the build-time render as ADR 0172 (proposed).
- M3-CRE-629: one weak-point colour (`spawn_wound`) for every foe (Pillar 4); creatures writes ADR 0151.
- Villagers: creatures owns the runtime (FieldNpc, VillagerLayer); zone owners own placement; VillagerLayer adopts zone-placed villagers.

## 3a. Live roster (new account, from 2026-10-25)
| Track | Session | Branch | Live log | Ids |
|---|---|---|---|---|
| Lead | session_018aiGwGLGkxsnMnu8VfCu1m | claude/undertow-lead-handoff-ze8rrn (integration) | lead-cloud.md | 1000–1099 |
| pc-gpu (Remote Control) | **session_01F3vrUMSWVyLnG3asrc8viy** (since 10-27 17:30; the old session_01DKdurcvrzq9PEvuSu5L2nA died when the PC was switched off mid-big11-gate) | gpu/* | pc-gpu.md | 900–999, ADR 0180+ |
| slice-polish | session_01KZCgTqxhHKjvMCm1dAosvZ | claude/m2-slice | slice-polish.md | 100–199, ADR 0101–0109 |
| act1-chapters | session_01TbP4NmiuX6qan2V9CWsDNN | claude/act1-chapters (new, cut from m2-slice 6c50823f) | act1-chapters.md | 1200–1299, ADR 0200–0209 |
| ui-menus | session_01KGBUwbYgXe9JS6D8jXw6ZG | claude/ui (claude/menus merged in, then retired) | ui-menus.md | 200–399, ADR 0110–0129 |
| battle-presentation | session_015hKkhtpX67kS4yZeA8AAhv | claude/battle-presentation | battle-presentation.md | 400–499, ADR 0130–0139 |
| characters | session_014AiZf1ZSvb9MAjxtUka4pd | claude/characters | characters.md | 500–599, ADR 0140–0149 |
| **integration-qa** (was hero-integration, repurposed 10-27 20:20: headless full-thread playthrough guards, save/load guards, cross-track seams, hero-layer maintenance) | session_01PzF7Jc4XVQdTWcaYUyCjPB | claude/hero-integration | hero-integration.md | 1100–1199, ADR 0190–0199 |
| creatures | session_01EbDaRQ5n7hpvwuRG6jEDQY | claude/creatures | creatures.md | 600–699, ADR 0150–0159 |
| env-art | session_01YbaV2c8yquRHqj6afQYg89 | claude/env-art | env-art.md | 700–799, ADR 0160–0169 |
| audio | session_01Wmj8xaLtwcqiS3qwC6PciW | claude/audio | audio.md | 800–899, ADR 0170–0179 |

**No combat, progression or systems track exists in this account:** ui-menus owns their UI-adjacent tasks (M3-RBL-201, M2-MNU-306, the shrine teleport list). The common brief is [`TRACK-RULES.md`](TRACK-RULES.md). The gate runners are retired.

## 4. Process rules that work: keep them
- **Never idle** (the human, 2026-10-24).
  - Every track keeps a long standing queue. When it empties, or the track waits on another track or a human verdict, it takes its next item, adjacent work or M3, and logs it.
  - **Human reviews never block work.**
  - The Lead checks every session's **real status** (`list_sessions` / `get_session`: idle, failed or completed means wake it with work) **every 20 minutes**, not just commit recency.
  - Sessions frequently end turns with items left, so re-wake them with explicit queues and "never end a turn while items remain".
- **Lead stays active:** monitor, route, merge, be the point of contact. Keep a 20-minute background heartbeat (`sleep 1200`) re-armed on every wake; scheduled routines (`create_trigger`/`send_later`) failed with ACCESS_DENIED. Run a stall watcher on each local merge agent (alert if its transcript is quiet AND no gate process of its own is running).
- **Gates without waiting.**
  - **Tracks:** per item, scoped checks only:
    - lint, format, validate_data, taskboard, dlgc;
    - Godot tests filtered to their area;
    - Blender verify only for changed jobs.
  - **Long runs:** in the background; never wait in the foreground.
  - **Batching:** several items per "MERGE-READY @ <sha>: items, checks run, checks skipped" line in the live log.
  - **The Lead** runs full gates **on the PC runner**.
- **Merge batches:** a local merge agent merges every MERGE-READY branch into `lead/bigN` (resolving conflicts properly). The Lead pushes `lead/gate-bigN` (the human allowed `lead/gate-*` staging branches) and the PC gates it. The PC pushes the out and diff PNGs of every failing shot to `gpu/gate-<name>-shots`. The Lead **views every drifted shot** before re-approving (`compare.py --update-baselines`), then merges into the integration branch and deletes the gate branch. **Never re-approve a baseline without viewing it.**
- **Fast-track playtest fixes:** cherry-pick the specific fix commits onto the integration branch with a scoped gate (filtered tests, affected shots, boot smoke) rather than waiting for a big batch. The human plays the integration branch, so tell them when a fix lands, and say plainly what is NOT merged yet.
- **Batch size:** keep batches small and frequent. Backlogs of 6+ branches caused multi-hour conflict merges.
- **Id blocks:** each track numbers new task, handoff and ADR ids from its own block, so ids never collide:
  - task ids: m2-slice 100–199, ui 200–299, menus 300–399, bpr 400–499, characters 500–599, creatures 600–699, env-art 700–799, audio 800–899, PC 900–999, Lead 1000–1099, hero-integration 1100–1199;
  - ADRs: 0100+ in blocks of ten in the same order;
  - handoff names: `<date>-<role>-<track>-<n>.md`.
  For new tracks in the new account, assign the next free blocks (slice-polish keeps 100s; act1-chapters takes 1200–1299 and ADR 0200–0209).
- **Shared append-only files:** strings.csv, flags.tres, PROVENANCE.md, validate_data.py, ownership.md, accessibility.json.
  - Merge them with `python3 tools/dev/merge_union.py <file>`.
  - Then **check duplicate loc keys** and keep the newer text: `cut -d, -f1 game/data/loc/strings.csv | sort | uniq -d`.
  - The union re-adds old duplicates on every merge, so check every time.
- **IP and asset rules:** no AI image or audio generation, no asset packs (except MPFB2 CC0 data, ADR 0021), every asset reproducible, with PROVENANCE rows.

## 5. Exact next steps for the new Lead (priority order)
1. **Gate `lead/gate-big9`** on the PC runner. Re-check `test_hero_clips` (tools) first. View the drifted shots: expect field shots with the real heroes, battle shots with hero rigs, prologue cutscene colour, and the arena or boss changes. Approve, merge, and tell the human, who has asked repeatedly for the real heroes and the prologue fixes.
2. **big10:** merge every track's newest head (each wrote a HANDOVER section with its MERGE-READY sha) and gate the same way.
3. **The human's open playtest complaints,** and where each stands:
   - The heroes are placeholders in the field and in battle: hero-integration plus characters; **in big9**, verify in play.
   - The prologue's motion is rigid and snapping: m2-slice's CutsceneMotion, M2-FP-29, **in big9**.
   - "Everyone is still here" was greyscale: m2-slice 583759c0, **in big9**.
   - The Hullgnaw boss intro framed too close: battle-presentation (fit the camera to the boss AABB). **Not done yet.**
   - "Parts look primitive": the queues of creatures (villager life, wildlife), menus (portraits), audio (footsteps) and battle-presentation (battle feel: hit-stop, shake, impact).
   - Fixed and merged: back-to-back encounters; enemies acting twice (M3-CMB-02, ADR 0038); the KO replay (M2-BPR-11); the start point; the coloured dusk frame.
4. **PC queue:** M1-QA-09 (Asha's braid, clipping and limbs on hardware), the slice re-sweep with `--budget`, then the Act I playthrough on hardware. M3-RND-02 (the min-spec proxy) waits on the owner's OK to limit GPU clocks. RND-16 (exit leak) is last.
5. **M2-CHR-11:** opt rhen, toma, base_body and the villagers into the SIMD snaps, so Blender rebuilds identically on the PC (AVX2), not just on the cloud (AVX-512). Until then the PC shows 9–10 known Blender DIFFs.
6. **After the human signs off M2:**
   - flip `prologue.next_location` and `end_card.next_location` to Act I;
   - run the **Godot 4.7.2 port** (ADR 0032; the PC has gpu/godot-472-port ready, with 4.7.2 parity checked; every baseline gets re-approved);
   - consider fast-forwarding `main` (it needs the human's permission).

## 6. Open questions for the human
- The M2 slice review (blocking; play the integration branch).
- Music: the listening verdict (docs/kb/audio/listening_notes.md), which blocks M1-LEAD-01.
- The Asha face direction (ADR 0019's stronger stylisation, or keep).
- ~~Git LFS~~: approved on 10-27 and **LIVE from 10-28** (ADR 0039): upload and download are verified from the cloud. The LFS paths are `assets/audio/music/actN/` and `assets/lfs/`. GitHub Actions never leave "queued"; check the repo settings.
- M3-RND-02: OK to cap the PC GPU's clocks or power for the min-spec proxy?

## 7. Toolchain and gotchas
- **Setup (cloud):** `pip install -r tools/requirements.txt` (it now includes Pillow), `python3 tools/dev/fetch_godot.py`, `python3 tools/dev/fetch_render_deps.py`. These come from the Ubuntu archive; Blender 5.0.1 via fetch_blender.
- **Tools tests:** `python3 tools/run_tool_tests.py -j 4` takes 2–3 min. ci_local uses it.
- **Baselines are lavapipe** (software Forward+). The PC's WSL2 distro `hymn` reproduces them pixel-for-pixel (llvmpipe "LLVM 22.1.8, 256 bits"). Never approve GPU captures.
- **The PC gate runner:**
  - **Docs:** `tools/dev/gate_runner.md`, plus `tools/dev/pc_gate/{sync,gate}.sh`.
  - **Fresh import:** it always does a fresh `.godot` import; stale caches made false shot drifts once.
  - **Resources:** WSL is capped at 10 GB with 2 shards (the owner approved this). Blender ignores `VIRTUAL_ENV`, so use the distro's Python.
  - **Scheduling:** gates never run during a GPU benchmark; total load stays ≤ 75%.
- **PC rules (the human's):**
  - ≤ 75% total CPU, memory and GPU;
  - one GPU benchmark at a time;
  - new `gpu/*` branches only, and never overwrite baselines;
  - Asha's materials only via `write_materials.py`;
  - keep pc-gpu.md current.
- **Blender determinism:** pin `threads` per job, and snap tiny values and UVs to a grid. numpy's SIMD dispatch differs between AVX-512 (cloud) and AVX2 (PC).
- **Known engine issues (4.6.3):**
  - **A RenderingDevice `vertex_formats` race:** a rare capture abort; re-run the shot once and never re-approve it.
  - **A shader-variant deadlock:** it hits when the advanced group (TAA motion vectors, VoxelGI, SSS) turns on lazily. M2-RND-14 turns it on at boot. Capture shots with TAA off plus VoxelGI need `"warm_shader_groups": true`.
  - **A per-shot hang guard** (`HYMN_SHOT_TIMEOUT`) is in capture.sh.
- **Hitch budgets (ADR 0029/0037):**
  - visible frames 50 ms;
  - hidden frames 1 s;
  - zone entry 3 s;
  - cold first launch: one hidden frame up to 1.7 s, only behind the boot card's first-run cue.
- **Line caps:** gdlint caps files at 1000 lines. `battle_controller.gd` and `shader_prewarm.gd` sit at the cap, so put new logic in helpers.
- **Shell safety:** never kill processes by pattern; never `pgrep -f` a pattern your own command contains; give every run a unique `HYMN_LOG_DIR` and `XDG_DATA_HOME`.
- **Cross-session messaging:**
  - **Lead → sessions:** works via `send_message`.
  - **Sessions → Lead:** often refused (an "untrusted device"). Read their live logs instead; the human sometimes relays.
  - **Bridge (PC) session:** it can message the Lead when it's active.
- **Usage limits:** they hit several times. When a limit resets, nudge EVERY session and local agent; they don't resume by themselves.

## 8. Where things are
- **Story:** docs/kb/story/ (beats, act outline).
- **Art:** docs/kb/art/.
- **Tech:** docs/kb/tech/ (architecture, battle_ctb, battle_presentation, chapter_flow, cutscenes, ui, water, undertow).
- **Design:** docs/kb/design/ (formulas, balance_targets, balance_report, economy).
- **GPU reports:** docs/kb/qa/gpu/.
- **Gate runs:** docs/kb/qa/gate-runs/ (on the gpu/*-shots branches).
- **Task files:** docs/kb/tasks/M1–M3/.
- **Handoffs:** docs/kb/handoffs/ and live/.
