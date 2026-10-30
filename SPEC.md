# PROJECT SPEC: *Hymn of the Undertow* (working title)

**A turn-based, story-driven RPG for Godot 4, inspired by Final Fantasy X**

> **To the receiving agent:** You are starting in an empty repository. This document is your full brief. Read it completely before writing any code. Then follow **§15 Bootstrap Sequence**. Wherever this spec leaves something open, make a reasoned decision, record it in `docs/kb/decisions/` (§13.4), and keep going. Stop and ask the human only for the items listed in **§16 Open Questions**, or for any choice that cannot be undone.

---

## 0. Mission in One Paragraph

Build an original, cinematic, turn-based JRPG in Godot 4. Its look, structure, and emotional register should borrow heavily from *Final Fantasy X* (2001) and that game's concept art: a sun-drenched, water-bound world drawn from Southeast Asian and Pacific motifs, a pilgrimage structure, a faith that hides a terrible truth, a tactical turn-order battle system, a graph-based character progression board, and a story that is beautiful, sad, and ends in a costly goodbye. The **world, characters, story, names, music, and every asset must be original.** No pre-made asset packs may be used. Any tool that *generates* or *helps author* content is allowed: procedural Blender/Python, shader code, Material Maker, audio synthesis, and so on. Graphical fidelity is a first-class priority. Stylization is welcome where it improves the result, but the tone must stay sincere and serious. It should never turn chibi, comedic, or toy-like.

---

## 1. Creative Pillars

These pillars settle disputes. When two goals conflict, the higher pillar wins.

1. **Sincerity.** The game believes in its own sorrow. Humor exists, as warmth between characters, but it never undercuts a tragic moment. No winking at the player and no meta jokes.
2. **Beauty in decline.** Every vista should look both gorgeous and doomed: sunlit ruins half-swallowed by sea, festivals held beside graveyards, light that comes from the dead.
3. **The pilgrimage.** The structure is a linear journey across the world toward a fixed destination. The world opens up late (an airship equivalent) for optional content.
4. **Tactical clarity.** Combat is deliberate and readable. The player always knows who acts next, why, and what an action will cost them in turn order.
5. **Growth you can see.** Progression is spatial and visible: the player physically walks a character across a board of nodes.
6. **The cost of ending a cycle.** The core theme is that breaking a long-standing cycle of sacrifice is right, but nobody gets to keep everything.

---

## 2. Originality and IP Guardrails (non-negotiable)

- **Do not use** any Square Enix names, characters, places, terms, logos, music, melodies, UI layouts copied pixel-for-pixel, or text. That includes Spira, Yevon, Sin, aeon, fayth, pyrefly, sphere grid, blitzball, Tidus, Yuna, and so on.
- **Do** borrow freely at the level of genre, mechanics, and mood: conditional turn-based combat, a node-board progression system, summoned guardians, an underwater sport minigame, ritual dances for the dead, Southeast Asian and Pacific-influenced design, and a corrupt church. Mechanics and aesthetics are not ownable. Specific expression is.
- **No reference images in the repo.** Agents may describe FFX concept art in words inside `docs/kb/art/references.md` (palettes, silhouettes, composition principles). Do not download, trace, or commit copyrighted images.
- **Music:** compose original pieces only. Do not imitate specific melodies such as the series prelude, "To Zanarkand," or the victory fanfare. Evoking the *style* is fine: piano-led melancholy, gamelan-like percussion, choral hymns, and some rock and fusion for battle.
- **Asset provenance:** every asset must be reproducible from source in the repo (a script, `.blend` file, shader, or synthesis patch), or be hand-authored by an agent in the repo. Track this in `assets/PROVENANCE.md` (§13.6).
- **CC0 and public-domain sources:** these are *also* treated as off-limits by default for meshes, textures, and audio, to respect the spirit of "made natively." Fonts and code libraries are excepted (§4.3). Any exception must be logged as a decision and flagged to the human.

---

## 3. World and Story Bible (seed; the Narrative agent expands it)

This is a **seed**. The Narrative agent owns `docs/kb/story/` and must expand it into a full story bible, chapter beat sheets, and a script before Chapter 2 production starts. It may change details, but it must keep the premise, the themes, and the shape of the ending.

### 3.1 The World: Maresh

- A tropical archipelago of hundreds of islands and the coastlines of one great southern continent. Ocean levels have risen over centuries, so old cities lie in shallow turquoise water and towers jut out of lagoons.
- **Cultural palette:** Balinese and Javanese temple architecture; Okinawan and Ryukyuan coastal villages; Polynesian navigation and tattoo traditions; Khmer stone ruins; Thai and Burmese lacquer and gold leaf; touches of Andean high-altitude culture for the cold northern ranges. Combine these into **new**, coherent cultures. Never reproduce a real sacred site one-to-one.
- **Technology:** the society has deliberately *regressed*. Ancient cities ran on **glimmer**: luminous, drifting motes released when a person dies. The church now forbids "binding" glimmer into machines. People use oil lamps, sail, and rope, while ancient glimmer-tech ruins sit everywhere, and a fringe culture (the **Saltwrights**) salvages it.

### 3.2 The Calamity: The Undertow

