# The Tide Matron (`tide_matron`), Ch18 optional boss

**Task:** M5-A3P-1852 (creatures-b, ADR 0207). **Where:** Ch18, the revisited zones, on an old wild route only, never
inside a town (act3_roster.md "Reconciled with the Act III beat sheets": rule 3 of the Ch18 beat sheet). **Kind:** Lit
Age construct, optional boss. **What it is for:** the Cinder Matron's lesson, mastered (act3_roster.md Ch18). In Ch5
the party learned that a forge-mother isn't broken; she banks, and sleeps (act1_ch05.md §5 End). The Tide Matron is a
sister kiln the sea took. She asks the same thing of a party that now knows it.

## The idea

One of the Cinder Matron's sisters, built for the same work at a lower forge that stood on the shore. When the sea
rose it drowned the shore-forge, and her fire went out a thousand years ago. She never stopped working. A reef has
grown over her where the slag lay on her sister: coral plates instead of slag, still bowed over an anvil that is now
a reef-stone. Her heart is still bound and still glowing, sealed behind a port of salt-glass that the sea polished.

The one exaggeration, as for her sister: **a kiln with arms.** Hers is cold and alive with reef.

Original design (README rule 1). She is the Cinder Matron's rig and silhouette on purpose: the player must know her at
once as **the Matron's kind**. Every difference is material and growth, never shape.

## Silhouette and size

- **The Cinder Matron's rig and mesh, unchanged** (`assets_src/creatures/cinder_matron/`): the same height (3.4 m
  crown), the same kiln-with-shoulders silhouette, ladle-hand and tong-hand, and the same bones and anchors
  (`vfx_core`, `vfx_wound`, `vfx_phase`). One rig means one source of truth, as for the Vowbound's held forms.
- **What the reef adds** (its own meshes, generated over hers, like her slag `Crust`):
  - `Reef`: coral plates over the belly, the yoke and the pauldrons, in the same courses as her sister's crust.
    The plates are broad and rounded (brain-coral domes, plate-coral shelves), not cracked slag. They break into
    shelves at the shoulders, so the silhouette gains a little width up top. It reads as heavier and older.
  - `Kelp`: short kelp ribbons hanging from the lowest plates and the ladle's rim. They sway in the idle; they are
    the only thing that moves when she is still.
  - The firebox door is **shut and grown over**: its grate bars are crusted coral, with no glow. This is the most
    important read: the warm shape her sister always showed is dark here.
- **Height in battle:** `stand_in.height` 3.4 (her sister's), so the effects anchors land where they did.

## Palette

| Part | Albedo | Light |
|---|---|---|
| The frame (copper kiln, arms) | `bronze_patina` over `brass`: the copper is green with a thousand years under water | none |
| The reef plates | `coral_stone` going to `coral_stone_weathered`; the domes' tops sun-faded where the tide leaves them | none |
| The kelp | `saltgrass`, dark and wet (clearcoat) | none |
| The shut firebox | `volcanic_stone` grate under `coral_stone` growth | **none** (the fire is out: the read) |
| The heart port | `salt_glass`, polished | the heart behind it: `glimmer_bound` `#4FB3B0`, steady (README rule 3: the Lit Age bound it, as in her sister) |
| The weak point | one hairline seam in the salt-glass port | `spawn_wound` `#3FE0C8`, closed, never shedding (a construct) |

No `ember_orange` anywhere: the fire is gone. No `glimmer_lift` (she doesn't die) and no `glimmer_held` (she isn't
the Undertow's).

## The fight (a proposal for Combat; mechanics are theirs)

She is the Matron's lesson turned around. Her sister's crust had to be broken before she could be hurt. The Tide
Matron's reef **regrows on its own** every few turns: the tide brings it back. So breaking it is never the answer.

- **Phase 1, the Reef:** the reef plates turn blows aside, like her sister's crust. Every third turn she
  **banks the tide**: the reef grows a shelf and she is Protected (a telegraphed self-buff, her sister's Bank the Fire).
- **Phase 2, the Calm (at 50%):** the reef has grown over her completely, and she stops attacking for a turn. A
  party that understood Ch5 **lets her bank**: a turn spent guarding or healing wins the fight at once (she settles
  and sleeps, the end below). A party that keeps striking makes her pour the sea (`slag_pour`'s sister, a party-wide
  water attack) and the fight goes on until she banks at 0 HP anyway.
- **The end is always the bank,** never a break: she settles back onto her reef-stone anvil, bowed, the heart glowing
  on behind the salt-glass. No motes rise (she's bound). This keeps pillar 1: no joke and no gloating, only the same
  quiet sleep.

**Reward:** the bank-ending gives more than the long ending (Combat's numbers). The only lesson she teaches is that
waiting was right.

## Clips

**Her sister's clips, played by the same rig** (`idle`, `ready`, `intro`, `attack`, `cast`, `hit`, `hit_b`, `ko`,
`phase_change`, `bank_the_fire`, `slag_pour`, `recrust_gather`, `recrust`). The variant is a second GLB built by the
same build script with a `tide` flag that swaps the materials and adds `Reef` and `Kelp` in place of `Crust`. Its
clips are the same keys, retimed **slower** (×1.25): she is under water and older. Two clip changes:
- `bank_the_fire` becomes **`bank_the_tide`**: the same pose, but the reef shelf grows (the `Reef` mesh's shelves
  scale up from 0 over 0.8 s through a `ReefGrow` bone) where her sister's firebox flared.
- `ko` becomes **`bank`** (2.8 s): she settles onto the anvil-stone, the head bowing last; the kelp settles still;
  it ends at rest. It is the Ch5 ending made into a clip.

No new rig, no new silhouette, and no travel (a moored kiln, her sister's rule).

## Open questions (for Combat and the chapter designer)

1. Is Phase 2's "a turn spent guarding wins it" too hidden? A bark from Kerrid (who broke her sister's crust in Ch5)
   could name it: one line, the chapter designer's.
2. Where exactly: which old wild route? (Ch18's beat sheet: the routes the party walked in Act I, now changed.)
3. Her music: the Ch5 boss cue slowed and drowned, or silence and the sea (audio's call).
