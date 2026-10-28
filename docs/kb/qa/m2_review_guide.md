# The M2 review: a guide for the vertical slice

This is the review SPEC §16 Q7 asks for: **play the vertical slice and decide whether we scale up to M3.** The slice
runs from the title through the Prologue, the beach at Haluna, the village, the causeway, the Shell Shrine and the
Drownbell, to the dock at night and the end card. It takes about 40–45 minutes. Ch1 and the later chapters are not
part of it; they stay behind a switch until you sign off.

## 1. Launch

1. Use **Godot 4.6.3 stable**, the standard build (not .NET). The steps are in `docs/PLAYTEST.md` "Running it".
2. Open the **integration branch** (today `claude/undertow-lead-handoff-ze8rrn`). Import `project.godot` and wait for
   the first import to finish (a few minutes).
3. Press **F5**. On the title, choose **New Game**.
4. **If it runs slowly,** open **Settings** on the title and try the **Low** preset.
5. **Controls** are in `docs/PLAYTEST.md` "Controls". The ones you need most:
   - E or Enter talks and uses;
   - hold Escape for a second to skip a cutscene (it still stops at each choice);
   - Escape opens the field menu.

## 2. The route, and what to look at

| Beat | What happens | What to look at |
|---|---|---|
| **Prologue** | A drowned white city at dusk, and the people of the story keeping a vigil apart. One line of Rhen's older voice. | Does the city read as beautiful and doomed (Pillar 2)? Does the colour hold through "Everyone I'm going to tell you about is still here tonight"? |
| **B01 Cutscene A, the girl on the beach** | Rhen wakes in the shallows. Asha smiles first, Toma's spear comes in, and two choices follow. The cyan lights in the water are the drowned. | Asha's face: she goes still for half a beat at the lantern. Does the grief land? Are the faces clear of the dialogue box? |
| **First battle** | On the beach path: a reef crab and a lantern eel. Toma opens it with one line about the turn order. | Do you always know who acts next and what an action costs (Pillar 4)? The timeline is on the right; a highlighted command shows where your turn will land. |
| **B02 Neme's table** | Noon. Being fed by strangers; Neme's fear shows in how much food there is. | Does Neme turn to Rhen when she talks? |
| **B03 Haluna by day** | Free to walk. Four people each say a piece of what a "Cantor" is. There are shops, an inn and a save shrine. | Does the village feel lived in (villagers on routines, gulls on the roofs, birds)? Did you put "Cantor" together, or miss it the way Rhen does? |
| **B04 Pila's Granddaughter** (optional) | Grandmother Osu at the wake-shell wall by the causeway head. | Tone only: is it sincere and quiet? |
| **B05 Low tide** | At the causeway head, Asha asks Rhen to come "to see it". | Asha and Toma stay in view, and their lines play on them. |
| **B06 Saltgrass Causeway** | The tidal path to the shrine islet. A gull harrier circles ahead (the first fight), then a few random fights, and three banter stops. | The pacing: two or three random fights, not six. The route itself is env-art's final causeway now, not grey blocks. |
| **B07 Shell Shrine trial** | Four basins; turn them so the spring's water reaches the inner pool. The side pool hides a charm. | Is the puzzle readable from the water alone? Does the hall feel tended and loved? |
| **B08–B09 Cutscene B** | On the steps, "Do you know what a Cantor is?" Then Asha goes in alone and sings the first verse. | The verse is the slice's emotional peak: joy with a cold undertone. |
| **B10 The Drownbell** | A two-phase boss with Rhen, Asha and Toma. In phase 2 the water rises and Asha calls Ilun. | Can you read the toll coming on the timeline? Does Ilun's call feel earned? |
| **B11 The dock at night** | Haluna after dark. Rhen walks out to Asha at the end of the dock and asks to come. | The night's light (moon, oil lamps, the faint sea-glow), and the two of them turning to each other. |
| **B12 End card** | Rhen's voice on black, then the card and credits. Accept returns to the title. | — |

## 3. What changed since your playtests

| You said | What we did |
|---|---|
| Random battles came back to back | The encounter meter no longer counts the jump back after a fight, and there's a grace distance after each one (M2-FP-28). The causeway gives two or three fights, not six to eight (M2-FP-114). |
| New Game went to the wrong place | New Game starts the slice again (Prologue → Haluna beach). Act I waits behind its switch. |
| The opening was greyscale | The dusk frame has a warm rim and a teal fill now. The Prologue stands in env-art's Iskarra (glazed towers, a broken plaza, a skyline of drowned towers) over a real sea. |
| "Everyone is still here" was grey | The figures wear colour, and Rhen's lantern is the one warm light. |
| Heroes were placeholders | Rhen, Asha and Toma are their real models in the field, in battle and in cutscenes, and Ysolde in the Prologue. |
| Motion was rigid and snapped | Walks ease in and out on their real gait, turns are eased at a hero's pace, held shots breathe, and fades and the letterbox ease. A scene no longer ends with someone jumping to a mark. |
| Enemies acted twice; a KO replayed | Fixed in combat (M3-CMB-02) and battle presentation (M2-BPR-11). |
| Villagers were capsules | Haluna's villagers are modelled people on routines who turn and talk to you. There are birds and other wildlife too. |
| Parts looked primitive | Real sets replaced the stand-ins: the causeway, the First Verse in the real shrine, the Prologue's city, offerings and tide wrack at the shrine. Haluna has env-art's dressing: yards, stalls and lamps. A test now fails if a stand-in shape appears in a slice scene without a listed reason. |
| The first battle didn't teach | Toma's line opens it, the timeline previews every command, and Rhen's first turn names the command flow. |
| The Hullgnaw intro was framed too close | Fixed (Ch1's boss; not on the slice route). |

## 4. Known issues

Each of these is a known placeholder or gap, and each has an owner:

| Issue | Owner |
|---|---|
| Kerrid, Pell and Liss stand as coloured silhouettes in the Prologue until their models exist. | character / hero track (M3-HER-100) |
| Rhen has no lying or sitting clips yet (in the shallows, on the shrine steps), so he holds a stand-in pose there. | character |
| The shopkeeper, the smith and the innkeeper wear other villagers' models. | character (M2-CHR-100) |
| Behind the shrine's sunken door there is only a dark passage, so Ilun's chamber shows as light over the inner pool. | environment |
| The music is still prototypes awaiting your listen (`docs/kb/audio/listening_notes.md`). | audio, and your verdict |
| The colour grade is a stand-in until Rendering's LUTs land. | rendering |
| Some cutscene sounds are stand-ins. | audio (M3-AUD-100) |
| A few slice shots are re-rendering after this week's framing fixes. What you play is current; only the reference images lag. | slice-polish |

## 5. Feedback

A line per issue is plenty: what you did, what you saw, what you expected. "This part felt long" is useful too.

1. **Scale up to M3?** Yes / Yes, after these fixes: … / No, because: …
2. **The moment that worked best:**
3. **The moment that worked least:**
4. **Per beat** (any you have a note on): Prologue / B01 / first battle / B02 / B03 / B04 / B05 / B06 / B07 / B08–B09 /
   B10 / B11 / B12:
5. **Did you always know whose turn was next and what an action cost?**
6. **Did anything feel like a joke at the story's expense, or undercut a sad moment?** (Pillar 1)
7. **Anything still looking primitive or placeholder that isn't in §4?**
