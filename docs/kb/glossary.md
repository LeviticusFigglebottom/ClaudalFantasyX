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
- **currency**: name TBD by Narrative (M1-NAR-01). Code uses `currency`.

## Elements
Fire, Water, Lightning, Ice, Holy, **Glimmer** (an original non-elemental spirit element). *§6.8*

## People (principal cast)
Rhen Sallow · Asha Velamir · Toma Okeru · Liss Varrow · Old Kerrid · Ysolde · Pell (Kirru) · High Warden Sefir Aurane. Full sheets: `docs/kb/story/characters/`.

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
| Unbroken Calm | Sefir's goal: a permanent Calm with himself as the eternal heart. |

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
| Ember Terrace | The Fire temple. |
| Brine Shoals | The mud-flat route of wrecks where Liss is found. |
| Tamsule | The trade-port stilt city. |
| Corrow / Corrow Bastion | The seawall coast and its garrison town. |
| Coilspire | The Lightning temple. |
| Ossa Fen | The Kirru mangrove estuary. |
| Reedhollow | The Kirru roost-village. |
| Sunken Vey | The great drowned Lit Age city. |
| Lowlight | The Glimmer temple. |
| Ullar Heights / Ullari | The cold northern ranges and their people. |
| Keth Pass | The mountain route into Ullar. |
| Quellan | The Ullari highland town. |
| Cloudloom | The Ice temple. |
| Ansedra | The Order's holy city on a still lagoon. |
| Lacquer Court | Ansedra's ceremonial heart and the wedding site. |
| Sanctum of the Level | The Holy temple. |
| Hollowmere | The largest Saltwright flotilla. |
| Iskarra | The drowned Lit Age capital and the Prologue setting. |
| Lamp Spire | Iskarra's anchor-engine tower. |
| Pale Rim | The white shallows at the edge of the known sea. |

### Vowbound (see [vowbound.md](story/vowbound.md))
| Term | Meaning |
|---|---|
| Ilun | Water Vowbound; Teyo Marrin; Shell Shrine. |
| Kahre | Fire Vowbound; Daro Pemakan; Ember Terrace. |
| Virel | Lightning Vowbound; Wenna Corr; Coilspire. |
| Hesk | Ice Vowbound; Ama Quillo; Cloudloom. |
| Nhoa | Glimmer Vowbound; Ressa; Lowlight. |
| Ethren | Holy Vowbound; Corran Ysel; Sanctum of the Level. |
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
