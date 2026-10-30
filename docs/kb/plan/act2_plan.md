# Act II plan: "The Truth" (Ch10–Ch16, milestone M4)

- **Status:** prepared ahead of the gate (ADR 0203). **Nothing here starts until the Lead tags `act1-complete`.** Until then ADR 0041's pause stands, and every task this plan files is `status: blocked`, `blocked-by: ADR 0203`.
- **Author:** the act2-plan track (docs only), 2026-10-30.
- **Sources:**
  - SPEC §3.3, §3.5 (Act II), §6, §7.2 (Act II is overcast, storm, moonlit, cold blue stone), §8.2 and §10.2 (M4: Act II complete, including the wedding set piece and the reveal);
  - [act_outline.md](../story/beats/act_outline.md) Ch10–Ch16 and [act1_ch09.md](../story/beats/act1_ch09.md) §10 (what Act I hands over);
  - [bible.md](../story/bible.md), [vowbound.md](../story/vowbound.md), the character sheets, [decisions_log.md](../story/decisions_log.md) N-15/N-18;
  - ADR 0015 (no frozen temple from Ch12 to Ch15), 0016 (the Act II re-staging), 0020 and 0022 (Kerrid);
  - the art sheets: [color_script.md](../art/color_script.md) `ch10`–`ch16`, `docs/kb/art/environments/{ossa_fen,lowlight,keth_pass,ansedra,open_sea_ch15,hollowmere,pale_rim}.md`, [act2_roster.md](../art/creatures/act2_roster.md) and `act2/*.md`, `vowbound/{nhoa,hesk,ethren}.md`;
  - [act2_finals.md](../audio/act2_finals.md) (the Act II score);
  - [balance_targets.md](../design/balance_targets.md) and [set_piece_battles.md](../design/set_piece_battles.md).
- **Lane docs:** each track drafts its own Act II lane plan under [`docs/kb/plan/act2/<lane>/`](act2/) (ui-menus, audio, creatures, act1-chapters so far, 2026-10-30). Where a lane doc and this plan differ, the lane doc is the detail and this plan is the index.
- **Companion files:** [act2_tracks.md](act2_tracks.md) (the proposed track split and ownership globs); [act2_inventory.md](act2_inventory.md) (the branch-by-branch evidence for §3); the M4 task files `docs/kb/tasks/M4/M4-A2P-*.md` (one per gap, filed by this plan).

## 0. The bar

ADR 0041 §3's "final" bar is Act II's bar from day one (ADR 0203: "Act I's bar becomes the standing bar for every later act"):
- no greybox mesh or material, no capsule or box stand-in;
- no placeholder texture, icon, portrait or temp sound, and no `TODO`/`placeholder` art the player can see or hear;
- every enemy has its real mesh, rig, clip set, battle VFX and sounds;
- every area is dressed, lit and walkable, with no seams or holes.

**Consequence for ordering:** the Act I tracks built every chapter as greybox → story → art → polish, and then had to repay the greybox under ADR 0041. Act II already **has** its greybox (M4-C10-02 … M4-C14-02, on the integration branch). So Act II goes straight to final: the kit and dressing land before a chapter is called playable, and a chapter is never "done" on greybox. integration-qa's `placeholder_audit.py --act 2` (ADR 0203, preparation) is the work list's backstop.

## 1. Act II at a glance

