---
draft: pre-gate
adr: 0203
vowbound: kesh
element: all six, in turn
chapter: 16
owner: creatures-b
---
# Kesh, the First Voice (`kesh`), Vowbound of all six: design sheet (draft: pre-gate)

**Nothing is built.** This is her first sheet (M3-CRE-649 wrote none; the plan splits it into M4-A2P-057). It is drawn
from [vowbound.md §7](../../../story/vowbound.md), plan §2 Ch16 and the Choir's art sheet. The art sheet proper
(`docs/kb/art/creatures/vowbound/kesh.md`) is written at the gate from this draft.

**Who:** Kesh Aurane, the 1st Cantor, a Lamplighter, and Sefir's wife. She sang herself in a thousand years ago and was
displaced forty years later. Sefir couldn't let her lift, so he bound her in the Choir's stones himself, and that
night the Abiding began. She has been awake in stone ever since. She hid the melody of the Eighth Verse in the stones.
**She reads as patient and enormous, and very tired**, never as a goddess or a monster. She is the oldest person in the
game, and she is still a person.

**In Act II:** she is bound at the Drowned Choir (Ch16 C4). The binding is a **memory sequence** in which Asha sees,
through Kesh, that the singer becomes the storm's next heart. Her summon (`kesh_summon`) belongs to Act III's H03, so
Act II needs her model, the bind and `kesh_bound`; the ally kit below is specified now so the model's clips are right
the first time.

## 1. Silhouette

- **Two scales.** In the bind she rises colossal from the Choir's sunken bowl, matched to the ten 24 m singers (a
  cinematic scale on the same rig). **In battle she is 4.2 m** (Kahre's rear height is the precedent for the summon
  framing), standing in the Vowbound slot.
- **The one shape: a woman made of standing seawater, from the hips up, rising out of a column of water**, her robe a
  long fall of open choir-mouths. Her lower body is the column itself, 1.2 m across where it meets the water and
  narrowing into her waist. Her head is bare, with long hair that is water falling, and her hands are open.
- **Facing:** `yaw_deg` −90; her face turned three-quarters to the camera. She looks at the foes. In the Act III fight
  she does not look at Sefir; that is staging, not the model.
- **Framing to hold:** at 4.2 m the top of her head must stay inside the default camera's top safe line in every clip
  (Kahre passed at 4.11 m). If it doesn't, the column shortens first, never her.

## 2. Materials

| Slot | Swatch | Light | Notes |
|---|---|---|---|
| `water` | `pale_rim` water's deep `#5E8C90` toward `turquoise_shallow` at the thin edges | none on the surface | refraction-like gloss, clearcoat 1.0; reads as standing water, not glass |
| `inner` | `deep_teal_shadow` | `glimmer_bound` 1.0, steady, deep inside | the bound heart, seen through the water; "Kesh pale cyan" (`lut_ch16_choir`) comes from this through the pale water |
| `mouths` | `cold_blue_stone`, the mouths' lips worn smooth | `glimmer_bound` 0.4 inside each open mouth | a hundred small carved mouths in the robe, rhyming with the Choir's singers |
| `hair` | `foam_white` at the falling ends | none | the hair is water falling, its ends breaking white |
| `key` | `brass` → `bronze_patina` | **none: it is an object** | the Lamplighter's lamp-key at her belt, the keepsake; never glows |

**Built like Nhoa's motes, not with particles:** the water is geometry skinned to her bones, so it obeys the
bound-light rule (steady; nothing drifts by itself). Running water is shown by the clips (the hair's chains, the robe's
chains), and the splash at the column's foot is battle VFX.

## 3. Rig *(proposed, about 34 bones)*

`root` (at the water), `column_0..2` (the standing water; it sways as one), `spine_0..2`, `neck`, `head`, three per arm
plus `hand`, `hair_l` and `hair_r` (chains of 3), `robe_f`, `robe_b`, `robe_l`, `robe_r` (chains of 3, the mouths ride
them), `key` (a short chain of 2 at the belt). **Anchors (unweighted):** `vfx_core` (the bound heart, on `spine_1`),
`vfx_keepsake` (the key). Grounded through the column: `column_0` stays at y 0 in every clip; nothing goes under.

## 4. Move list *(skill ids proposed; Combat owns them, M4-A2P-025)*

Her identity: **she cycles through all six elements in turn**, in the order the pilgrimage met them (Water,
Lightning, Fire, Ice, Holy, Glimmer). **The next element shows on the timeline** next to her next turn, so the player
always knows what she will do (pillar 4). Each element has its own clip, because what the *water* does carries the
element. The element colours are the battle VFX's (effects.json), on top of her own steady light.