- Once a generation, the **Undertow** rises: a colossal, sentient maelstrom-storm that wanders the seas and drowns coastal towns. It leaves the drowned's glimmer drifting over the water for days.
- Only a **Cantor** can stop it. A Cantor is a pilgrim-singer who travels to the ancient temples, learns the verses of the **Hush** from the spirits bound there, and finally sings the full Hush at the **Drowned Choir** at the edge of the world. This calms the Undertow into ten or more years of sleep, called the **Calm**. The Cantor never returns.
- The faith, the **Order of the Still Water**, teaches that the Undertow is divine punishment for the old glimmer-binding, and that it will one day end if people atone.

### 3.3 The Truth (revealed in Acts II–III)

- The Undertow is made of the **unreleased dead**. Grief that is never let go, and glimmer that is hoarded, pool together into a storm.
- The Order's founders bound themselves *and* the Undertow together centuries ago. The Hush does not calm the storm. It **feeds it a new heart**: each Cantor becomes the Undertow's next core and keeps it coherent and sleeping, so it never tears free and floods the world for good.
- The Order's leadership is made up of glimmer-sustained revenants who have avoided death for centuries by drawing on the same reservoir. They know everything.

### 3.4 Principal Cast (original; expand into full character sheets)

| Character | Role | Battle niche | Arc |
|---|---|---|---|
| **Rhen Sallow** (protagonist, narrator) | Lamp-diver from a sunken city who scavenges ruins. Brash, curious, funny when scared. | Fast striker: speed and turn manipulation | Learns to stop running from loss. His father was a Saltwright who vanished into the Undertow. |
| **Asha Velamir** | The young Cantor. Gentle, stubborn, smiles to protect others. | Healer/white mage; calls the **Vowbound** (summons) | Chooses her own path instead of a sanctioned death. Her mother was the last Cantor. |
| **Toma Okeru** | Asha's guardian, a former temple warrior | Tank/defender; counterattacks | Faith shattered and rebuilt into something truer. |
| **Liss Varrow** | Saltwright mechanic and engineer, Rhen's foil | Item specialist; steals and builds gadgets | Represents the outlawed past. Her people are persecuted. |
| **Old Kerrid** | Silent, scarred ronin-like warrior who knew both Rhen's and Asha's parents | Heavy hitter that breaks armor | Is secretly one of the "unsent" dead who has stayed among the living. Reveals this in Act II. |
| **Ysolde** | Cold, elegant black mage, Asha's appointed tutor | Elemental magic | Grieving widow who sees the pilgrimage as a mercy. Becomes its fiercest critic. |
| **Pell** | A Kirru (an original non-human people: tall, quiet, sea-otter/heron-like) | Learns enemy abilities by listening to them | Outcast who has his own reasons to see the Undertow end. |

**Antagonist:** **High Warden Sefir Aurane**, the Order's leader. Charming and reasonable, he is also a centuries-old revenant. He believes stasis is mercy and wants to make the Calm permanent by becoming the Undertow's eternal heart himself, which would also make him eternal.

### 3.5 Story Shape

- **Prologue (in medias res):** the party at the ruins of a dead city at dusk. Rhen narrates, "Everyone I'm going to tell you about is still here tonight. Remember that, later." Then cut back.
- **Act I: The Pilgrimage.** Rhen survives an Undertow attack, washes up, meets Asha's group, and joins as a guardian. They visit temples, attend festivals, and play a sport tournament (the **Reefball** analogue, §6.10). The Undertow attacks a coastal fortress, followed by the first great dance for the dead.
- **Act II: The Truth.** The Order's corruption is revealed. A wedding becomes a trap. The party is declared heretics. Kerrid is revealed as one of the dead. They reach the Drowned Choir and learn what the Hush really does.
- **Act III: The Unbinding.** The party refuses the sacrifice. They gain a ship-of-the-air (a restored glimmer-tech vessel, the **Kite**), and optional content opens up. Finale: they dive into the Undertow itself, confront the founders' bound spirits, defeat Sefir, and perform the **Great Unbinding**: releasing *all* glimmer in the world at once.
- **Ending (bittersweet, required):** the Undertow ends forever. In the same instant every glimmer-light and every lingering soul is released, including Kerrid and Asha's mother, who appears for one last scene. Asha lives, but the Hush took her singing voice for good. Rhen loses his father for real, and this time he gets to say goodbye. The final image: Asha on a dock at night, the whole sea dark for the first time in a thousand years, and the stars reflected in it. Post-credits: the first new oil lamp lit in a rebuilt city.

### 3.6 Writing Rules

- About 40–60k words of in-game dialogue for the full game, with a hard ceiling of 80k.
- Each character has a distinct voice, documented in a voice guide with sample lines.
- Exposition comes through scene and action, never lore dumps longer than four lines.
- Every major town has at least one optional emotional side scene.
- Dialogue lives in data files (§5.6), never hard-coded.

---

## 4. Technical Foundation

### 4.1 Engine and Language

- **Godot 4.x, latest stable release** at bootstrap. Pin the exact version in `docs/kb/tech/engine.md` and in CI. Do not upgrade mid-project without a decision record.
- **Renderer: Forward+** (desktop). Mobile and web are explicitly out of scope.
- **GDScript** is the primary language, with static typing everywhere (`class_name`, typed vars, typed arrays). Use **C# or GDExtension (C++/Rust)** only for proven hot paths, with a decision record.
- Target platforms: Windows and Linux first, macOS best effort.

### 4.2 Performance Targets

