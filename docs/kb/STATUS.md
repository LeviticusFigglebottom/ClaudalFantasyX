# STATUS

- **Milestone:** M0 is reviewed (fresh-agent approve-with-fixes, fixes landed). **M1 is in progress** with parallel streams.
- **Updated:** 2026-10-22 by Lead (lead-bootstrap)
- **M0 progress:** done, pending the human's look. `tools/ci_local.sh` passes from a fresh checkout: 153 Godot tests, 96 tool tests, 3 screenshot baselines.
- **M1 progress:** about 30%. 1 task done and 8 in review (story, audio PoC, art direction, dialogue system, Lattice, screenshots, graphics presets, prewarm). See `python3 tools/taskboard.py --milestone M1`.

## The project in one page (Lead's reading of SPEC v1.0)

We're building *Hymn of the Undertow*: an original, cinematic, turn-based JRPG in Godot 4 (Forward+, desktop). Its mood and structure borrow from FFX: a sun-drenched, drowning archipelago (**Maresh**), a pilgrimage, a faith hiding a terrible truth, conditional turn-based combat, and a node-board progression system. The story ends in a costly goodbye. **Everything is original and made in-repo:** no asset packs, no CC0 meshes, textures, or audio, and no AI generation (unless the human approves). Only OFL fonts and permissive code are exempt. Every asset regenerates from source in `assets_src/` or `tools/` and is logged in `assets/PROVENANCE.md`.

**Story.** Once a generation, the **Undertow**, a sentient storm made of the unreleased dead, drowns the coasts. A **Cantor** gathers the verses of the **Hush** at the temples and sings it at the **Drowned Choir**, buying a decade-long **Calm** at the cost of her life. The truth is that the Hush makes each Cantor the storm's next heart, and the Order's undying leadership knows it. Rhen (a lamp-diver), Asha (the Cantor), and their guardians refuse the sacrifice. They fly the restored **Kite**, dive into the storm, defeat High Warden Sefir, and perform the **Great Unbinding**. All glimmer is released: the Undertow ends, the lingering dead (Kerrid, Asha's mother, the seven Vowbound) go with it, and Asha lives but loses her singing voice. The final image is a dark sea under stars. Pillars, in order: sincerity, beauty in decline, pilgrimage, tactical clarity, visible growth, and the cost of ending a cycle.

**Systems.** CTB battles (agility-based tick delays × action rank, a 16-turn timeline with action preview, free party swaps among 3 active members), Swell limit gauges with unique inputs, Vowbound summons that replace the party, the Lattice board with Facets, equipment ability slots, directed camera rails in the field, random encounters, save shrines, temple trials, Reefball, a bestiary, a codex, and full settings and accessibility. A headless, deterministic battle engine drives the tests and a balancing simulator.

**Fidelity** is first-class: painterly realism ("saturated by sun and water, lit by the dead"). Signature R&D covers water, underwater, glimmer, skin, hair, cloth, stone weathering, a battle VFX library, and the **Undertow storm** (prototype due by M2). The targets are 1440p60 on RTX 3060-class hardware and 1080p30–60 on GTX 1060-class.

**Process.** The Lead orchestrates role agents through the repo: the KB (`docs/kb/`), a file task board, ADRs, handoffs, and an ownership file. CI gates everything. Milestones run M0 → M7, and the **M2 vertical slice is a blocking human review** (Q7). The scale fallback is to cut zones and optional content before story beats or the graphical bar.

## What exists now
- **Engine and tooling:** Godot 4.6.3 (Forward+). `tools/dev/fetch_godot.py` fetches it in the sandbox, and `tools/dev/fetch_render_deps.py` adds **software Forward+ rendering** (Mesa lavapipe plus Xvfb, ADR 0009). `tools/ci_local.sh` is the merge gate while Actions has no runner (ADR 0008).
- **Core:** autoloads `EventBus`, `Game` (flags), `SaveSystem` (v2: versioned, migrating, with Lattice progress), and `SceneRouter` (async load, fade, shader prewarm installed).
- **Battle:** a deterministic CTB engine (exact integer damage; a timeline that simulates status countdown; swap, escape and the XP rule; target validation; data-driven AI). Sandbox balance bands are asserted in tests.
- **Progression:** Lattice data, logic, and editor (`tools/lattice_editor/`). The first 87-node section covers Rhen, Asha, and Toma. Movement and Facet rules are in formulas.md.
- **Narrative tech:** the `.dlg` compiler (`tools/dlgc.py`), `DialogueRunner`, and a typewriter `DialogueBox` with per-speaker blips. Sample scene: ch02 "The Girl on the Beach".
- **Rendering:** graphics presets (Low to Ultra, every API checked against 4.6.3), shader prewarm, shared shader includes and globals, and screenshot capture plus RMSE regression.
- **Content docs:** story bible, characters, voice guide, act outline (vertical slice = Ch2–3 at Haluna), 7 Vowbound; art references, a 25-frame color script, `palette.json`, design sheets for Asha, Rhen and Toma, the Haluna brief, and UI rules.
- **Audio:** a numpy synth library, a Hush theme sketch at −16 LUFS, and UI SFX. **Nobody has listened to it yet.**

## Top risks
1. **No real GPU anywhere.** Software rendering proves correctness and look, but performance targets (§4.2) are still estimates. The CPU-side scene-swap frame already measures 51–71 ms on the dummy renderer, over the 50 ms budget. Investigate in M1-RND-06 follow-up.
2. **Character fidelity** (§14): M1-CHR-01 and M1-CHR-02 must prove Asha before anything scales. Blender is being fetched the same way as Godot.
3. **Generated music quality** (§14, Q3): the agent's self-assessment is about 30–40% of a commercial theme, with the piano the weakest part. It needs human ears.
4. **Binary storage:** Git LFS is deferred (ADR 0005). Hero textures will need it.
5. **GitHub Actions does not run** (runs stay queued). We gate locally instead, so the export job has never run.

## Blockers / questions for the human
- **Listen to `assets/audio/music/hush_theme_sketch.ogg`** (69 s) and tell us whether the synthesized direction is acceptable, or whether you'd supply or commission music (§16 Q3, raised early per §14).
- **GitHub Actions:** check Settings → Actions (are workflows allowed?) and the account's minutes when convenient.
- **LFS:** may we enable Git LFS (quota)? It's needed before the M1-CHR-02 textures land.
- **Q1 title/world:** proceeding with the defaults. "The Calm" overlaps a term from the inspiring game; Narrative kept it and banned the compounds. Say the word to rename it.
- **Q2 (MPFB):** default is "allowed as a tool, heavily modified". The character stream records it in an ADR.
- Q4, Q5, Q6 and Q7 are at their spec defaults.
