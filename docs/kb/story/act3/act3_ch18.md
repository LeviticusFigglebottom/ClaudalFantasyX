---
draft: pre-gate
---
# Act III Beat Sheet: Ch18 "The Kite" — the world opens; Pell turns around; Haluna lifts its own (M5)

**draft: pre-gate.** Planning only (the Lead, 2026-10-30). No `.dlg`, flag or data until the Act III gate.

Owner: Narrative (story track). Reviewer: Cinematics; **Design** reviews §4–§5 (the open world's shape, SPEC §6.6).
Sources: [act outline Ch18](../beats/act_outline.md); SPEC §3.5 (ship-of-the-air), §6.6 (the Kite world map, secret
coordinates); ADR [0016](../../decisions/0016-act-two-restaging.md) (Ch18 row); characters: [Pell](../characters/pell.md),
[Toma](../characters/toma_okeru.md), [Asha](../characters/asha_velamir.md), [Liss](../characters/liss_varrow.md); Act I
and II flags (§3); [vowbound §1, §5](../vowbound.md).

Previous: [act3_ch17.md](act3_ch17.md). Next: [act3_ch19.md](act3_ch19.md).
Zones: `ch18/kite` (the hub: deck, engine room, cabin, the chart table), Reedhollow (`ch10/reedhollow`, revisited), and
the revisits in §4. The world map is the Kite's (SPEC §6.6).

**The rules this chapter must keep:**
1. **The critical path is short**: maiden flight → Reedhollow → back aboard. Everything else is offered, never forced.
2. **Pell turns around** (pell.md): he tells the elders he will turn around at last, and his name is carved again on a
   new shell. He teaches Asha the farewell-tide **wordless**: the melody that holds the Eighth Verse (README rule 3).
3. **Every revisited town has changed**, and its side scene shows how its grief has changed, not its quest log.
4. **Nothing is lifted by Asha.** Haluna's dead are lifted by Haluna, in the Kirru way, led by Toma (optional,
   flagged). Asha watches. The Cantor doesn't perform it; the town does.
5. **Held light in every town until H09.** A lifting rite in Act III lifts what it can (a few motes rise, as in Ch10);
   the storm still holds the rest.

---

## 0. The chapter in one paragraph

The Kite rises off Hollowmere's water on Dace's sails and Liss's engines, and for the first time the party can go
anywhere. The world they flew over on foot looks smaller and kinder from the air, and every town in it has changed since
they passed: Oruvel is being rebuilt on new hulls, Haluna has a new name-shell in its wake wall, Corrow's stair has a
watch again. The one road that must be taken goes back to Reedhollow. Pell walks in through the gate he was kept out of,
tells the eldest he will turn around next time, and Owa carves his name on a new shell. That evening, on the shore, he
teaches Asha the farewell-tide without words. If the player brings the Kite to Haluna, Toma gathers the village and they
lift their own dead the Kirru way, with their backs to the water; Asha stands at the back.

## 1. Running order (critical path, then offered)

| # | Beat | Place | Mode | Min | Flags |
|---|---|---|---|---|---|
| K01 | **Maiden flight** | `ch18/kite`, over Hollowmere | C → P | 3.0 | `ch18_started` |
| K02 | The chart table (the world opens) | Kite cabin | E | 1.5 | `ch18_world_open` |
| K03 | **Reedhollow: through the gate** | `ch10/reedhollow` gate | C | 2.0 | — |
| K04 | **The new shell** | the clutch's stone | C | 3.0 | `ch18_pell_named` |
| K05 | **The farewell-tide, taught** | the shore, dusk | E (held input) | 4.0 | `ch18_learned_farewell_tide` |
| K06 | The child, older (optional) | Reedhollow | E | 1.5 | `ch18_child_answered` |
| — | **Offered** (any order; §4): Haluna (and the lifting), Oruvel, Pemakar, Tamsule, Corrow, Quellan, Ansedra (closed; one scene), Hollowmere; heirloom errands (§5); secret coordinates | the Kite map | P | 60–120 | per town |
| K07 | The Kite at night (party talk) | Kite deck | E | 3.0 | `ch18_night_aboard` |
| K08 | "Iskarra." | the chart table | C | 1.0 | `ch18_complete` |
| | **Critical path** | | | **~18** | |

## 2. Beat detail

### K01. Maiden flight (C → P, 3 min)
- The hull lifts on Liss's held count (three held inputs, the bench rhythm again if `ch11_lamp_repaired`). Dace's sails
  fill: the flare-kite cut. Liss, at the wheel, says nothing for the whole lift; then: *"He'd have hated the trim."*
- First control of the Kite over Hollowmere's flotilla; the hull-captains' current-song from below.

