# Act III bestiary: roster proposal (M3-CRE-646)

The creatures track's proposal for Act III (act_outline.md Ch17–Ch21, "The Unbinding"), written ahead of the Act III
encounter design so the chapters have bodies to place, as act2_roster.md did for Act II. Ids are proposals. The
chapter track that designs the encounters decides which ship, and their stats, skills and AI.

**Act III's colour** is dusk gold, then the glimmer abyss, then total darkness under stars (act_outline.md). Its
creatures follow it:
- The dungeons (the Lamp Spire, the Undertow layers) are where **held** and **bound** light finally show their
  cost, so `glimmer_held` and `glimmer_bound` carry more of the frame than in Acts I–II.
- `glimmer_lift`, the released light, appears only at a release (color_script.md rule 1). On a creature, that means
  only a Vowbound's release KO and a founder's fall in the Cage.

**The README rules hold:** a real animal or object of Maresh with one exaggeration; weak points glow `spawn_wound`
(ADR 0151); Undertow-spawn carry the wet lacquer carapace; a Lit Age construct's light is `glimmer_bound`.

**What this track does not build:** people, as before. Warden Hesper Oan and Ilsabet Rue (Ch19), the four bound
founders' own figures (Ch20), and Sefir (Ch21) are the characters track's. The Undertow-heart (Sefir's phase 2) and
the storm's eye are the rendering track's Undertow, not a creature.

## Chapter by chapter

| Ch | Zone | Id | What it is | Battle role (what it teaches) | Kind |
|---|---|---|---|---|---|
| 17 | Hollowmere | none | A Saltwright flotilla in mourning: no fights | | |
| 18 | revisited zones (the world opens) | `deep_scuttler` | **Variant of the scuttler**: spawn that has crawled further up the coasts as the Calm fails, darker, with more wounds open | The Act I swarm grown dangerous: a revisit's foe, not a new lesson | variant |
| 18 | revisited zones | `tide_matron` | **Variant of the Cinder Matron's rig** for the reef: a coral-kiln, no fire, her heart bound in salt-glass | An optional revisit boss: the bank-not-break lesson, mastered | variant, optional boss |
| 18 | secret coordinates | `old_leviathan` | A whale-sized sea turtle older than the Calm, its shell a reef, asleep on a secret shoal | The secret-coordinates superboss: a long, patient fight. It has no wounds, so it is no spawn; it simply never stopped growing | beast, optional superboss |
| 19 | the Iskarra Lamp Spire | `wick_crawler` | A Lit Age lamp-tending machine: a brass body on many fine legs that crawls the spire's lamp-ropes, trimming wicks that went out 1,000 years ago | Construct that **relights** (buffs) the spire's other constructs until shut down | construct |
| 19 | the Lamp Spire | `chain_lamp` | A hanging lamp-cage on a chain, its bound light pulsing on a slow fixed beat (steady between beats, so the rule holds) | A hazard-foe: every few turns its beam sweeps the field, so you learn to act between beams. Pillar 4: the timeline shows the beat | construct |
| 19 | the Lamp Spire | `spire_moth` | **Variant of the flue moth**: moths that have lived for centuries on the spire's warm lamp-glass, glass-winged and pale | A fragile swarm that blinds (Accuracy down) | variant |
| 20 | the Undertow layers | `held_shoal` | A school of fish made of **held** light (`glimmer_held`), drifting in the drowned rooms as the sea's memory of fish | Untargetable while it drifts; it strikes when the room's memory turns. Teaches reading the layer, not the foe | spawn (held light) |
| 20 | the Undertow layers | `drowned_lantern` | The Oruvel and Corrow lamps of the remembered rooms, gone wrong: lantern-jellies with held light in their bells | It drains MP and lights the party's way when broken: the first foe whose death makes the room brighter | spawn (held light) |
| 20 | each layer (the releases) | `ilun_held` … `ethren_held` | **The six Vowbound as foes**: the same models (M3-CRE-638–644) with a **held** material set (`glimmer_held` in place of `glimmer_bound`) and a release KO that turns the light to `glimmer_lift` and lifts | Each release fight (vowbound.md): gentle to hardest. The KO is the release, the only place a creature's light rises | Vowbound (foe form) |
| 20 | the last layer (boss) | `the_cage` | **The Cage**: the founders' anchor, a Lit Age lattice of lamp-bars and chains wrapped around four bound figures (characters' figures inside our frame). Multi-part: each founder's quarter of the cage is a part that breaks | The multi-part boss (act_outline): break each quarter to free a founder, who thanks the party and falls (`glimmer_lift`) | construct, boss frame |

**Not foes on purpose:**
- Hollowmere (Ch17) and Reedhollow (Ch18) have no fights.
- Kerrid's last night (Ch19) has none.
- Ch21's walk to the heart is "one rail, no encounters: the walk is the threat" (act3_ending.md H01).