| Tier | Hardware reference | Target |
|---|---|---|
| Recommended | RTX 3060 / RX 6600 class, 16 GB RAM | 1440p, 60 fps, high settings |
| Minimum | GTX 1060 / RX 580 class | 1080p, 30–60 fps, low preset |

- A graphics settings menu with presets is required: GI quality, shadows, volumetrics, SSR, SSAO/SSIL, render scale and FSR, and anti-aliasing (TAA/FXAA/MSAA).
- No visible hitch over 50 ms: battle transitions, dialogue and cutscene cuts, and the first 60 frames after any fade lifts. Frames hidden behind a full-screen fade or loading screen are loading time: no single hidden frame over 1 s, and zone entries under 3 s. The shader warm-up (a prewarm stage plus the boot warm-up of resident shaders) keeps the visible frames in budget (ADR 0029). On a cold first launch only, behind the boot card with its first-run cue, a hidden frame may take up to 1.7 s (ADR 0037).

### 4.3 Allowed Tooling and Libraries (examples, not limits)

- **3D:** Blender (headless via `blender --background --python`), Geometry Nodes, procedural Python generators, Blender's Rigify for rigs, MPFB/MakeHuman **only as a parametric human base generator** (see §16 Q2).
- **Textures and materials:** Blender bake pipelines, Material Maker, numpy/PIL/OpenCV procedural texture scripts, Godot `.gdshader` procedural materials.
- **VFX:** GPUParticles3D, custom particle shaders, flipbooks rendered from Blender or simulations.
- **Audio:** music authored as code or MIDI and rendered through open synths and soundfonts the agents build themselves, or through tools such as SuperCollider, Csound, FluidSynth with *self-authored* instruments, or pure DSP in Python. Sound effects come from synthesis (jsfxr-style generators, Python DSP) and processed recordings that agents generate procedurally.
- **Fonts:** open-licensed fonts (SIL OFL) are allowed. Log the license in PROVENANCE.
- **Godot addons:** code-only addons (for example GUT or gdUnit4 for testing, dialogue or state-machine plugins) are allowed under permissive licenses. Addons that ship art assets are not allowed.
- **Python tooling** for build steps, data validation, balancing simulations, and asset generation. Keep it in `tools/` with a `requirements.txt` or `pyproject.toml`.

---

## 5. Architecture

### 5.1 Repository Layout

```
/
├─ SPEC.md                      # this file (read-only except by the Lead)
├─ CLAUDE.md                    # agent operating rules (Lead writes at bootstrap)
├─ project.godot
├─ game/                        # all runtime Godot content
│  ├─ core/                     # autoloads, save system, events bus, scene router
│  ├─ battle/                   # CTB engine, AI, actions, UI glue
│  ├─ progression/              # Lattice board, equipment, abilities
│  ├─ world/                    # field controller, cameras, triggers, encounters
│  ├─ narrative/                # dialogue runner, cutscene sequencer
│  ├─ ui/                       # menus, HUD, theme resources
│  ├─ minigames/reefball/
│  ├─ shaders/
│  ├─ vfx/
│  ├─ audio/
│  ├─ data/                     # .tres / JSON / CSV: items, enemies, skills, dialogue
│  └─ levels/<chapter>/<zone>/
├─ assets_src/                  # SOURCE for every asset (.blend, .py, patches)
│  ├─ characters/ environments/ props/ textures/ music/ sfx/
├─ assets/                      # GENERATED/exported assets imported by Godot
│  └─ PROVENANCE.md
├─ tools/                       # python/blender pipelines, validators, sims
├─ tests/                       # GUT/gdUnit4 unit + integration tests
├─ docs/kb/                     # shared knowledge base (see §13)
└─ .github/workflows/           # CI
```

### 5.2 Core Patterns

- **Data-driven everything.** Enemies, skills, items, Lattice boards, encounter tables, shops, and dialogue are all `Resource` (`.tres`) or validated JSON/CSV. Designers (agents) tune numbers without touching code.
- **Event bus** autoload for decoupled signals: battle start and end, flags changed, dialogue events.
- **Story flags** live in one typed `GameState` resource. Every flag is declared in `game/data/flags.tres` with a description. CI fails on any undeclared flag usage.
- **Scene router** with async loading, transition effects, and shader prewarm hooks.
- **Save system:** versioned save files with schema migrations, a save-point-only model matching the genre (glowing save shrines), plus an autosave on chapter boundaries.
- **Determinism:** the battle engine must run headless with a seeded RNG so balancing simulations (§6.9) and tests can drive it without rendering.

### 5.3 Scene Ownership (to avoid `.tscn` merge conflicts)

- One agent owns each scene file at a time. Claims live in `docs/kb/ownership.md`: agent role, path glob, and since-date.
- Prefer composition: small, single-purpose scenes instanced into level scenes.
- Never edit another role's claimed scene. Open a request in the task board instead (§13.3).

### 5.4 Coding Standards

- Typed GDScript, `snake_case` files, `PascalCase` classes, no magic numbers outside data resources.
- Every system ships with tests. A PR that lowers coverage of `battle/` or `progression/` gets rejected.
- Debug overlays (F1–F12) for: turn-order internals, encounter rate, flag inspector, a teleport menu, a battle sandbox, and a Lattice cheat.

### 5.5 CI (GitHub Actions or an equivalent local script)

