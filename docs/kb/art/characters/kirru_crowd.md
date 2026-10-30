# The Kirru crowd (Reedhollow's clutch)

Owner: the creatures track (the Lead, 2026-10-30: "build the Kirru crowd bodies yourself in the crowd generator ...
Characters keep the named Pell; you own the crowd variants"). Design source: [pell.md](pell.md) (proportions §1,
silhouette §2, fur, crest and whiskers §5, posture §10) and [bible §8](../../story/bible.md) (the Kirru: 2.1–2.4 m,
very still). The named Kirru (Pell, Owa, the Kirru child) are the characters track's (act2_tracks.md row 55).

## How they are built
- **Pell's own build, re-parameterised.** `assets_src/crowd/kirru/build_kirru.py` imports `build_pell.py` as a library
  and runs it on Pell's `pell_params.json` with a body's overrides from `kirru_bodies.json` deep-merged on top
  (`kirru_params.py`). The bodies therefore share his head warp, fur, crest, whisker and webbing rules, his mantle,
  name-shell and fishing-staff, and his palette rules (wet dark brown, cream, reed gold and bone). A fix to Pell reaches
  them on their next rebuild.
- **Costume measures scale with height.** Pell's `_costume` and `_shell` are in his own metres. Every `*_m` measure
  there is scaled by the body's height over his. Without that, the youngster's mantle bunched and a cord stood off
  its shoulder.
- **What ships.** Only the LOD1 ships (about 27k triangles), as `assets/crowd/<id>/<id>.glb`, with Pell's maps
  regenerated on the body's bake at half resolution (about 6.5 MB a body).
- **Mantle reed.** Each body's `textures` block sets the reed colour: dark and weathered for the man, warm for the
  woman, bleached for the elder, green for the youngster.
- **Clips.** `kirru_clips.py` takes `idle`, `talk` and `walk` out of Pell's own library (`pell_clips.tres`: the
  wading-bird stand, the neck's S, his stillness) onto the crowd armature, as `crowd_kirru_clips.tres`. The crowd
  import fits the hips track to each body's height.
- **Build jobs.** One `crowd_kirru_*` job per body in tools/dev/blender_builds.json, verified byte-identical.

## The four bodies

| Body | Read |
|---|---|
| `kirru_man` | 2.38 m, a little heavier than Pell, the darkest fur, a weathered reed mantle |
| `kirru_woman` | 2.20 m, slighter, warm red-brown fur, a broader cream stripe |
| `kirru_elder_woman` | 2.16 m, grey guard hairs through the fur (50%), a pale worn crest, bleached reed |
| `kirru_youngster` | 1.62 m, 7 heads, a shorter crest and whiskers, green reed, a shorter staff |

Age shows only in the fur and the crest (pell.md §1): no stoop, no lines. They carry the carved name-shell (Pell's is
the blank one) and a staff sized to their height.

## Reedhollow (`game/data/world/npc/zones/ch10_reedhollow.json`)
- **The clutch.** Eight `body` rows sit on the greybox's hidden `clutch_0..7` stage actors on the Shore, so the
  farewell-tide (B09) shows Kirru. The bodies alternate so no two neighbours match in either line.
- **The watchers.** One stands on each house platform, facing the lagoon (R01: "already watching from the
  platforms"), on a `CrowdSpots` stand-in made from the row's `at`.
- Pell is never inside (rule 3).

Review shots: `kirru_lineup_front` and `kirru_lineup_faces` (game/levels/_tests/npc/kirru_lineup.tscn, the four
beside Pell).
