# STATUS

- **Milestone:** M0 Bootstrap, gates **green locally** (ADR 0008), awaiting a fresh-agent review. **M1 is open**: parallel streams are running.
- **Updated:** 2026-10-22 by Lead (lead-bootstrap)
- **M0 progress:** about 98%. Every §15 step 1–6 artifact is in the repo, and `tools/ci_local.sh` passes (42/42 Godot tests on 4.6.3).
- **M1 progress:** about 10%. The CTB engine core and story bible are in review, and the audio PoC is landing. See `python3 tools/taskboard.py --milestone M1`.

## The project in one page (Lead's reading of SPEC v1.0)

We're building *Hymn of the Undertow*: an original, cinematic, turn-based JRPG in Godot 4 (Forward+, desktop). Its mood and structure borrow from FFX: a sun-drenched, drowning archipelago (**Maresh**), a pilgrimage, a faith hiding a terrible truth, conditional turn-based combat, and a node-board progression system. The story ends in a costly goodbye. **Everything is original and made in-repo:** no asset packs, no CC0 meshes, textures, or audio, and no AI generation (unless the human approves). Only OFL fonts and permissive code are exempt. Every asset regenerates from source in `assets_src/` or `tools/` and is logged in `assets/PROVENANCE.md`.

**Story.** Once a generation, the **Undertow**, a sentient storm made of the unreleased dead, drowns the coasts. A **Cantor** gathers the verses of the **Hush** at the temples and sings it at the **Drowned Choir**, buying a decade-long **Calm** at the cost of her life. The truth is that the Hush makes each Cantor the storm's next heart, and the Order's undying leadership knows it. Rhen (a lamp-diver), Asha (the Cantor), and their guardians refuse the sacrifice. They fly the restored **Kite**, dive into the storm, defeat High Warden Sefir, and perform the **Great Unbinding**. All glimmer is released: the Undertow ends, the lingering dead (Kerrid, Asha's mother, the seven Vowbound) go with it, and Asha lives but loses her singing voice. The final image is a dark sea under stars. Pillars, in order: sincerity, beauty in decline, pilgrimage, tactical clarity, visible growth, and the cost of ending a cycle.

**Systems.** CTB battles (agility-based tick delays × action rank, a 16-turn timeline with action preview, free party swaps among 3 active members), Swell limit gauges with unique inputs, Vowbound summons that replace the party, the Lattice board with Facets, equipment ability slots, directed camera rails in the field, random encounters, save shrines, temple trials, Reefball, a bestiary, a codex, and full settings and accessibility. A headless, deterministic battle engine drives the tests and a balancing simulator.

**Fidelity** is first-class: painterly realism ("saturated by sun and water, lit by the dead"). Signature R&D covers water, underwater, glimmer, skin, hair, cloth, stone weathering, a battle VFX library, and the **Undertow storm** (prototype due by M2). The targets are 1440p60 on RTX 3060-class hardware and 1080p30–60 on GTX 1060-class.

**Process.** The Lead orchestrates role agents through the repo: the KB (`docs/kb/`), a file task board, ADRs, handoffs, and an ownership file. CI gates everything. Milestones run M0 → M7, and the **M2 vertical slice is a blocking human review** (Q7). The scale fallback is to cut zones and optional content before story beats or the graphical bar.

## What exists now
- Godot project (4.6.3, Forward+) with autoloads `EventBus`, `Game` (flags/state), `SaveSystem` (versioned and migrating), and `SceneRouter` (async load, fade, prewarm hook).
- **CTB engine core** (`game/battle/`): formulas (documented 1:1 in `design/formulas.md`), a timeline with preview, an engine with swap, escape, XP, and statuses, data-driven enemy AI, and JSON data for 4 heroes, 3 sandbox enemies, and all 21 statuses.
- Tests: an in-repo runner (ADR 0006) with unit tests for formulas, timeline, engine, saves, and flags, plus an integration test on real data.
- Tools: a data validator (schema, refs, flags, loc, provenance, banned terms, size), a task board, and a screenshot-regression stub. CI runs all of it, plus export on `main`.
- Story bible, 8 character sheets, voice guide, act outline (vertical slice = Ch2–3, Haluna), and 7 Vowbound.

## Top risks
1. **GitHub Actions does not run.** Runs sit in `queued` with no runner (Actions disabled, or no minutes). We gate locally instead (ADR 0008), with Godot fetched from the Ubuntu archive, and GPU-dependent checks are still missing.
2. **Character fidelity** (§14): procedural humans may look uncanny. M1-CHR-02 must prove Asha before anything scales.
3. **Generated music quality** (§14, Q3): see the audio PoC assessment in `audio/pipeline.md`.
4. **Binary storage:** Git LFS is deferred (ADR 0005), and M1 hero textures will need it.
5. **No GPU CI:** screenshot regression and performance checks need a GPU-capable runner (M1-QA-01).

## Blockers / questions for the human
- **GitHub Actions:** when convenient, check the repo's Settings → Actions (are workflows allowed?) and the account's Actions minutes. Nothing is blocked meanwhile, thanks to the local gate.
- **LFS:** may we enable Git LFS on this repo (quota)? It's needed before M1-CHR-02 textures land.
- **Q1 title/world:** proceeding with the defaults. Note that "the Calm" is spec-mandated but overlaps a term from the inspiring game. Narrative kept it and banned the compounds. Say the word if you'd rather rename it.
- **Q2 (MPFB/MakeHuman as a base tool):** the default (allowed as a tool, heavily modified) will be logged in an ADR at M1-CHR-01 unless you say otherwise.
- **Q6 platforms/hardware:** proceeding as written (Windows and Linux, macOS best effort).
- Q3, Q4, Q5, and Q7 are at their spec defaults; they're asked at the stated points.
