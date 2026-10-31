# The Cage, as built: the seats amendment (M5-A3P-1851)

creatures-b's note beside creatures' sheet ([the_cage.md](the_cage.md), unchanged). It records how the build
(`assets_src/creatures/the_cage/build_the_cage.py`) applies the amendment in act3_roster.md ("Reconciled with the Act
III beat sheets", U07): "each bay becomes a **seat** (the figure seated, chained at wrists and ankles), with the chains
as the breakable part per seat ... one combatant, four parts." Where this note is silent, the sheet stands: the plan,
the heights, the palette, the weak points, the camera numbers, and the break's timing and founder cues.

## What changed from the sheet

- **Seats, not standing bays.** Each bay keeps its posts, arch, crown lamp and keystone clasp, at the sheet's heights
  (2.9 m outer, 3.3 m inner).
  - A brass seat (0.48 m over the sill) has armrests at 0.92 m and a salt-glass backrest bar up to about 1.8 m.
  - `q<n>_seat` is the founder's root: on the seat, +z out of the bay.
  - A seated figure up to 1.9 m tall fits.
- **Chained at the wrists and ankles.**
  - The wrist rings (`q<n>_wrist_l/_r`, at ±0.34 m, y 0.97, over the armrests' fronts) chain to the posts' feet.
  - The ankle shackles (`q<n>_ankle_l/_r`, ±0.14 m on the sill) chain to the sill.
  - `_l` is the founder's own left (+x, facing out). The hands rest on the armrests, the palms down: a seated vigil,
    never arms spread or raised.
- **No gate leaves.** The front of a seat is open, so the founder is seen whole. The chains are the breakable part,
  so the gates had no job left.
- **The anchor chain** keeps the sheet's bones (`q<n>_chain_0..2`), with heavier mooring links, to a ring on the floor
  1.2 m behind. It goes slack in the `ko` and eases in the break; its parting at 1.0 s is effects', not a mesh change.
- **The bay doesn't sag on break.** Its sill and seat are the frame's, so a held sag would also move the seat the
  founder rises from. The bay jolts, and its dark crown lamp swings.
- **The `ko` doesn't break the last quarter.** The KO can't swap meshes (the sheet's open question), so the row has a
  fourth phase, `break_q4`, for Combat to place just above 0 HP. The `ko` is the empty frame letting go: the chains
  slack, the arches leaning out and the crown lamps swinging.
- **The phases are cumulative.** `break_q<n>` hides `Q1Whole..Q<n>Whole`, shows `Q1Broken..Q<n>Broken` and, once its
  clip has played, hides `FounderQ1..FounderQ<n>`. One blow that crosses two thresholds then leaves no quarter
  whole. The break order is fixed, q1 to q4 (the sheet's proposal).
- **The founders' placeholders.** `the_cage_battle.tscn` holds `FounderQ1..Q4` (Node3D) at each seat's pose. The
  characters track instances its figures under them.
- **Rig:** 47 bones: the sheet's set without gates, with ankle rings, plus `vfx_core` at the row of clasps.
  **Triangles:** 17.4k (budget 22k).

## For the characters track

- The founders' bound pose is **seated**: hands on the armrests at the wrist rings, feet at the shackles.
- The `freed` clip is timed to the cue at 0.5 s: they rise from the seat, step down, give their thanks, then kneel
  and lift, as the sheet's table, but starting seated.
