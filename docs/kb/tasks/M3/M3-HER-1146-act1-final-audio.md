---
id: M3-HER-1146
title: "ADR 0041 (Act I at final quality): audio's items in the placeholder inventory (12: 0 high, 12 medium, 0 low)"
role: audio
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
ADR 0041: everything a player meets from the title to the end of Ch9 reaches final quality. integration-qa's audit
(`python3 tools/placeholder_audit.py`, docs/kb/qa/act1_final_inventory.md) lists what is still placeholder.
**audio** owns sound. This task carries those rows; the inventory's "audio" section is the live list.

## Acceptance criteria
- [ ] Every row of the inventory's "audio" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [ ] The audit lists nothing for audio: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "audio" line.

## The rows as first audited (2026-10-28)
- **medium**, Ch1: `assets/audio/music/oruvel_raft.ogg`: @music oruvel_raft is silent (no assets/audio/music/oruvel_raft.ogg); music.json has a `oruvel_raft` cue row (assets/audio/music/oruvel.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch1: `assets/audio/music/oruvel_underway.ogg`: @music oruvel_underway is silent (no assets/audio/music/oruvel_underway.ogg); music.json has a `oruvel_underway` cue row (assets/audio/music/lamp_diver.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch1: `assets/audio/music/undertow_rising.ogg`: @music undertow_rising is silent (no assets/audio/music/undertow_rising.ogg); music.json has a `undertow_rising` cue row (), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch4: `assets/audio/music/brightwater_crossing.ogg`: @music brightwater_crossing is silent (no assets/audio/music/brightwater_crossing.ogg); music.json has a `brightwater_crossing` cue row (assets/audio/music/brightwater_ferry.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch4: `assets/audio/music/haluna_wake.ogg`: @music haluna_wake is silent (no assets/audio/music/haluna_wake.ogg); music.json has a `haluna_wake` cue row (assets/audio/music/pilgrims_wake.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch5: `assets/audio/music/ashcrown_trial.ogg`: @music ashcrown_trial is silent (no assets/audio/music/ashcrown_trial.ogg); music.json has a `ashcrown_trial` cue row (assets/audio/music/ashcrown.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch5: `assets/audio/music/pemakar_terraces.ogg`: @music pemakar_terraces is silent (no assets/audio/music/pemakar_terraces.ogg); music.json has a `pemakar_terraces` cue row (assets/audio/music/terraces_of_ash.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch7: `assets/audio/music/tamsule_port.ogg`: @music tamsule_port is silent (no assets/audio/music/tamsule_port.ogg); music.json has a `tamsule_port` cue row (assets/audio/music/tamsule.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch8: `assets/audio/music/coilspire_flues.ogg`: @music coilspire_flues plays the stand-in temple_trial; music.json has a `coilspire_flues` cue row (assets/audio/music/coilspire.ogg), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch8: `assets/audio/music/corrow_day.ogg`: @music corrow_day plays the stand-in corrow_seawall
- **medium**, Ch8: `assets/audio/music/seawall_hold.ogg`: @music seawall_hold is silent (no assets/audio/music/seawall_hold.ogg); music.json has a `seawall_hold` cue row (), but CutsceneSequencer only reads music_dir/<id>.ogg and music_stand_ins: a seam between audio's table and the sequencer
- **medium**, Ch8: `assets/audio/music/undertow_reach.ogg`: @music undertow_reach plays the stand-in undertows_reach_p1

## Review log