- Headless Godot import plus project validation.
- Unit and integration tests.
- Data validators (`tools/validate_data.py`): schema, dangling references, undeclared flags, missing localization keys, missing PROVENANCE entries.
- **Screenshot regression:** render fixed camera shots of key scenes headless (or on GPU runners if available) and compare them against approved baselines, flagging drift above a threshold.
- An export build for Windows and Linux on the main branch.

### 5.6 Dialogue and Cutscenes

- Dialogue is authored in a plain-text, writer-friendly format (Yarn-like or a custom `.dlg` format) and compiled to resources by a tool. It must support speaker, emotion/expression tag, camera cue, animation cue, branching on flags, and localization keys.
- **Cutscene sequencer:** a timeline built from `AnimationPlayer`, a custom track system, or both. It must cover camera moves, character marks and paths, facial expressions, lip-flap (procedural from text), fades, letterboxing, music cues, and VFX triggers.
- **No voice acting by default** (§16 Q4). Text boxes use a typewriter reveal with per-character "voice blips" or silence. The style decision is recorded.

---

## 6. Gameplay Systems

### 6.1 Battle: Conditional Turn-Based (CTB)

- Each combatant has a **tick counter**. Lower acts sooner. Each action has a **rank** (cost) that sets the next delay: `delay = base_delay(agility) × rank`.
- **Turn-order timeline UI** is always visible and shows the next ~16 turns. Hovering or selecting an action **previews** how the order would shift.
- Status effects that alter time (Haste, Slow, Stop, Delay-attacks) are core tactical tools.
- **No ATB, no real-time pressure.** Time stops while the player chooses.
- **Party swapping:** three active fighters. On a character's turn, the player can swap any active member for a reserve member at no turn cost. All party members can earn XP in a fight (the rule for who gets credit is documented).
- **Weakness and role design:** every encounter is built so a specific party member's niche is the elegant answer (flying enemies → Rhen's precise strikes, armored → Kerrid, magical → Ysolde), which rewards swapping.
- **Escape** is allowed except in scripted fights.
- **Scan** equivalent ("Read" ability) shows enemy stats, weaknesses, and a lore blurb, and logs the result into a bestiary.

### 6.2 Limit Gauge ("Swell")

- A per-character gauge fills according to a selectable **mode** (for example, taking damage, dealing damage, an ally being hurt, or using a healing item). Players unlock new modes through play.
- When full, the character can use **Swell techniques**. Each character's Swell has a **unique interactive input**: a timing ring, a button-sequence chant, a reel-stop, or a dice/tile mechanic. These are visually distinct, short, and cancelable.

### 6.3 Summons: The Vowbound

- Six to eight bound spirits acquired at the temples. **When summoned, a Vowbound replaces the whole party on the field** and has its own HP, abilities, and Swell (signature finisher).
- Each Vowbound has a **summon cinematic**: a full version for its first use, then a shortened one, with a skip toggle in settings.
- Vowbound grow with Asha's stats plus item-taught abilities.
- Narratively, Vowbound are the bound spirits of past Cantors. **Each one must be fought at the end of the story** as part of the Unbinding, which carries emotional weight.

### 6.4 Progression: The Lattice

- A **shared, node-based board** (a 2D graph rendered in 3D with depth, glow, and a parallax starfield). Every character starts at their own location and travels across nodes using **movement points** earned from battle.
- Nodes are **activated with typed consumable crystals** ("Facets": Power, Mind, Speed, Ability, Fortune, Key). Stat nodes give fixed boosts. Ability nodes grant skills. Locked gates need Key Facets.
- An **Expert-mode variant** board (open layout) can be chosen at the start.
- Late-game items can rewrite empty nodes (stat customization).
- Board layout is stored as data (nodes, edges, node type, value) and generated or edited with a tool in `tools/lattice_editor/`.

### 6.5 Equipment Customization

- Weapons and armor carry up to four ability slots, for example "Firestrike," "Piercing," "SOS Haste," "Poisonproof," or "Double Gil."
- A **Customize** menu crafts abilities into empty slots using items, at defined item costs.
- Every character has a signature **Ultimate Weapon** with a multi-step side quest that requires an exploration puzzle, a minigame, and an optional boss.

### 6.6 Field Exploration

- **3D field with directed, cinematic camera rails**, in the spirit of FFX's fixed or semi-fixed composed shots. Each zone has camera volumes that blend between authored shots. No free orbit camera, except optionally in large hub zones. This is a key fidelity lever: composed shots let every frame be art-directed.
- **Random encounters** using a step-and-danger meter, plus ability-based modifiers (Encounter-Off, Encounter-Up), and visible "danger zone" ambience cues.
- **Save shrines** with full heal, a save menu, and later a teleport network.
- **Temple Trials:** short environmental puzzles (pushing glyph pedestals, lighting glimmer channels, rotating water flows) leading to each Vowbound. There is a hidden optional reward per temple.
- **Treasure:** chests with a visible "already opened" state; key items; hidden caches tied to a late-game ability (sight of the dead).
- **Towns:** NPCs with schedule-free but state-changing dialogue that updates per story beat, shops, inns, side scenes, and lore.
- **Kite (airship), Act III:** a world-map menu to fly between unlocked locations, plus coordinate-search secret locations.

### 6.7 Enemies and Bosses