| Ch | Title | Zones (`game/levels/…`) | Boss | Vowbound | Set piece / big beat | Colour (`color_script`) |
|---|---|---|---|---|---|---|
| 10 | Fen of the Kirru | `ch10/ossa_fen`, `ch10/reedhollow` | Mangrove Drowner | — | The Kirru farewell-tide (the motes lift) | overcast dusk, tannin water, 6,500 K |
| 11 | Lowlight | `ch11/sunken_vey`, `ch11/lowlight` | Lamp Engine | **Nhoa** (Ice) | Rhen admits he is Dace's son; Pell before Ressa | overcast midday, bound teal, 7,000 K |
| 12 | The Cold Road | `ch12/keth_pass`, `ch12/quellan`, `ch12/cloudloom` | Avalanche Ram | **Hesk** (Holy) | Kerrid's breath doesn't fog; Ysolde's lie and confession | cold 09:00, woven reds, 6,800 K |
| 13 | Gold and Lacquer | `ch13/ansedra`, `ch13/sanctum`, `ch13/lamp_archive` | — (no boss) | **Ethren** (Glimmer) | The Lamp Archive: the founding truth on paper | overcast 16:30, cold gold, 6,200 K |
| 14 | The Peace Wedding | `ch13/ansedra_lacquer_court`, the lagoon | Warden Malcor Venn (+ the flat-engine) | — | **The wedding trap; heretics; Tobin dies; the escape across still water** | dusk 2,800 K, contrast 0.70 (the game's peak) |
| 15 | Unlamped | `ch15/open_sea`, `ch17/hollowmere` (first visit) | The Wakefin | — | **Kerrid's reveal**, by his own word; Toma's faith breaks | moonlight 9,000 K, sea-glow 0.12 |
| 16 | The Edge of the World | `ch16/pale_rim`, `ch16/drowned_choir` | Sefir's Abiding guard, then the storm wakes | **Kesh** (all six) | **The Drowned Choir: what the Hush really does**; Sefir's "go home" | white noon 7,500 K, contrast 0.25 (the game's lowest); the Choir at moonrise |

**Zones:** 15 zone scenes (13 Act II-only plus the lagoon variant of Ansedra and Hollowmere's first visit, which Act III re-uses). **Bosses:** 6 fights (4 creature bosses, 2 people bosses), plus the flat-engine part and the storm's waking. **Vowbound bound:** 4 (Nhoa, Hesk, Ethren, Kesh). **Regular foes:** 10 ids already in data (M4-C10-03, M4-C11-03), plus `conduit_crawler` and the variants.

**The party through Act II:** all seven from Ch10 (three active, four in reserve). Party-state changes the flow must express:
- **Ch10:** Pell stays out of Reedhollow (a `party` step, as ch13.json does for Kerrid in the Sanctum). Kerrid's rope-burns show `glimmer_held` from Ch10 on (ADR 0022 (g)).
- **Ch13:** Kerrid never enters the Sanctum (already in `chapters/ch13.json`).
- **Ch14:** the party are **heretics** from the trap on (§4.2).
- **Ch15:** Kerrid is **revealed** (§4.3); nothing about his kit changes, but his barks, codex page and field presence do.
- **Ch16:** the Choir binds Kesh; the act ends with the party swept away.

## 2. Chapter by chapter

**Beat-sheet drafts (pre-gate, 2026-10-30)** now exist for every chapter: [Ch10](../story/beats/act2_ch10.md), [Ch11](../story/beats/act2_ch11.md), [Ch12](../story/beats/act2_ch12.md), [Ch13](../story/beats/act2_ch13.md), [Ch14](../story/beats/act2_ch14.md), [Ch15](../story/beats/act2_ch15.md) and [Ch16](../story/beats/act2_ch16.md). Where a draft and this section differ, the draft is newer. The main differences: the Ram's hazard is stone and scree, not snow (ADR 0015); the Abiding guard are living; and Kesh is bound in Ch16 but callable only from Ch17.

Each chapter lists zones and kit needs; cast and NPCs; enemies, bosses and Vowbound; set pieces; cutscenes; music and ambience; new menus and systems; balance targets. "Exists" means on a branch today (§3, the inventory); "gap" means a task in §6.

### Ch10 "Fen of the Kirru"
- **Zones and kits:**
  - `ch10/ossa_fen`: mangrove channels at dusk, root-walks over tannin water, a side pocket, the Drowner's clearing and the way on. `ch10/reedhollow`: the Kirru roost-village, woven reed lodges on mangrove roots, twelve platforms round a lagoon, the clutch's stone on the shore.
  - **Kit:** `ossa_fen.py` in the Haluna kit (art sheet [ossa_fen.md](../art/environments/ossa_fen.md), M3-ENV-718): mangrove prop-roots and trunks, root-walk planks, reed lodges, woven screens, name-shell racks, mooring stakes, dusk fireflies (wildlife, not glimmer). Vegetation: a **mangrove** system (SPEC §7.4 names it; not yet built for Act I) plus reed beds.
  - **Water:** `tannin_fen` (validated in the colour script). **Arena:** `ossa_fen_roots`.
- **Cast and NPCs:**
  - Party of seven; Pell at the fen's edge (the act's first image).
  - **The Kirru:** the clutch (6–10 bodies), the eldest who still swims, **a Kirru child** (the side scene). They are a people, never monsters (act2_roster), and the characters track builds them: one Kirru base (Pell's rig, ADR 0021-style heavy modification), with age and size variants and name-shells.
- **Enemies:** `tannin_archer`, `root_crab` (variant of the reef crab), `fen_leech` (variant of the sail leech): data and sim bands exist (M4-C10-03); models don't.
- **Boss:** the **Mangrove Drowner**, two phases (rooted, then uprooted): breaking a root lets a few held motes rise, a foreshadow of the Letting. Design sheet `act2/mangrove_drowner.md`. Music stems exist (§3).
- **Set piece:** the **farewell-tide** at dusk. The clutch sings, turns its back, and the motes lift straight up into the stars; Asha can't stop looking. Rendering: the first big `glimmer_lift` (rising spiral) event. It must read as the opposite of the Ch9 Ebbing's seaward drift (bible's visual rule).
- **Cutscenes:**
  - C1: Pell stops at the fen's edge;
  - C2: arrival at Reedhollow (Pell left outside);
  - C3: the farewell-tide (the act's first showpiece, ~90 s);
  - C4: the Drowner's intro and its fall (the root-lift);
  - C5: the side scene, a Kirru child asks Asha why humans make their dead swim.
- **Music and ambience:**
  - `ossa_fen` and `reedhollow` (zone finals exist); `farewell_tide` (~90 s, from reedhollow's clutch line; it carries the Letting's first cell); `mangrove_drowner` (2 stems, exist).
  - Ambience: fen (insects, drips, root creak), Reedhollow (reed wind, wordless clutch hum).
  - Creature voices for the three regulars (M4-AUD-1001).
- **New systems:**
  - **drain** on enemy skills (M4-CMB-1001; the fen leech's lesson);
  - **rooted** (no swap) as a status or skill effect (the root crab);
  - Pell's battle kit and place in the formation (M3-C09-07, `todo`: "fights from Ch10"; a hard dependency).
- **Balance:** regulars on the Act II curve (naive 5–35%, role ≥ 90%, smart ≥ 95%, p90 ≤ 40); the Drowner on the boss curve (naive ≤ 3%, role 55–80%, smart 70–90%, p90 ≤ 80).
  - The existing suites run on the `ch08_seawall` loadout. They must re-run on a **Ch10 loadout** (the Act II shops, Lattice progress through Ch9, Pell in).

### Ch11 "Lowlight"
- **Zones and kits:**
  - `ch11/sunken_vey`: drowned galleries, salt-glass floors, drowned pillars, the conduit court with its housing-mark (`conduit_mark`), the fig-choked side gallery.
  - `ch11/lowlight`: the temple half underwater: the atrium's lamp bench, the Lamp Engine's hall, the well-shaft's two flights down past the waterline, and the **drowned sanctum** (Nhoa).
  - **Kit:** `lowlight.py` (art sheet [lowlight.md](../art/environments/lowlight.md), M3-ENV-716): Lit Age conduits with `glimmer_bound` cores, salt-glass, brass, strangler fig.
  - **Water:** `overcast_lagoon`. **Arena:** `lowlight_engine_hall`.
  - **Open design question** (M4-C11-01 asks it): is the sanctum swum (Ch1's underwater field) or walked? **Plan default: walked** down the flooded shaft to a dry ledge, with the sanctum *seen* underwater from the ledge. That avoids a second underwater field mode in Act II; the underwater shader (M2-RND-02) still lights the view. Narrative can overrule.
  - **ADR 0015:** nothing frozen. The cold is the deep's.
- **Cast:** party; no new NPCs. **Nhoa** is Ressa: Pell kneels before his sister for a full scene and says nothing.
- **Enemies:** `gallery_ray`, `rime_urchin` (data exists); `conduit_crawler` (design sheet exists, **no data**: the roster asks whether it is a foe or a hazard; plan default is a **boss add**, §2 Ch11 boss).
- **Boss:** the **Lamp Engine**, two phases (the lamps, then the core bared), with conduit crawlers repairing parts. Releasing the core makes a small upward lift and a 3 s warm grade lift (`lut_ch11_vey`). Music stems exist.
- **Vowbound:** **Nhoa** (Ice). Bind cinematic, summon cinematic (full and short), battle kit (Ice on sifting mote-swarms; copies the last enemy action), Swell *Farewell-Tide* (the only finisher whose motes go **up**). The art sheet exists (`vowbound/nhoa.md`); the model, rig, VFX and data don't.
- **Set pieces and cutscenes:**
  - C1: Liss reads the Saltwright housing-mark (the same make as Rhen's lantern); Rhen admits he is Dace's son; Liss is furious. This pays Ch8's stopped "My—".
  - C2: the Lamp Engine intro and its release.
  - C3: the descent and the binding of Nhoa (the bind cinematic; Pell's silent scene).
  - C4: the side scene, Rhen and Liss repairing a lamp in silence (the truce).
  - Optional: one more of Wenna's marks (`ch08_liss_found_marks` thread).
- **Music:** `sunken_vey`, `lowlight` (exist); `lamp_engine` (exists); `nhoa_bound`/`nhoa_summon` stings (gap).
- **New systems:** the Vowbound runtime for a 4th Vowbound (data rows; the summon menu already lists them); the enemy **repair** behaviour (a skill that restores a broken part: CreatureActor `break_parts` exists from the flat-engine design; the engine needs a "restore part" effect).
- **Balance:** the Act II curve. The Engine is the act's first "kill the adds or lose" boss; the role answer is Rhen or Ysolde on the crawlers, then Kerrid on the bared core.

### Ch12 "The Cold Road"
- **Zones and kits:**
  - `ch12/keth_pass`: three switchback flights along a cliff, the pass-cords on the drop side, the knotted post, the Ram's shelf under the seeping Lit Age wall, the saddle.
  - `ch12/quellan`: the Ullari highland town: street, houses, the inn with its red banner, the well.
  - `ch12/cloudloom`: the stair up, the **open-roofed weaving-hall** with thousands of keth, Hesk's dais.
  - **Kit:** `keth.py` (art sheet [keth_pass.md](../art/environments/keth_pass.md), M3-ENV-717): cut slate, terrace walls, keth cords (thousands: instanced, with wind), woven reds, white stone. Quellan's town modules and Cloudloom's hall need the same kit, extended.
  - **Arena:** `keth_seep_terrace`. Snow and wind are weather only (ADR 0015: no ice in any temple from Ch12 to Ch15).
- **Cast and NPCs:** Quellan townsfolk (Ullari: a new villager costume set on the crowd generator), the **Ullari woman** at the pass-cord (side scene), an innkeeper, a keth-reader.
- **Enemies:** `ridge_lynx`, `cord_moth`, `scree_crawler` (variant of the slag tortoise): data exists; models don't.
- **Boss:** the **Avalanche Ram**: its charge brings the snow down, a field hazard round by round. `field_rules` (set_piece_battles §4) already carries per-turn statuses, so the hazard is data plus a falling-snow field VFX. Music stems exist.
- **Vowbound:** **Hesk** (Holy). Bind cinematic in the weaving-hall (noon light writing the keth shadows on white stone), summon cinematics, kit (Holy, cleanse, Mending), Swell *Pass-Cord*. The art sheet exists; the rest is a gap.
- **Cutscenes:**
  - C1: the pass-cords; Toma notices **Kerrid's breath doesn't fog** (the cold-breath VFX on the six living, none on Kerrid: a rendering and character request);
  - C2: the Ram's intro;
  - C3: Hesk's binding; Ysolde reads Ama's keth and lies;
  - C4: night at Quellan: Ysolde's confession to Asha ("forty-seven voices, seven houses");
  - C5: the side scene, the Ullari woman's knot.
- **Music:** `keth_pass`, `quellan` (exist); `cloudloom` (gap, ~120 s); `hesk_bound`/`hesk_summon` (gap); `avalanche_ram` (exists).
- **New systems:** a **buff-strip** skill (`unravel` exists in data: check that the engine removes one buff); the **formation-aware** pounce (the lynx strikes the back row first: the CTB engine has no rows today, so the plan default is "strikes the reserve-adjacent slot", or drop the row idea and keep "pounces on the weakest", which the data already does). Breath-fog: a field VFX toggle per actor.
- **Balance:** the Act II curve. The Ram is the "mind the field" boss.

### Ch13 "Gold and Lacquer"
- **Zones and kits:**
  - `ch13/ansedra`: the holy city of perfect stillness: outer moorings with lacquered barges, causeways with gold lamp-posts, gold bowl-domes doubled in a mirror lagoon, Sefir's house, Corran's old house.
  - `ch13/sanctum`: the Sanctum of the Level, the still basin lit from beneath by a light that never moves.
  - `ch13/lamp_archive`: the reading room between stacks.
  - **Kit:** `ansedra.py` (art sheet [ansedra.md](../art/environments/ansedra.md), M3-ENV-721): Order marble and gold, red lacquer, still water. This is the **Order culture kit** SPEC §7.4 lists, and the act's hero zone (bespoke hero meshes on top of the kit, SPEC §7.4).
  - **The still mirror:** a still-water look (the water shader at zero wave amplitude, with an exact planar reflection) is a rendering task, not yet validated (colour script: "ch13 mirror … re-checked when its mood frame is built").
- **Cast and NPCs:**
  - **Sefir Aurane** (host; the art review exists: `sefir_review.md`); **Tobin Varrow** and **Merel Dask** (new, characters; act1_npcs.md defers them to Act II);
  - Tenders, pilgrims, barge-polers, Stillguard (Act I's Stillguard enemy rig re-dressed as guards);
  - **Corran** as Ethren; the Conclave (5 revenants: Sefir, Hesper Oan, Malcor Venn, Ilsabet Rue, Old Tamsin Druse) seen at a distance;
  - Kerrid stays at the outer moorings at night, never in the Sanctum.
- **Enemies:** none (a town and an archive).
- **Vowbound:** **Ethren** (Glimmer). Bind cinematic in the Sanctum (Ysolde before Corran, a Cantor beside her), summon cinematics, kit (Glimmer, Slow and Stop, mass wards), Swell *Still Water*. The art sheet exists.
- **Set piece:** **the Lamp Archive** (ADR 0016): the founders' lamp-ledgers, the Cantor roll's *kept/spent* column and Corran's line ("to be spent at the next Calm"), the same few hands across four hundred years. Nobody says "revenant". Liss lays the pages side by side.
  - **New menu:** a **document reader** that lays two or three records side by side, with the matching hand highlighted on the player's own action (SPEC §6.11's codex "text records"). The ui-menus track is the narrative seat for the codex (M3-NAR-01).
- **Cutscenes:**
  - C1: arrival in the still city;
  - C2: Sefir's hospitality;
  - C3: the Sanctum and Liss before the light;
  - C4: Ethren's binding;
  - C5: the wedding announced;
  - C6: the Archive's three days (2–3 in-engine scenes);
  - C7: the pact of silence; Sefir knows what Liss read;
  - C8: the side scene, Ysolde shows Rhen the house she shared with Corran.
- **Music:** `ansedra`, `lamp_archive` (exist); `sanctum_of_the_level` (gap, ~120 s); `ethren_bound`/`ethren_summon` (gap).
- **New systems:** heresy isn't set yet, but **Order shops** must be marked so Ch14 can close them (§4.2). Ansedra's shops are the Act II tier-2 gear (economy.md rule: about six of the chapter's fights; Ch13 has no fights, so price for Ch12's fights).
- **Balance:** none (no fights). The economy is checked against Ch12's lume.

### Ch14 "The Peace Wedding"
- **Zones and kits:**
  - `ch13/ansedra_lacquer_court`: the red-lacquered colonnade, the dais, the galleries, the Conclave's gallery, the water-steps, the bridal barge and the water-gate.
  - **The lagoon at night** (the `ansedra` lagoon variant): every stroke of the pole is the first ripple in four hundred years; the bells ring; the whole city comes to its windows.
  - **Kit:** `ansedra.py`, extended with the court, the bridal barge (shared with Ch15's `bridal_barge.py`), the pursuit barge with its flat-engine, and window-light instancing for the watching city.
  - **Arena:** `ansedra_lagoon_escape`.
  - **Rendering:** a **ripple propagation** on the still mirror (the water shader's still mode plus a ripple ring source per pole stroke and wake). This is the chapter's hero visual.
- **Cast:**
  - Sefir officiates; the Conclave; Stillguard; Saltwright leaders (Hollowmere's hull-captains, seized);
  - **Tobin** (killed shielding Merel); **Merel** (cuts her bridal barge loose, poles the party out, stays to drop the water-gate, and is taken in wedding red with Tobin's blood on her sleeve); **her father** (a Warden's Stillguard take her; the plan reads "her father" as one of the Conclave, Narrative to name which);
  - **Warden Malcor Venn** (the boss: a person, so the characters track).
- **Boss:** **Malcor Venn** on the Conclave's pursuit barge, two phases.
  - Phase 1: the barge's bound **flat-engine** pulls the water flat and slows the timeline. Liss breaks it (a breakable part: act2/flat_engine.md).
  - Phase 2: he boards, fighting as a living-seeming man. Nothing about what he is is revealed.
  - Rules: the fight is `scripted` (no Escape); Liss should be `locked_active` in phase 1 or carry a lent skill (set_piece_battles §1).
  - **The open question in act2_roster** (is the flat-engine its own combatant or a part?): plan default is **a part** (CreatureActor `break_parts`) with a timeline entry row for its slow pulse (an `entries` row, role `tide`, so pillar 4 holds: the player sees the pulse coming).
- **Set piece: the wedding trap** (M4's named set piece, SPEC §10.2). Ceremony at dusk on still water → the Conclave springs the trap → the Saltwright leaders are seized → **the party is declared heretics** → Tobin is killed → the barge escape → Kerrid holds the water-steps, last onto the barge → Merel stays → the boss on the lagoon → the Warden left standing on his crippled barge in the ripples.
  - **Design default:** the trap is a cutscene into a short **set-piece battle on the court steps** (an objective battle: hold the steps for N turns while Merel cuts the barge loose; Kerrid `locked_active`, the ward entry is "Merel's knife", ADR 0100's schema). Then the barge escape is a cutscene with the boss fight inside it. The Ch8 set-piece schema covers all of this with data. Narrative and Combat confirm.
- **Cutscenes (the act's longest chapter of cinema):**
  - C1: the ceremony;
  - C2: the trap and the declaration of heresy;
  - C3: Tobin's death;
  - C4: the cut barge and the first ripple;
  - C5: the bells and the city at its windows;
  - C6: Merel at the gate, taken;
  - C7: the Warden's barge closes (boss intro);
  - C8: the Warden left standing.
  - No side scene (the outline: the chapter runs straight on).
- **Music:** `peace_wedding` (the ceremony loop exists; **the break at the trap** is a gap); `lagoon_escape` (gap, ~2 min); `malcor_venn` (gap, 2 stems).
- **New systems:**
  - **Heretic state** (`ch14_declared_heretics`): Order shops close, Order save shrines are refused or desecrated (decide which), Stillguard become a hostile faction (no random fights in Act II, per the roster), the party's title in the status menu changes;
  - **timeline-slow field** (the flat-engine): `field_rules` with Slow on the party side already exist;
  - **breakable part targeted by one hero** (Liss's break): a skill `breaks_part` or a `requires_actor` on the part's targeting.
- **Balance:** the Warden on the Act II boss curve; the step-hold set piece on the Ch8 set-piece curve (`scripted_escape` counts as a win).

### Ch15 "Unlamped"
- **Zones and kits:**
  - `ch15/open_sea`: the unlamped bridal barge drifting south at night, Tobin's bier under Merel's bridal cloth, the shoal of an old Rising's held dead below, the bow at dawn in fog.
  - `ch17/hollowmere`, first visit: the Saltwright flotilla, lashed hulls, windmills, tide-wheels, the dock, the supper, the pyre-raft. Act III's zone: the kit and the zone are shared with Ch17, so build them once, at final quality, here.
  - **Kits:** `bridal_barge.py` (art sheet [open_sea_ch15.md](../art/environments/open_sea_ch15.md), M3-ENV-720) and `hollowmere.py` (art sheet [hollowmere.md](../art/environments/hollowmere.md), M3-ENV-723; its grade file `hollowmere_grades.py` may already exist, §3). Saltwright scrap-tech is the culture kit SPEC §7.4 lists.
  - **Water:** `night_sea` (validated); `bridal_barge_night` arena; the shoal's held motes rising from below.
- **Cast:**
  - Party; Merel's absence; Tobin's body (a covered bier: no corpse model needed);
  - **Liss's father** (Hollowmere's dock-master: new, characters; name him in the beat sheet); hull-captains; Hollowmere crowd (Saltwright costume set on the crowd generator).
- **Boss:** **the Wakefin**, fought on the drifting barge in the dark. Telegraphs are sounds and the sea-glow (pillar 4: the timeline still shows them). Music stems exist; the art sheet exists.
- **The reveal: Kerrid**, at sea and by his own word (ADR 0020, 0022; kerrid.md §Act II).
  - Past midnight the barge drifts over the shoal; held motes drift toward him; a few of his own leave his hands through the rope-burns (held cyan, up to 0.6 intensity, sideways).
  - He sits, holds his hands still, and tells them about Corrow in 1001. Nobody performs a rite, nobody attacks.
  - The act's longest dialogue scene (~2.5 min) under `kerrid_at_sea`. Kerrid's `grief` and `guilty` face rows are reserved for it (art/characters/kerrid.md §face). The mouth must read through the beard ("so the mouth shows when he finally speaks at length").
  - **The reveal "rig"** is three things: (1) the per-actor mote-emission sockets on the rope-burns (kerrid.md §9) driven by a cutscene track; (2) the held-mote shoal VFX with attraction toward one actor; (3) Kerrid's long-speech facial performance. None needs a new skeleton.
- **Set pieces:** the reveal; dawn: Liss sings a current-song into the fog and **Hollowmere answers**; Liss tells her father; **Toma's faith breaks**, he confesses the camp burning to Liss, and she lets him carry Tobin to the pyre-raft.
- **Cutscenes:**
  - C1: the unlamped drift;
  - C2: the Wakefin intro and its fall;
  - C3: **the reveal** (the act's emotional peak);
  - C4: the fog and the current-song;
  - C5: Liss and her father;
  - C6: Toma's confession;
  - C7: the pyre-raft;
  - C8: the side scene, Rhen and Liss's father share a supper and two memories of Dace.
- **Music:** `unlamped` (exists); `wakefin` (exists); `kerrid_at_sea` (gap, ~2.5 min); `hollowmere_answers` (gap, ~60 s); a Hollowmere zone loop (gap: act3_plan.md may hold it, §3); the pyre-raft (no new cue: Narrative picks a reprise).
- **New systems:** a **darkness-lit battle** (battle-presentation: the arena's light is the sea-glow, telegraph VFX as glow and sound); Kerrid's codex page updated (in the bible's own words: "unrisen", "held"; `tools/banned_terms.txt` bans the inspiring game's term for the lingering dead); no random fights on the barge.
- **Balance:** the Wakefin on the Act II boss curve. Darkness must never hide information the timeline should show.

### Ch16 "The Edge of the World"
- **Zones and kits:**
  - `ch16/pale_rim`: white shallows under a white sky, the waiting Hollowmere ship, the wade by the cairns. Days pass (a time-skip montage, not days of walking).
  - `ch16/drowned_choir`: the ring of colossal mouths at moonrise in the Choir's sunken bowl.
  - **Kit:** `drowned_choir.py` (art sheet [pale_rim.md](../art/environments/pale_rim.md), M3-ENV-722); this is a **hero zone** (SPEC §7.4: bespoke hero meshes for the Choir).
  - **Water:** `pale_rim` (validated; the game's lowest contrast). **Arena:** `drowned_choir_ring`.
- **Cast:** party (Kerrid walks last, as on a stair); **Sefir** in person; **Sefir's Abiding guard** (people: Stillguard elite or the Conclave's revenant guard, so characters); **Kesh** (a colossal woman of standing seawater).
- **Enemies:** `glass_skate`, `rim_crawler` (variant of the tide crawler): data exists; models don't.
- **Boss:** **Sefir's Abiding guard** (two stems: the storm waking early is stem 2), then the storm wakes as Imra's heart falters, Kerrid holds the line, and the party is swept away. The second half is the Undertow render (§8.2 item 9), at the Choir.
  - **Design default:** the storm's waking is a `scripted_escape` set piece (Kerrid `locked_active`, "Holding the line"), as Ch8's Reach.
- **Vowbound:** **Kesh** (all six elements in turn). The binding is the reveal of what the Hush does: through Kesh's memory, the singer becomes the storm's next heart, and Sefir is shown binding her in the stones.
  - Needs a design sheet (`vowbound/kesh.md`: **gap**, the only Vowbound without one), model, rig, element-cycling VFX, data, and a bind cinematic built as a **memory sequence** (a new cinematic look: Kesh's point of view a thousand years ago).
  - `kesh_summon` belongs to Act III's H03 (act2_finals.md), so Act II needs only `kesh_bound`.
- **Set pieces:**
  - **the Drowned Choir: what the Hush really does** (the memory sequence);
  - **Sefir's temptation:** "go home", the Long Stillness offered as a gift. Asha refuses; Ysolde: "Then who does it take?"; Kerrid: "I carried her up so you could do this." Said, never drawn.
  - The storm wakes early; Kerrid holds the line; the party is swept away.
- **Cutscenes:**
  - C1: the ship waits at the Rim;
  - C2: the wade (montage);
  - C3: arrival at the Choir;
  - C4: Kesh's binding and memory;
  - C5: Sefir arrives and tempts;
  - C6: the refusal;
  - C7: the guard fight intro;
  - C8: the storm wakes; swept away;
  - C9: **the act break**: a Rhen voice-over.
- **Music:** `pale_rim`, `drowned_choir` (exist); `kesh_bound` (gap); `sefir_go_home` (gap, ~2 min, ORDER_HUM); `abiding_guard` (gap, 2 stems); `act2_break` (gap, ~90 s).
- **New systems:** the **element-cycling** boss and Vowbound telegraph (Kesh: "telegraph each shift on the timeline"); Sefir's guard as people-enemies (the characters pipeline making battle actors for humans: Act I's Stillguard boss is the precedent).
- **Balance:** the Abiding guard on the Act II boss curve, with the storm's waking on the set-piece curve.

## 2a. Guardrails specific to Act II

Act II is where the inspiring game's shape is closest (a wedding that is a trap, the party declared outlaws, a companion revealed as dead). The story track already moved every beat off its echo (ADR 0015, 0016, 0020, 0022; decisions_log N-09, N-15, N-18). These rules hold for every Act II task:
- **The escape goes out across the water, never under the city.** There is no prison, no trial scene and no sewer or underground route at Ansedra.
- **Nothing is revealed about any Warden at the wedding.** No revenant reveal and no rite at the wedding; Malcor Venn fights as a living-seeming man.
- **Nothing frozen in any temple or set piece from Ch12 to Ch15.** No ice, frost, glacier or frozen basin; Ice belongs to Nhoa, under Sunken Vey (Ch11). Keth Pass's snow is weather.
- **Kerrid's reveal is his own confession at sea.** Nobody exposes him, nobody performs a rite on him, and nobody attacks.
- **Nobody says "revenant" at the Archive (Ch13) or the wedding (Ch14)** (act_outline Ch13: Liss just lays the pages side by side), and no line voices the lantern-to-Haluna link aloud before Ch15.
- **Our own words for the lingering dead:** unrisen, held, lifted. `tools/banned_terms.txt` bans the inspiring game's words for them and for the rite.
- **Sefir's temptation is "go home and live".** He never asks to be sung in.
- **New names** (NPCs, foes, skills, places) are checked against `tools/banned_terms.txt` and for near-misses before they land. Add any near-miss you notice.

## 3. What already exists (the inventory)

The detailed, branch-by-branch evidence is [act2_inventory.md](act2_inventory.md) (every `origin/claude/*` branch, 2026-10-30). The summary:

**Where it is.** Almost everything is already **on the integration branch**. Twelve current branches carry byte-identical copies of the 80 task files blocked by ADR 0041. Three Act II commits are still on track branches only and must merge before anything is rebuilt:

| Commit | What | On |
|---|---|---|
| `e1db6170` | M3-CRE-663: `kirru_roost` rebuilds byte for byte on every SIMD path (`ossa_fen.py`) | characters, creatures-b, env-art, m2-slice |
| `2224e784`, `c3f61ea6` (+2) | The primitive pass's rebuilt `rim_crawler` | characters, creatures, creatures-b, m2-slice |
| `6b399185` | `grounding.pinned`: changes `rim_crawler.glb` and `root_crab.glb` | creatures |

The first PC renders of the Act II shots with no baseline (Nhoa, Hesk, Ethren, the kit rows, Hollowmere, the Kite, the Act II maps) are in `docs/kb/qa/gate-runs/big14/out/` on act1-chapters, creatures and battle-presentation only. Integration pruned them, so view them there before re-rendering.

**Against ADR 0041 §3's final bar** (yes / partial / no):

| Area | What exists | Final? | What is missing |
|---|---|---|---|
| **Zones** (15) | Greybox for all of Ch10–Ch16 and Hollowmere (`tools/act1/ch1x_greybox.py`, Ch10–Ch17 zone scripts, flow json, 15 locations, 15 flags, loc, thread and walkable tests) | **no** | Every zone is greybox blocks with no kit placed; no story, NPCs, triggers, shops or shrines; Ch9 doesn't hand off to Ch10 yet |
| **Env kits and arenas** | `ossa_fen.py`/`reedhollow.py`, `lowlight.py`, `keth.py` (with Quellan and Cloudloom pieces), `ansedra.py` (court, basin, stacks, pursuit barge), `bridal_barge.py`, `drowned_choir.py`, `hollowmere.py` (+grades), `kite.py`; grades `lut_ch10_fen` … `lut_ch16_choir`; six arenas (five with baselines; `drowned_choir_ring` has none); swap maps in ossa_fen.md §4, lowlight.md §5, keth_pass.md §6 | **partial** | Not placed in the zones; PC render approval; no mangrove vegetation system beyond the kit trees; no still-mirror or ripple look; Ch13–16 swap maps |
| **Boss creatures** (4 + part) | Mangrove Drowner, Lamp Engine, Avalanche Ram, Wakefin, flat-engine: mesh, rig, clips, scene, portrait, sounds, baselines | **partial** | **No `enemies.json` row and no encounter for any boss**; break parts unwired; VFX (snagged motes, lamps, snow, wake) not built |
| **Regular creatures** (11) | All built (M3-CRE-627/628/645), with sounds and baselines; ten have enemy rows and encounters (M4-C10-03, M4-C11-03) | **partial** | **The enemy rows have no `model` key**, so they fight as capsules; `conduit_crawler` has no row; no skill VFX; suites run on the Ch8 loadout |
| **People bosses** | Arenas only | **no** | Malcor Venn and the Abiding guard: no sheet, model, music or encounter |
| **Vowbound** | Nhoa, Hesk, Ethren modelled (13 clips each, `vowbound_pending`, summon-path tests, held forms) | **partial** | `vowbound.json` rows, skills, Swells, summon and bind VFX, first-call flags, baselines |
| **Kesh** | Story only (vowbound.md §7) | **no** | Sheet (M3-CRE-649 wrote nothing), model, everything |
| **Music** | 12 zone finals and 4 boss stem pairs rendered (LFS) with cue rows; Act II creature SFX for all 15 creatures | **partial** | `music.json` has **no zone rows for Ch10+** and no boss encounter or phase rows; 14 cues not written (scene cues, stings, cloudloom, sanctum, Malcor Venn, the Abiding guard, act2_break) |
| **Battle presentation** | `choreo.json` intros and phase moments for the four creature bosses (M3-BPR-408/418), `test_battle_act2_bosses.gd` | **partial** | Waits on the enemy rows; no shots; no Act II skill VFX; no Vowbound summons |
| **Menus** | Act II area maps (15 zones), Act II codex places and peoples, the act card for Act III, shop and inn data (Quellan, Ansedra, Hollowmere), the Kite map (Act III) | **partial** | Baselines; maps follow greybox layouts; no story codex; no triggers; no document reader; no portraits for new NPCs |
| **Characters** | Kerrid (M3-CHR-505 in review), Pell (battle kit todo, M3-C09-07), Sefir (Act I model) | **partial / no** | Tobin, Merel, Malcor Venn, Liss's father, the Kirru, the Ullari: nothing on any branch; Kerrid's reveal VFX and facial pass |
| **Story** | act_outline Ch10–16, the ADRs, character sheets, colour script, env, creature and audio sheets | **no** | **No beat sheet and no `.dlg` for Ch10–16 on any branch** (M4-C10-01 … M4-C16-01 unstarted) |
| **Balance** | 10 regular suites, `--check` clean, on `ch08_seawall` | **partial** | No Act II loadout; no boss suites; no set-piece suites |
| **Audit tool** | `placeholder_audit.py` stops at `LAST_CHAPTER = 9` | **no** | `--act 2` (ADR 0203 names integration-qa) |

**The ADR 0041 tasks at the gate.** ADR 0203 says the ADR-0041-blocked tasks move to `todo` when the gate passes, but only the **Act II** ones should. Act III stays paused. The Lead flips these at the gate:
- **Act II → `todo` (58):**
  - audio M3-AUD-831, 839–845, 849;
  - battle presentation M3-BPR-408, 418, 419;
  - creatures M3-CRE-620, 621, 623, 624, 626, 627, 628, 635, 637, 642, 643, 644, 645;
  - environment M3-ENV-716–718, 720–722, 732–736;
  - UI M3-UI-206, 207, 208, 209, 210;
  - 15 of the 16 M4 tasks (all but M4-AUD-1001);
  - M3-CRE-649 (only its Kesh sheet: split it, §6);
  - M3-ENV-723 (Hollowmere: its Ch15 first visit is Act II).
- **Close, don't flip (3):**
  - M3-AUD-804/805 (the sketches, superseded by the finals);
  - M4-AUD-1001 (satisfied: creature_voices.json has non-silent rows for all three Ch10 foes; verify and close).
- **Stay blocked, Act III (18, plus M3-CRE-649's revisit half):**
  - audio M3-AUD-836, 851, 852, 853, 856, 858, 859;
  - creatures M3-CRE-646, 647, 648, and M3-CRE-649's three revisit sheets;
  - environment M3-ENV-725–731;
  - UI M3-UI-205 (the Kite map).
- **Not an act's work (1):** M3-AUD-837 (ADR 0172's render prototype) is tooling. It waits for the PC, not for an act.

**Never rebuild:** the kits, arenas, grades, creature models, Vowbound models, music finals, creature SFX, boss staging, maps and codex rows above. Act II tasks place, wire, finish and approve them. A task that thinks something must be rebuilt states why against the final bar first.

## 4. Cross-chapter systems and menus new in Act II

### 4.1 Party and roster
- **Pell in the formation** from Ch10 (M3-C09-07, `todo`; it's Act I's last hand-off, so it may land before the gate). Plan rule: if it is not done at the gate, it is the first Act II combat task.
- **Seven heroes, three active:** the formation menu must show seven (four in reserve). Check the party bars and the swap UI at seven.
- **Lattice:** the Act II section of the board (new regions reached in Ch10–Ch16; Key Facet gates). lattice.md's seam is "the hub spur's L3 gate". Progression owns it.
- **Swell modes:** one or two new modes unlocked by play in Act II (SPEC §6.2: "players unlock new modes through play").

### 4.2 Heresy (from Ch14)
- One flag, `ch14_declared_heretics`, read by: shops (Order shops refuse), save shrines (plan default: **Order shrines go dark and refuse**; the Saltwright and Kirru places keep working; an un-dark shrine stands at every chapter boundary so the save-point model still holds), NPC barks (ui-menus' state-changing dialogue), the status menu's party title.
- No random Stillguard fights (act2_roster: people are not random foes).

### 4.3 Kerrid
- From Ch10: the rope-burns' `glimmer_held` cue in dim light (character material plus a rendering emission mask; ADR 0022 (g)).
- Ch12: no breath-fog on Kerrid.
- Ch15: the reveal (§2 Ch15). After it, his codex page and barks change; his battle kit doesn't.

### 4.4 The Vowbound (4 new)
- Nhoa, Hesk, Ethren, Kesh: for each, the model and rig (creatures-b's lane in Act I), the summon cinematic (full and short, with the skip toggle), the bind cinematic, battle VFX and the Swell finisher (battle-presentation), the `vowbound.json` row and skills (combat), the `*_bound` and `*_summon` stings (audio).
- The summon menu must list seven.

### 4.5 Menus and UI
- **The document reader** for the Lamp Archive (Ch13) and the codex's found records (Wenna's marks, Ama's keth).
- Codex and bestiary entries for every Act II foe, boss, Vowbound, place and person.
- Shops: Act II tiers (Ansedra, Quellan, Reedhollow trade (if the Kirru trade), Hollowmere), plus the heresy rules.
- Portraits for every new speaking NPC: Tobin, Merel, Malcor Venn, Liss's father, the Kirru eldest and child, the Ullari woman, Corran (Ethren's veil-fall is Act III), and any named Tender.
- The battle HUD for set pieces: the objective counter (the step-hold), a part's broken state (the flat-engine), and the darkness fight's glow telegraphs.

### 4.6 Engine features the Act II fights need
| Feature | For | State |
|---|---|---|
| Drain (`drain_pct`) | `fen_leech` | M4-CMB-1001 (blocked) |
| Rooted (no swap) | `root_crab` | gap |
| Glide (untargetable on alternate turns) | `gallery_ray` | gap (an `untargetable` toggle per turn; phases have it already) |
| Ambush (untargetable until it has acted once) | `glass_skate` | gap |
| Repair a broken part | `conduit_crawler` | gap |
| Strip one buff | `cord_moth` (`unravel`) | check the existing `cleanses` key |
| Field hazard by round | Avalanche Ram | `field_rules` exists |
| Timeline slow field | flat-engine | `field_rules` exists |
| Breakable part, one hero's answer | flat-engine | gap (`break_parts` exists on CreatureActor; the targeting rule doesn't) |
| Element cycling with timeline telegraph | Kesh | gap |
| Darkness-lit telegraphs | Wakefin | presentation gap |

### 4.7 Balance
- The Act II curve (balance_targets.md): regular naive 5–35%, role_answer ≥ 90%, smart ≥ 95%, p90 ≤ 40; boss naive ≤ 3%, role 55–80%, smart 70–90%, p90 ≤ 80.
- **A Ch10 loadout and per-chapter loadouts to Ch16** (each chapter's Lattice progress, gear tier and party). Today all ten Act II suites run on `ch08_seawall`.
- Boss suites for the six bosses and the two set pieces; every boss sandbox-tested before integration (SPEC §6.7).
- The economy: Act II tier gear and consumable prices by economy.md's rules of thumb.

## 5. The critical path and the risks

### 5.1 What must land first (in order)
1. **Day 0 (the gate's first batch, by the Lead):**
   - flip the 58 Act II tasks to `todo` and close the 3 listed in §3;
   - merge the three unmerged Act II commits (`e1db6170`, the `rim_crawler` rebuild, `6b399185`);
   - apply act2_tracks.md.
2. **Story is the long pole.** No beat sheet and no `.dlg` exists for any Act II chapter, and every cutscene, scene cue, NPC, codex page and boss placement hangs off them. The seven sheets are chained (M4-C11-01 depends on M4-C10-01, and so on).
   - Start the story track on day 1 with Ch10.
   - **Write Ch14 and Ch15 early, out of order:** they carry M4's named set piece and the reveal, and the characters track needs their cast lists before anything else.
3. **Cheap wins that make existing work count:**
   - `model` keys on the ten regular enemy rows: they fight as capsules today;
   - the four creature bosses' enemy rows and encounters with M3-BPR-419's staged ids, so the existing models, staging and music go live;
   - music.json zone rows for the twelve existing finals (M4-A2P-091);
   - the three Vowbound rows (M4-A2P-024);
   - `placeholder_audit.py --act 2` (M4-A2P-100; allowed now as tools work, ADR 0203).
4. **The zone kits are placed before encounters are called done.** The kits and arenas exist; placing them (M4-A2P-040…046, M3-ENV-736, M4-A2P-017) is the largest volume of work in the act. It runs in parallel from day 1 on env-art (Ch10–12) and env-art-b (Ch13–16).
5. **Engine features before boss suites:** rooted, glide and ambush, repair, part-break targeting, element cycling (M4-A2P-020…025), plus drain (M4-CMB-1001). Pell's battle kit (M3-C09-07) comes before any Ch10 balance number.
6. **The longest art lead times:**
   - the **people of Ch13–14** (Tobin, Merel, Malcor Venn; M4-A2P-050/051), because the characters track also carries Act I FAST-TRACKs;
   - **Kesh** (sheet, then model; M4-A2P-057);
   - **the still mirror and ripples** (M4-A2P-047), which gates Ch13–14's look.
   Start all three on day 1.
7. **Kerrid's reveal rig** is VFX plus a facial pass, not a new skeleton (M4-A2P-049, 054, 073). It needs M3-CHR-505 (his model, in review) merged.
8. **Last:** the Act II playthrough (M4-A2P-101) and the gate file (M4-A2P-102).

### 5.2 The chain, as a picture
```
beat sheet ─► .dlg ─► cutscene staging ─► scene cues ─┐
kit placement (env) ─► greybox retired ───────────────┼─► chapter playable ─► audit zero ─► playthrough ─► Act II gate
enemy rows + engine features ─► boss suites ──────────┤
models (people, Kesh) ─► portraits, VFX, summons ─────┘
```

### 5.3 Risks and unknowns
| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | **Story throughput:** seven chained beat sheets plus ~10–14k words of script, with no narrative track in Act I | Everything downstream idles | A dedicated story track (act2_tracks.md); Ch14/15 early; sheets drafted from act_outline's already-detailed beats |
| R2 | **LFS uploads are blocked** (TRACK-RULES 2026-10-30), and `assets/audio/music/act2/**` is an LFS path | 14 new Act II cues can't be pushed as specified | Files under 5 MB go as plain blobs in a non-LFS path, or wait in PC-QUEUE; the real fix is the human allowing `lfs.github.com` in the network policy (LEAD-ASK) |
| R3 | **No PC renders** (the PC is offline), and many Act II kits and creatures have only unapproved big14 PC renders | Approvals pile up at the gate | Self-render ≤ 15 shots per item and VIEW them; view the existing big14 PNGs on act1-chapters, creatures or battle-presentation before re-rendering |
| R4 | **IP echo:** a wedding trap, outlaws, a companion revealed dead | Guardrail §2 | Plan §2a's rules; the Lead reviews Ch14–16's sheets and staging (SPEC §12.3) |
| R5 | **Hero zones' cost:** Ansedra's still mirror and the Choir's colossal mouths | Perf and the hitch budget (ADR 0203 condition 5) | Perf checks in M4-A2P-047 and M4-A2P-084; real-GPU numbers queue for the PC |
| R6 | **People bosses:** human battle actors at boss quality (Malcor Venn, the Abiding guard) | Ch14 and Ch16 slip | Start M4-A2P-051 on day 1; Act I's Stillguard boss is the precedent |
| R7 | **Act I regressions** from shared files (encounters.json, skills.json, music.json, effects.json, strings) | Breaks ADR 0203's protection | Append-only rows, `merge_union.py`, and Act I tests in every batch |
| R8 | **Scope:** 15 zones, 6 bosses, 4 Vowbound, ~30 cutscenes at the Act I bar | M4 runs long | SPEC §10.2's cut list (act_outline "Cut Notes": Keth Pass folds into Quellan first). Cutting is the human's call (LEAD-ASK) |
| R9 | **Open design defaults** (§2): the sanctum walked, the wedding step-hold, the shrines going dark, the flat-engine as a part, the lynx without rows | Rework if overruled | Each one is a LEAD-ASK, defaulted so work proceeds |

### 5.4 SPEC §16 and other human items
- **No SPEC §16 question is newly due for Act II.** Q1, Q2, Q3, Q5, Q6 and Q7 are answered or defaulted (ADR 0021, 0042). Q4 (voice) is defaulted to none, and Kerrid's long confession is written for text, not voice.
- **Two items only the human can decide:**
  - (a) allowing `lfs.github.com` in the environment's network policy (R2);
  - (b) whether to apply SPEC §10.2's cut list to Act II (R8).
  Both are LEAD-ASKs, so the Lead can carry them to the human.

## 6. Task index

All `status: blocked`, `blocked-by: ADR 0203`; the Lead flips them to `todo` at the gate along with §3's 58. Ids `M4-A2P-001`…`199` are this plan's block.

| Id | Role | Reviewer | Title |
|---|---|---|---|
| [M4-A2P-001](../tasks/M4/M4-A2P-001-ch10-dialogue.md) | narrative | cinematics | Ch10 “Fen of the Kirru” dialogue scripts (.dlg), barks and codex text |
| [M4-A2P-002](../tasks/M4/M4-A2P-002-ch11-dialogue.md) | narrative | cinematics | Ch11 “Lowlight” dialogue scripts (.dlg), barks and codex text |
| [M4-A2P-003](../tasks/M4/M4-A2P-003-ch12-dialogue.md) | narrative | cinematics | Ch12 “The Cold Road” dialogue scripts (.dlg), barks and codex text |
| [M4-A2P-004](../tasks/M4/M4-A2P-004-ch13-dialogue.md) | narrative | cinematics | Ch13 “Gold and Lacquer” dialogue scripts and the Lamp Archive's record texts |
| [M4-A2P-005](../tasks/M4/M4-A2P-005-ch14-dialogue.md) | narrative | cinematics | Ch14 “The Peace Wedding” dialogue scripts: the trap, the heresy, the escape |
| [M4-A2P-006](../tasks/M4/M4-A2P-006-ch15-dialogue.md) | narrative | cinematics | Ch15 “Unlamped” dialogue scripts: Kerrid's confession, Hollowmere, Toma's confession |
| [M4-A2P-007](../tasks/M4/M4-A2P-007-ch16-dialogue.md) | narrative | cinematics | Ch16 “The Edge of the World” dialogue scripts and the Act II break voice-over |
| [M4-A2P-008](../tasks/M4/M4-A2P-008-heresy-barks-and-people-codex.md) | narrative | ui | Act II state lines: heresy barks, Kerrid's revealed barks, and the people's codex pages |
| [M4-A2P-010](../tasks/M4/M4-A2P-010-ch10-playable.md) | cinematics | combat | Ch10 playable at final quality: story wired, Pell out of Reedhollow, the Drowner's encounter |
| [M4-A2P-011](../tasks/M4/M4-A2P-011-ch11-playable.md) | cinematics | combat | Ch11 playable at final quality: the Lamp Engine with its crawlers, Nhoa's binding |
| [M4-A2P-012](../tasks/M4/M4-A2P-012-ch12-playable.md) | cinematics | combat | Ch12 playable at final quality: the Avalanche Ram's snow field, Hesk's binding |
| [M4-A2P-013](../tasks/M4/M4-A2P-013-ch13-playable.md) | cinematics | ui | Ch13 playable at final quality: Ansedra, the Sanctum, Ethren, the Lamp Archive |
| [M4-A2P-014](../tasks/M4/M4-A2P-014-ch14-playable.md) | cinematics | combat | Ch14 playable at final quality: the wedding trap set piece, heresy, Malcor Venn on the lagoon |
| [M4-A2P-015](../tasks/M4/M4-A2P-015-ch15-playable.md) | cinematics | combat | Ch15 playable at final quality: the Wakefin in the dark, Kerrid's reveal, Hollowmere's first visit |
| [M4-A2P-016](../tasks/M4/M4-A2P-016-ch16-playable.md) | cinematics | combat | Ch16 playable at final quality: the Pale Rim, Kesh, Sefir, the Abiding guard and the storm's waking |
| [M4-A2P-017](../tasks/M4/M4-A2P-017-ch13-16-greybox-swap.md) | cinematics | environment | Swap the Ch13–16 and Hollowmere greyboxes onto env-art-b's kits (the Ch10–12 swap is M3-ENV-736) |
| [M4-A2P-018](../tasks/M4/M4-A2P-018-move-act2-generators.md) | cinematics | qa | Move the Act II greybox and flow generators from tools/act1/ to tools/act2/ |
| [M4-A2P-019](../tasks/M4/M4-A2P-019-act2-loadouts.md) | combat | progression | Act II loadouts (Ch10–Ch16) and every Act II suite re-run on its own chapter's loadout |
| [M4-A2P-020](../tasks/M4/M4-A2P-020-rooted-status.md) | combat | progression | Rooted: a status that refuses the swap (the root crab's Root Drag) |
| [M4-A2P-021](../tasks/M4/M4-A2P-021-glide-and-ambush.md) | combat | progression | Glide and ambush: untargetable on alternate turns, and until it has acted once |
| [M4-A2P-022](../tasks/M4/M4-A2P-022-part-repair.md) | combat | character | Repairing adds: the conduit crawler restores the Lamp Engine's broken parts |
| [M4-A2P-023](../tasks/M4/M4-A2P-023-part-break-targeting.md) | combat | character | A part only one hero breaks: Liss and the flat-engine |
| [M4-A2P-024](../tasks/M4/M4-A2P-024-vowbound-rows-nhoa-hesk-ethren.md) | combat | progression | Nhoa, Hesk and Ethren in vowbound.json: stats, skills, Swells, bind flags |
| [M4-A2P-025](../tasks/M4/M4-A2P-025-kesh-element-cycling.md) | combat | progression | Kesh: the element-cycling Vowbound, with each shift telegraphed on the timeline |
| [M4-A2P-030](../tasks/M4/M4-A2P-030-act2-lattice-section.md) | progression | combat | The Act II section of the Lattice (Ch10–Ch16) |
| [M4-A2P-031](../tasks/M4/M4-A2P-031-act2-shops-gear-heresy.md) | progression | combat | Act II shop tiers, gear, drops and prices, and the heresy shop rules |
| [M4-A2P-032](../tasks/M4/M4-A2P-032-act2-swell-modes.md) | progression | combat | One or two Swell modes unlocked by play in Act II |
| [M4-A2P-040](../tasks/M4/M4-A2P-040-ch10-zones-final.md) | environment | rendering | Ossa Fen and Reedhollow dressed, lit and walkable at final quality, with a mangrove vegetation system |
| [M4-A2P-041](../tasks/M4/M4-A2P-041-ch11-zones-final.md) | environment | rendering | The Sunken Vey and Lowlight dressed, lit and walkable at final quality |
| [M4-A2P-042](../tasks/M4/M4-A2P-042-ch12-zones-final.md) | environment | rendering | Keth Pass, Quellan and Cloudloom dressed, lit and walkable at final quality |
| [M4-A2P-043](../tasks/M4/M4-A2P-043-ch13-zones-final.md) | environment | rendering | Ansedra, the Sanctum and the Lamp Archive dressed, lit and walkable at final quality (the hero zone) |
| [M4-A2P-044](../tasks/M4/M4-A2P-044-ch14-court-lagoon-final.md) | environment | rendering | The Lacquer Court and the lagoon at night at final quality, with the watching city |
| [M4-A2P-045](../tasks/M4/M4-A2P-045-ch15-sea-hollowmere-final.md) | environment | rendering | The open sea at night and Hollowmere's first visit at final quality |
| [M4-A2P-046](../tasks/M4/M4-A2P-046-ch16-rim-choir-final.md) | environment | rendering | The Pale Rim and the Drowned Choir at final quality (a hero zone) |
| [M4-A2P-047](../tasks/M4/M4-A2P-047-still-mirror-and-ripples.md) | rendering | environment | The still mirror and the first ripples: Ansedra's water look |
| [M4-A2P-048](../tasks/M4/M4-A2P-048-storm-wakes-at-the-choir.md) | rendering | environment | The storm waking early at the Drowned Choir (the Undertow render on stage) |
| [M4-A2P-049](../tasks/M4/M4-A2P-049-act2-glimmer-events.md) | rendering | character | Act II's glimmer events: the farewell-tide lift, Kerrid's rope-burns, the held shoal, cold breath |
| [M4-A2P-050](../tasks/M4/M4-A2P-050-tobin-and-merel.md) | character | rendering | Tobin Varrow and Merel Dask: models, rigs, faces and wedding costumes |
| [M4-A2P-051](../tasks/M4/M4-A2P-051-malcor-venn-and-abiding-guard.md) | character | combat | Malcor Venn and Sefir's Abiding guard: field and battle actors |
| [M4-A2P-052](../tasks/M4/M4-A2P-052-liss-father-and-crowds.md) | character | rendering | Liss's father, and the Ansedran, Hollowmere and Quellan crowd costume sets |
| [M4-A2P-053](../tasks/M4/M4-A2P-053-kirru-and-ullari.md) | character | rendering | The Kirru people (base, eldest, child, clutch) and the Ullari woman |
| [M4-A2P-054](../tasks/M4/M4-A2P-054-kerrid-reveal-performance.md) | character | cinematics | Kerrid's reveal: the rope-burn emission mask and the long-speech facial pass |
| [M4-A2P-055](../tasks/M4/M4-A2P-055-sefir-in-person.md) | character | rendering | Sefir Aurane at final quality for Act II's close scenes |
| [M4-A2P-056](../tasks/M4/M4-A2P-056-act2-wildlife.md) | character | environment | Act II wildlife for the new zones |
| [M4-A2P-057](../tasks/M4/M4-A2P-057-kesh-sheet-and-model.md) | character | rendering | Kesh, the First Voice: the design sheet, then the model |
| [M4-A2P-058](../tasks/M4/M4-A2P-058-act2-creature-vfx.md) | character | combat | Act II creatures' own VFX: snagged motes, lamps, snow, wake and the regulars' skills |
| [M4-A2P-059](../tasks/M4/M4-A2P-059-avalanche-ram-no-ice.md) | character | rendering | The Avalanche Ram without ice: wet, matted, seep-lit wool (ADR 0015; Lead 2026-10-30) |
| [M4-A2P-060](../tasks/M4/M4-A2P-060-act2-battle-vfx.md) | combat | rendering | Act II battle VFX in effects.json: every new skill, boss and set piece |
| [M4-A2P-061](../tasks/M4/M4-A2P-061-vowbound-summons.md) | combat | rendering | Nhoa, Hesk, Ethren and Kesh: summon cinematics (full and short) and Swell finishers |
| [M4-A2P-062](../tasks/M4/M4-A2P-062-darkness-fight.md) | combat | rendering | The Wakefin in the dark: a battle lit only by the sea-glow, telegraphs by sound and glow |
| [M4-A2P-070](../tasks/M4/M4-A2P-070-farewell-tide.md) | cinematics | narrative | Stage the farewell-tide (Ch10): the clutch sings, turns its back, the motes lift |
| [M4-A2P-071](../tasks/M4/M4-A2P-071-vowbound-bindings.md) | cinematics | narrative | Stage the four bindings: Nhoa, Hesk, Ethren and Kesh |
| [M4-A2P-072](../tasks/M4/M4-A2P-072-wedding-and-escape.md) | cinematics | narrative | Stage the wedding trap and the escape across the water (Ch14) |
| [M4-A2P-073](../tasks/M4/M4-A2P-073-kerrid-reveal.md) | cinematics | narrative | Stage Kerrid's reveal at sea (Ch15) |
| [M4-A2P-074](../tasks/M4/M4-A2P-074-choir-and-act-break.md) | cinematics | narrative | Stage the Drowned Choir: Sefir's temptation, the refusal, the storm, the act break |
| [M4-A2P-075](../tasks/M4/M4-A2P-075-act2-other-scenes.md) | cinematics | narrative | Stage Act II's other scenes and side scenes (Ch11–Ch15) |
| [M4-A2P-080](../tasks/M4/M4-A2P-080-document-reader.md) | ui | narrative | The document reader: the Lamp Archive's records side by side, and found records in the codex |
| [M4-A2P-081](../tasks/M4/M4-A2P-081-act2-portraits.md) | ui | character | Portraits for Act II's new people, bosses and Vowbound |
| [M4-A2P-082](../tasks/M4/M4-A2P-082-heresy-and-seven-in-menus.md) | ui | progression | The heresy in the menus, and the formation and summon menus at seven |
| [M4-A2P-083](../tasks/M4/M4-A2P-083-act2-bestiary-and-hud.md) | ui | combat | The Act II bestiary and the set-piece HUD bits |
| [M4-A2P-084](../tasks/M4/M4-A2P-084-act2-loading.md) | ui | qa | Act II scene changes within the hitch budget |
| [M4-A2P-090](../tasks/M4/M4-A2P-090-act2-scene-cues.md) | audio | cinematics | Act II scene cues: farewell_tide, lagoon_escape, the wedding's break, kerrid_at_sea, hollowmere_answers, sefir_go_home, act2_break |
| [M4-A2P-091](../tasks/M4/M4-A2P-091-act2-zone-loops-and-stings.md) | audio | cinematics | cloudloom and sanctum_of_the_level loops; the Vowbound stings; music.json zone rows for Ch10+ |
| [M4-A2P-092](../tasks/M4/M4-A2P-092-people-boss-stems.md) | audio | combat | Boss stems for Malcor Venn and the Abiding guard, and the battle phase rows for all six bosses |
| [M4-A2P-093](../tasks/M4/M4-A2P-093-act2-ambience-foley.md) | audio | cinematics | Act II ambiences and foley |
| [M4-A2P-100](../tasks/M4/M4-A2P-100-placeholder-audit-act2.md) | qa | lead | placeholder_audit.py --act 2 (report only), and the Act II inventory file |
| [M4-A2P-101](../tasks/M4/M4-A2P-101-act2-playthrough.md) | qa | lead | The Act II headless playthrough: Ch9's end → Ch16's act break, with save and load at every shrine |
| [M4-A2P-102](../tasks/M4/M4-A2P-102-act2-gate-file.md) | qa | lead | The Act II completion gate: docs/kb/qa/act2_complete.md (the same five conditions) |

**Existing tasks this plan relies on, not re-filed:** the beat sheets M4-C10-01 … M4-C16-01; the greybox M4-C10-02 … M4-C14-02 and the regulars M4-C10-03, M4-C11-03; drain M4-CMB-1001; the creature builds M3-CRE-620 … 645; the env kits M3-ENV-716 … 736; the boss staging M3-BPR-408, 418, 419; the menus M3-UI-206 … 210; the audio finals M3-AUD-831 … 849; Pell's kit M3-C09-07; Kerrid's model M3-CHR-505; the lantern housing-mark M3-ENV-719; the Choir body pop M3-HER-1230.