| Skill (id) | Clip | Wind-up → contact (length) | What the water does | Target |
|---|---|---|---|---|
| rise | `rise` | — (3.0 s) | the column climbs out of the water and she forms from it, head last | — |
| idle | `idle`, `idle_b` | — (4.0 s / 1.6 s) | the column sways; the hair falls and falls; `idle_b` she closes her eyes for a breath | — |
| ready | `ready` | — (1.4 s) | the robe's mouths open wider; the hands lift | — |
| `kesh_shift` *(proposed; her free action at turn start)* | `shift` | — (0.9 s) | the whole body goes still, then the robe's mouths turn outward in a ripple from the waist down | self: next element |
| `voice_water` *(proposed)* | `voice_water` | 0.0–0.75 s: she draws water up out of the column into her arms → 0.9 s (1.8 s) | a wave poured forward from both hands | all foes |
| `voice_lightning` *(proposed)* | `voice_lightning` | 0.0–0.6 s: her hair lifts and stands → 0.7 s (1.4 s) | one sharp downward cut of the hand | one foe (ignores defence, as Kahre's lightning does) |
| `voice_fire` *(proposed)* | `voice_fire` | 0.0–0.7 s: the water at her hands boils into steam → 0.8 s (1.6 s) | three quick casts left, right, left | three hits, delay (as Virel's fire does) |
| `voice_ice` *(proposed)* | `voice_ice` | 0.0–0.8 s: **she goes completely still**; a cold haze gathers, nothing freezes → 0.9 s (1.6 s) | the hands open slowly downward | all foes: Ice, Slow |
| `voice_holy` *(proposed)* | `voice_holy` | 0.0–0.7 s: the robe's mouths all open and light inside them → 0.8 s (1.6 s) | a lift of both arms | all allies: cleanse, Regen |
| `voice_glimmer` *(proposed)* | `voice_glimmer` | 0.0–0.8 s: the heart's light shows through her chest → 0.9 s (1.8 s) | both palms pressed flat, as the Level Saint does | all foes: Glimmer; one turn of delay |
| `the_seven` (Swell) | `special` | 0.0–1.8 s: she rises 1 m on the column, every mouth open, arms wide → 1.8 s (3.0 s) | all six at once, then a seventh note | all foes |
| defend | `defend` | — (1.2 s) | the robe wraps forward, mouths closed | — |
| hit | `hit`, `hit_b` | peak 0.1 s | the water shudders through her, the column ripples | — |
| KO | `ko` | — (2.2 s) | she sinks into the column to the shoulders, head bowed | — |
| dismiss | `dismiss` | — (1.2 s) | she pours back down into the water | — |
| victory | `victory` | — (2.2 s) | she straightens and looks up | — |

Act III's held form (the fight before Sefir) needs a `release` clip in which the key is the last thing to fade; it
waits for Act III, as the other three's did.

## 5. Phases

As an ally the six elements are **not stances**: she keeps one stance, and the element lives in the clip and on the
timeline. That keeps it to six clips, not thirty-six. In Act III's fight the six elements become real enemy phases
(Combat's), telegraphed the same way.

## 6. Where she is seen

- **Bind (Ch16 C4), the memory sequence:** a new cinematic look, Kesh's point of view a thousand years ago (cinematics
  and rendering). It needs **Kesh living, as a person** (a Lamplighter, the lamp-key at her belt) and the young Sefir:
  both are the characters track's, not this rig.
- **Battle:** the Vowbound slot, from Act III. In the Choir arena (`drowned_choir_ring`, moon 0.35, sea-glow 0.1) she is
  the brightest thing on the dais; in a daylight arena her water must still read as water (to check on first render).

## Balance, engine, owners

- **Balance:** not used in Act II's fights (bound after the guard fight; the storm sweeps the party away).
- **Engine:** element cycling with a timeline telegraph (gap, M4-A2P-025).
- **Owners:** creatures-b (the art sheet at the gate, model, rig, clips); combat (row, skills, the cycle); cinematics
  and rendering (the memory sequence); characters (living Kesh and young Sefir); battle-presentation (summon, Act III);
  audio (`kesh_bound`).

## Open questions (answered: ADR 0204, 2026-10-30; the drafts stand unless marked)

1. Battle scale: 4.2 m (this draft) or larger with a summon-shot exception? Larger means a new shot for her alone.
2. Is the element order the acquisition order (this draft), or something the bind's memory fixes?
3. Echo check: a boss or ally that cycles its element is a known idea. Ours never hides the change and never shifts
   when struck. Each shift is her own turn and shows on the timeline a turn ahead. Her finisher is named for the verses,
   not for any series' ultimate.

## Built (M4-A2P-057, 2026-10-30)

The model, rig and clips are built: the art sheet is `docs/kb/art/creatures/vowbound/kesh.md` (its "As built"
section has the numbers). For combat, the clip map. Paste it into `kesh` in creatures.json once these ids are in
skills.json; validate_creatures rejects unknown skill ids before that:

```json
"clip_by_skill": {
  "kesh_shift": "shift",
  "voice_water": "voice_water", "voice_lightning": "voice_lightning", "voice_fire": "voice_fire",
  "voice_ice": "voice_ice", "voice_holy": "voice_holy", "voice_glimmer": "voice_glimmer",
  "the_seven": "special"
}
```

Each element also has its own shift beat, `shift_<element>` (`shift_water` ... `shift_glimmer`), for presentation to
play for the element the timeline shows next. The contacts are already in creatures.json:

| Clip | Contact (s) |
|---|---|
| `voice_water` | 0.9 |
| `voice_lightning` | 0.7 |
| `voice_fire` | 0.8 (then 1.05 and 1.3) |
| `voice_ice` | 0.9 |
| `voice_holy` | 0.8 |
| `voice_glimmer` | 0.9 |
| `special` | 1.8 |
| `attack` | 0.55 |
| `cast` | 0.8 |
