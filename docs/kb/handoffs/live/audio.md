# Live log: audio (branch `claude/audio`)

Environment: cloud session `session_01FtDSYm5dJHkdC3RqXsDjif`, branch `claude/audio` (from the integration branch
`claude/undertow-lead-handoff-423ixt` at 1023a25). Role: Audio. The Lead reads this file; newest state first.

## MERGE-READY @ c99e6f2b
`tools/ci_local.sh` exit 0 (HYMN_SKIP_BLENDER=1: no Blender source touched): 1499 Godot tests, 0 failed; 75/75 shots
(rmse 0); coverage battle 99.95 % / progression 96.52 % (within baseline); boot smoke clean. Integration branch merged
at f95b27cb. Items: M2-AUD-01..06 and M2-AUD-10/11, M3-AUD-01..07 (all `status: review`). Since c99e6f2b only docs.

## State (2026-10-24)
- **Done (review):** M2-AUD-10 world reverb, M2-AUD-11 saltgrass_causeway, M3-AUD-01 lamp_diver, M3-AUD-02 Tidecup match,
  M3-AUD-03 Sefir's motif, M3-AUD-04 Terraces of Ash and Corrow seawall, M3-AUD-05 the Ebbing, M3-AUD-06 Reefball /
  underwater / dive SFX, M3-AUD-07 voice-ready blips (request M3-ARC-01 filed for a DialogueBox hook).
- **Fixes this round:** hush_first_verse's buried piano and haluna_dawn's loud metallophone (measured bus levels now;
  listening_notes.md flags them); saltgrass_causeway's wrap; the boot smoke test's leaked Ogg playback (no
  first-scene music on a headless run); the shrine audio test derives its turns from the trial data.
- **Gotchas:** the grand-piano model's raw level is ~31 dB under the breath flute's, so always set piano bus gains from
  measured bus loudness (hush_theme_v2._bus_stats). corrow_seawall and saltgrass_causeway start a sixteenth before
  their downbeat (sidecar `downbeat_offset_s`).

- **In progress (worktree agents, scoped checks per the new gate rules):** M3-AUD-08 Hullgnaw + Spar-Wraith; M3-AUD-09
  Cinder Matron + Undertow's Reach (stems); M2-AUD-13 causeway beds + M3-AUD-10 Oruvel and the living funeral.
- **Filed for m2-slice:** M2-AUD-12 (B06 causeway music/beds zone rows, the B05 crossfade, B12 end card plays only
  hush_coda).

## Exact next step
Merge the three agents' branches as they report, run the audio-filtered tests, then one full Godot suite in the
background and a batch MERGE-READY line.

## Un-pushed state
None.
