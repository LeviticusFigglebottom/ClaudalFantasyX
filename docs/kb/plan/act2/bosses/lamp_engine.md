---
draft: pre-gate
adr: 0203
boss: lamp_engine
adds: conduit_crawler
chapter: 11
owner: creatures-b
---
# The Lamp Engine (`lamp_engine`) and its conduit crawlers, Ch11 boss: design sheet (draft: pre-gate)

**Built:** the engine's mesh, rig and the clips `idle`, `attack`, `cast`, `hit`, `ko`, `phase_change`, `idle_opened`,
`attack_opened`, `cast_opened`, `hit_opened` ([art sheet](../../../art/creatures/act2/lamp_engine.md)); the crawler's
model and 5 clips ([conduit_crawler.md](../../../art/creatures/act2/conduit_crawler.md)). Choreo has the intro
(`boss_tall`, 2.4 s) and the `opened` moment (M3-BPR-408). Music `lamp_engine` exists. **Missing:** both enemy rows (the
crawler has none), the "repair a part" effect (M4-A2P-022), the ring parts wired, a clip per skill, the anchors,
`intro`, `ready`, `hit_b`, `idle_b`, and the lamp VFX.

**What the fight teaches:** the act's first "kill the adds or lose" boss. The crawlers aren't cruel; they tend. The
engine isn't cruel either; it keeps. Releasing the core makes a small upward lift and a 3 s warm grade lift: the dead
it held, let go.

**Adds, decided by the plan (§2 Ch11):** the conduit crawler is a **boss add**, not a hazard. It ignores the party
until the engine is struck, never attacks first, and repairs broken rings.

## 1. Silhouette (at 12 m)

- **Engine:** a 3.4 m bell-hooded tower of steady lights on four short legs, three gimballed rings of four lamps, and
  two trimming arms raised. The one shape: **a ringed tower of lights standing knee-deep in water**. Vertical and
  ringed; it faces the party with the near ring's lamps.
- **Opened:** the rings fold back like petals, and the cracked core globe (the brightest light in the hall) faces the
  party.
- **Crawlers:** 0.7 m domes on six legs read as props at 12 m. So they are **lit and placed**: each sits on the dais
  edge between the engine and the party (enemy slots 1 and 2, in front of the engine's knees), and the small bound
  light inside each clear shell is the read. The `crawler_mend` clip walks it to the engine's leg and back, so the
  repair is a journey the player watches.

## 2. Materials

| Slot | Swatch | Notes |
|---|---|---|
| `frame` | `brass` → `bronze_patina` at the waterline | dry above, wet below (clearcoat 0.5) |
| `joint` | `lacquer_black` | |
| `chimney` | `salt_glass` | translucent, with `sea_glow` drips (emission 0.2) where water runs |
| `lamp` | `glimmer_bound` 1.6, steady | twelve lamps; a broken ring's four go to 0 (mesh swap: static emission) |
| `core` | `glimmer_bound` 2.2, steady | the brightest light in the hall; dark after the KO |
| `wound` | `spawn_wound` | the three gimbal hubs (one closed mark each: a construct, ADR 0151) |
| crawler `shell` / `light` / `wound` | `salt_glass` / `glimmer_bound` 0.6 / `spawn_wound` | the shell's seam is its weak point |

The hall's own light: twelve rail lamps in `glimmer_bound` at 1.6, and grey daylight from the broken bay (`ch11`,
`lut_ch11_vey`). The engine's lamps match the rail lamps exactly, so the hall and the machine read as one keeping.

## 3. Rig

Engine: body, three ring bones, twelve lamp gimbals, two arms of 3, four legs of 2, the core. **Add (unweighted):**
`vfx_wound` (the near gimbal hub, on `ring_1`), `vfx_core` (the core globe's centre), `vfx_phase` (the core's crack,
where the opened burst comes from). **Break parts:** `ring_0`, `ring_1`, `ring_2`, each with `whole` and `broken`
(lamps dark, gimbals slack). Legs planted by IK while it stands in the water (the floor is −0.6, the water −0.15):
nothing goes below −0.6. Crawler: body, six legs of 2, two arms of 2, plus `vfx_core`; its legs planted.