- About 120 regular enemy types (including palette variants with new behaviors), about 35 story bosses, and an optional superboss tier (a monster-capture-and-arena system is a stretch goal).
- Every boss has at least two phases, a gimmick that teaches a mechanic, and a lore justification. Bosses are tested in the battle sandbox before integration.
- **Enemy AI:** a data-defined priority and condition system (if HP < 30% → use X; if a target is Silenced → do Y), with weighted randomness and scripted turns.

### 6.8 Status Effects, Elements, Formulas

- **Elements:** Fire, Water, Lightning, Ice, Holy, and **Glimmer** (an original non-elemental-spirit element).
- **Statuses:** Poison, Sleep, Silence, Darkness, Petrify, Slow, Haste, Stop, Berserk, Confuse, Last Tide, Hollowed, Tide Ward, Bulwark, Mirrorwater, Mending, Sundered, Unmoored, Weakened, Dimmed, and Provoke (names per ADR 0202).
- All formulas live in **one documented file** (`docs/kb/design/formulas.md`) mirrored exactly by `game/battle/formulas.gd`, with unit tests per formula. The damage cap is 9,999, with an ability that lifts it later.

### 6.9 Balancing

- A headless battle simulator (`tools/balance/sim.py` invoking Godot headless, or a GDScript runner) runs thousands of seeded fights for each encounter and reports win rate, average turns, and item usage. Target curves per chapter are documented. Any boss whose expected party-loss rate sits outside its target band is rebalanced before release.

### 6.10 Minigame: Reefball (FFX's blitzball analogue)

- An underwater team sport played inside a suspended sphere of water. **Stretch-scope:** build a simplified version for Act I (a story-mandated match), then a deeper league with recruitment in Act III if time allows.
- The design must be **turn-paused and tactical** rather than twitch: the player issues pass/shoot/dribble decisions at contact moments, resolved by stats.

### 6.11 Other Required Features

- Bestiary, a lore codex (which also unlocks text records found in the world), a "Memories" scene-replay gallery post-game, a full item/key-item menu, a party formation menu, settings (graphics, audio sliders, text speed, battle speed, summon-cinematic length, colorblind-friendly UI options, input remapping), and controller plus keyboard and mouse support.

---

## 7. Art Direction

### 7.1 Visual Thesis

**"Painterly realism, saturated by sun and water, lit by the dead."** Aim for the look of FFX's concept art brought into present-day real-time rendering: warm, high-key daylight; deep teal shadows; enormous skies; gold, red-lacquer, and turquoise accents; and a **spectral glow** (glimmer) that turns every night scene into something sacred and eerie.

### 7.2 Color Script

- The Lead Art agent produces a **color script**: a strip of key frames, one per chapter, rendered as paintovers of blockout screenshots or generated as shader-only mood frames. It lives in `docs/kb/art/color_script.md`.
- Act I is warm, high-noon, festival color. Act II shifts to overcast, storm, moonlit, and cold blue stone. Act III moves through dusk gold and then the underwater abyss of glimmer, and the finale ends in total darkness under stars.

### 7.3 Characters

- **Proportions:** realistic adult proportions, roughly 7–7.5 heads tall, with a slight stylization: larger eyes by about 10%, crisp hair cards, and clean costume silhouettes.
- **Costumes:** the hallmark FFX idea of mixing culturally grounded garments with bold asymmetric fantasy elements, such as belts, straps, sashes, single sleeves, and oversized accessories. Each character must be identifiable from silhouette alone.
- **Fidelity targets:** 40–70k triangles per hero with LODs, 2K–4K textures for the face, and hair cards with anisotropic shading. Face rigs use either a blendshape set (visemes, brows, eyelids, about 30 expressions) or a bone-driven face rig. Eyes get a separate cornea and refraction shader.
- **Pipeline:** parametric base body → sculpt-ready mesh (procedurally modified in Blender Python) → costume built from procedural cloth panels, solidify, and bevel → bakes (normal, AO, curvature) → procedural material layers → Rigify rig → animation → export glTF → Godot import scripts.
- **Animation:** a hand-keyed and procedural hybrid. Required sets for battle are idle, ready, attack ×3, cast, hit, death, revive, victory, swap-in, and swap-out, plus a Swell sequence. Required sets for the field are walk, run, turn, interact, talk gestures (×8), and emotional poses (×12). Use procedural secondary motion (spring bones for hair, cloth, and accessories) and IK foot placement on the field.

### 7.4 Environments

- **Modular kits per culture** (temple stone, village timber and thatch, ruined-city concrete-and-coral, Saltwright scrap-tech, Order marble and gold), all generated procedurally from Blender scripts with parameters for weathering, moss, and erosion.
- **Hero zones** (temples, holy city, Drowned Choir) get bespoke hero meshes on top of the kits.
- **Vegetation:** procedural palm, banyan, frangipani, mangrove, and grass systems (Geometry Nodes or a custom L-system in Python) with wind shaders.
- **Water is the signature element** and gets a dedicated R&D track (§8.2).

### 7.5 Creatures and Vowbound

- Monsters are grounded in natural forms with a supernatural twist, such as coral-armored reef beasts or lantern-lure eels. Each has a "glimmer weak point" glow. Undertow-spawn are distinguishable at a glance by a shared visual language: dark wet carapaces and drifting glimmer wounds.
- Vowbound are huge, regal, and spectral, each tied to an element and to the past Cantor it was. Design sheets are written in `docs/kb/art/vowbound/` before modeling.

