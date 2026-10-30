# Lamptongue: the Hush's verses and the sung texts (Audio)

Lamptongue is the old Iskarran liturgical language of the Hush (glossary). Audio owns its lyrics (act2-plan, the
drafts README; the Lead, 2026-10-30). This sheet fixes the text of every verse and every Lamptongue line a script or
draft leaves to Audio. Where it gives a text, scripts and drafts take it **as written**: lines stay `#notr` and
`#lamptongue`, and the translation is never shown in the game. Only Ysolde's help lines translate, where a draft asks.

The voice question is open (SPEC §16 Q4/Q5). Until it closes, the sung lines are carried by the vocalise: the breath
flute shaped by vowels, as `hush_first_verse` is. These texts fix which vowels it shapes. When a voice is chosen, it
sings them exactly.

## 1. The language
**Roots.** The glossary's nine roots: *vey* water · *ish* light · *karra* gathering, city · *hal* shell · *ennu*
sleep, hush · *mir* stay · *tash* let go · *re* again · *oan* home.

This sheet adds eight more, one for each verse that needs its own world:
- *arre* fire, flare;
- *seli* sail, kite;
- *aun* deep, below;
- *thel* cord, thread;
- *sen* count, number;
- *sev* still, level;
- *kor* storm;
- *una* one, the first.

