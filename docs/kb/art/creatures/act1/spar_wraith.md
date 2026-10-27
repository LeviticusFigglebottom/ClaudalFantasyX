# Spar-Wraith (`spar_wraith`), Ch4 boss

**Idea.** Undertow-spawn tangled in the dead trader's rigging (act_outline Ch4). It came aboard in the Rising and the
rigging held it: now it **wears** the rigging. A long, many-jointed black body hangs in a web of shrouds and ratlines
between two broken spars it uses as limbs, a ship's block-and-tackle swinging from it. It is fought on the deck, under
it. One exaggeration: the rigging as its body.

**Silhouette.** 3.4 m tall, hanging: a dark shape in a web of lines, two long spars angled down to the deck like a
mantis's legs. The rigging lines are the read: nothing else in the game is a silhouette of ropes.

**Palette.** Body `lacquer_black` wet; rigging `timber_weathered`/`sand_cloth` hemp, tarred black near the body;
spars `timber_weathered`; wounds `spawn_wound`. Its changing elemental weak points glow in turn on three knots of the
web (the art is the knots; the colour per element comes from the VFX).

**Clips.** `idle`: it sways in the web, lines tightening and slackening. `attack`: a spar stabs down. `cast`: the web
draws taut and the body rises into it. `hit`: it jerks in the lines. `ko`: the lines part one by one and it drops to
the deck. Rig: a body chain, two spar arms, a dozen line bones. Budget ≤ 16k.

## The two phases (m2-slice act1_ch04 §5, built 2026-10-24)

- **Shrouded** (phase 1): its own sail-membranes, a torn and tarred canvas, wrap the body (`Shroud`, its own mesh,
  two-sided, rotted through in rents, with a ragged hem short of the head). Fire is the weak point there; the burn
  is VFX.
- **Hauled Down** (`hauled_down`): the shroud goes at once (`hide`), `phase_drop` (1.6 s) drops the body out of the web
  onto the deck while the spars stay planted, and the sea it hauled up its lines then sheathes it (`Sheath`, a
  streaked water skin, `show_after`). The head stays bare. On the deck it idles on `idle_deck` and strikes with
  `attack_deck`, `cast_deck` and `hit_deck` (the base clips played from the deck pose, mapped by the phase's
  `clips`). 8.0k triangles in all.
