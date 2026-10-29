---
id: M3-AUD-858
title: "Act III: Ch19's revenant pair and Kerrid's last night (hesper_and_ilsabet, two boss stems; kerrid_last_night)"
role: audio
status: blocked
owner_session: "audio worktree agent"
reviewer: design
depends_on: [M3-AUD-836]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
Two of act3_plan.md §2's Ch19 rows. `hesper_and_ilsabet` is the boss on the Iskarra Lamp Spire's crown
(`iskarra_spire_crown`): Wardens Hesper Oan and Ilsabet Rue, two of the Abiding, who have held their posts for
centuries and fight together. **Two lines that never meet**: one stem per Warden, two independent voices in
counterpoint that never land on a unison or share a cadence, so that when one Warden falls `phases` takes that stem
out and the other plays on alone as a whole fight. It has the Order's hum for colour, beautiful and airless like the
Conclave, but it is a battle: driven, not a lament. `kerrid_last_night` is his last quiet night with Rhen, at rest:
KERRID_STAIR's stride under a low string at KERRID_STAIR_BPM, the night sea, and nothing ending yet. It must not
spend E3's gesture (`goodbye_kerrid` slows the stair to a stop).

## Acceptance criteria
- [x] `assets_src/music/act3/hesper_and_ilsabet.py` renders `hesper_and_ilsabet_s0.ogg` (Hesper) and
      `hesper_and_ilsabet_s1.ogg` (Ilsabet) with a `.loop.json` each into `assets/audio/music/act3/`. The cue is in E
      aeolian over the hum's G, 4/4 at 120 BPM, 45 bars (five nine-bar grounds), **90.00 s**, both stems exactly
      3,969,000 samples, LOOPSTART 0. The files start a sixteenth before bar 1 (`downbeat_offset_s` 0.125). Measured
      on the decoded files: stem 0 **888,988 bytes, -19.00 LUFS, -2.55 dBTP**; stem 1 **994,960 bytes, -19.00
      LUFS, -4.25 dBTP**; the pair summed **-16.03 LUFS, -1.70 dBTP**. Each stem alone is 3.0 LU under the pair: two
      equal, uncorrelated halves. Seam: stem 0 jump **x1.48**, flux x1.67; stem 1 jump **x0.65**, flux x1.01. Vorbis
      tags match the sidecars, and determinism is identical for all four files.
- [x] The lines never meet, and this is checked in code: `never_meet()` runs at every render and raises on a
      violation. It checked 16,704 note pairs. No two notes of the same pitch class start within a sixteenth of each
      other. No two notes of the same pitch class sound together for more than a beat (the longest is 1.0). The held
      cadences never overlap: Hesper holds B or F# on ground beats 29-35, and Ilsabet holds D on 11-16.5, because her
      phrases start half a ground after his. The registers never cross (Hesper B3-E5, Ilsabet F#5-A6).
- [x] Each stem carries its own half of the pulse and harmony, so either one alone is a whole fight. Stem 0 has
      Hesper's marcato low strings, the hummed ground, a low-string 3+3+2 eighth ostinato, and frame drums with a big
      drum. Stem 1 has Ilsabet's glass with violins, a high open pad and a bowed low root, a metallophone 3+3+2
      figure, and a big drum and kettle gong on the same accents.
- [x] `assets_src/music/act3/kerrid_last_night.py` renders `kerrid_last_night.ogg` (through-composed). It is in D
      major, 4/4 at **48 BPM (KERRID_STAIR_BPM, never changed)**, 14 bars plus the ring, **73.70 s, 782,399
      bytes, -16.04 LUFS, -2.29 dBTP**, and determinism is identical. The tread and the stair keep exact tempo to the
      end and fade in level only. The cue ends open on a held G major-ninth (IV with A on top), with no cadence and no
      slowing. No voices.
- [x] Every tune that recurs is loaded, never retyped: motifs.py `ORDER_HUM` (the ground) and `KERRID_STAIR`,
      `KERRID_STAIR_BPM`, `KERRID_STAIR_STRIDE`; sefir_theme.py `glass` (the Conclave's instrument); kerrid_stair.py
      `bowed`, `cello_body`, `BOW_PRE`; unlamped.py `sea`. Everything else is original (SPEC §2): no samples,
      recordings or generated audio.
- [x] Both rows are in render_all.py `ACT3_FINALS`. Nothing under `assets/audio/music/act3/` is committed (LFS is
      not live). `python3 -m unittest tools/tests/test_act2_finals.py` passes, and `validate_data.py` reports 0
      errors.
- [ ] Design's review. Do the two lines read as two Wardens, independent but in step, and does either stem alone
      still sound like a fight? Is the night cue at rest, with nothing ending yet?
- [ ] Design/Tech: the encounter must emit a `phase_changed` id when one Warden falls (`hesper_fallen`,
      `ilsabet_fallen` below). `battle_audio.gd` already honours `stems_off`. Note that the surviving Warden's stem
      plays at about -19 LUFS, 3 LU under the pair. If that drop reads as too much in play, a per-stem volume would be
      a runtime change, not a re-render.
- [ ] Lead: add the music.json rows below once LFS is live and the encounter and the `ch19` night scene exist.

Intended music.json rows (not added here, because music.json is owned elsewhere and the files are waiting on LFS):

```json
    "hesper_and_ilsabet": {
      "stems": [
        "res://assets/audio/music/act3/hesper_and_ilsabet_s0.ogg",
        "res://assets/audio/music/act3/hesper_and_ilsabet_s1.ogg"
      ],
      "start_stems": [0, 1],
      "_note": "Ch19 boss, Wardens Hesper Oan (stem 0) and Ilsabet Rue (stem 1) on the Lamp Spire's crown: two lines that never meet over the Order's hum as a ground; 90.0 s loop, both stems from the start; when one Warden falls their stem goes out and the other plays alone (M3-AUD-858)"
    },
    "kerrid_last_night": {
      "file": "res://assets/audio/music/act3/kerrid_last_night.ogg",
      "_note": "Ch19, Kerrid's last quiet night with Rhen: the stair at rest at 48 BPM under a solo cello, the night sea; 73.7 s, ends open on a held chord (never slows: goodbye_kerrid owns that) (M3-AUD-858)"
    }
```

```json
  "battle": {
    "encounters": {"ch19_hesper_ilsabet": "hesper_and_ilsabet"},
    "phases": {
      "hesper_fallen": {"stems_off": [0], "sec": 2.5, "_note": "M3-AUD-858: Hesper falls; Ilsabet's line plays on alone"},
      "ilsabet_fallen": {"stems_off": [1], "sec": 2.5, "_note": "M3-AUD-858: Ilsabet falls; Hesper's line plays on alone"}
    }
  }
```

Listening points:
- At 0:09-0:12 (ground beats 18-24), Ilsabet's glass enters on B5 while Hesper is mid-phrase. At 0:14-0:18 he holds
  his B3 while she moves, and at 0:24-0:26 she holds her D6 while he runs. They take turns breathing and never
  arrive together.
- Solo each stem (mute the other). Stem 0 is the hum, the ostinato and the drums under Hesper. Stem 1 is the glass,
  bells, gong and pad. Both should still drive.
- kerrid_last_night 1:05-1:13: the cello's open A over G major-ninth while the tread walks on at the same pace,
  quieter each step. The tread must not sound as if it slows.

## Review log