### 7.6 UI Art

- An elegant, translucent, deep-blue UI with thin gold and white lines and soft gradients, inspired by FFX's clean menu style but redesigned. Use an original serif or sans pairing (OFL fonts) and an original iconography set built as SVGs authored by agents.
- **Battle HUD:** turn-order timeline (right side), party bars (bottom right), command menu (bottom left), and target highlights with a ground-ring shader.
- All UI is built with Godot Control nodes plus shaders. No raster mock-ups get shipped.

---

## 8. Rendering and Graphics R&D

### 8.1 Lighting

- **SDFGI** for open zones, **VoxelGI** or baked **LightmapGI** for interiors and hero zones. Choose per zone and record it in the level's README.
- Volumetric fog with light shafts, SSAO/SSIL, SSR plus reflection probes, and a time-of-day system for authoring. Story scenes lock a specific time of day.
- A custom **tonemapping and color grade** per zone through LUTs authored in Python or by a shader generator.
- Physically based sky model plus painted procedural cloud layers. Clouds are a signature element: big, sculpted cumulus.

### 8.2 Signature Shaders (each one is a dedicated work item with its own test scene)

1. **Ocean and shallows water:** Gerstner/FFT waves, depth-based color absorption, caustics projected onto the seabed, shoreline foam, subsurface scattering in wave crests, refraction, and flowmaps for rivers.
2. **Underwater:** fog volume, god rays, floating particulate, and caustic lighting on characters. Required for Reefball and the finale.
3. **Glimmer:** drifting motes (GPU particles with curl-noise motion), bloom, soft additive trails, and an interaction where motes gather around the living and swirl during the dance for the dead.
4. **Skin:** a pre-integrated or screen-space subsurface approximation, a detail normal, and pore-level micro-roughness.
5. **Hair:** an anisotropic Kajiya-Kay style highlight with alpha-to-coverage or dithered transparency and TAA.
6. **Cloth:** sheen and fuzz layer, embroidery and gold-thread masks, and wind sway.
7. **Stone and weathering:** triplanar blending of moss, salt-crust, and wet layers driven by vertex color and world height.
8. **Battle VFX library:** one quality bar per element at three power tiers (lesser, greater, grand; in-game names are original and set by Narrative), plus Swells and Vowbound finishers.
9. **The Undertow:** a colossal volumetric storm with animated vortex shading, raymarched or layered, plus glimmer wounds. It is the most important visual in the game and needs a prototype by Milestone 2.

### 8.3 Cinematic Quality

- **In-engine cinematics only** (no pre-rendered video). Add depth-of-field, motion blur where it suits, letterboxing, and camera shake curves.
- **Facial performance:** each cutscene's dialogue lines have an emotion tag that drives expression blends. Major beats get hand-keyed facial animation.

### 8.4 Graphics Quality Gate

A zone is "art-complete" only when:
- Ten or more composed camera shots each pass review against the color script and the zone's mood brief.
- It holds performance targets on the recommended tier.
- Screenshot baselines are approved and committed.
- There are no visible placeholder assets (CI greps for a `PLACEHOLDER` tag in asset metadata).

---

## 9. Audio

- **Score:** about 60–80 original cues. A main theme (the "Hush" melody, piano-led, which the story also uses diegetically), a love theme, the Order's choral hymn (with lyrics in an original constructed language), character themes, regional and town themes, standard battle, boss battle, final boss (a multi-section suite), Reefball, temple trial ambience, and the ending suite.
- **Adaptive layers:** field-to-battle transitions use stingers. Major bosses use layered intensity stems.
- **Instrument palette:** piano, strings, flutes and shakuhachi-like winds, gamelan-like metallophones, frame drums, choir, and a rock and fusion layer for action pieces. Instruments are synthesized or sampled from **self-generated** samples (physical modeling, FM, additive, or Python-rendered).
- **SFX:** UI, footsteps by surface, weapons, magic by element, creatures, ambiences (surf, rain, temple wind, crowd murmur).
- A mixing and loudness standard documented in `docs/kb/audio/mix.md` (for example, a −16 LUFS integrated target for music beds).
- If the generated music fails its quality bar, raise it to the human early (§16 Q3).

---

## 10. Scope, Content Targets, and Milestones

### 10.1 Full-Game Targets (the ambition)

- 25–35 hours to finish the main story, 50+ for completionists.
- Roughly 30 distinct zones (8 towns or hubs, 6 temples, about 16 routes and dungeons) plus the optional areas.

### 10.2 Milestones (each ends with a playable build plus a written review)

| # | Name | Exit criteria |
|---|---|---|
| **M0** | Bootstrap | Repo layout, CLAUDE.md, knowledge base skeleton, CI green, ownership file, task board, engine pinned. |
| **M1** | Tech & Look Prototypes | CTB battle sandbox (two heroes vs. three enemies, timeline preview, swap). Ocean/shallows water. Glimmer particles. One hero character at final fidelity (modeled, rigged, shaded). One five-shot environment mood test. Undertow storm prototype. |
| **M2** | **Vertical Slice** (most important gate) | A 30–45 minute playable stretch with final-quality art: one coastal village, one route, one small temple trial, one Vowbound, a boss with two phases, a first Lattice section, equipment, saving and loading, two cutscenes with facial animation, three final music cues. **The human reviews this before scaling up (§16).** |
| **M3** | Act I Complete | Prologue through the end of Act I, including the Reefball story match. |
| **M4** | Act II Complete | Including the wedding set-piece and the reveal. |
| **M5** | Act III + Ending | The full critical path is playable end to end. |
| **M6** | Optional Content | Kite exploration, Ultimate Weapons, superbosses, extended Reefball, Expert Lattice. |
| **M7** | Polish & Ship | A balancing pass, a localization-ready string table, accessibility, performance, bug burn-down, credits, and exports. |

