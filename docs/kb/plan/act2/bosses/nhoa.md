---
draft: pre-gate
adr: 0203
vowbound: nhoa
element: ice
chapter: 11
owner: creatures-b
---
# Nhoa, the Rootlight (`nhoa`), Ice Vowbound: design sheet for Act II (draft: pre-gate)

**Built** (M3-CRE-642, in review): 14,820 triangles, 28 bones, 13 clips (`idle`, `idle_b`, `ready`, `attack`, `cast`,
`hit`, `hit_b`, `defend`, `ko`, `victory`, `rise`, `dismiss`, `special`), five slots; the Act III held form with its
`release` clip (M3-CRE-647). [Art sheet](../../../art/creatures/vowbound/nhoa.md). **Missing:** the `vowbound.json` row
and skills (M4-A2P-024), `clip_by_skill`, the two anchors, the per-skill clips below, the summon and bind cinematics
(M4-A2P-061, 071), Farewell-Tide's rising column (VFX), the `nhoa_bound` and `nhoa_summon` stings.

**Who:** Ressa, the 56th Cantor, the only Kirru Cantor and Pell's clutch-sister. Bound in Lowlight's drowned sanctum at
the foot of the well-shaft (Ch11). **Grave and kind: a sister, not a spirit of winter.**

**ADR 0015 guard:** Ice is hers alone, and **nothing about her is frozen**: no crystals, frost, icicles or frozen
surface. Her cold reads through the pale light, the stillness and a cold haze. Every VFX request below keeps that rule.

## 1. Silhouette (summon shot and default camera)

- 3.2 m to the antler tips, tall and narrow, hovering 0.15 m over the water. The one shape: **a long heron neck and
  two crowns of mangrove root**, held still. Grainy at the edge (the beads), never a solid.
- **Facing:** `yaw_deg` −90 on the Vowbound slot, her left side to the default camera, the face turned a little toward
  the foes. Her name-shell sits on the camera side of her throat.
- **Framing (as built):** inside the default camera's safe frame in every clip; the summon shot cuts the lower 0.45 m of
  strands under the HUD band (Kahre's precedent). New clips must hold the same margins.

## 2. Materials (as built)

`body` `abyss_navy`; `motes` `salt_glass` lit `glimmer_bound` 1.2 steady (a per-bead mask 0.4–1.0); `antler`
`timber_weathered` to `bone`, tips 0.25; `eye` `glimmer_bound` 0.55; `shell` `bone` with `tattoo_ink` carving, **never
lit**. Dry: she never wets, because she never touches the water. Her light is bound light: steady, no drift, no shed
motes. The one exception is Farewell-Tide's column (VFX, rendering's sanction requested in the art sheet).

## 3. Rig

As built (28 bones). **Add (unweighted):** `vfx_core` (the chest, on `spine_2`), `vfx_keepsake` (the name-shell, on
`neck_0`). Hovering: the strands' lowest point stays ≥ 0.05 m over the water in every clip.

## 4. Move list *(skill ids proposed; Combat's M4-A2P-024)*

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera |
|---|---|---|---|---|---|
| rise | `rise` (built) | — (2.6 s) | from folded low she unfolds upward, strands last | — | summon shot; full and short versions (the skip toggle) |
| idle | `idle`, `idle_b` (built) | — | the strands sway in a slow current | — | — |
| ready | `ready` (built) | — (1.4 s) | head lifts, hands spread, strands gather | — | — |
| `attack` | `attack` (built) | 0.0–0.55 s: the hand drawn back across her body → 0.55 s (1.2 s) | an open-handed sweep, strands following | one foe | — |
| `silt_fall` *(proposed)* | `cast` (built) | 0.0–0.8 s: both hands drawn up, strands streaming → 0.8 s (1.6 s) | hands pushed forward | one foe: Ice | a mote-swarm settles onto the target like silt; a cold haze, no crystals |
| `deep_well` *(proposed)* | `deep_well` *(proposed)* | 0.0–0.9 s: she sinks 0.3 m, arms wide and low → 1.0 s (1.8 s) | her arms sweep up from below | all foes: Ice, Slow | the swarm rises from the water under the foes and settles on them |
| `nhoa_echo` *(proposed)* | `echo` *(proposed; not built)* | 0.0–0.5 s: a mirror-still pause, head cocked toward the foe → 0.65 s (1.4 s) | her own version of the move, in strands | as the copied action | a faint double of her outline (VFX) |
| `farewell_tide` (Swell) | `special` (built) | 0.0–1.45 s: arms lifted, strands drawn up → 1.45 s (2.4 s) | the column | all foes | **the only Vowbound finisher whose motes go up**: the settling silt turning and rising (`glimmer_lift`); `finisher` shot, then up the column |
| defend | `defend` (built) | — (1.2 s) | arms crossed, strands wrapped round her front | — | — |
| hit | `hit`, `hit_b` (built) | peak 0.1 s | the neck snaps back, strands scatter and settle | — | — |
| KO | `ko` (built) | — (1.8 s) | she bows and folds, strands hanging straight | — | — |
| dismiss | `dismiss` (built) | — (1.0 s) | she folds back down | — | — |
| victory | `victory` (built) | — (2.2 s) | full height, antlers lifted | — | — |

**The echo.** Combat decides whether her copy has its own clip. Act I's finding was that a shared clip reads as
nothing, so the draft asks for `echo` (1.4 s, the stance above). Her version of the copied move reuses her own
`attack`, `cast` or `deep_well` after the pause, chosen by the copied skill's kind.

## 5. Phases

None as an ally. The summon runs `rise` → her turns → `special` (when her Swell is full) → `dismiss`. Every clip starts
from `idle`'s first frame. The Act III held form (`release`) is built and is Act III's fight.

## 6. Where she is seen

- **Battle:** the Vowbound slot (party Slot1, x 3.0, z −1.1). The arena is the fight's own (any Act II or Act III
  arena), so her light must hold in daylight arenas too: the motes at 1.2 hold against `ch12`'s key 2.8 (to check on the
  first render).
- **Bind cinematic (Ch11 C3):** the drowned sanctum, seen from the dry ledge at the foot of the shaft (plan default:
  walked, not swum), under the underwater shader. Pell kneels and says nothing for a full scene. Her clips for it are
  `rise` and `idle`; the rest is cinematics.

## Balance, engine, owners

- **Balance:** Vowbound are not on a curve by themselves; the Act II boss suites run with her bound from Ch11
  (M4-A2P-019).
- **Engine:** copying the last enemy action (a new effect; check that the engine records the last enemy skill).
- **Owners:** combat (row, skills, copy); creatures-b (anchors, `deep_well`, `echo`); battle-presentation (summons,
  column); rendering (the column's one exception to the bound-light rule); audio (stings).

## Open questions

1. Copy limits: does `nhoa_echo` copy a boss's charge skill, or only ordinary skills? Draft: ordinary skills only.
2. Echo check: Ice in fourth place is the residual overlap ADR 0015 accepted. Her setting is unfrozen and her beat is
   Pell's silence. No skill name here is a tiered spell name.
