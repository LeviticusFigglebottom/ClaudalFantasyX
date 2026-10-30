# Glossary

Every in-world term, with its canonical spelling and meaning. **Add new terms here before using them in data or dialogue.** `tools/validate_data.py` scans this file for banned terms ([`tools/banned_terms.txt`](../../tools/banned_terms.txt)), so keep anything that resembles a term from the inspiring series out of it entirely.

Format: **Term** (part of speech; pronunciation hint when it's ambiguous): meaning. *Source.*

## World
- **Maresh** (n., MAH-resh): the world, a tropical archipelago plus the coast of one great southern continent. Old cities lie drowned in shallow water. *SPEC §3.1*
- **glimmer** (n., uncountable; "a glimmer-mote" for one): luminous drifting motes released when a person dies. Once used to power ancient machines. *§3.1*
- **binding / to bind** (n./v.): harnessing glimmer in a machine or vessel. Forbidden by the Order. *§3.1*
- **glimmer-tech** (n.): ancient machines run on bound glimmer, found in ruins everywhere. *§3.1*
- **Saltwrights** (n., pl.; sing. *Saltwright*): a fringe, persecuted culture that salvages glimmer-tech. *§3.1*
- **the Undertow** (proper n., always with "the"): the once-a-generation sentient maelstrom-storm that drowns coasts. *§3.2*
- **Undertow-spawn** (n.): creatures shed by the Undertow, with dark wet carapaces and drifting glimmer wounds. *§7.5*
- **Cantor** (n., capitalized as a title): a pilgrim-singer who learns the Hush and sings it at the Drowned Choir, and never returns. *§3.2*
- **the Hush** (proper n.): the song, gathered verse by verse at the temples, that ends an Undertow cycle. In truth, it feeds the storm a new heart. *§3.2–3.3*
- **verse** (n.): one part of the Hush, learned from a temple's bound spirit. *§3.2*
- **the Drowned Choir** (proper n.): the place at the edge of the world where the full Hush is sung. *§3.2*
- **the Calm** (proper n.): the ten-or-more-year sleep of the Undertow after a Cantor's sacrifice. *§3.2*
- **Order of the Still Water** (proper n.; "the Order"): the faith and church. It teaches that the Undertow is punishment for binding. *§3.2*
- **High Warden** (title): the head of the Order. Currently Sefir Aurane. *§3.4*
- **revenant** (n.): a glimmer-sustained undying person, like the Order's leadership. *§3.3*
- **the unrisen** (n., pl.; sing. *an unrisen*): the dead who have stayed among the living, like Kerrid. Replaces the spec's working word (IP near-miss). *§3.4, story/glossary_additions.md*
- **Kirru** (n., pl. and sing.; adj. *Kirru*): an original non-human people, tall, quiet, and sea-otter/heron-like. *§3.4*
- **the Kite** (proper n.): the restored glimmer-tech airship of Act III. *§3.5*
- **the Great Unbinding** (proper n.): the finale's release of all glimmer in the world at once. *§3.5*
- **Reefball** (proper n.): the underwater team sport played inside a suspended sphere of water. *§6.10*
- **lamp-diver** (n.): one who dives drowned ruins by lamplight to scavenge, like Rhen. *§3.4*

## Game systems (player-facing names)
- **Vowbound** (n., pl. and sing.): bound spirits of past Cantors, summoned by Asha. Each one replaces the party on the field. *§6.3*
- **Swell** (n.): the per-character limit gauge and its techniques. *§6.2*
- **the Lattice** (proper n.): the shared node-board progression system. *§6.4*
- **Facet** (n.): a typed crystal that activates Lattice nodes. Kinds: Power, Mind, Speed, Ability, Fortune, Key. *§6.4*
- **Read** (ability): reveals an enemy's stats, weaknesses, and lore, and logs it to the bestiary. *§6.1*
- **save shrine** (n.): a glowing save point. It fully heals the party and opens the save menu. *§6.6*
- **Temple Trial** (n.): an environmental puzzle leading to a Vowbound. *§6.6*
- **Unfettered** (equipment ability): lifts the 9,999 damage cap to 99,999. *design/formulas.md*
- **lume** (n., uncountable; "a lume" for one coin): the Order-minted currency of Maresh, a holed disc of pressed lamp-brass named for oil-lamp light, the only light the Order allows. Code uses `currency`. *design/economy.md*

## Elements
Fire, Water, Lightning, Ice, Holy, **Glimmer** (an original non-elemental spirit element). *§6.8*

## People (principal cast)
Rhen Sallow · Asha Velamir · Toma Okeru · Liss Varrow · Old Kerrid · Ysolde · Pell (Kirru) · High Warden Sefir Aurane. Full sheets: `docs/kb/story/characters/`.

## Art terms (Art direction M1, docs/kb/art/)
- **sea-glow** (n.): the faint teal night glow of held glimmer on the sea (`#1C6B78`). It is in every night frame and absent only in the final shot.
- **held light / released light** (n.): glimmer that sinks or drifts seaward in cool cyan (held by grief) vs. glimmer that rises in warm gold (released).
- **wake-shell wall** (n.): Haluna's wall style of set shells. **fan-shell roof** (n.): its roof style.
- **tide-notch** (n.): the UI corner treatment (a small stepped notch). **lamp-node / lamp mote**: UI ornaments.

- **gilt line** (n.): a thin gold stroke a Tender paints on a Cantor before an Order rite. Asha wipes hers off at the Drowned Choir. *story/decisions_log.md N-04*

## Story terms (Narrative M1, merged 2026-10-22)

These come from `docs/kb/story/bible.md`. Where a row conflicts with an entry above, this section wins (it is the newer refinement).

### Metaphysics
| Term | Meaning |
|---|---|
| lamp | A living being's inner glimmer. "Her lamp went out" means she died. |
| mote(s) | The individual specks of light a lamp breaks into at death. |
| lift / lifting | The natural release of motes upward into the stars. It is the healthy end of the dead. |
| anchored | Describes motes held down by the grief of the living. They sink toward water. |
| binding / bound | Trapping motes in salt-glass or ceramic to power devices. It is forbidden by the Order. |
| salt-glass | The Lit Age material used to house bound glimmer. |
| unrisen | A dead person whose motes re-cohered into their own shape around an unkept promise. (Replaces the spec's working word.) |
| Undertow-spawn | Creatures formed from the Undertow's overflow, with dark wet carapaces and glimmer wounds. |
| heart (of the Undertow) | The Cantor's lamp at the storm's centre that keeps it coherent and asleep. |
| displaced heart | A former heart pushed out when the next Cantor sings. It becomes either a Vowbound or food for the Abiding. |
| hearer | A person who can hear glimmer as a faint hum. Cantors are chosen from hearers. |
| Lamptongue | The old Iskarran liturgical language of the Hush. |
| the Letting / the Eighth Verse | The suppressed final verse of the Hush, which lifts glimmer instead of gathering it. |

### History and Factions
| Term | Meaning |
|---|---|
| AL | "After the Level." The Order's calendar. The present is 1012 AL. |
| Lit Age | The glimmer-powered civilisation before the First Rising. |
| First Rising | The first Undertow, in 0 AL, which drowned Iskarra. |
| Lamplighters | The six Iskarran founders who composed the Hush. |
| the Cage | The four Lamplighters bound around the Undertow's heart: Orin Tesk, Halde Moor, Isse Varan, and Cael Imbrey. |
| the Abiding | Glimmer-sustained revenants who lead the Order in secret. |
| Abiding Conclave | The five Abiding (Sefir, Hesper Oan, Malcor Venn, Ilsabet Rue, and Tamsin Druse). Publicly they are the "Conclave of Elders." |
| the Shortening | The steady shrinking of Calms from 30–40 years to 11–15. |
| Salt Edicts | The 212 AL laws outlawing binding and salvage, which created the Saltwrights. |
| Last Calm | The Order's promised final sleep of the Undertow, once the "debt" is paid. |
| the Long Stillness | Sefir's goal: a permanent sleep of the storm with himself as the eternal heart. (Renamed from an IP near-miss; decisions_log N-10.) |

### The Order of the Still Water
| Term | Meaning |
|---|---|
| the Level | The Order's symbol (a circle crossed by a horizontal line) and its palms-down gesture. |
| "Be level." / "And still." | The Order's greeting and its response. |
| High Warden | The head of the Order. |
| Warden | A regional governor of the faith. |
| Tender | A temple priest who tends a Vowbound and runs its trial. |
| Ebb-priest | A priest who performs small Ebbings for ordinary deaths. |
| Stillguard | The Order's temple warriors, in red-lacquered shell armour. |
| Reed | An Order novice. |
| the Ebbing | The dance for the dead, which secretly herds motes seaward into the storm. |
| the Stilling | The Order's rite to tear an unrisen apart and send its motes to sea. |
| Pilgrim's Wake | A living funeral held for a Cantor the night before she departs. |
| wake-shell | A shell carved with a Cantor's name and set in her home shrine wall at her Wake. |
| Lampfast | The eve of a Calm, when every lamp in Maresh is put out. |
| Vigil of the Calm | The festival held on the day a Cantor sings. |
| leaf-boat | A folded palm-leaf offering with rice and a lit wick, floated for the dead. |
| Canticle of Level Water | The Order's scripture, recited and never sung. |
| lantern-staff | A Cantor's tall staff topped with an open lantern, used in the Ebbing. |
| verse-sleeve | Asha's long ceremonial sleeve, embroidered with one band per verse learned. |
| the Cistern | The reservoir under Ansedra where displaced hearts are consumed. |
| the Underreach | Ansedra's sunken under-city. |
| "Level preserve us." | An Order oath. |

### Peoples and Customs
| Term | Meaning |
|---|---|
| lamp-diver | An Oruvel salvager who dives drowned towers by oil lantern. |
| reach-band | A Low Reaches forearm tattoo, one per voyage survived. |
| star-path | A Low Reaches navigation chant of star sequences. |
| tide-wall | A curved, dry-stacked coral wall with wind-gaps. |
| lintel-gull | A carved wooden seabird on Low Reaches roof ridges, said to warn of the Undertow. |
| "Salt and stone." | A Low Reaches oath. |
| stair-mountain | The Pemakar temple form: stepped tiers climbing a hillside. |
| open-hand gate | A Pemakar gateway of two carved forearms with cupped palms. |
| Lanternfall | Pemakar's festival of a thousand leaf-boats on the terrace channels. |
| Tidecup | Tamsule's Reefball tournament. |
| Tamsule Bell | The Lit Age dome in Tamsule that holds the Reefball water-sphere. The Order "sanctified" it. |
| Watchers | The carved humming faces on the Corrow seawall. |
| line-marks | Saltwright circuit-like tattoos, one per device restored. |
| brine-branding | The Order's punishment of salt-burning a Saltwright's line-marks. |
| current-song | A Saltwright sung chart of sea currents. |
| "Rust it." | A Saltwright oath. |
| clutch | A Kirru sibling group. |
| farewell-tide | The Kirru dusk song for the dead, after which mourners turn their backs to the water. |
| name-shell | A Kirru's carved name-token. It is scraped blank on exile. |
| scraped | Kirru term for exiled for refusing to let go. |
| keth | Ullari knotted-cord records, read by touch. |
| pass-cord | A cord across an Ullar pass where knots are tied for the dead. |
| woolback | An Ullari long-necked, shaggy pack animal. |
| bowl-dome | Ansedra's inverted gilded bowl roofs. |

### Places
| Term | Meaning |
|---|---|
| Low Reaches | The southwest coral archipelago. |
| Haluna | Asha's home village (vertical slice). |
| Saltgrass Causeway | The tidal route from Haluna to the Shell Shrine (vertical slice). |
| Shell Shrine | Haluna's small Water temple (vertical slice). |
| Oruvel | Rhen's raft-town above a drowned district. |
| Oruvel Underway | The drowned tower beneath Oruvel (the tutorial dive). |
| Brightwater Crossing | The ferry route out of the Low Reaches. |
| Pemakar Terraces / Pemakar | The central volcanic isles and their town. |
| Ashcrown | The Lightning temple (zone `ch05/ashcrown`; was Ember Terrace, N-09). |
| Brine Shoals | The mud-flat route of wrecks where Liss is found. |
| Tamsule | The trade-port stilt city. |
| Corrow / Corrow Bastion | The seawall coast and its garrison town. |
| Coilspire | The Fire temple (N-09). |
| Ossa Fen | The Kirru mangrove estuary. |
| Reedhollow | The Kirru roost-village. |
| Sunken Vey | The great drowned Lit Age city. |
| Lowlight | The Ice temple: its drowned sanctum lies in the deep's cold, and nothing in it is frozen (N-15, ADR 0015). |
| Ullar Heights / Ullari | The cold northern ranges and their people. |
| Keth Pass | The mountain route into Ullar. |
| Quellan | The Ullari highland town. |
| Cloudloom | The Holy temple: an open-roofed stone weaving-hall hung with keth (N-09, N-15). |
| Ansedra | The Order's holy city on a still lagoon. |
| Lacquer Court | Ansedra's ceremonial heart and the wedding site. |
| Sanctum of the Level | The Glimmer temple: its basin is a perfect mirror, lit from beneath by bound glimmer (N-15, ADR 0015). |
| Hollowmere | The largest Saltwright flotilla. |
| Iskarra | The drowned Lit Age capital and the Prologue setting. |
| Lamp Spire | Iskarra's anchor-engine tower. |
| Pale Rim | The white shallows at the edge of the known sea. |

### Vowbound (see [vowbound.md](story/vowbound.md))
| Term | Meaning |
|---|---|
| Ilun | Water Vowbound; Teyo Marrin; Shell Shrine. |
| Kahre | Lightning Vowbound; Daro Pemakan; Ashcrown. Swell *Last Strike*. |
| Virel | Fire Vowbound; Wenna Corr; Coilspire. Swell *Flare Line*. |
| Hesk | Holy Vowbound; Ama Quillo; Cloudloom. |
| Nhoa | Ice Vowbound; Ressa; Lowlight. Swell *Farewell-Tide*. |
| Ethren | Glimmer Vowbound; Corran Ysel; Sanctum of the Level (its basin is a lit mirror). Swell *Still Water*. |
| Kesh | The First Voice, all six elements; Kesh Aurane; the Drowned Choir. |

### Named Supporting Characters
| Name | Who |
|---|---|
| Imra Velamir | The 61st Cantor, Asha's mother, and the current heart. |
| Dace Sallow | Rhen's father, a Saltwright, inside the Undertow. |
| Neme | Asha's aunt in Haluna. |
| Grandmother Osu | Haluna elder, granddaughter of Pila. |
| Pila Marrin | Teyo's younger sister. |
| Mother Kell | The Oruvel diver whose wick lights the post-credits lamp. |
| Tobin Varrow | Liss's brother, killed at the peace wedding. |
| Merel Dask | Tobin's bride, the living daughter of a Warden. |
| Corran Ysel | Ysolde's husband, the 60th Cantor (Ethren). |
| Ressa | Pell's clutch-sister, the 56th Cantor (Nhoa). |

### Weapons and Props
| Term | Meaning |
|---|---|
| reef-hooks | Rhen's twin hooked short blades. |
| tide-shield | Toma's turtle-shell round shield. |
| anchor-cleaver | Kerrid's blade, forged from an anchor fluke. |
| folding lacquer book | Ysolde's accordion grimoire. |
| ink-guards | Ysolde's lacquered nail-sheaths. |
| Level-pin | An Order hairpin bearing the Level symbol. |
| work-sleeve | Liss's copper-mesh arm guard. |

### Bosses Named in the Outline
Hullgnaw, Drownbell (slice), Spar-Wraith, Cinder Matron, the Undertow's Reach, Mangrove Drowner, the Lamp Engine, Avalanche Ram, the Cistern Keeper. Each is described in [beats/act_outline.md](story/beats/act_outline.md).

### Lamptongue Roots (for Audio lyrics)
*vey* water · *ish* light · *karra* gathering/city · *hal* shell · *ennu* sleep/hush · *mir* stay · *tash* let go · *re* again · *oan* home.

### Added 2026-10-23 (M1-NAR-05)
- **the Velamir lullaby**: the family lullaby that became the first verse; Imra knew it before she was named, and Dace heard it from her at Haluna (N-11).
- **heirloom weapons**: the per-character ultimate-weapon quest line (SPEC §6.5).
- **the Weir** (contingent): an alternative Reefball arena form, only if the human changes the sphere (N-12).

### Added 2026-10-23 (M1-NAR-08)
- **Element reassignment (ADR 0015, N-15):** Nhoa (Lowlight) is now Ice and Ethren (the Sanctum) is now Glimmer. Hesk (Cloudloom) stays Holy. No temple is frozen. The rows above for Lowlight, Cloudloom, the Sanctum, Nhoa and Ethren are updated to match.

### Added 2026-10-23 (M1-NAR-08, review-sweep-D; ADR 0016, N-18)
- **Lamp Archive**: the Order's library of Lit Age records in Ansedra, where the founders' ledgers and the full Cantor roll are kept (Ch13).
- **kept / spent**: the Cantor roll's hidden column. *Kept* Cantors are Saints (Vowbound). *Spent* ones were consumed in the Cistern.
- **Wakefin**: the Ch15 boss, an Undertow-spawn that follows the first wake out of Ansedra's lagoon. It replaces the Cistern Keeper, which is cut.
- **the Underreach / the Cistern** (rows above): still canon as places, but never visited. The party learns of them from the Archive.

### Added 2026-10-23 (M1-NAR-09; ADR 0017, N-20)
- **name-board**: a ship's carved name plank. Low Reaches sea-law says a hull drowned in a Rising is not passed without bringing its name-board home (Ch4).
- **Fisher Stair**: the broad stone stair up the inner face of the Corrow seawall, by which the low town climbs onto the wall ahead of the sea (Ch8).
- **Tavi Orse**: captain of Oruvel's Reefball side and Mother Kell's grandson. Rhen dives for his side at the Tidecup (Ch7).
- **Edict progress**: the High Warden's once-a-Calm journey along a coast to see the Salt Edict kept. Sefir is first met on one (Ch6).
- **Spar-Wraith** (boss row above): now fought on the deck of a drifting dead trader, not on the ferry.

### Added 2026-10-23 (M1-NAR-09 and M1-NAR-08, review-sweep-E; ADR 0020, N-21, N-22)
- **stair-law**: the Corrow Stillguard rule "first down the stair, last up it": a captain doesn't come off the wall while anyone is still below.
- **Stair's clear**: the Stillguard all-clear at the Fisher Stair, meaning nobody is left below. Kerrid's first line in his last scene.
- **the straw-cape man**: an anonymous Low Reaches fisher's tale about a big man in a straw cape who pulls the drowning out of the sea and is gone before anyone can thank him. It is Kerrid, and nobody knows it.
- **dock-master**: the keeper of Hollowmere's dry-dock berths, an office and not a chief. Liss's father holds it.
- **Old Kerrid** (roster row above): no longer Imra's guardian. He was the Stillguard captain of the Corrow wall and died at the foot of the Fisher Stair in 1001 AL.

### Added 2026-10-23 (M1-NAR-11, review-sweep-F; ADR 0022, N-23)
- **stair-watch**: Corrow's conscripted fishers who keep the Fisher Stair, under a captain chosen from among them. It has no rank in the Order: the Stillguard hold the Bastion and the wall-head, and the watch holds the stair.
- **stair-law** and **Stair's clear** (rows above): the stair-watch's rule and all-clear, not the Stillguard's.
- **Old Kerrid** (rows above): captain of the Corrow stair-watch, never a Stillguard officer, with no title or fame outside Corrow.
- **Dace Sallow** (row above): never Imra's guardian. He was Kerrid's hired diver at Corrow in 1001, a stranger to Imra until she went down the Fisher Stair into the sea for him.
- **the Velamir lullaby** (row above): Dace heard Imra hum it at Haluna without ever learning her name.

### Added 2026-10-23 (M1-NAR-11, review-sweep-G; ADR 0022 append note, N-24)
- **Mother Kell** (row above): the old Oruvel diver who kept Rhen from eight to nineteen, at Dace's one message. She drowns in Ch1.
- **Dace Sallow** (rows above): he never went home after Corrow, because his line-marks were seen on the stair and a hunted Saltwright would bring the Order to his son.

### Added 2026-10-23 (M1-NAR-11, review-sweep-H; ADR 0022 sweep-H append note, N-25)
- **Mother Kell** (rows above): Oruvel's chandler, who sold the lamp-divers their oil and wicks and never learned to swim. She took Rhen in at eight, unasked, when nobody came for him. Dace's message asked nothing of her. She drowns in Ch1. Not a diver: this corrects the rows above.
- **lantern pair**: a Saltwright wright builds lanterns two at a time, one to wear and one on the hook against a flooded housing. Rhen wears the first of Dace's pair, which never left Oruvel. The one Asha saw at Haluna was its twin.

### Added 2026-10-23 (M1-CMB-04, Combat)
- **Swell modes** (how a gauge fills; formulas.md § Swell): **Ballast** (taking hits), **Wake** (striking foes), **Tether** (allies hurt), **Salve** (using a healing item). The names avoid the inspiring series' mode names on purpose.
- **Lamp Ring**: Rhen's Swell input, a lantern that flares three times as a ring closes on it. **Lamp Dive**: his first Swell technique.

### Added 2026-10-23 (M1-CMB-03, Combat)
- **bestiary** (n.): the party's record of the creatures it has Read or defeated. *§6.1, §6.11*
- **preemptive opening** / **ambush** (battle openings): the party, or the foes, take their first turns before the other side. *design/formulas.md § Openings*

### Added 2026-10-23 (M2-CMB-01, Combat)
- **Verse Chant**: Asha's Swell input, a short phrase of direction buttons that follows a verse of the Hush. **Shallows Verse**: her first Swell technique (heals every ally).
- **Tide Brace**: Toma's Swell input: hold through the blows, let go on the counter. **Return Tide**: his first Swell technique.
- **Glyph Trace**: Ysolde's Swell input: trace a Lamptongue glyph's strokes before the window closes (*swift* for a clean, quick trace). **Written Light**: her first Swell technique (strikes every foe).

### Added 2026-10-24 (M3-RBL-01, Combat)
- **float** (Reefball): the woven ball. A score is **bringing it up** through the single **ring** at the top of the drop (N-12). *design/reefball.md*
- **fetch** (Reefball): a side may only score a float it has taken down to low water or deeper this possession, from the rescue drill. A float won high up must be fetched first.
- **the weep** (Reefball): the lowest band of the drop, where it weeps its column into the catch-pool; kickoffs start there. The bands from the top: the ring, high water, mid water, low water, the weep.
- **rise, dive, pass, loft** (Reefball actions): swim up with the float, swim down with it, hand it on, throw it up through the ring.
- **lifter, anchor, presser, ringward** (Reefball roles). A **ringward** waits at the ring to ward off lofts; there is no keeper.
- **breath** (Reefball): the divers' resource; it comes back only at the ring, so a winded diver leaves play to breathe.

### Added 2026-10-24 (M3-CHR-506, Character Art)
- **shell-tile wraps**: the cords of small square shell tiles on Pell's forearms (the art sheet's reading of his "beaded cord wraps"). The left wrap's sequence is the call and the right's the mirrored response, echoing his call-and-response Swell input. *art/characters/pell.md §3*

### Added 2026-10-29 (M3-NAR-1000, Narrative)
- **unrisen** (row above): a dead person whose motes re-cohered into their own shape around anything unfinished (a
  promise, a duty, a watch not yet over; bible §2). Supersedes the table row's "around an unkept promise".
- **Mother Kell**, **stair-law**, **Stair's clear** (rows above): the later rows hold: Kell is Oruvel's chandler, never a
  diver; the stair-law and the all-clear are the stair-watch's, never the Stillguard's (decisions_log N-25, N-27).

### Spelling (Lead, 2026-10-30)
Player-facing text uses British spelling with Oxford -ize: colour, armour, defence, grey, harbour, honour, traveller, but Customize. Code ids and loc keys keep their spelling (`STAT_DEFENSE`, `EQUIP_MENU_SLOT_ARMOR`).

### Lamptongue Roots, added (Audio, 2026-10-30)
The Hush's verses 3-8 (docs/kb/audio/lamptongue.md, the full sheet): *arre* fire/flare · *seli* sail/kite · *aun* deep/below · *thel* cord/thread · *sen* count/number · *sev* still/level · *kor* storm · *una* one/the first.