## 4. Move list

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera |
|---|---|---|---|---|---|
| intro | `intro` *(proposed)* | — (2.8 s) | the lamps light ring by ring, bottom to top; the rings start turning; the arms rise | — | `boss_tall`, 2.4 s hold |
| idle | `idle`, `idle_b` | — (4.0 s / 1.4 s) | rings turn against each other; `idle_b` an arm trims the air | — | water drips |
| ready | `ready` *(proposed)* | — (1.6 s) | the near ring swings its lamps to the party | — | — |
| `engine_trim` *(proposed)* | `attack` (built) | 0.0–0.6 s: the arm lifts and opens its scissor head → 0.6 s (1.3 s) | one arm snips | one foe | `target` shot |
| `lamp_gather` *(proposed, charge)* | `lamp_gather` *(proposed)* | — (1.8 s, holds) | every lamp swings to one hero and brightens in sequence: a held breath | marks one foe | the timeline shows the charge; lamps brighten (emission is static, so the brightening is a VFX glow card on each lamp) |
| `lamp_burn` *(proposed)* | `lamp_burn` *(proposed)* | 0.0–0.7 s: the rings lock still → 0.8 s (1.6 s) | the lamps fire together | the marked foe; power falls by a third per broken ring | a steady beam, no flicker; `cast` shot |
| `call_the_tenders` *(proposed)* | `call` *(proposed)* | 0.0–0.6 s → 0.7 s (1.4 s) | the engine strikes its own frame with an arm, a ringing knock | rouses the crawlers (`spawn` up to 2) | audio carries it; the crawlers' lights come on |
| *(phase 2)* `engine_trim` | `attack_opened` (built) | → 0.6 s | from the open stance | one foe | |
| *(phase 2)* `twin_trim` *(proposed)* | `twin_trim_opened` *(proposed)* | 0.0–0.7 s: both arms cross high → 0.85 s (1.7 s) | both arms snip, two targets | two foes | `boss_sweep` |
| *(phase 2)* `core_flare` *(proposed)* | `cast_opened` (built, retimed) | 0.0–0.9 s: petals spread wide, the core leans out → 1.0 s (2.0 s) | the core flares | all foes; power by unbroken rings | a pale shock across the dais; `push` |
| crawler `brush_jab` *(proposed)* | crawler `attack` (built, retimed to 0.55) | 0.0–0.55 s: the brush arm cocks back → 0.55 s (1.0 s) | a jab | the foe that last struck the engine | — |
| crawler `crawler_mend` *(proposed)* | crawler `cast` (built, "the repair") | walk 0.0–0.8 s → 1.0 s (1.8 s) | it scuttles to the engine's leg, arms work | restores one broken ring (M4-A2P-022) | the ring's `broken` mesh swaps back to `whole`; lamps relight |
| hit | `hit`, `hit_b`; opened `hit_opened`, `hit_b_opened` *(proposed)* | peak 0.1 s | rings jolt, a lamp swings loose | — | — |
| phase `opened` | `phase_change` (built, 2.0 s) | — | rings fold back, the core bared | — | choreo `opened` moment, `vfx_phase` |
| KO | `ko_opened` *(proposed)* | — (2.6 s) | the core goes dark; the frame settles on its knees | — | a small lift of motes from the core (`glimmer_lift`), and the 3 s warm grade lift (`lut_ch11_vey`) |
| crawler KO | crawler `ko` (built) | — | its light dims, legs fold | — | no lift: the crawler holds no dead |

## 5. Phase change

- **Trigger:** 50% HP.
- **Clip:** `phase_change`, ending on `idle_opened`.
- **Stance:** petals open, the core out. The `clips` map adds `twin_trim`, `hit_b_opened`, `ready_opened` *(proposed)*
  and `ko_opened`.
- **Broken rings stay broken through the phase** (the petals carry their state); the crawlers can still mend them.
- **What the player learns:** the core is the target now, and every ring a crawler mends makes `core_flare` stronger.
  So kill the tenders first, then turn on the core.

## 6. Arena read (`lowlight_engine_hall`)

- **Light:** `ch11` 12:30 overcast through the broken bay; twelve rail lamps; `lut_ch11_vey`; SSR water.
- **Placement:** the engine on the `BossAnchor` (−6.4, −0.6, −2.6), knee-deep off the dais; crawlers on enemy slots 1
  and 2 on the dais.
- **Must never happen:** an arm crossing the camera ray to a party slot; the core leaving frame in `twin_trim` (both
  arms high); the crawler's mend walk crossing in front of the party lane. It walks on the enemy side of the dais only.
- **Hazard:** none from the hall. The danger is the repair loop.
- **Camera and seats:** `boss_tall` intro; a short `actor` shot on a crawler when it mends, so the player sees why the
  ring relit; hint `the_lamps` for `lamp_gather`.

## Balance, engine, owners

- **Curve:** Act II boss. **Role answer:** Rhen or Ysolde on the crawlers, then Kerrid on the bared core (plan §2).
- **Engine:** part repair (gap, M4-A2P-022), parts that scale a skill's power (`break_parts` exists; the scaling rule is
  new), spawn (exists, Drownbell's polyps).
- **Owners:** creatures-b (clips, anchors, ring parts, the crawler's mend walk); combat (both rows, AI, repair, suite);
  battle-presentation (the mend shot, the core release); rendering (the warm lift); audio (the knock, the mend).

## Open questions

1. How many crawlers: two at the start, or none until `call_the_tenders`? Draft: two at the start, dormant (they
   ignore the party until the engine is struck), plus one call per phase to replace a lost one.
2. Echo check: a machine boss with repairing drones is common across games. Nothing names or stages it like a known
   fight. No change needed.
