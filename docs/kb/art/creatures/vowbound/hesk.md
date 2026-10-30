# Hesk, the Cord-Keeper (`hesk`), Asha's Vowbound: design sheet (built, M3-CRE-643)

**Who:** the fourth Vowbound (docs/kb/story/vowbound.md §4): the glimmer of **Ama Quillo**, the 47th Cantor, about 175
years ago. She was an Ullari keth-reader and a devout believer who started *counting* on her pilgrimage, and hung
the arithmetic in keth among the thousands of cords in Cloudloom's open hall. She is bound at Cloudloom, on the
summit of the Ullar Heights (Ch12). **Kind:** a Vowbound: bound light. **Role:** an ally, Holy. Her battle identity
is holy damage, cleansing (she lifts statuses off the party) and Regen. Her Swell is *Pass-Cord*, a line of shining
knots across the field. **Status:** built (M3-CRE-643, 2026-10-27): assets_src/creatures/hesk/build_hesk.py →
assets/creatures/hesk/hesk.glb, in review (art). She is not yet in vowbound.json; Combat adds the row, and until then
her creatures.json row carries `"vowbound_pending": "M3-CRE-643"` (tools/validate_creatures.py; Nhoa's key) and her clips are the stand-in
set (no `clip_by_skill`). Measured numbers are in "As built" at the end.

**The idea:** a great condor whose wing feathers are **knotted cords**, patterned like Ullari weaving and lit from
inside. She clutches **a keth bundle** in one talon, the keepsake. She reads as **a reader, steady and plain**. She
is no angel and no thunderbird: a high-pass carrion-eater, the bird that lifts the dead off the passes. That is the
Ullari meaning, and it fits "her light is the truth held up to be read".

Original design (README rule 1). It starts from the Andean-type condor (broad fingered primaries, a ruff, a bare
head) and from keth, the knotted-cord records of the Ullari (docs/kb/glossary.md). The cords are the game's own keth,
not any real-world script.

## Silhouette and size

| | |
|---|---|
| Wingspan | **4.2 m** when spread, but she rests **perched**, wings half-folded and mantled: 2.6 m across at rest, so the HUD's right edge stays clear (Ilun's tail crossed it) and the span is kept for the clips |
| Height | 2.4 m perched (head at 2.1 m) |
| Perch | she stands on the water's surface on her talons, grounded: every frame at y ≥ 0 (GroundedClipsTest). The keth bundle hangs from her left talon to 0.1 m above the water |
| Primaries | each of the eight "fingers" of each wing is a **cord** (a twisted rope, 1.1–1.5 m), knotted along its length: long knots, figure-eights and single knots in readable groups, like keth |
| Ruff | a collar of short, soft cords around the neck, `gauze_white` |
| Head | a condor's bare head: smooth, `bone`, a small dark beak, with two soft eyes, never a vulture's grimace |

## The knots

Built as geometry by the build script, from a seeded `default_rng` and a small table of knot kinds: a bead (single
knot), a long coil (2–5 turns) and a figure-eight. Each cord carries 3–7 knots in clusters, the clusters spaced like
digits. The patterns can come from **real numbers**: the build script can encode "47", "7" and the Cantor counts from
vowbound.md as knot clusters on her primaries, so a reader who knows keth (Ysolde, in the Ch12 scene) could read her
wings. Narrative decides whether that is said aloud; the geometry costs nothing extra.

