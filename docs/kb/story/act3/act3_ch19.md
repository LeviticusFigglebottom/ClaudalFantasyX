---
draft: pre-gate
---
# Act III Beat Sheet: Ch19 "Iskarra" — the prologue catches up; the anchor-engine; Kerrid's last quiet night (M5)

**draft: pre-gate.** Planning only (the Lead, 2026-10-30). No `.dlg`, flag or data until the Act III gate.

Owner: Narrative (story track). Reviewer: Cinematics. **The Lead reviews the vigil** (ADR 0020 (g): the prologue line is
the human's).
Sources: [act outline Prologue, Ch19](../beats/act_outline.md); ADRs [0017](../../decisions/0017-act-one-restaging.md)
(the vigil), [0020](../../decisions/0020-kerrid-restaging.md) ((g) the line; Kerrid "first down the stair"),
[0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) ((k), sweep notes: nothing groups the three),
[0016](../../decisions/0016-act-two-restaging.md) (revenants first fought openly in Ch19); glossary (*the Abiding*,
*revenant*); [kerrid.md](../characters/kerrid.md) (Act III: teaches Rhen the last of what Dace taught him);
[act3_ending §0 rule 8](../beats/act3_ending.md); tech: battle_arenas.md (Iskarra Lamp Spire), M3-ENV-726, M3-AUD-858.

Previous: [act3_ch18.md](act3_ch18.md). Next: [act3_ch20.md](act3_ch20.md).
Zones: `prologue/iskarra_dusk` (full version), `ch19/iskarra_spire` (a dungeon; M3-ENV-726 builds its crown).

**The rules this chapter must keep:**
1. **The vigil is the Prologue's frame, shot for shot** (ADR 0017): the broken plaza at dusk, all seven **apart**, no
   fire, Kerrid standing, Pell with his back to the sea, Ysolde with her book shut, Asha on the steps; Rhen walks among
   them, never away; he sits by Asha and trims his lantern's wick; it is the only flame. **The line plays verbatim**:
   *"Everyone I'm going to tell you about is still here tonight. Remember that, later."* Nothing is added to it.
2. **Nothing names Imra, Dace and Kerrid together** (act3_ending §0 rule 8; ADR 0022 note). No VO, caption or bark.
3. **The Abiding are fought openly as revenants** here, for the first time (ADR 0016). "Revenant" may be said from this
   chapter; nobody says it with relish. Their hands are the ones Ysolde saw in the Archive's ledgers (Ch13): that is how
   the party knows them.
4. **Held light only.** The spire's light is bound; the defeated Wardens do **not** lift (nothing does before H09).
5. **Kerrid's last night is quiet and practical** (kerrid.md): he teaches, he doesn't confess. No farewell is said.

---

## 0. The chapter in one paragraph

The Kite sets down at dusk on the drowned city where the founders lived, and the party walks out onto the broken plaza
from the first minute of the game. They keep vigil apart, the way they did then; Rhen walks among them, sits by Asha,
trims his wick, and we hear the line we heard at the start, now understood. That night Kerrid sits with Rhen on the
plaza's edge and teaches him a hitch Dace taught him at the rings: one that holds any weight and lets go with a single
pull. In the morning they climb the Lamp Spire, past lamps that have burned since the Lit Age, to the founders'
anchor-engine at its crown, which holds the storm's eye shut. Two of the Abiding keep it, a Warden and a scribe whose
signatures Ysolde last saw on four-hundred-year-old ledgers. They fight as people who have kept a post too long. When
the engine stops, far out at sea the storm opens.

## 1. Running order

| # | Beat | Place | Time | Mode | Min | Flags |
|---|---|---|---|---|---|---|
| I01 | The Kite comes down at Iskarra | the drowned city | dusk | C | 1.5 | `ch19_started` |
| I02 | **The vigil** (the Prologue's frame) | the broken plaza | dusk | P (walk) → C | 4.0 | `ch19_vigil` |
| I03 | **The hitch** (Kerrid and Rhen) | the plaza's edge | night | E (held input) | 4.0 | `ch19_learned_the_hitch` |
| I04 | Ysolde and Asha: the words (optional) | the plaza steps | night | E | 2.0 | `ch19_words_whole` |
| I05 | The spire's foot | `ch19/iskarra_spire` | morning | P | 3.0 | — |
| I06 | **The Lamp Spire** (dungeon) | spire tiers 1–4 | day | P | 25.0 | `ch19_spire_tier_<n>` |
| I07 | The signatures | the crown's antechamber | day | C | 1.5 | — |
| I08 | **Boss: Warden Hesper Oan and Ilsabet Rue** | `iskarra_spire_crown` | day | P | 9.0 | `ch19_abiding_beaten` |
| I09 | **The engine stops** | the crown | day | C | 2.0 | `ch19_engine_stopped` |
| I10 | The eye opens | the crown, looking out to sea | day | C | 1.0 | `ch19_complete` |
| | **Total** | | | | **~53** | |

## 2. Beat detail

### I01. The Kite comes down (C, 1.5 min)
- Gold dusk over drowned white towers, the Prologue's grade (`prologue` color script). Liss sets the Kite on the water
  beside the plaza. Nobody says this is where they were.

### I02. The vigil (P → C, 4 min)
- Rule 1, exactly. Each companion goes to their Prologue place without being told. The walk is the Prologue's controls
  walk again; each companion gets a look or a gesture, no words. **What changes is only what the player knows**: Kerrid
  is unrisen (Ch15), Pell has a name (Ch18), Ysolde's shut book holds the Eighth Verse's words, Asha's sleeve is full.
- Rhen sits by Asha, trims his wick (his oil lantern; not Kell's wick, which stays in the tin until E7). The VO line,
  verbatim. Cut to the vigil wide; hold. Sets `ch19_vigil`.
- **The Prologue's "glimmer rises around him"** is not repeated here (light grammar: nothing rises before H09; see
  act3_threads T-14 for the Prologue).

### I03. The hitch (E, 4 min): Kerrid's last quiet night
- Night. Kerrid sits (he sits since Ch15). Rhen comes over with the lantern. Kerrid has a length of line.
- He teaches the hitch Dace taught him over eight low tides at the rings (kerrid.md): it holds a man's weight on a
  stair, and comes free with one pull on the tail. Held inputs: tie, load, pull.
- Sample (voice only):
  - Kerrid: *"Your father's. He showed me eight times. I got it on the ninth."*
  - Kerrid: *"Holds anything. Then one pull, and it lets go."*
  - Rhen: *"Why are you teaching me this now?"* / Kerrid: *"Somebody should have it."*
- No farewell (rule 5). If `ch17_read_the_ledger`: Rhen tells him what the ledger said about the stair; Kerrid says only
  *"Eight tides. He talked about you every one."* Sets `ch19_learned_the_hitch` (read in H02 and E3: §10 Q3).

### I04. The words (optional, E, 2 min)
- Ysolde and Asha on the steps. Ysolde has the Eighth Verse whole: the words from the Choir stones (Ch16), the tune read
  through the farewell-tide (Ch18), and its place from Ama's question-knot (Ch12). She reads the words aloud, **spoken, not sung** (README rule 3). Asha
  repeats them once, spoken. *"Never the words and the tune together,"* Ysolde says. *"Not until it's time."* Then, dry, never a joke (ending_cost_audit §6): *"I came to give you a good death. I would like to give you a long,
  dull life instead."* Sets `ch19_words_whole`.

### I05–I06. The Lamp Spire (P, ~28 min)
- Four tiers up the founders' lamp-tower: Lit Age lamps still burning (bound, steady), lamp-engines, conduits, the
  founders' living quarters preserved like a museum. Act III regulars; lamp puzzles on Liss's tools (the conduit routing
  from Ch11, harder). Kerrid leads on every stair (ADR 0020: first down — here, first up).
- Records on the way (the document reader): the founders' household notes, plain and human (a child's height marks on
  a door frame). Nothing new about the binding beyond Ch13's ledgers.

### I07. The signatures (C, 1.5 min)
- The crown's antechamber: a lectern with a duty roll. Ysolde turns it: the same two hands, signing every watch, for four
  hundred years. *"I've seen these hands. In the Archive. On every page."* (rule 3).

### I08. Boss: Warden Hesper Oan and Ilsabet Rue (P, 9 min). See §5.

### I09. The engine stops (C, 2 min)
- Liss shuts the anchor-engine down: a Lit Age lever and three held inputs. As it winds down the spire's lamps don't go
  out (they're bound; only H09 frees them) but they **stop being fed**: the hum stops. Liss: *"That's the first one."*
- The Wardens lie still on the crown's floor, their light held in them (rule 4). Toma closes Hesper Oan's eyes.

### I10. The eye opens (C, 1 min)
- From the crown, far out at sea: the Undertow's wall turns, and at its centre a calm opens, a well of dark water going
  down. Kerrid: *"There's the stair."* Sets `ch19_complete`.

## 3. Flags
| Flag | Set at | Read by | Use |
|---|---|---|---|
| `ch19_started`, `ch19_complete` | I01, I10 | flow | — |
| `ch19_vigil` | I02 | — | — |
| `ch19_learned_the_hitch` | I03 (critical) | H02, E3 | Rhen ties Dace's hitch in the heart; Kerrid sees it before he goes |
| `ch19_words_whole` | I04 (optional) | H07 | Asha says the words faster in the Letting countdown (Design: a small timeline bonus, §10 Q4) |
| `ch19_spire_tier_<n>` | I06 | save, map | — |
| `ch19_abiding_beaten` | I08 | Ch20, H04 | Sefir knows two of his have fallen |
| `ch19_engine_stopped` | I09 | Ch20 | the way in |

**Reads:** `ch17_read_the_ledger` (I03), `ch18_learned_farewell_tide`, `ch17_verse_begun`, `ch12_ysolde_confessed`
(I04), `ch13_read_ledgers` (I07), `ch15_kerrid_revealed` (I02, I03), `ch16_line_held` (I06).

## 4. No side scene
The vigil and the hitch are the chapter's quiet. Optional content is the spire's records and I04.

## 5. The boss: Warden Hesper Oan and Ilsabet Rue (I08)
- **Who they are:** two of the Abiding, the Order's hidden leadership: a Warden (Hesper Oan) and the scribe who kept her
  watch roll (Ilsabet Rue), held alive by bound light for four hundred years at the post the founders gave them. Sincere,
  tired, and certain. They are not Sefir's mouthpieces; they believe the engine is mercy.
- **Lines (combat, ~40 words):** Hesper: *"Go home, children. We have this watch."* / at 50%: *"Four hundred years and
  nobody has asked to relieve us."* Ilsabet (writing as she fights): *"Noted."* / at the end: *"Mark the time."*
- **Kerrid and Hesper** (one exchange, the dead to the dead, mid-fight): Hesper: *"You kept a watch."* Kerrid: *"I did.
  I'd have liked relieving."*
- **Mechanics** (Combat's call): a pair; Ilsabet's roll records the party's last three actions and Hesper answers the
  most frequent (the watch-roll); break the roll to reset it. Music: M3-AUD-858's `hesper_and_ilsabet` (exists: two
  cadences that never overlap).
- **When they fall** they lie still; nothing rises (rule 4).

## 6. Music cues
`prologue_vigil` (I02: the Prologue's cue, same mix; the only change is that Act III's sea-glow sits under it),
`kerrid_hitch` (I03: no melody; rope, water, one held note at the pull), `iskarra_spire` (I05–I06),
`hesper_and_ilsabet` (exists, M3-AUD-858), `engine_down` (I09: the hum stopping is the cue), `the_eye` (I10).

## 7. Camera shots (proposals)
The Prologue's shot list for I02, reused frame for frame (Cinematics owns it). I03: two-shot on the plaza edge, the
line between their hands. I07: insert, the duty roll's two hands. I10: the eye from the crown, the Kite small below.

## 8. Word counts
I02 ~20 (the VO line only), I03 ~140, I04 ~100, I05–I07 records ~250 read, I08 combat ~60, I09–I10 ~50, barks ~120.
**~490 spoken + ~250 read.** Under SPEC §3.6's band by design: this chapter is the quiet before the dive.

## 9. Requests to other roles
- **Cinematics:** the Prologue vigil reused shot for shot (rule 1).
- **Environment Art:** `ch19/iskarra_spire` tiers 1–4 (M3-ENV-726 builds the crown); the founders' household rooms.
- **Combat:** the Warden pair (§5).
- **Audio:** §6 (`hesper_and_ilsabet` exists).
- **Characters:** Kerrid's `teach_hitch` clip; Rhen's `tie_hitch`.

## 10. Open questions and defaults
1. **Warden Malcor Venn.** act2_ch14's flag table promised Venn "fought again, openly a revenant, in Ch19", but the
   outline's Ch19 bosses are Hesper Oan and Ilsabet Rue. **Default:** Venn is not refought; he isn't one of the Abiding
   (a living man doing what he believed). act2_ch14's row is corrected (act3_threads T-05).
2. **The Prologue's rising glimmer** (act_outline Prologue: "Glimmer rises around him"). **Default:** I02 doesn't repeat
   it; the Prologue's own beat sheet should make it drift, not rise (act3_threads T-14).
3. **The hitch** is a new prop of meaning (it holds, then lets go). **Default:** paid in H02 (Rhen ties it on Dace's
   lamp-line in the heart) and seen by Kerrid in E3 before he goes. act3_ending owns those beats; it adds one insert each.
4. **`ch19_words_whole`'s timeline bonus** in the Letting is Design's call. **Default:** none; the scene alone.
5. **How many Abiding are there?** Glossary: "glimmer-sustained revenants who lead the Order in secret". **Default:**
   the Conclave's five plus their keepers; two fall here; Sefir gathers the rest into the storm (sefir_aurane.md Act III).
