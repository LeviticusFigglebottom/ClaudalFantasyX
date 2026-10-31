# The Wardens of the crown: Hesper Oan and Ilsabet Rue (Ch19's boss)

M5-A3P-1202. Brief: [act3_ch19.md §5](../../story/act3/act3_ch19.md) (I08). These two are of the Abiding, the
Order's hidden watch, held alive by bound light for four hundred years at the post the founders gave them. They are
sincere, tired and certain, and they believe the engine is mercy. Kin to Sefir's Abiding guard (M4-A2P-051) and to
Warden Malcor Venn, so they are built on the same kit.

## Shared
- **Build:** named entries on the Stillguard kit (`assets_src/characters/stillguard/stillguard_variants.json`,
  `named.hesper_oan` and `named.ilsabet_rue`). Both are women (the body builder's `femininity`/`breast`).
- **Kit:** the Abiding's lames in black lacquer piped in gold, the tunic in order_marble, no helm (their faces are
  the point).
- **Their tell:** irises of pale bound gold (write_materials `IRIS`). Nothing else glows. The light is *held* in them,
  and nothing about them rises (light grammar: nothing rises before H09).
- **When they fall** they lie still (rule 4). Their `ko` is the shared fall, lying flat, and neither has a revive.
  Toma closes Hesper's eyes in I09: the cinematic's.

## Warden Hesper Oan
- A tall, spare woman held at about sixty (1.76 m), upright as a standard. A grey soldier's crop. The face is long
  and lined, with a set mouth.
- **Kit:** the sash and trousers are in the Abiding's old gold, Venn's halberd two-handed, no shield.
- **Fights** as Venn does: the officer's economy, the halberd kept upright at her right, and the two-handed parry.
- Her lines: *"Go home, children. We have this watch."* / *"Four hundred years and nobody has asked to relieve us."*

## Ilsabet Rue
- Small and exact (1.58 m), held at about forty. A dark crop.
- **Kit:** the sash and trousers are ink-black, with no weapon or shield.
- **Props** (`assets/characters/props/act3/`, act3_hand_props.py; the battle actor attaches them):
  - the watch roll, two dark rollers with brass ends and the pale vellum half open between them, in her left fist;
  - the stylus, bone with a brass collar and an iron nib, in her right.
- **Fights writing:**
  - `attack` is one hard stroke of the stylus across the roll ("Noted.");
  - `cast` is the roll's record held out at the party (the watch-roll mechanic);
  - `defend` is the roll raised before her face;
  - `finisher` is the roll snapped up and the stylus driven down ("Mark the time.").

## Files
- **GLBs:** `assets/characters/{hesper_oan,ilsabet_rue}/` (Blender jobs `hesper_oan`, `ilsabet_rue`).
- **Clips:** `hero_clips.py`, the Wardens block.
- **Battle actors:** `game/characters/foes/{hesper_oan,ilsabet_rue}_battle.tscn`.
- **Field actors:** `game/characters/villagers/` wrappers (the crown's scenes).
