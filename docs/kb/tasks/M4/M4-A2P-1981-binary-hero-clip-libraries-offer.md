---
id: M4-A2P-1981
title: "Request (creatures-b -> characters): binary .res for the largest hero clip libraries? Your call"
role: character
status: todo
owner_session: ""
reviewer: character
depends_on: [M4-A2P-1980]
milestone: M4
request-from: creatures-b
---
## Goal
An offer, for characters to accept or decline. The Lead's decision (2026-10-31) is that characters own the clip
pipeline. creatures-b's binary conversion (a0ba72003, M4-A2P-1980 part 2) is reverted, and characters' .tres
rebuild (abf7391b) stands.

## The numbers (measured 2026-10-31, Godot 4.6.3 headless, this cloud CPU; the libraries as of a0ba72003^)

| Library | .tres (text) | .res (binary, FLAG_COMPRESS) | Cold load .tres | Cold load .res |
|---|---|---|---|---|
| asha_clips (74 clips) | 4.02 MB | 0.65 MB | 595 ms (best of 3) | 28 ms |
| rhen_clips (97 clips) | 3.99 MB | 0.66 MB | 573 ms | 30 ms |

- That is about 6× smaller and about 20× faster to load cold.
- **Caveat:** Godot's export converts text resources to binary by default, so shipped builds already get most of
  the load win. The gain is for the editor, the test suites, the screenshot runs, and git (four MB text diffs per
  regeneration).
- The test's 4 MB text cap (test_hero_clips MAX_BYTES) is what started it. The .res sidesteps it, where splitting
  the story clips into their own library would only defer it.

## What the conversion was (to reuse or not)

All of it is in git at a0ba72003 (reverted at c8f7af0bc):
- `hero_clips.py` builds the text as now, then saves it through a headless Godot step,
  tools/characters/clips_to_res.gd (`ResourceSaver.save` with FLAG_COMPRESS, `resource_path` cleared, saved to its
  `res://` path). It is deterministic for that path. A `<hero>_clips.res.sha256` of the text lets the Python tests
  check the build without Godot.
- `BINARY_LIBS` names the heroes converted.
- asset_import_rules.gd's `animation_library_path` falls back to the `.res` sibling.
- The stage scenes and scene_loads.json point at `.res`.
- **Gotcha** if adopted: an existing `.godot` cache keeps the GLBs' imports pointing at the old `.tres`. Reimport
  asha/rhen (and their `_lod1`): add a line to their `.import` files and run `godot --headless --import`; Godot
  rewrites the files back. Deleting the `.md5` doesn't force it.

## Acceptance criteria
- [ ] Characters decide: adopt (they or creatures-b port it onto their current pipeline), or decline (close this).

## Review log
