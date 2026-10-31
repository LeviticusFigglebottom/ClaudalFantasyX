---
id: M5-A3P-1951
title: "Act III score, part 2: the finale (Ch21 H01-H06: the heart, Kesh, Sefir)"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: [M5-A3P-1950]
reviewer: story
milestone: M5
---
## Goal
The finale's cues as act3_ending.md names them, before the Letting (M5-A3P-1950).

## Acceptance criteria
- [x] **`heart_approach`** (H01–H02, a 72 s loop): the heart's low A drone, its colour sinking. Over it, the Hush's first phrase backwards, very slow: its notes last to first, each a whole piano note reversed in time, so it swells out of nothing and stops where the hammer would strike. H02's `@music silence` cuts it on Sefir's first word.
- [x] **`heart_rest`** (R1, a 48 s loop): the drone alone at a bed's stillness (-22).
- [x] **`kesh_first_voice`** (H03, a 60 s loop at 112 BPM): a 3+3+2 frame-drum and low-string ostinato. The stones' choir sings each verse's first line in Lamptongue (verses 1–7) to the Hush's first cell, a step higher each verse, so the seven climb; the seventh, her own, is the fullest. The metallophone answers each line. Then `release_sting`.
  - The verses run in their own time. Her BattleCycle changes element every turn she acts, faster than a sung line. **For combat:** a `cycle_changed` signal would let the music follow it if wanted.
- [x] **`sefir_warden`** (H04, a 74 s loop): C major, the Order's pure key. The congregation hums ORDER_HUM three times over close, dark strings; his motif hangs on its C# over F; soft low bells (C, then C# under the held C#). A dead room: beautiful and airless.
  - **For combat:** no draft starts H04's fight yet. Its encounter id needs a `battle.encounters` row to `sefir_warden`.
- [x] **`sefir_heart`** (H05–H06, a 51 s loop in 7/8 (2+2+3) at 132 BPM): the storm's own note, defined here as the heart's A (heart.py's drone). Many huge low throats on A swell a quarter tone over a sub, under rock-fusion percussion (a big drum on each group, a slap backbeat, ghosts, a tom run every eighth bar) and a Phrygian low-string riff. His motif returns, and its C# now lands on an A major chord: the leading tone that never led has found its chord, the storm's.
- [x] `battle.encounters`: `ch21_kesh` maps to `kesh_first_voice` and `ch21_sefir_heart` to `sefir_heart` (the drafts' ids, pending combat).
- [x] Checks:
  - render_all: loudness, loop seams, determinism.
  - The `kesh_first_voice` seam first failed on flux (a pile of onsets on the seam). It is now offset half a beat, `downbeat_offset_s` 0.268, and passes at 0.57x.
  - True peaks are held under -1 dBTP with a -2.0 master ceiling.
  - Mono fold and PROVENANCE.

## Review log
