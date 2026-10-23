# STATUS

- **Milestone:** M1 (Tech & Look Prototypes) is in progress; M0 is done.
- **Updated:** 2026-10-23 by Lead (lead-bootstrap)
- **Gate:** `tools/ci_local.sh` is green on `claude/new-session-mj8c3c` at d5f62c7 (ci20): 811 Godot tests, coverage battle 99.75% / progression 95.61%, and 58 Forward+ screenshot baselines.
- **Task board:** 47/68 M1 tasks done.
- **M1 exit criteria (SPEC §10.2):** CTB battle sandbox ✅ · ocean/shallows water ✅ · glimmer ✅ · Undertow prototype ✅ (prototype; production cost is M2-RND-01) · five-shot mood test 🔄 (M1-ENV-01 reopened: sky misses the palette) · **one hero at final fidelity 🔄 (CHR-02 built, failed the §14 face review at dialogue range; M1-CHR-03 rebuilds on the MPFB2 CC0 topology per the human's Q2 answer)**.

## The project in one page (Lead's reading of SPEC v1.0)

We're building *Hymn of the Undertow*: an original, cinematic, turn-based JRPG in Godot 4 (Forward+, desktop). Its mood and structure borrow from FFX: a sun-drenched, drowning archipelago (**Maresh**), a pilgrimage, a faith hiding a terrible truth, conditional turn-based combat, and a node-board progression system. The story ends in a costly goodbye. **Everything is original and made in-repo:** no asset packs, no CC0 meshes, textures, or audio, and no AI generation (unless the human approves). Only OFL fonts and permissive code are exempt. Every asset regenerates from source in `assets_src/` or `tools/` and is logged in `assets/PROVENANCE.md`.

**Story.** Once a generation, the **Undertow**, a sentient storm made of the unreleased dead, drowns the coasts. A **Cantor** gathers the verses of the **Hush** at the temples and sings it at the **Drowned Choir**, buying a decade-long **Calm** at the cost of her life. The truth is that the Hush makes each Cantor the storm's next heart, and the Order's undying leadership knows it. Rhen (a lamp-diver), Asha (the Cantor), and their guardians refuse the sacrifice. They fly the restored **Kite**, dive into the storm, defeat High Warden Sefir, and perform the **Great Unbinding**. All glimmer is released: the Undertow ends, the lingering dead (Kerrid, Asha's mother, the seven Vowbound) go with it, and Asha lives but loses her singing voice. The final image is a dark sea under stars. Pillars, in order: sincerity, beauty in decline, pilgrimage, tactical clarity, visible growth, and the cost of ending a cycle.

**Systems.** CTB battles (agility-based tick delays × action rank, a 16-turn timeline with action preview, free party swaps among 3 active members), Swell limit gauges with unique inputs, Vowbound summons that replace the party, the Lattice board with Facets, equipment ability slots, directed camera rails in the field, random encounters, save shrines, temple trials, Reefball, a bestiary, a codex, and full settings and accessibility. A headless, deterministic battle engine drives the tests and a balancing simulator.

**Fidelity** is first-class: painterly realism ("saturated by sun and water, lit by the dead"). Signature R&D covers water, underwater, glimmer, skin, hair, cloth, stone weathering, a battle VFX library, and the **Undertow storm** (prototype due by M2). The targets are 1440p60 on RTX 3060-class hardware and 1080p30–60 on GTX 1060-class.

**Process.** The Lead orchestrates role agents through the repo: the KB (`docs/kb/`), a file task board, ADRs, handoffs, and an ownership file. CI gates everything. Milestones run M0 → M7, and the **M2 vertical slice is a blocking human review** (Q7). The scale fallback is to cut zones and optional content before story beats or the graphical bar.

## What exists now
- **Engine and tooling:** Godot 4.6.3 and Blender 5.0.1 fetched from the Ubuntu archive (ADR 0008); software Forward+ capture (ADR 0009); coverage gate (ADR 0013); `tools/dev/merge_union.py` for append-only conflicts. Agents gate with `HYMN_SHOTS`, and the Lead runs the full manifest on merge.
- **Battle:** a deterministic CTB engine with all 21 statuses, swap and item previews, equipment effects, item use, lume rewards, and a balance simulator with gear-aware bands. The HUD covers the timeline, statuses display, and accessibility settings, and its build is staged across five frames.
- **Progression and economy:** the Lattice (first section), items, equipment with ability slots, Customize, shops (currency: lume), save v3. Save v4 has landed, with hardened writes, shape validation, a deferred autosave, a New Game confirm, and .tmp recovery (ADR 0018).
- **World:** field controller, camera rails with a cutscene `play_shot` API, debug overlays F1–F12, save shrine and save/load menu, autosave.
- **Narrative:** a story bible free of the IP near-misses, the vertical-slice beat sheet, two full cutscenes, the Act III ending beats, and a strict `.dlg` compiler.
- **Rendering:** water, glimmer, vegetation, character shaders (skin, hair, eye, cloth), the Undertow prototype, graphics presets, prewarm, a palette with on-screen targets (ADR 0014: default light units).
- **Audio:** three cues (Hush v2, battle, temple) plus UI SFX. **Nobody has listened to them yet.**

## Top risks
1. **Character fidelity (§14):** Asha's face is still uncanny at dialogue range. ADR 0019 applies the painterly close-up look now; M1-CHR-03 rebuilds on the MPFB2 donor topology (CC0 data only, no GPL code).
2. **Undertow cost:** solved for M1. High 1440p is 3.95–5.35 ms on the RX 9070 XT (M1-RND-10), down from 26–36 ms. It still needs confirming on a real RTX 3060 and GTX 1060.
3. **GPU access:** the human's PC (RX 9070 XT, via Remote Control) runs GPU benchmarks and look work on `gpu/*` branches. The reference-tier cards (RTX 3060, GTX 1060) are still unmeasured.
6. **IP echoes:** ADRs 0015/0016/0017/0020 re-staged the temple order, Act II, Act I and Kerrid. M1-NAR-11 removes Dace as Imra's guardian and closes the remaining gaps.
4. **Repo binaries:** the screenshot baselines are about 9 MB and every re-approval adds history. Git LFS (human decision) is increasingly needed.
5. **The shared machine is oversubscribed** with parallel agents (load 10-20 on 4 CPUs). Mitigated with `HYMN_SHOTS`, per-run `user://`, and a load-aware perf test.

## Blockers / questions for the human
- **Listen to the music** (docs/kb/audio/listening_notes.md, §16 Q3).
- **Reefball arena form:** keep the spec's suspended water sphere, differentiated as narrative proposes in story/decisions_log.md N-12, or switch to the alternative "Weir"? Default: keep.
- **Git LFS:** may we enable it (quota)?
- **GitHub Actions:** runs never leave `queued`; check Settings → Actions and minutes when convenient.
- **Answered 2026-10-23:** Q2, MPFB/MakeHuman allowed as a tool (CC0 data only, heavily modified; ADR 0021 pending in M1-CHR-03). The prologue line was replaced at the human's direction (SPEC v1.1, ADR 0020 §g).
- **Usage:** the account's weekly limit is at warning level until 29 Oct 17:00 UTC. The Lead keeps about 4 to 6 agents in parallel.
- Q1 (title/world), Q4, Q5 and Q6 are at their defaults.