**As built, the convention** (the build script's KETH comment): a number per cord, its digits as clusters read from
the hand outward, the highest place first. In every place but the units a digit *d* is *d* single knots (beads); the
units digit is one long knot of *d* turns (2–9), a figure-eight for 1, and a bare gap for 0. The two leading cords
of each wing read **47** (the Cantors) and **7** (the houses). The other six are her ledger, seeded: 22, 45, 22, 45,
38, 26 on the left wing and 67, 65, 49, 43, 67, 57 on the right. Narrative may give them meaning later. A changed
number is a one-line change to `KETH_FIXED` or the seed.

## Colour (palette.json swatches)

| Part | Albedo | Light |
|---|---|---|
| Body plumage | `overcast_slate` `#6F7E8E` toward `storm_slate` `#3E4A57` | none |
| Cord primaries and ruff | `gauze_white` `#EBE7DF`, cords twisted with a `sand_cloth` strand | `glimmer_bound` at 1.2 from inside, with a mask strongest **at the knots** (1.0) and faint along the cord (0.2): the knots are what shines |
| Head | `bone` | none |
| Eyes | `deep_teal_shadow` | `glimmer_bound` 0.55 |
| The keth bundle | `sand_cloth` and `faded_teal_cloth` cords | none: it is an object |

**The "white light" of vowbound.md.** The story calls it "the clean white light of the high passes". The palette
allows only `glimmer_bound` for Vowbound light, so she shines in `glimmer_bound`. The whiteness comes from the
`gauze_white` cords around that light, and from the high-pass lighting of the zone and the arena. That keeps one bound
light colour for every Vowbound (rule 2) and reads white against the slate body. If the Lead wants a true white-gold
holy light, that is a palette ADR (`glimmer_bound` is defined as the one bound colour), not a sheet decision.

## Clips

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | perched; she shifts her weight from talon to talon; the cords sway |
| `ready` | 1.4 s | the wings half open, the cords lift, the head raised |
| `attack` | 1.2 s, contact ~0.55 s | a wing-buffet: one wing swung forward, the cords lashing |
| `cast` | 1.6 s, contact ~0.8 s | the holy light: wings spread wide, the knots lit, held |
| `cleanse` (or `cast` again) | 1.6 s | wings brought forward and around the party's side in a lifting sweep, the way the high passes lift the dead. A separate clip only if Combat's cleanse skill wants one |
| `hit` | 0.5 s, peak ~0.1 s | a flinch, the head drawn into the ruff |
| `defend` | 1.2 s | the wings mantled forward |
| `ko` | 1.8 s | she settles down onto the water, wings spread flat, the head bowed |
| `victory` | 2.2 s | full span, the cords raised |
| `rise` | 2.6 s | from hunched and folded she opens and stands |
| `dismiss` | 1.0 s | folding and hunching down |
| `special` | 2.4 s, contact ~1.45 s | Pass-Cord: she spreads to the full 4.2 m, then sweeps both wings down and forward, and the line of shining knots runs across the field (VFX) |

## Rig and budget

About 26 bones: `root`, `body`, a 3-bone `neck`, `head`, three bones per wing plus a chain root for each cord
primary's base (the cords sway as soft chains), two bones per leg plus `talon`, and a two-bone chain for the bundle.
Up to 14k triangles; the cords and knots are about half of it. Six slots: `plumage`, `cord`, `head`, `eye`,
`bundle`, `ruff`.

## Open questions
- Her vowbound.json row (Combat).
- Holy light as `glimmer_bound` (the default above) or a new swatch (a Lead/art ADR).

## As built (M3-CRE-643, 2026-10-27)

Measured from the build's own numpy mesh and clips (`python3 assets_src/creatures/hesk/build_hesk.py --report`) and
from the exported GLB (tools/tests/test_creatures.py GroundedClipsTest).

- **Size.** At rest x ±1.22 m (the wings half-folded and mantled, **2.45 m across**; the sheet said about 2.6), y 0 to
  2.34 m (the head at 2.07 m), z −0.68 to +0.67 m. The full span is **4.2 m**: Pass-Cord holds 4.13–4.19 m spread and
  reaches 4.39 m on the downstroke; victory holds 4.24 m. `cast` opens 4.03 m (wide, not full).
- **Grounded.** Her right talon is planted and solved onto the water at every baked frame; the cords, the bundle and
  the held left leg are kept off it by `grounding.grounded`. Every frame of every clip is at y ≥ 0 (lowest 0.000,
  where the bundle's cord ends or a cord tip touch the water). No GroundedClipsTest allow-list entry.
- **Triangles: 13,602** (budget 14k): knots 4,056, cords 3,680, ruff 1,104, feet 936, wing plumage 800, body 792,
  bundle 710, legs 512, head 452, neck 336, eyes 160, tail 64. 7,782 vertices; GLB 1.58 MB. Six slots as above.
- **Rig: 25 bones** (the sheet said about 26): `root`, `body`, `neck_0..2`, `head`, `wing_l0..2` and `wing_r0..2`,
  `cord_l0`, `cord_l1` and the right (one soft two-bone chain per wing that all eight cords sway on), `leg_l0`,
  `leg_l1`, `talon_l` and the right, `bundle_0`, `bundle_1`, `tail`.
- **Clips (13):** `idle` 4.0 s loop, `ready` 1.4 s, `attack` 1.2 s (contact 0.55 s), `cast` 1.6 s (contact 0.8 s),
  `hit` 0.5 s (peak 0.10 s), `hit_b` 0.5 s (authored, the other side and heavier: the kit's scaled copy would push the
  solved talon through the water), `defend` 1.2 s, `ko` 1.8 s, `victory` 2.2 s, `rise` 2.6 s, `dismiss` 1.0 s,
  `special` 2.4 s (Pass-Cord, contact 1.45 s), `idle_b` 1.2 s. No separate `cleanse`: `cast` serves until Combat's
  cleanse skill asks for one.

**Changes from the proposal, and why.**
- **The open wings cup forward.** The open poses sweep every wing bone forward (build `WING_SWEEP`), the inner wing's
  cape hangs down and back rather than straight back, and the cord primaries droop as soft rope would. Built straight
  out, the near wing's trailing cords and secondaries crossed the default battle camera's right safe edge (−0.049 of
  the screen in victory) and the span reached 5.2 m against the sheet's 4.2.
- **The KO settles, it does not sink.** She drops 0.5 m and bows, the belly 4 cm over the water; the wings fall open
  and lie flat at 3.83 m. On the way down they pass 4.35 m for about 0.2 s (every path from the mantled wings to flat
  sweeps the arm through the horizontal); the full span otherwise opens only in Pass-Cord and victory.

**Framing (no render).** Every vertex of every baked frame projected with the camera director's own math (the
`summon` shot from choreo.json `BattleCameraDirector.shot_pose`; the battle axis is the default camera's flat −x) on the
Vowbound slot (party Slot1, x 3.0, z −1.1), turned by `yaw_deg` −90, 16:9, against choreo.json `camera.safe_frame`.
- *Default battle camera:* every clip inside on every side. At rest the margins are left 0.65, right 0.015, top 0.17,
  bottom 0.13 of the screen; the tightest frames are the KO's fall (right +0.001) and victory (right +0.003).
- *Summon shot:* left, right and top inside in every clip (at rest 0.28, 0.20, 0.20). Her feet are under the HUD's
  bottom band (−0.15), as Kahre's are from that low camera looking up.

**The light.** `cord`, `ruff` and `eye` are `glimmer_bound` #4FB3B0 at 1.2, steady. The build's emission mask is 1.0
on every knot and 0.2 along the cords and the ruff, and 0.55 on the eyes. `plumage`, `head` and `bundle` are not lit:
the keth bundle is an object and never glows.

## As built: the held form (M3-CRE-647, 2026-10-28)

The foe form for the Ch20 release fight (act3_roster.md, "The Vowbound as foes").

- **`release`** (3.4 s, its KO as a foe; the only clip added, every other clip samples identically): she opens to the full span, cords spread to be read, head raised, held (1.0–1.8 s); one slow down-stroke and she lifts 1.5 m up and 0.5 m back, gliding on open wings, the keth bundle still held. Her planted talon comes off the water only here (her test skips it for this clip).
  Lowest vertex over every frame +0.005 m. GLB 1.58 → 1.69 MB.
- Scene `game/creatures/hesk/hesk_held_battle.tscn` (the same GLB; `CreatureActor.material_dir` puts on `assets/creatures/hesk/materials_held/`, written by write_materials.py from the `held` block in materials.json: 3 emissive slots glimmer_bound to glimmer_held `#7FC6D9` at the same energy, steady; the rest as they are). creatures.json row `hesk_held`: no `vowbound` key, `ko` = `release`, `phases.release` = {clip `release`, `hold` true}, `stand_in.yaw_deg` 90 (facing the party), height 2.4 and radius 0.6 kept. Review shot `creature_hesk_held` (not rendered yet). No enemies.json row (Combat's, with the chapter designer). The turn to `glimmer_lift` and the rising motes are presentation (battle VFX), not the model.

## Final quality (M4-CRB-007, 2026-10-30)

ADR 0041 §3 and ADR 0205: Hesk at the Act I Vowbound bar (Ilun, Kahre, Virel), from her design sheet
([plan/act2/bosses/hesk.md](../../../plan/act2/bosses/hesk.md)). Audited from the party side of the default battle camera
(a scratch fixture seats her on battle_sandbox.json's `vowbound_slot` in `ch05_cinder_matron`, every clip frozen at
five beats) and up close (two close-up cameras), then re-rendered and viewed after each change.

**What the audit found, and the fixes.** The budget goes from 14k to **≤ 18k**, the Act I Vowbound final bar (Ilun
15.6k, Kahre 18.0k, Virel 17.8k); the extra went where the camera sees her.
- **The cords read as a rake of straight rods** at battle distance (the fan swings rigidly on its two chain bones).
  Each cord now leaves the hand along its fan line and **bends toward straight down as it hangs** (and a little back,
  trailing; build `CORD_HANG` 0.45), with a small wander of its own and ±5 % length; it ends in a whipping and a
  flared, sand-tinted **unlaid tuft**, so it reads as soft rope. Rest span 2.45 → 2.23 m.
- **The knots were hexagonal blobs** up close (3 × 6 ellipsoids) and the long knots a 5-sided zigzag sleeve. A single
  knot is now a 5 × 8 lump with its **crossing strand** standing proud across it (a tilted band); a long knot's wraps
  run round the cord as a **helix** (3 rings a turn, 6 round) tapering into the cord at both ends; a figure-eight is
  two crossed lumps. **The light follows the form:** the mask runs from 0.4 where a knot tucks into the cord to 1.0 on
  its proudest part (the crossing strand, each wrap's crest), so a lit knot keeps its shape instead of a flat glow.
  The keth (47, 7 and the ledger) are unchanged.
- **The ruff's loose ends read as fingers** round the neck. The fringe is now **loops of soft cord** in two tiers
  (12 and 10), each leaving the roll and coming back to it, the lower tier longer: a lace of knotted cord.
- **The neck was a smooth cone** (0.185 m at the base). It is lean above the ruff now (0.143 → 0.043 m), the bare skin
  **folded in five rings** with darker hollows; a low **brow** over each eye gives the bare skull a steady, reading look.
- **Triangles: 17,930** (≤ 18k): knots 8,056, cords 3,000 (ring spacing 0.05 → 0.06 m), ruff 1,792, feet 936, wing
  plumage 800, body 792, bundle 710, head 580, neck 528, legs 512, eyes 160, tail 64. 10,082 vertices. Rest bounds
  x ±1.14, y 0.005 to 2.34, z −0.68 to 0.67 m.

**Rig: 27 bones**, the 25 plus two unweighted anchors: **`vfx_core`** on `body` (the breast, 0.0, 1.32, 0.30) and
**`vfx_keepsake`** on `bundle_1` (the keth bundle's middle, 0.21, 0.22, 0.25: it swings, and rises in the Mending).

**Clips (16).** The Vowbound contract (`idle`, `idle_b`, `ready`, `rise`, `dismiss`, `attack`, `cast`, `hit`, `hit_b`,
`defend`, `ko`, `victory`, `special`), `release` (the held form), and two new ones, one per skill on the sheet:
- **`cleanse`** (Cord-Lift, 1.6 s, contact **0.9 s**): she bows and brings both wings low and forward, the hands
  reaching round in front of her (the gather, 0.0–0.7 s: hands 0.87 m forward and 1.2 m lower than at rest, the cords
  brushing the water), then lifts them up and open with her head raised (the cords rise 1.44 m by the contact),
  trailing under the hands: the high passes lifting the dead. Span 3.83 m at most, no wider than `cast`. A new wing
  pose `scoop`.
- **`mending`** (her Mending, ADR 0204, 1.4 s, contact **0.8 s**): she swings the held talon up (the bundle rises
  0.22 m and comes 0.2 m forward, still hanging) and bows her head 0.6 m over it, the wings curled forward round it
  (0.0–0.6 s); at the contact a little deeper, as if reading one knot. Quiet where Cord-Lift is wide. `pose(raise_=)`.
- **Every one-shot is played from `idle`'s first frame** (`ck.in_pose`, as the Act I bosses' move pass did): it starts
  there, and `rise` ends there. Before, they started from rest, a few degrees off the idle's first frame.
- Contacts (creatures.json `contact`): `attack` 0.55, `cast` 0.8, `cleanse` 0.9, `mending` 0.8, `special` 1.45 s; every
  striking clip winds up ≥ 0.55 s before its contact. Lowest vertex over every frame of every clip ≥ 0.000 m (the
  cords and the bundle kept off the water by `grounding.grounded`).

**The clip map, ready to paste** into creatures.json `hesk` when M4-A2P-024 adds her skills to skills.json (the
validator rejects `clip_by_skill` keys for skills that do not exist yet):
`"clip_by_skill": {"knot_light": "cast", "cord_lift": "cleanse", "hesk_mending": "mending", "pass_cord": "special"}`.

**Viewed.** Every clip at five beats from the battle camera (before and after), the two close-ups, the review shots
`creature_hesk` and `creature_hesk_held` (front: the soft hanging cords, the lace ruff, the folded neck read), and the
re-baked portraits `hesk.png` and `hesk_held.png` (assets/ui/portraits/creatures/). She stays inside her side of the
frame in every clip from the party camera. Nothing frozen on her or in her clips (ADR 0015): the white is cord, the light
`glimmer_bound`.

**Test:** tests/unit/test_creature_vowbound_act2.gd (`test_hesk_...`): the clip set, a wind-up ≥ 0.45 s before every
contact, the unweighted anchors, every one-shot from idle's first frame, Cord-Lift's gather and lift, and the
Mending's raised bundle and bow.
