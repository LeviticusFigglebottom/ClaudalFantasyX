# 0207: Act III opens per track; empty-queue tracks may supplement others

- **Status:** accepted (the human's directive, 2026-10-30 ~21:50 UTC)
- **Date:** 2026-10-30
- **Roles affected:** all
- **Author role:** lead
- **Amends:** ADR 0205 ("Act III stays paused")

## Context
Several tracks report empty queues in their own Act I and Act II lanes. The human: "if there's nothing else they can work on in their lane, permit them to either supplement other sessions or proceed with their chapter 3+ work as applicable".

## Decision
A track whose own Act I and Act II rows are all done, or are waiting only on another track, does one of the following, in this order of preference:
1. **Supplement:** take a well-scoped item from a busier track. Agree it in both live logs by request task first, so the owner can say no; the owner keeps ownership of the paths and the review. Act I items come first.
2. **Act III production** (Ch17 onward and the ending) in its own lane, built from act2-plan's Act III beat sheets and drafts (docs/kb/story/act3/). Same bar as Act I and Act II: final quality, no stand-ins, procedural and reproducible, with PROVENANCE rows, ADR 0204 world rules and banned_terms. Act III task ids come from the track's ADR-0205 range, prefixed M5-A3P.
- Act I and Act II FAST-TRACKs (human playtest notes, gate reds, QA rows) always pre-empt Act III work.
- Act III merges ride the normal fast batches.

## Consequences
No track idles. Act III starts early on the tracks with free capacity; Act I and Act II polish keep their priority.
