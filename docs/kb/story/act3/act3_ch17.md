---
draft: pre-gate
---
# Act III Beat Sheet: Ch17 "Hollowmere" — Dace's dry-dock, the ledger, the choice (M5)

**draft: pre-gate.** Planning only (the Lead, 2026-10-30): Act III production is paused. No `.dlg`, flag or data is
built from this sheet until the Act III gate.

Owner: Narrative (story track). Reviewer: Cinematics (SPEC §12.3). **The Lead reviews it too**: the decision to unbind is
the act's hinge.
Sources: [act outline Ch17](../beats/act_outline.md); ADRs [0016](../../decisions/0016-act-two-restaging.md) (Ch17 row),
[0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) ((j), sweep notes S4, S6, J), [0020](../../decisions/0020-kerrid-restaging.md);
decisions_log N-26; [bible §3, §7, §10](../bible.md); characters: [Rhen](../characters/rhen_sallow.md),
[Liss](../characters/liss_varrow.md), [Asha](../characters/asha_velamir.md), [Ysolde](../characters/ysolde.md),
[Kerrid](../characters/kerrid.md); [vowbound §3 Virel](../vowbound.md) (the Kite's sails); Act II:
[act2_ch15.md](../beats/act2_ch15.md), [act2_ch16.md](../beats/act2_ch16.md).

Previous chapter: [act2_ch16.md](../beats/act2_ch16.md). Next: [act3_ch18.md](act3_ch18.md).
Zone: `ch17/hollowmere` (exists as Ch15's map; the dry-dock berths and Dace's hull are new rooms).

**The rules this chapter must keep:**
1. **The ledger is read, never voiced.** Dace's logs are a written ledger on screen (N-26 watch, ADR 0022 sweep-J S1). No
   VO in Dace's voice, no flashback of him speaking. Rhen reads; the player reads with him.
2. **The ledger's facts are exact** (act_outline Ch17; ADR 0022 S4, S6):
   - Rhen's name is in every entry;
   - the stair, the comb carried to Haluna, a Cantor whose name Dace learned only on the stair;
   - why he never went home: torn sleeves, the line-marks seen, the Bastion asking for the marked diver by morning; a
     hunted Saltwright going home brings the Order to Oruvel and to his son; Haluna he risked once, after dark;
   - "Kell. Of course." comes **first** among the Rhen entries a season after Corrow;
   - the **last** entry, the night he went into the storm after Imra: *"If I bring him here he's a wright's son for life.
     Oruvel thinks he's a diver's boy. Let him be one. After the storm"* — and it breaks off. The next page is blank and so
     is every page after it.
   - **The reasons never fully excuse him** (ADR 0022 watch). Nobody in the scene says they do.
3. **Asha chooses the Unbinding in her own words**, after Ch16's truth and refusal, and she says what it costs out loud
   once: everything bound goes. Not a vow, not a speech.
4. **Liss's father has not spoken since the night of the pyre-raft** (act_outline): his last words were at the Ch15
   supper, if the player had it (§10 Q1).
5. **Held light only.** Hollowmere's lamps are held cyan; nothing rises.

---

## 0. The chapter in one paragraph

The Hollowmere ship that waited at the Rim finds the party in the morning, clinging to Choir stone in a sea gone flat
and wrong, and brings them home to the flotilla. Hollowmere takes them in without asking. Liss's father has not said a
word since the pyre-raft; he shows them the dry-dock by pointing. In the last berth stands a hull nobody has touched in
eleven years: Dace Sallow's unfinished ship, sails cut to a shape no Saltwright has seen. In its cabin is the ledger.
Rhen reads it with Liss beside him and finds his own name in every entry, the stair, the comb, why his father never
came home, and that Dace went into the storm on purpose, after Imra. That night, on the hull's deck, Asha tells them she
won't sing herself in and won't go home: she will end it, and everything bound will go with it. Liss starts on the
engines the next morning. Ysolde starts on the words.

## 1. Running order

| # | Beat | Place | Time | Mode | Min | Flags |
|---|---|---|---|---|---|---|
| B01 | **Pulled from the sea** | open water off the Rim → the ship's deck | dawn | C | 2.0 | `ch17_started` |
| B02 | The flotilla takes them in | `ch17/hollowmere` dock | morning | P | 4.0 | — |
| B03 | The dock-master points | dry-dock berths | noon | C | 1.5 | `ch17_saw_the_hull` |
| B04 | **Dace's hull** | the last berth | noon | P | 3.0 | — |
| B05 | **The ledger** | the hull's cabin | afternoon | E (held page-turns) | 6.0 | `ch17_read_the_ledger` |
| B06 | After the blank page | the hull's deck | dusk | C | 1.5 | — |
| B07 | Side scene (optional): "The First Berth" | the dock-master's berth | dusk | E | 4.0 | `ch17_first_berth` |
| B08 | **The choice** | the hull's deck | night | C | 4.0 | `ch17_chose_the_unbinding` |
| B09 | Kesh, once more (optional bark) | the hull's deck | night | E | 0.5 | — |
| B10 | The first lamp | the hull's engine room | next morning | E (held input) | 2.0 | `ch17_first_lamp_lit` |
| B11 | Ysolde's table | the dock-master's house | next morning | C | 1.5 | `ch17_verse_begun` |
| B12 | Hollowmere at work (field, barks, shop, inn) | the flotilla | day | P | 6.0 | — |
| | **Total** | | | | **~36** | `ch17_complete` |

## 2. Beat detail

### B01. Pulled from the sea (C, 2 min)
- After Ch16's swept-away: grey dawn, flat sea, the party in the water among broken Choir stone. The Hollowmere ship's
  current-song comes before the ship does (`ch15_hollowmere_answered`: the same song Liss sang into the fog).
- Kerrid is the last hauled up, as on a stair (he holds the rope for each of them first). Nobody remarks it.
- Asha's sleeve: full (S7). She holds it in her fist the whole way up.

### B02. The flotilla takes them in (P, 4 min)
- Free walk. Hollowmere is quieter than Ch15: Tobin's absence, the cracked lamp on Liss's back. Barks are kind and
  practical. The tally hull (if `ch15_toma_on_the_tally`): the keeper nods to Toma.

### B03. The dock-master points (C, 1.5 min)
- Aldous Varrow hasn't spoken since the pyre-raft. He walks them to the berths and points at the last one. If
  `ch15_toma_carried_tobin`: he nods once to Toma first (act2_ch15 flag table).

### B04. Dace's hull (P, 3 min)
- An unfinished lashed-hull airship: ribs, a keel of Lit Age brass, Saltwright sails cut like a flare-kite. Liss stops:
  *"That's not a Saltwright cut."* (Virel's shape: Liss knows it only in Ch20; plant it, don't pay it.)
- Interactables: the tool rack (his hooks, the same make as Rhen's), the chart wall (Corrow circled), the cabin door.

### B05. The ledger (E, 6 min): the chapter's centre
- Rhen sits; Liss sits beside him (if `ch11_lamp_repaired`: she hands him the lamp to read by, without a word, the same
  way as at the bench). Held page-turns; each page is the ledger on screen, Rhen's lines between.
- The order of what the player reads (rule 2): the stair → the comb at Haluna, sleeves down, after dark → the marks and
  the Bastion → "Kell. Of course." → the hull begun "to follow her" → the last entry → the blank page, and every page
  after it blank (the page-turn lands on blank and nothing follows: ADR 0022 sweep-J).
- Rhen's lines are few. Sample (voice only): *"He knew where I was."* / *"He knew where I was the whole time."* At the
  blank: nothing. He turns two more blank pages himself, then stops.
- If `ch12_rhen_tied_knot`: he touches the place on his wrist where the cord rubbed. No line.
- Sets `ch17_read_the_ledger`. This is where Rhen learns Dace went into the storm **on purpose**, after Imra. Kerrid
  never knew it (rule: ADR 0022).

### B06. After the blank page (C, 1.5 min)
- Rhen on the hull's deck at dusk. Kerrid is there (standing). Kerrid: one line, plain: *"He was first down the stair.
  He'd have been first into that, too."* Rhen doesn't answer. Kerrid stays.

### B07. Side scene (optional): "The First Berth" (E, 4 min). See §4.

### B08. The choice (C, 4 min): the hinge
- Night, the hull's deck, the whole party. Asha speaks first and plainly (her voice: gentle, precise, unbending). What
  she says, in her own words (sample, voice only):
  - *"I'm not going to sing myself in. And I'm not going home to sing nothing."*
  - *"I'm going to end it. All of it."*
  - the cost, said once: *"Everything that's held goes. The lamps. Their engines. Ressa. Corran. Kerrid."*
- Each companion's answer is one line, and none of them is a vow (rule 3). Liss's is the hardest and comes last:
  *"Then I'd better build you something that gets you there."* (her pillar 6: she builds the rig anyway).
- Kerrid's: *"First down the stair."* (ADR 0020: he leads them in).
- Sets `ch17_chose_the_unbinding`.

### B09. Kesh, once more (optional bark, E, 0.5 min)
- If the player opens the Vowbound menu here: Kesh's call bark changes (she knows what Asha chose). One line.

### B10. The first lamp (E, 2 min)
- Morning, the hull's engine room. Liss and Rhen fit the Kite's first lamp the way they mended the Ch11 lamp, with
  three held inputs; if `ch11_lamp_repaired` the inputs are the same rhythm (the player's hands remember).
- **The lamp is bound light**, and Liss says so: the Kite flies on the held dead, the way everything Saltwright does.
  *"It'll fly on them. To let them go."* Nobody answers that. Sets `ch17_first_lamp_lit`.

### B11. Ysolde's table (C, 1.5 min)
- The dock-master's house; Ysolde lays out three sources on the table: the keth count (Ch12), her Choir-stone rubbings
  (Ch16), and a blank page for the Kirru song she doesn't have yet. *"Words I can do. The tune isn't mine to learn."*
  (Pays forward to Ch18: Pell.) Sets `ch17_verse_begun`.

### B12. Hollowmere at work (P, 6 min)
- Field: the chandler (Act III stock), the inn, barks. Optional: Toma at the tally hull; Pell watching the windmills;
  Ysolde asleep over the keth. The chapter ends when the player boards the hull (`ch17_complete`); Ch18 opens on the
  maiden flight.

## 3. Flags
| Flag | Set at | Read by | Use |
|---|---|---|---|
| `ch17_started` | B01 | flow | chapter step |
| `ch17_saw_the_hull` | B03 | objectives | — |
| `ch17_read_the_ledger` | B05 (critical) | Ch18, Ch19, Ch21 H02, E2 | Rhen knows why; his Ch19 night with Kerrid; E2's "this time he says it back" |
| `ch17_first_berth` | B07 (optional) | Ch18 (Hollowmere revisit), E2 | the dock-master speaks again |
| `ch17_chose_the_unbinding` | B08 (critical) | every Act III chapter | the act's premise |
| `ch17_first_lamp_lit` | B10 | Ch18 | the Kite's lamps |
| `ch17_verse_begun` | B11 | Ch18, Ch19 | the Eighth Verse thread |
| `ch17_complete` | B12 | flow | — |

**Reads from Act II:** `ch15_hollowmere_answered` (B01), `ch15_toma_on_the_tally` (B02), `ch15_toma_carried_tobin`
(B03), `ch11_lamp_repaired` (B05, B10), `ch12_rhen_tied_knot` (B05), `ch15_supper_with_father` (B07),
`ch14_spoke_with_tobin` (B07), `ch16_learned_the_hush`, `ch16_refused_sefir` (B08), `ch16_kesh_bound` (B09),
`ch12_ysolde_confessed` (B11).

## 4. The optional side scene: "The First Berth" (B07)
- The dock-master breaks his silence for Rhen: he shows him the berth where Dace built his first hull, thirty years ago,
  and says the first words he has said since the pyre-raft. Two of them are about Dace; the third is about Tobin.
- Sample (voice only): *"Your father built his first hull here. Badly."* / *"Tobin used to sit on that post and tell him
  so."*
- If `ch15_supper_with_father`: he starts more readily (act2_ch15 flag table: "more readily"); if
  `ch14_spoke_with_tobin`: Rhen can tell him what Tobin said before the vows. Sets `ch17_first_berth`.

## 5. No boss
Ch17 has no boss and no forced fight (the act's breath after Ch16). Optional fights only on the flotilla's outer
moorings (Act III regulars).

## 6. Music cues (requests; none exist)
`hollowmere_morning` (B01–B02, the current-song family, never Dace's), `dace_ledger` (B05: a solo instrument that stops
on the blank page — the stop is the cue), `the_choice` (B08, bed only; it does not resolve), `kite_first_lamp` (B10,
a held tone that becomes the Kite's engine theme).

## 7. Camera shots by beat (proposals)
H01 the ship's bow through fog (B01) · H02 Kerrid's hand on the rope, last (B01) · H03 the dock-master's arm, pointing
(B03) · H04 the hull in its berth, sails half-rigged (B04) · H05 insert: the ledger, Rhen's name (B05) · H06 insert: the
blank page (B05) · H07 the deck, Rhen and Kerrid not looking at each other (B06) · H08 the party in a ring on the deck,
Asha standing (B08) · H09 the first lamp's held cyan (B10).

## 8. Word counts
B05 ledger text ~450 (on screen, read), B05 lines ~60, B06 ~40, B07 ~180, B08 ~220, B10 ~40, B11 ~60, barks ~150.
**~1,200 spoken + ~450 read.** SPEC §3.6 band for ~36 min: 880–1,300 spoken. In band.

## 9. Requests to other roles
- **Environment Art:** the dry-dock berths and Dace's hull (unfinished Kite) at `ch17/hollowmere`.
- **Character Art:** Liss carries Tobin's cracked lamp (ADR 0204 §13) — it was left on the ship in Ch16; she has it
  back from B01.
- **UI:** the ledger reader (the document reader, M4-A2P-080, with held page-turns and a blank-page end).
- **Audio:** §6.
- **Combat/Progression:** Act III shop tier at the chandler.

## 10. Open questions and defaults
1. **The Ch15 supper vs "hasn't spoken since the pyre-raft".** Ch15's B14 side scene (`ch15_two_daces`, scripted, eight
   lines for the dock-master) comes *after* the pyre-raft (B13), the same night. **Default:** his silence starts after
   that supper: "since the night of the pyre-raft". act_outline Ch17's line gets that one-word fix (act3_threads T-03).
   If the player skipped the supper, his last words were at the pyre.
2. **Where the Kite's power comes from.** **Default:** bound light, said aloud once (B10). If the Lead prefers the Kite
   on wind and oil until a late refit, cut B10's line and move the moral beat to Ch20's dive rig.
3. **Tobin's lamp.** **Default:** Liss carries it and tries to mend the crack in Ch18 and can't. At Ch20 U00 she seats
   it in the Kite's engine (ending_cost_audit §4); it is released at H09 with everything else. No scene in Ch17 beyond
   carrying it.
4. **Kerrid's B06 line** is the only Kerrid line in Ch17 apart from B08. Cut if it reads as explaining Dace for him.
5. **The flotilla's safety.** The Order's patrols (Ch15) are not seen in Ch17. **Default:** a lookout bark only.
