---
id: M1-NIT-02
title: Small fixes from review-sweep-L
role: qa
status: todo
owner_session: ""
depends_on: [M1-CMB-03, M1-ENV-05, M1-RND-16]
milestone: M1
request-from: "lead"
---
## Goal
From the review-sweep-L entries (file:line references there).

## Acceptance criteria
- [ ] CMB-03: ADR 0023's Retry claim matches the code (Retry re-rolls at seed+1, or keeps the opening, whichever is intended; amend the ADR append-only); one shared enemy-id rule for Read and victory credit (battle_bestiary.gd ~:74-75)
- [ ] CHR-06: the thread-count test covers every Blender job and build script; PROVENANCE Asha rows mention --threads 4
- [ ] ENV-05: a missing water publisher is an error in debug or uses a sane default, not a stale level (weathering_tide.gd ~:49-85); note the one-frame lag
- [ ] RND-16: a push does not replace the shared base settings of an earlier override (graphics_settings.gd ~:401); a reparent does not pop the override; settings.cfg is cached
- [ ] UI-09: a second skip does not restart the fade; ENV-06: plan the playable zone's move off _tests/ before content lock (note in architecture.md)

## Review log