**Scale fallback:** if velocity data after M3 shows the full scope is unrealistic, the Lead proposes a cut list to the human. The default plan is to shrink zone count and optional content before touching the story's emotional beats or the graphical bar.

---

## 11. Quality Bars ("Definition of Done")

A feature or asset is done when:
1. It works, meets the spec, and has tests where code is involved.
2. It is data-driven where applicable and passes validators.
3. It holds performance targets.
4. Its source is in `assets_src/` with a PROVENANCE entry (for assets).
5. It is documented in the knowledge base (what it is, how to extend it, gotchas).
6. It has been reviewed by a **different** agent role than the author (§12.3), with the review notes recorded in the task file.
7. For visuals: it has been captured in screenshots and compared to the color script and briefs.

---

## 12. Team Structure and Delegation

You (the receiving agent) are the **Lead/Orchestrator**. Delegate as you judge most efficient. A recommended structure follows, but you may merge or split roles. Spawning parallel sessions or environments is allowed and encouraged once M0 is done.

### 12.1 Roles

| Role | Owns |
|---|---|
| **Lead / Orchestrator** | Spec integrity, milestones, task board, merges, final arbitration, human communication |
| **Systems Architect** | Core autoloads, save system, scene router, data schemas, CI |
| **Combat Designer-Engineer** | CTB engine, AI, statuses, formulas, balancing sim, battle UI logic |
| **Progression & Economy** | Lattice, equipment customization, items, shops, drop tables |
| **Narrative Director** | Story bible, beat sheets, script, character voice guides, dialogue data, cutscene direction notes |
| **Cinematics** | Cutscene sequencer, camera rails, staging, facial performance |
| **Technical Artist (Rendering)** | All shaders, lighting setups, post-processing, VFX framework, performance |
| **Character Artist** | Character and creature/Vowbound pipelines, rigs, animation |
| **Environment Artist** | Kits, vegetation, zone dressing, composed camera shots |
| **UI/UX** | Menus, HUD, iconography, fonts, accessibility, input |
| **Audio Director** | Score, synthesis pipeline, SFX, mixing, adaptive music system |
| **QA & Tools** | Test harnesses, screenshot regression, validators, playthrough scripts, bug triage |

### 12.2 Parallelization Guidance

- **M0–M1:** mostly serial. The Lead plus the Architect build the foundations, while Rendering R&D and Narrative's story bible can run in parallel from day one because they are isolated.
- **From M2:** run parallel streams in **git worktrees or separate environments**, one per role. Integrate frequently: at least daily merges to `main` behind passing CI.
- Avoid having two agents work on the same zone at once unless the ownership file splits it explicitly.

### 12.3 Review Pairs (cross-checking)

- Combat ↔ Progression (balance interplay)
- Narrative ↔ Cinematics (does the staging serve the beat?)
- Rendering ↔ Environment/Character (fidelity versus performance)
- Lead reviews everything that touches §1 pillars or §2 guardrails.
- High-stakes reviews (milestone gates, endgame story beats) use a **fresh agent** that did not produce the work.

---

## 13. Shared Knowledge Base and Communication Protocol

All coordination happens **through the repo** so any agent, in any environment, at any time, can catch up from files alone.

### 13.1 `docs/kb/` Structure

```
docs/kb/
├─ INDEX.md            # map of the KB; every new doc gets linked here
├─ STATUS.md           # current milestone, % complete, top risks (Lead updates daily)
├─ ownership.md        # scene/asset claims (§5.3)
├─ glossary.md         # every in-world term, spelling, and meaning
├─ decisions/          # ADRs: 0001-renderer-forward-plus.md, ...
├─ tasks/              # task board (see 13.3)
├─ handoffs/           # session handoff notes (see 13.5)
├─ story/  art/  audio/  design/  tech/  qa/
```

### 13.2 CLAUDE.md (the Lead writes it at M0)

It must include the following: a link to this spec, the pillars, the guardrails, the coding standards, how to claim work, how to write a handoff, the branch and merge rules, and "read STATUS.md and your role's KB folder before starting any session."

### 13.3 Task Board (file-based)

- One Markdown file per task: `docs/kb/tasks/<milestone>/<id>-<slug>.md`, with frontmatter for `id`, `title`, `role`, `status` (todo / doing / review / done / blocked), `owner_session`, `depends_on`, and `milestone`.
- Body: goal, acceptance criteria, notes, review log.
- `tools/taskboard.py` prints a board summary and flags stale "doing" tasks (more than 48h without commits).

### 13.4 Decisions (ADRs)

- Any choice that affects more than one role, or that departs from this spec, gets an ADR covering context, options, decision, and consequences. ADRs are append-only; to overturn one, write a new ADR that supersedes it.

### 13.5 Handoffs

- Every session ends by writing `docs/kb/handoffs/<date>-<role>-<n>.md`: what was done, what's in progress, the exact next step, known issues, and files touched. The next session for that role starts by reading the latest handoff.

