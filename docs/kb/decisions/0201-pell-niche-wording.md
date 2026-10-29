# 0201 — Pell's battle niche is described in our own words

- **Status:** accepted
- **Date:** 2026-10-29
- **Roles affected:** story, design, ui, all writers
- **Author role:** lead

## Context
SPEC §3's roster row, `docs/kb/story/characters/pell.md` and ADR 0017 named Pell's niche with the inspiring series' own job-class word. ui-menus flagged it on 2026-10-29 (its N-27 guard 3). SPEC §2 bans the series' names and coined terms. This is a coined job name, not a generic genre word.

## Options
1. Keep the term, since it's common usage in the genre.
2. Describe the niche in plain words and ban the term in player-facing text and story docs.

## Decision
Option 2.
- **SPEC §3:** the row now reads "Learns enemy abilities by listening to them", with version note v1.5.
- **pell.md:** uses the same wording.
- **`tools/banned_terms.txt`:** gains `i:blue mage` (case-insensitive), so validate_data catches it in game/, assets_src/, docs/kb/story/, the glossary and .dlg files.
- **ADR 0017:** left as written, since ADRs are append-only. This ADR supersedes its wording, not its decision.

## Consequences
- No design change: Pell still learns enemy abilities.
- Any future text calling him by the job word fails the data gate.