## The Vowbound as foes: how, without breaking the rules

- `tools/validate_creatures.py` forbids an enemy using a Vowbound's scene as its `model`. That rule is right: the
  ally scene carries `vowbound: true` and its stand-in behaviour.
- So each release fight gets its own battle scene, `game/creatures/<id>/<id>_held_battle.tscn`, instancing the same
  GLB with a **held** material override set (`materials_held/`, written by `write_materials.py` from a `held`
  block in the creature's materials.json), and its own creatures.json row with `phases` for the release.
- No new geometry: one GLB per Vowbound stays the source of truth, so the ally and the foe can never drift apart.
- **The release KO:** a new clip `release` per Vowbound (the light lifting off, the form unfurling one last time).
  The phase swaps the materials back from held to lift. The VFX motes rising are battle VFX's; the model only stops
  being held.
- **Kesh (Ch16 bind, Ch21 release)** is the seventh Vowbound: a colossal woman of standing seawater, robed in choir
  mouths. She is closer to a person than a beast, so her build is a split, our seawater body with the characters
  track's face. Her sheet comes after the six held forms.

**As built (M3-CRE-647, 2026-10-28):** the six held forms exist as planned. Each sheet in `vowbound/` has an "As
built: the held form" section, and pipeline.md §5 has the mechanism.
- **Materials:** `write_materials.py` reads a `held` block (`emission_from` glimmer_bound, `emission_to`
  glimmer_held) and writes `assets/creatures/<id>/materials_held/`. Every emissive slot is swapped at the same
  energy and stays steady; the other slots are copied. Without the block nothing more is written, and all 53 creature
  jobs verify identical.
- **Scene:** `<id>_held_battle.tscn` instances the same GLB. `CreatureActor.material_dir` puts the held set on it by
  slot name in `_ready`. One GLB has one import, so the second set has to come from the actor, not the import.
- **Row:** `<id>_held` has no `vowbound` key, `ko` is `release`, `phases.release` is `{"clip": "release", "hold":
  true}` (a new phase key: it stays on the last frame, and the KO doesn't replay it), and `stand_in.yaw_deg` is 90.
- **The `release` clips** (3.3–3.5 s) open, hold, then lift each form about 1.5 m up and 0.5 m back, away from the
  party, ending at peace:

  | Vowbound | Length | The release |
  |---|---|---|
  | Ilun | 3.3 s | gentle |
  | Kahre | 3.4 s | drawn up tall, then the weight let go |
  | Virel | 3.4 s | unrolls into a climbing kite line |
  | Hesk | 3.4 s | full span, one down-stroke, a glide |
  | Nhoa | 3.4 s | her strands of motes lift as she rises |
  | Ethren | 3.5 s | wings open, the ringed hand held out toward Ysolde, nearest her and last |

- **Still open:** the swap to `glimmer_lift` at the release and the rising motes belong to battle VFX and
  presentation. The enemies.json rows (`model` = the held scene) belong to Combat and the chapter designer. The
  review shots and the `_held` portraits are not rendered yet.

## Order of work (art)

1. **The six held forms first** (cheap: materials plus one `release` clip each). The releases are never cut
   (act_outline Cut Notes), and they reuse finished models.
2. **The Cage frame** (the boss), with the characters track for the four figures.
3. **Ch19's three** (`wick_crawler`, `chain_lamp`, `spire_moth`). The Lamp Spire is on the cut list
   ("shorten it to a single boss arena"), so it goes after the never-cut items.
4. **Ch20's two regulars** (`held_shoal`, `drowned_lantern`).
5. **Ch18's revisit set** (`deep_scuttler`, `tide_matron`, `old_leviathan`): the optional content, last.
6. Kesh, with the characters track.

Design sheets go in `docs/kb/art/creatures/act3/<id>.md` (README template), each before its build.

**Sheets (M3-CRE-648):** [the_cage](act3/the_cage.md) (the frame; the founders' figures are the characters
track's), [wick_crawler](act3/wick_crawler.md), [chain_lamp](act3/chain_lamp.md), [spire_moth](act3/spire_moth.md)
(Ch19), [held_shoal](act3/held_shoal.md) and [drowned_lantern](act3/drowned_lantern.md) (Ch20). Each ends with its
open questions for Combat and the chapter designer.

## Open questions (for the chapter designer and Combat, not the human)
- Ch18: which revisited zones get new foes at all (the "changed towns" may be quieter, not more dangerous)?
- Ch20: does each release fight happen inside that Vowbound's remembered layer (the Shell Shrine for Ilun, Ashcrown
  for Kahre, …), so the arenas come from env-art's existing kits?
- The Cage: one combatant with break parts (as the flat-engine), or four combatants plus a frame?
