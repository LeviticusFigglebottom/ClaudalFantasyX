---
id: M3-AUD-866
title: "FAST-TRACK: a sound per status effect (apply), the cure, the fade, and the revive"
role: audio
status: review
owner_session: "claude/audio (2026-11-03)"
reviewer: qa
depends_on: [M2-AUD-04]
milestone: M3
request-from: lead
---
## Goal
The human's playtest FAST-TRACK 3 says status effects must be obvious on the character. FAST-TRACK 5 adds a revive
item. The Lead's brief lists both: "the sounds for combat-systems' new revive item and the status-effect apply and
cure cues". Audio built them ahead of the other tracks' requests, and they work with what is already on integration.

## Done
- **`assets_src/sfx/status_sfx.py`** writes 24 mono cues to `assets/audio/sfx/battle/`, plain git (not an LFS path).
  Rows are in `game/data/audio/sfx_status.json`. The cues:
  - one `status_<id>` for each of statuses.json's 21 statuses;
  - `status_cure`, `status_fade` and `revive`.
  - **The grammar:**
    - harmful statuses sink (falling, dulled), and each has its own material;
    - beneficial statuses rise (bright glass and metal);
    - the four breaks share one crack, then their own material falls;
    - the cure lifts to a clear fifth;
    - the fade is a quiet falling glass;
    - the revive goes from a heartbeat, through a swell, to an open fifth.
  - **Levels:** −20 LUFS momentary max (the fade −21, the revive −18), inside targets.py's `sfx/battle/*.ogg` rule.
    `--determinism` is identical for all 24.
  - **By analysis:** every harmful cue's centroid trends down except berserk's growl and confuse's wobble. Each
    beneficial cue trends up or holds. The closest pair by band energy (magic_break and reflect, distance 0.13) still
    differs in contour.
- **`battle_sfx.json` `statuses`:** `apply` {status → sfx}, `cure`, `fade`, `revive`, and `generic` (status_apply).
- **`BattleAudio.play_statuses`**, on the engine's `action_resolved`:
  - each hit's `statuses_added` plays its own cue;
  - the generic `status_apply` that the view's `status` effect started in the same action is stopped, or dropped if
    it arrives second;
  - an item hit's `statuses_removed` plays the cure for a harmful status (statuses.json `category`) and the fade for
    a beneficial one;
  - a `revived` hit plays the revive;
  - a miss plays nothing;
  - a status with no row keeps the generic.

## For other tracks
- **combat-systems (the revive item, FAST-TRACK 5):** nothing to wire. Any item whose hit carries `revived: true`
  (ItemBattleAction.resolve_on already sets it) plays `revive`, whatever the item is named. Revival after a won
  fight, at 1 HP, isn't in a battle, so it has no cue yet; ask if the result screen should play one. A new status
  needs a row in battle_sfx.json `statuses.apply` (test_status_audio fails without one), so request it from audio.
- **battle-presentation (the on-body status VFX):** nothing to wire for sound. If you add one effect per status
  (e.g. `status_on_<id>`), map it in battle_sfx.json `vfx` to the same `status_<id>` row, and the dedupe keeps it
  to one sound. The natural expiry of a status (a turn count running out) has no engine signal yet. When one lands,
  `status_fade` and `status_cure` are its cues.

## Tests
`tests/unit/test_status_audio.gd` (6):
- every status has its own existing cue, and no two share one;
- an added status plays its own cue and silences the generic;
- two targets each play theirs, and a miss plays none;
- the generic is dropped when it comes second;
- an unknown status keeps the generic;
- cure, fade and revive play in hit order.

The loudness suite measures the 24 new files.

## Review log
