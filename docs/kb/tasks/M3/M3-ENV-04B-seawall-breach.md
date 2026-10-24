---
id: M3-ENV-04B
title: Ch8 the Seawall falls: the breach state of the Corrow kit (and the Ch9 night pass)
role: environment
status: todo
owner_session: ""
depends_on: [M3-ENV-04]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-04 (filed by env-art when the kit landed without its destroyed state). Ch8 "The Seawall":
"**The wall falls anyway.** The stair was not wide enough" (act outline), and after the storm the Stillguard
cut Liss's hoist down. Ch9 "The Ebbing" plays on the same pieces at night (`ch09`). The kit is built for this:
every wall piece is a 12 m segment on the R = 300 m arc (docs/kb/art/environments/corrow.md §2), so a breach
replaces segments one for one.

## Acceptance criteria
- [ ] `seawall_breach_a/b` (12 m each, on the same arc, LOD chains): the wall broken through to below the town
      level, its courses torn in steps, blocks tumbled into the low town and out onto the rip-rap; the walk's
      paving hanging over the gap; `seawall_breach_end` caps for the segments either side.
- [ ] `watcher_head_fallen`: a head down on its side in the rubble (the face still humming), and a cracked
      head leaning out of the line.
- [ ] `fisher_stair_broken`: the upper flight hanging where the wall went, the hand-line slack.
- [ ] `liss_hoist_cut`: the spar down on the walk, the cut rope ends, the strap-plates still bolted into the
      head (corrow.md §1.4; act outline Ch8 last beat).
- [ ] A rubble field for the flooded lanes (`lowtown_rubble`), so the stair foot reads after the fall.
- [ ] The preview gains a `fallen` phase (post-storm grey light) and a `ch09` night phase (stars, half moon,
      sea-glow, the motes going out to sea are VFX, not the kit), with one composed view each; at most one
      new screenshot baseline.
- [ ] `verify_blender_builds --job corrow_kit` byte-identical; PROVENANCE rows; no glow at the stair foot
      in any shot (ADR 0022 (g)).

## Review log
