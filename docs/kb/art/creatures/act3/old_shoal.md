# The Old Shoal (`old_shoal`; the roster's `old_leviathan`), Ch18 secret superboss

**The name (guardrail, CLAUDE.md §2):** "Leviathan" is a recurring summon's name in the series we must not echo, so
neither the player nor the data ever sees it. The id is `old_shoal`, and its player-facing name is "the Old Shoal",
which is what the sailors who charted it took it for. The roster row keeps its old id until creatures update it
(LEAD-ASK, 2026-10-30). The design itself is ours: a shoal that turns out to be an animal, not a monster with a shell.

**Task:** M5-A3P-1853 (creatures-b, ADR 0207). **Where:** Ch18, the secret coordinates: a shoal no chart marks, on
the open sea (act3_roster.md, "Reconciled with the Act III beat sheets": never inside a town). **Kind:** beast,
optional superboss. **What it is for:** a long, patient fight at the edge of the map. It has no wounds, so it is no
spawn: it simply never stopped growing (act3_roster.md Ch18).

## The idea

A sea turtle older than the Calm, grown to the size of a whale. It sleeps on a shoal so long that the shoal has grown
onto it: its shell is a reef, with its own small life on it (barnacle-crowns, weed, a few nesting gulls' stones). It
isn't angry, and it isn't the Undertow's. It wakes because someone has climbed onto its back, and it fights the way
the tide comes in: slowly, and without stopping.

The one exaggeration: **a landscape that breathes.** In the first seconds the player shouldn't be sure which part of
the shoal is the animal.

Original design (README rule 1): a turtle is common to every sea's stories. This one's look is our own, built from
the reef-and-age language of the Low Reaches.

## Silhouette and size

- **Scale:** the shell is about 9 m long and 3.8 m high at the crown. In battle only the **head, the fore-flippers and
  the front third of the shell** stand in frame. The party fights its face, and the rest is the shoal behind it.
  `stand_in.height` 3.8 (the crown), and the camera is battle presentation's (an arena framing like the Lamp Engine's).
- **The head:** broad, blunt and low, the beak worn smooth, the skin folded deep at the neck like old rope. The eyes
  are small, dark and wet; they open slowly (the wake). **No glow in the eyes:** it is a beast, not a lamp.
- **The shell:** high-domed, the scutes worn into terraces. Each terrace is crusted in coral (the same `coral_stone`
  courses as the Tide Matron's reef, so Ch18 reads as one sea) with weed hanging off its rim. On the crown a few
  standing stones lean, left by someone who thought the shoal was an island.
- **The flippers:** two great fore-flippers with a scalloped trailing edge, resting on the sand; they are its attacks.
  The hind-flippers are out of frame.

## Palette

| Part | Albedo | Light |
|---|---|---|
| The skin (head, neck, flippers) | `cold_blue_stone` going to `volcanic_stone` in the folds; pale `sand_cloth` on the underside of the jaw | none |
| The beak | `tortoiseshell`, worn to `timber_weathered` at the edge | none |
| The shell's scutes | `tortoiseshell` under `coral_stone_weathered` crust, `coral_stone` on the sun-bleached crown | none |
| The weed | `saltgrass`, wet (clearcoat) | none |
| The standing stones | `cold_blue_stone` | none |
| The eyes | `lacquer_black`, wet | none |

**No light anywhere.** It is the only boss in the game with no emission at all: no glimmer of any kind, bound, held
or lifted. That is the read: it was never part of the cycle.

## The fight (a proposal for Combat; mechanics are theirs)

- **Long and patient:** a huge HP pool and slow turns. On the timeline it acts once for every two of the party's turns
  (pillar 4: the timeline shows it plainly).
- **The tide:** every few of its turns it **draws the tide in**, a telegraphed party-wide push (no damage, but a
  turn of delay), then **lets it out** with a heavy flipper sweep. The rhythm is the whole fight.
- **The shell:** blows to the shell do almost nothing. The head and the flippers are the targets (parts, if Combat
  wants them: two flippers that can be made to rest, not broken).
- **The end:** it doesn't die. It lowers its head to the sand, closes its eyes and sleeps again (the KO `settle`). The
  shoal is quiet. Pillar 1: no triumph cue, only the sea.

**Reward:** whatever Combat sets for a superboss. The note for the chapter designer is that nobody in the world will
believe the party.

## Clips (all in place; it never travels)

| Clip | Length | What it shows |
|---|---|---|
| `idle` (loop) | 6.0 s | The breath: the shell rises and falls 4 cm, the head sways a little, the eyelids heavy |
| `ready` (loop) | 4.0 s | Awake: the head lifted from the sand, the flippers braced |
| `intro` | 4.0 s | The wake: a long stillness, then the eyes open, then the head lifts out of the sand and the shoal shifts |
| `attack` | 2.4 s | The flipper sweep: the right fore-flipper lifts and sweeps across the front (contact 1.5 s) |
| `cast` | 3.0 s | Drawing the tide: the head lifts high, the mouth opens, a long breath in (contact 2.2 s; the tide is VFX) |
| `bite` | 2.0 s | The head lunges low and bites (contact 1.2 s) |
| `hit`, `hit_b` | 0.8 s | A slow flinch: the head draws back a little into the shell's rim |
| `settle` (its KO) | 4.0 s | The head lowers to the sand and the eyes close; it ends asleep, held |

## Build notes

- Its own build script, `assets_src/creatures/old_shoal/build_old_shoal.py`. The shell's coral courses reuse
  the Tide Matron's cell code (from build_cinder_matron.py) where they can.
- Rig: root, shell, neck_0–2, head, jaw, eyelid_l/r, flipper_l/r (upper, fore, tip), and VFX anchors `vfx_core` (the
  chest), `vfx_phase` (the crown) and `vfx_mouth`. No `vfx_wound`: it has no wound.
- The triangle budget is a boss's, and the back two-thirds of the shell can be coarse because the camera never sees
  them.

## Open questions (for Combat and the chapter designer)

1. Parts: are the two fore-flippers parts (rest, not break), or is it one body?
2. The secret coordinates: how does the party learn them (a chart, a Kirru song, Kerrid's father's log)? This is the
   chapter designer's call.
3. Its music: silence and the sea, or a very low drone (audio's call).
