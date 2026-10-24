---
id: M3-C08-01
title: Ch8 "The Seawall" beat sheet
role: narrative
status: review
owner_session: "m2-slice subagent C (Ch8, Ch9 beats)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Write the beat sheet for Ch8 "The Seawall" (ch08/corrow, ch08/coilspire) in `docs/kb/story/beats/act1_ch08.md`, in the format of `docs/kb/story/beats/vertical_slice.md`: the chapter in one paragraph, the running order with beat ids, each beat in detail, flags, the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and requests to other roles (env-art kits, audio cues, creatures).

It covers Coilspire's flue trial and Virel, the Fisher Stair evacuation set-piece (ADR 0017: no weapon against the Undertow), Kerrid at the stair foot (ADR 0020/0022), the Undertow's Reach boss with its scripted escape, and Rhen's freeze. It follows `act_outline.md`, the bible, the voice guide and the character files, and ADRs 0015, 0016, 0017, 0020 and 0022. It's sincere (pillar 1), with no echoes of other IP and nothing on `tools/banned_terms.txt`.

## Acceptance criteria
- [x] `docs/kb/story/beats/act1_ch08.md` exists, with every outline beat for the chapter placed, timed and tagged C (cutscene), E (in-engine) or P (play).
- [x] Flags are named `ch08_*`, with who sets each and who reads it, including links to other chapters.
- [x] Each request to another role is listed with enough detail to file as a task.
- [x] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- 2026-10-24 (m2-slice subagent C): written: [act1_ch08.md](../../story/beats/act1_ch08.md). 18 beats (B01–B18), 58.5 min on the critical path (72% playable), and a set-piece of 30 min. It is ready for the cinematics review.
- **The set-piece design (§5a):** three chained scripted battles plus the boss, with a carried stair meter (`ch08_stair_groups_up`, a numeric flag). It needs one new combat primitive, the scripted timeline entry, used three ways: the Climb (a ward with no HP that takes turns; spawn push it back), the Surge (an untargetable spawner) and Pell (a guest whose Storm-Call removes one mover). It also needs an objective victory, a `scripted_escape` outcome, phase `untargetable`/`damage_immune`, Toma's slot locked with Attack replaced by Stand Firm, and Kerrid unavailable. There's no real-time system. The full list is §9 Combat.
- **Creature ids:** these are the creatures track's (`tide_crawler`, `squall_wing`, `wall_polyp`, `undertows_reach`). The first draft's "Tidegrip"/"Spraywing" are renamed, and its "Lampshell" and *Batter* are cut. The foes-on-screen table is in §9 Creatures (at most 3, 3, 4, and 3 at the boss).
- **Story calls decided here** (they are within the ADRs; none needs a new ADR):
  - Kerrid leaves at landfall ("Later.") because the old watch knows his face by day.
  - Asha doesn't sing at Coilspire, so her verse is never the storm's cause.
  - Nobody tells the 1001 captain's story in Ch8.
  - Virel is called to light the wall (Flare Line clears `storm_dark`), echoing what Dace saw in 1001. The Reach's last phase can't be damaged.
  - The player never causes a death by playing badly.
  - Asha hums the lullaby to a child on the stair (paid off by Ch17's ledger).
  - Pell is silent in Ch8.
  - Kerrid's collar grab is with the wrapped left hand (E3 consistency), and he never shares a frame with the figure.
  - New NPCs: Ivo Brannick (Toma's shield-mate, who was at the 1003 burning), Old Marra (the fishwife), Hobb (the watch captain now) and Fenn (the beacon-keeper, in the side scene "The Keeping Flame").
  - A new Corrow custom: kites for a Cantor. New items: Wenna's sailmaker's needle (an optional Coilspire reward, paid off in Ch20).
- **For the Lead, glossary rows to append when convenient:** Ivo Brannick, Old Marra, Hobb, Fenn, the Corrow kite custom, Storm-Call.
- **Checks:** `validate_data` is clean (it includes the banned-terms grep over docs/kb/story), and `taskboard --check` passes. This is docs only, so there was no Godot run.

## Review log
