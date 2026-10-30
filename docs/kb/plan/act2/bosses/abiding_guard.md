---
draft: pre-gate
adr: 0203
boss: abiding_guard
chapter: 16
owner: characters
---
# Sefir's Abiding guard, Ch16 boss, then the storm wakes: design sheet (draft: pre-gate)

**Model and rig: the characters track's** (people; M4-A2P-051). This sheet writes the design for the fight. **Nothing
exists** except the arena (`drowned_choir_ring`, no baseline yet) and the act2_finals row for `abiding_guard`
(2 stems, a gap: stem 2 is the storm waking early).

**Who:** Sefir's own guard at the Drowned Choir, three of them, after his "go home" is refused. Whether they are
Stillguard elite or the Conclave's revenant guard is narrative's call (open question 1). Either way **the fight shows
nothing that names what they are.** They fight in silence, and they don't look up when the storm wakes.

**What the fight teaches:** the last Act II fight is not the climax; the storm is. Phase 1 is a disciplined group that
protects its leader. Phase 2 is the same fight with the sky failing over it. Then the fight hands over to Kerrid
holding the line (a `scripted_escape` set piece, as Ch8's Reach) and the party is swept away.

**Proposed ids:** `abiding_first` (the leader, the boss row) and `abiding_guard` (two). Sefir is present and watches;
he is not a combatant.

## 1. Silhouette (at 12 m)

- **Three tall pale hooded figures with long poles**, in a shallow arc on the enemy side of the dais. People read
  small at 12 m, so their read is the group's vertical rhythm: each 2.0 m tall in a deep hood, carrying a 3.2 m
  **lamp-hook** (a Lamplighter's pole: a hooked head with an empty iron lamp cage). The leader's hook carries a
  longer, older cage.
- They echo the colossal hooded singers standing in the sea behind them. That is the intended rhyme: small figures
  against huge ones, both hooded, both silent.
- **Facing:** square to the party, hooks upright at rest. The leader stands at the arc's centre (enemy slot 1), half a
  step forward.

## 2. Materials

| Slot (characters' kit) | Swatch | Notes |
|---|---|---|
| `mantle` | `gauze_white` over `order_marble` | heavy, dry; wet and dark at the hem after phase 2's water |
| `shell` | `mortar_white` lacquer plates, `cold_blue_stone` in the shadows | white-lacquered shell armour (the Stillguard's form, not its red) |
| `trim` | `gold_leaf` (edges, ≤ 5% of frame) | the leader only: the cage and the hood's rim |
| `hook` | `brass` worn to `bronze_patina`, `lacquer_black` haft | the cage is empty: **no lamp, no flame** |
| `face` | in deep shadow under the hood | a human face exists (characters), lit only by moon and fill; nothing glows in it |

Arena light: the Choir at moonrise (fill 0.25, the moon low behind the enemy line between two singers, sea-glow 0.1,
`lut_ch16_choir`, stone cold). The figures are the palest values on the dais, so they hold against the dark ring.

## 3. Rig

The characters' human rig per guard, plus a `hook` prop bone (two-handed: both hands IK'd to the haft), a hood cloth
chain, a mantle chain of 3. **Anchors (unweighted):** on the leader `vfx_wound` (chest), `vfx_core` (sternum),
`vfx_phase` (the hook's cage); on the two guards `vfx_core` only. **Grounding:** feet planted on the dais flags at y 0;
phase 2 water rises to the ankles as VFX (never pushes a foot under).

## 4. Move list

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera |
|---|---|---|---|---|---|
| intro | `intro` *(proposed)* | — (2.8 s) | the three step forward from Sefir's side together, hooks lowered as one | — | `boss`, on the leader; Sefir in the back of frame |
| idle | `idle`, `idle_b` | — (4.0 s / 1.6 s) | still; the hood cloth moves in the wind; `idle_b` a grip shift on the haft | — | — |
| ready | `ready` *(proposed)* | — (1.4 s) | the hook comes level | — | — |
| `hook_sweep` *(leader, proposed)* | `hook_sweep` *(proposed)* | 0.0–0.65 s: the hook swings back high over the shoulder → 0.8 s (1.6 s) | a wide sweep at shin height | the front two foes | `boss_sweep` |
| `hook_draw` *(leader, proposed)* | `hook_draw` *(proposed)* | 0.0–0.55 s: the hook reaches out, cage first → 0.7 s (1.5 s) | it hooks a hero and draws them a step out | one foe: delay; strips one buff (`unravel`'s rule) | `target` shot |
| `close_ranks` *(guards, proposed)* | `close_ranks` *(proposed)* | — (1.2 s) | a guard steps in front of the leader, hook across | cover the leader for one turn | — |
| `hook_thrust` *(guards, proposed)* | `hook_thrust` *(proposed)* | 0.0–0.5 s: the haft drawn back to the hip → 0.65 s (1.3 s) | a straight thrust | one foe | — |
| *(phase 2)* `storm_bearing` *(leader, proposed)* | `storm_bearing` *(proposed)* | 0.0–0.8 s: he plants the hook and stands into the wind → 1.0 s (1.8 s) | the three brace and press on | self and allies: `protect`; they ignore the field | they never look at the sky |
| hit | `hit`, `hit_b` *(proposed; each guard)* | peak 0.1 s | a step back, hood snapping | — | no motes, no light |
| phase `storm_wakes` | `storm_brace` *(proposed)* (2.2 s) | — | the water in the ring channel heaves; the three lower their stance and set their feet | — | the Undertow render (M4-A2P-048) starts behind the singers |
| KO (a guard) | `kneel` *(proposed)* | — (2.4 s) | he goes down to one knee, hook upright, head bowed, and **stays kneeling** | — | he does not fall or vanish; he stays in frame to the end |

## 5. Phase change and the hand-over

- **Phase `storm_wakes`:** at turn 6 *or* the leader at 50% HP, whichever comes first (Imra's heart falters on its own
  clock, not because the party is winning).
- **Stance:** lower and wider, the mantles blown toward the party. Every phase-2 clip starts from `idle_storm`
  *(proposed)*.
- **Field:** `storm_rising` (`field_rules`): water to the ankles, a Slow on both sides, rising damage per turn.
- **Hand-over:** when the leader falls to 25% *or* at turn 10, the fight ends by script into the storm set piece:
  Kerrid `locked_active`, "Holding the line", a `scripted_escape` win. The guards don't die; they are still kneeling or
  still standing when the wave comes.
- **What the player learns:** the enemy was never the guard. The storm doesn't wait.

## 6. Arena read (`drowned_choir_ring`)

- **Light:** the Choir at moonrise, low contrast, `lut_ch16_choir`. No `BossAnchor` (a group).
- **Placement:** the three on the enemy slots of the singer's dais (r 7.5). Sefir stands beyond them at the dais edge,
  never in a slot and never between the camera and a fighter.
- **Must never happen:** the hooks crossing the camera ray to a party slot at rest; the storm render's water or spray
  covering the party's faces or the timeline; Sefir's figure taking focus during a telegraph.
- **Camera:** `boss` intro; `the_mouths` low and up at the singers for the storm's phase moment; `the_ring` wide for the
  hand-over.

## Balance, engine, owners

- **Curve:** Act II boss for the guard fight; the storm's waking on the set-piece curve (`scripted_escape` counts as a
  win). Both on the Ch16 loadout.
- **Engine:** cover (`close_ranks`; check the existing cover or provoke rules), a phase trigger on HP *or* turn (check),
  a scripted end into a set piece (Ch8's precedent).
- **Owners:** characters (models, rigs, clips); combat (rows, AI, suites); battle-presentation (the hand-over);
  rendering (the storm render); audio (M4-A2P-092); narrative (who they are, and whether Sefir speaks during it).

## Open questions (answered: ADR 0204, 2026-10-30; the drafts stand unless marked)

1. Stillguard elite or the Conclave's revenant guard? The sheet shows neither (no tell either way), so the art and the
   fight work for both. Narrative decides the bestiary text.
2. Do the guards survive the wave on screen? Draft: we cut away before; nobody sees them again in Act II.
3. Echo check: an antagonist's guard fought at the last holy site before the act break. Our beats differ (the storm
   interrupts the fight, the guard is not the climax, the companion holds the line and the party is swept away). Keep
   any final-form or transformation out of this fight.