### K02. The chart table (E, 1.5 min)
- Dace's charts (Corrow circled), Ysolde's keth notes, Liss's engine log. The world map opens (SPEC §6.6). Ysolde: *"I
  have the words. Pell has the tune. We go to Reedhollow."* (pays Ch17 B11).

### K03. Reedhollow: through the gate (C, 2 min)
- The same gate as Ch10 (`ch10_pell_kept_out`). Pell walks in first this time. The clutch doesn't stop him; they turn to
  see who it is. Owa meets him at the clutch's stone.

### K04. The new shell (C, 3 min)
- Pell to Owa (sample, voice only): *"Next time, I will turn around."* Owa: *"Then you may have your name back."*
- The shell-carver from Ch10 (`ch10_bark_kirru_shellcarver`) carves it. The scraped shell goes into the lagoon; Pell
  does not watch it sink (he turns his back: the first time). Costume state change: the new shell (pell.md).
- If `ch11_pell_knelt`: Owa says she heard where he knelt. Sets `ch18_pell_named`.

### K05. The farewell-tide, taught (E, 4 min)
- Dusk, the shore. Pell teaches Asha the tune, wordless, the way Kirru children learn it: hum, then turn your back,
  then hum again. Held inputs on the turn (the player turns Asha's back). The clutch hums under them.
- Ysolde writes the melody's shape in her book, no notes, only rises and falls. *"That's the Letting."* (said once).
- Asha never sings words here (README rule 3).
- **The trade** (ending_cost_audit §1): when Pell is done, Asha hums the Velamir lullaby back to him, unasked: her
  family's song for his people's. It is the only time in the game she hums something just because she wants to, and
  nobody says it's the last. Rhen hears it from the shore's edge. Sets `ch18_learned_farewell_tide`.

### K06. The child, older (optional, E, 1.5 min)
- If `ch10_child_asked`: the Kirru child from Ch10, a year older, asks Asha a second question (act2_ch10 flag table):
  *"Will you turn around, when it's yours?"* Asha: *"I hope someone will turn around for me."* Sets
  `ch18_child_answered`.

### K07. The Kite at night (E, 3 min)
- After any number of revisits; the party on deck. One talk per pair the player has seen in camp (Ch10–16 camp flags):
  each pair gets one more short exchange (§10 Q4). Kerrid stands at the stern rail.

### K08. "Iskarra." (C, 1 min)
- At the chart table Kerrid puts his finger on the drowned city. *"Where it started. Where we go in."* (The anchor-engine
  is Ch19's; nobody explains it here.) Sets `ch18_complete`.

## 3. Flags
| Flag | Set at | Read by | Use |
|---|---|---|---|
| `ch18_started`, `ch18_world_open`, `ch18_complete` | K01, K02, K08 | flow, map | — |
| `ch18_pell_named` | K04 (critical) | Ch20 Nhoa, codex, costume | Pell's new shell |
| `ch18_learned_farewell_tide` | K05 (critical) | Ch19, H07 | the tune half of the Eighth Verse |
| `ch18_child_answered` | K06 (optional) | — | — |
| `ch18_haluna_lifted` | §4 Haluna (optional, flagged) | Ch20 Ilun, Ending (Toma's beach) | Toma's arc |
| `ch18_heirloom_<hero>` | §5 | Ch20/21 | per hero |
| `ch18_night_aboard` | K07 | — | — |

**Reads from Acts I–II:** `ch10_pell_kept_out` (K03), `ch11_pell_knelt` (K04), `ch10_child_asked` (K06),
`ch10_farewell_tide_seen` (K05: Asha has seen it from the back), `ch11_lamp_repaired` (K01), `ch04_shell_set`,
`ch15_toma_confessed`, `ch09_toma_knelt_with_ivo` (Haluna, Corrow), `ch07_told_tavi`, `ch07_blessed_moorings`
(Oruvel, Tamsule), `ch05_told_the_smith` (Pemakar), `ch14_merel_taken` (Ansedra), `ch17_first_berth` (Hollowmere).

## 4. The revisits (offered; one side scene each)
| Town | What changed | Side scene | Reads |
|---|---|---|---|
| **Haluna** | Asha's shell in the wake wall (`ch04_shell_set`) | **"Backs to the Water"** (optional, flagged): Toma gathers the village and they lift their own dead the Kirru way. A few motes rise; most don't (the storm still holds). Asha stands at the back. Toma's line: *"We don't need a Cantor for this. We need each other."* Sets `ch18_haluna_lifted`. | `ch15_toma_confessed`, `ch10_farewell_tide_seen` |
| **Oruvel** | new hulls lashed to the old keel-hull; a rebuild begun | Tavi has come to help (if `ch07_told_tavi`); Kell's stall is an empty frame on the second mooring. Rhen doesn't touch the wick. | `ch07_told_tavi` |
| **Pemakar** | the mooring rings for the boats | Garo's boat-folding, now for others (if `ch05_told_the_smith`). | `ch05_told_the_smith` |
| **Tamsule** | the Reefball season restarted | the moorings with Pio's band (if `ch07_blessed_moorings`). | `ch07_blessed_moorings` |
| **Corrow** | a watch on the Fisher Stair again | Marra's child keeps the stair at dusk; Kerrid watches from the Kite and doesn't land. Toma at Ivo's stone (if `ch09_toma_knelt_with_ivo`). | `ch09_heard_stair_clear`, `ch09_toma_knelt_with_ivo` |
| **Quellan** | Dorro's daughter has tied a new cord | the pass-cords from the air; one bark. | `ch12_returned_herd_cord` |
| **Ansedra** | closed to heretics: the Kite can't land | one scene from the air: Merel at a window of her father's house; a red thread on the sill (§10 Q2). | `ch14_merel_taken` |
| **Hollowmere** | the dock-master working again | if `ch17_first_berth`, he's teaching windmills (the epilogue's seed for Liss). | `ch17_first_berth` |

## 5. Heirloom errands (one per hero, each tied to someone they lost; SPEC §6.6)
Defaults (Design and Progression own the rewards; Narrative owns the person):
| Hero | Someone lost | Heirloom (weapon) | Where |
|---|---|---|---|
| Rhen | Dace | Dace's diving hooks, from the hull's tool rack, re-edged | Hollowmere (Ch17's rack) |
| Asha | Imra | Imra's lantern-staff, from the Velamir house | Haluna |
| Toma | Ivo | Ivo's boarding spear, from the Corrow armoury the watch reopened | Corrow |
| Ysolde | Corran | Corran's recipe book, bound as her folding book (he was a terrible cook) | Ansedra, by courier (she can't land) |
| Liss | Tobin | a launcher built from Tobin's tide-wheel drawings | Hollowmere |
| Kerrid | his watch of fishers | the stair-watch's anchor, from the stair foot | Corrow (he lands for this one) |
| Pell | Ressa | Ressa's reed-spear, given by Owa | Reedhollow (needs `ch18_pell_named`) |

## 6. Music cues (requests)
`kite_theme` (K01; the engine tone from Ch17 B10 becomes melody), `reedhollow_return` (K03–K04), `farewell_tide`
(K05: the Ch10 cue, now taught; Audio: a version with one voice, Asha's hum, and the clutch under it), `haluna_lifting`
(§4 Haluna), `kite_night` (K07).

## 7. Camera shots (proposals)
K01 the hull leaving the water, sails filling · K03 Pell first through the gate, the clutch turning · K04 insert: the new
shell, carved side out · K04 the old shell sinking, Pell's back to it · K05 two backs to the water, Asha and Pell · §4
Haluna: the village's backs, a few motes rising behind them.

## 8. Word counts
Critical path ~650 (K01–K08). Revisit side scenes ~150 each × 8 = ~1,200. Heirloom errands ~80 each × 7 = ~560.
**~2,400 total, ~650 critical.** The critical path is short on purpose (rule 1).

## 9. Requests to other roles
- **Design:** the Kite world map, landing rules (Ansedra closed), secret coordinates (SPEC §6.6).
- **Progression/Combat:** heirloom weapons (§5); Act III shop tiers in revisited towns.
- **Environment Art:** each revisited town's changed state (a `variants` row per town on `ch17_complete`).
- **Character Art:** Pell's new name-shell; Asha's sleeve stays S7.
- **Audio:** §6.

## 10. Open questions and defaults
1. **Is the Haluna lifting optional?** act_outline: "optional flagged scene". **Default:** optional, but its flag pays in
   the Ending (Toma's beach) and Ch20 (Ilun), so the game is warmer with it, never broken without it.
2. **Merel's fate** (act2_ch14 flag table: "Narrative's call"). **Default:** she lives, kept in her father's house; seen
   once from the air, a red thread on the sill. No rescue (the Kite can't land; the cost stays seen).
3. **Kell.** **Default:** Kell is not seen in Act III. Her stall is an empty frame; the wick stays in Rhen's tin until E7.
4. **K07's pair talks** draw on which camp talks the player saw (Ch10–16 `ch1N_camp_talk`). **Default:** one follow-up
   line each, optional; if none were seen, K07 plays the generic deck scene.
5. **Ansedra's heretic state** holds in Act III. **Default:** no landing; no shop; one scene from the air.
6. **Order of revisits** is free. **Default:** the Kite map highlights Haluna first after Reedhollow (Asha's home).