They're appended to the glossary's own block. Place names already carry the old roots (Iskarra = *ish karra*, "light
gathering"; the Sunken Vey; the Velamir lullaby's *mir*), and the new roots take none from a name in the game.

**How it's built.**
- Words stand side by side, with no inflection.
- A word said twice is said to someone, or meant with the whole heart.
- *re* after a word means "and again".

**How it's said.**
- Every vowel is sounded, and *oan* is two syllables (o-an).
- *ennu* is two syllables with a long *n*. The voice guide holds Asha to it: "It is pronounced *ennu*. Two syllables."
- The stress falls on the first syllable.
- *rr* is tapped, not rolled.

**How a verse is shaped.** Each of the Hush's seven verses has four lines:
1. A two-word call, said twice.
2. Three or four words naming what the verse's Cantor kept.
3. A word said again, trailing off.
4. ***mir***, alone: *stay*. Every verse ends on *mir* (ch05_kahre's direction).

The Eighth Verse, the Letting, is the one that doesn't end on *mir*: it ends on ***tash***.

## 2. The verses
| # | Taught by (chapter) | Text, line by line | What it says (never shown) |
|---|---|---|---|
| 1 | Ilun (Ch3) | *Vey ennu, vey ennu, / hal oan, ish karra. / Ennu re, ennu re... / ...mir.* | Water, hush. Shell, home; light, gathering. Hush again... stay. **As written in ch03_the_first_verse** (`ch03_verse_042`–`045`). |
| 2 | Kahre (Ch5) | *Ish karra, ish karra, / vey hal ennu, / re ish, re ish... / ...mir.* | Light-city. Water, shell, hush. Light again... stay. **Final as written** in ch05_kahre (`ch05_kahre_014`–`017`): it is sung to the mountain, and the light is the forge's. |
| 3 | Virel (Ch8) | *Seli arre, seli arre, / vey karra oan, / arre re, arre re... / ...mir.* | Kite of fire. Water, city, home. Fire again... stay. Wenna's flare over Corrow: a signal home that nobody read. |
| 4 | Nhoa (Ch11) | *Aun vey, aun vey, / ish aun ennu, / vey re, vey re... / ...mir.* | Deep water. Light, deep, hush. Water again... stay. Ressa's cold well; the light sifting down. |
| 5 | Hesk (Ch12) | *Thel ish, thel ish, / sen karra, sen oan, / thel re, thel re... / ...mir.* | Cord of light. Count the gathering, count the homes. Cord again... stay. Ama's arithmetic, knotted and hung where nobody read it. |
| 6 | Ethren (Ch13) | *Sev vey, sev vey, / ish sev ennu, / ennu sev, ennu sev... / ...mir.* | Still water. Light, still, hush. Hush, still... stay. The Sanctum's mirror: the creed of the Level in one verse, and Corran waiting under it. |
| 7 | Kesh (Ch16) | *Una kor, una kor, / vey ish hal oan, / kor re, kor re... / ...mir.* | The first storm. Water, light, shell, home: all the verses' words at once. Storm again... stay. She has stayed a thousand years. |
| 8 | the Letting (Act III) | *Ish oan, ish oan, / vey hal, ennu tash, / oan re, oan re... / ...tash.* | Light, go home. Water, shell; hush, let go. Home again... let go. The first verse turned over: *mir* becomes *tash*, as MEL_A's cell is turned upward (`motifs.letting()`). |

**Sung where.**
- Verses 1 and 2 are sung by Asha: `hush_first_verse` in Ch3 and `hush_second_verse` in Ch5.
- Verses 3–7 come back from each Vowbound at the binding, in its own voice. The scripts' notes:
  - Nhoa (Ch11): "a Kirru voice, very old and very young".
  - Hesk (Ch12): "a plain reader's voice".
  - Ethren (Ch13): "a patient, kind man's voice".
  - Kesh (Ch16): the stones, all ten mouths at once.
  
  Today's `*_bound` stings (`vowbound_stings.py`) are instrumental (Nhoa's Kirru whistle, Hesk's single sung "a", glass and bowed string). When SPEC §16 Q4/Q5 settles a voice, each takes its verse's first line from the table. Kesh's Swell, *The Seven*, sings verses 1–7 at once.
- Verse 8 is cut plain in the Choir stones. Ysolde reads it in Ch19; Asha sings it in the Letting.

## 3. Act III's placeholders: the final texts
The drafts (act2-plan, `docs/kb/story/act3/drafts/`) marked these "PLACEHOLDER Lamptongue (Audio owns the lyric)".
Their final text follows. A drafted line that already matches stays as it is.

| Draft line | Placeholder | Final | Notes |
|---|---|---|---|
| `ch19_words_001` (Ysolde reads the stones, spoken flat) | *Ish mir, ish re. Oan, oan. Tash.* | *Ish oan, ish oan. Vey hal, ennu tash. Oan re, oan re... tash.* | The Eighth Verse as cut in the stones (verse 8). Spoken, not sung: the tune is Pell's to teach (Ch18 K05). |
| `ch19_words_002` (Asha repeats it once, spoken) | the same | *Ish oan, ish oan... tash.* | She says only its first line and its last word: she doesn't have the rest by heart yet. |
| `ch20_fight_006` (Isse Varan, a Cage founder) | *Mir, mir. Tash.* | **Kept**: *Mir, mir. Tash.* | "Stay, stay. Let go." The help line carries the meaning. |
| the Cage founders' other lines (`ch20_the_cage`) | from the roots | Build from these only: *mir* · *tash* · *oan* · *ennu* · *una* (the first). Any pair from §2's verse lines. | Ysolde translates in the help line. Never a full verse: the founders speak in pieces of it. |
| H07 (Ch21, the Letting, sung) | not written | Verse 8, whole, as in §2. | The melody: `motifs.letting()`. The voice is SPEC §16 Q4/Q5's; until then, the vocalise on its vowels. |

## 4. For scripts and localization
- Lines in Lamptongue carry `#lamptongue #notr` with a translator note "keep exactly as written". Sung lines add
  `#sung`.
- Spelling is exactly as in this sheet: lower case after the first word, a comma between a doubled call, and an
  ellipsis before the last word.
- Nothing is translated on screen. Meaning reaches the player through Ysolde's help lines (Ch19, Ch20) and the scenes
  themselves.
- New lines in Lamptongue are built from §1's roots only. A new root is added here first, then to the glossary.