### 13.6 Asset Provenance

- `assets/PROVENANCE.md` (or a CSV) records, per generated asset: path, source file or script, generating command, author role, date, and any third-party license (fonts and code only). CI fails on any asset under `assets/` with no entry.

### 13.7 Messaging Between Parallel Agents

- For async requests, open a task with `role: <target>` and `status: todo`, tagged `request-from: <role>`.
- For urgent blockers, add them to the "Blockers" section of `STATUS.md`. The Lead triages at least once per working session.
- If your environment supports direct agent-to-agent messaging, use it for quick questions, but **any resulting decision must still be written to the KB**. The KB is the source of truth, not chat logs.

---

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Procedural characters look uncanny or low quality | Prove one hero at final quality in M1 before scaling up. Lean on stylization (slightly painterly skin, strong silhouettes) if photoreal fails. Record the result in an ADR. |
| Generated music sounds cheap | Prototype three cues in M1–M2, and escalate to the human with samples early (§16 Q3). |
| Scope explosion | Milestone gates, the vertical slice review, and the cut-list protocol (§10.2). |
| `.tscn` merge hell | Ownership file, small composed scenes, frequent integration. |
| Performance collapse from GI and volumetrics | Per-zone GI choice, quality presets, a Rendering agent with performance budgets per zone. |
| Tonal drift (too goofy, too grim) | §1 pillars, Narrative voice guides, Lead review on tone-sensitive scenes. |
| IP contamination | §2 guardrails, glossary checks in CI (a banned-term list of FFX proper nouns grepped across data and dialogue). |

---

## 15. Bootstrap Sequence (do these in order)

1. Read this spec fully. Write a one-page summary of your understanding into `docs/kb/STATUS.md`.
2. Initialize Godot 4 (latest stable), Forward+, the repo layout (§5.1), `.gitignore`, `.gitattributes` (LFS for binaries if available), and `CLAUDE.md`.
3. Create the KB skeleton (§13.1), the banned-term list, and the glossary seeded from §3.
4. Set up CI with import, tests, validators, and a stub screenshot test.
5. Write ADRs 0001–0005: engine version, renderer, language policy, dialogue format, asset pipeline (Blender headless → glTF → Godot import scripts).
6. Break M1 into tasks on the board, with roles, dependencies, and acceptance criteria.
7. Start the parallel streams: (a) CTB battle sandbox, (b) water shader, (c) hero character pipeline (Asha first), (d) story bible expansion, (e) audio synthesis proof-of-concept.
8. At the end of M1, write a milestone review with screenshots, a short captured video or GIF if tooling allows, and an honest assessment of the fidelity bar. Notify the human.

---

## 16. Open Questions for the Human (ask before or at the stated point; otherwise use the default)

| # | Question | Default if unanswered | When needed |
|---|---|---|---|
| Q1 | Is the working title and world seed (§3) approved, or should it change? | Proceed with it | Before M2 |
| Q2 | May MPFB/MakeHuman (CC0 parametric human generator) serve as a base for character topology, or must bodies be built from scratch procedurally? | Allowed as a *tool*, with heavy modification; logged in an ADR | Before M1 character work |
| Q3 | If self-synthesized music can't reach the quality bar, can the human supply or commission music, or is a simpler style acceptable? | Keep iterating and show samples | End of M1 |
| Q4 | Voice acting: none, text-to-speech, or human-provided later? | None (text plus blips), with the architecture ready to add voice | Before M3 |
| Q5 | Are AI image or audio generation tools allowed for textures, concept paintovers, or sounds? | **Not allowed** unless approved | Any time |
| Q6 | Target platforms and the minimum hardware tier (§4.2): confirm? | As written | M0 |
| Q7 | Vertical slice review (M2): approve to scale up? | **Blocking.** Do not start M3 without approval | End of M2 |

---

*End of spec. The Lead owns this file. Changes require an ADR and a version note at the bottom.*

**Version log**
- v1.0: initial spec
- v1.1 (2026-10-23): §3.5 prologue line replaced at the human's direction (it echoed the inspiring game's opening line); see ADR 0020 §(g). §16 Q2 answered by the human: MPFB/MakeHuman allowed as a tool, CC0 data only, heavily modified (ADR 0021).
- v1.2 (2026-10-23): §8 item 8 tier wording neutralised. The old suffixes echoed the inspiring game's spell-tier names (IP guardrail §2); no design change.
- v1.3 (2026-10-24): §4.2's hitch limit now names the visible frames (50 ms) and budgets frames hidden behind a fade as loading time (1 s per frame, 3 s per zone entry); see ADR 0029 (accepted with an amendment by review-sweep-Q).
- v1.4 (2026-10-24): §4.2 allows a hidden frame of up to 1.7 s on a cold first launch only, behind the boot card with its first-run cue; see ADR 0037 (measured by M2-RND-18; Godot compiles one draw's pipeline set synchronously).
- v1.5 (2026-10-29): §3's roster row for Pell describes his niche in our own words; it named the inspiring series' job class (IP guardrail §2). See ADR 0201; no design change.
- v1.6 (2026-10-29): §6.8's status names replaced with our own (Shell, Protect, Reflect, Regen, Doom, Zombie and the four Breaks echoed the inspiring series' set; IP guardrail §2). See ADR 0202; no mechanic changes.
