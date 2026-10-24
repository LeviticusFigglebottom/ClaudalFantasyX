# 0037: Hidden frames on a cold first launch (amends ADR 0029's first-launch exception)

- **Status:** accepted (Lead, 2026-10-24)
- **Date:** 2026-10-24
- **Roles affected:** Rendering/PC GPU, Architect, QA
- **Author role:** Lead
- **Amends:** ADR 0029, "The process's first 3D frame on a first launch" exception (it does not supersede the rest of 0029)

## Context
- ADR 0029 excepts one frame from the 1 s hidden-frame limit: the renderer's first-use frame on a first launch, measured at 1.35 s on Low with the **driver's pipeline cache warm**.
- M2-ARC-08's re-measure, with **every cache cleared, including the AMD driver's VkCache**, found worst hidden boot frames of 1.6 s (Low) and 2.9 s (High).
- M2-RND-18 (gpu/m2-rnd-18-cold-boot-frame) split the costs that shared that frame: the renderer's first use, a first-run scene load, and the first material draw. Worst hidden frames are now 1.40–1.43 s on High and 1.41–1.68 s on Low, over 7 cold runs.
- What remains is one material's first draw, Haluna's palm frond: 10 surface, 8 specialisation and 10 mesh pipelines, 1.36–1.68 s. Godot 4.6.3 compiles one draw's pipeline set synchronously, so the project can't split it further.
- Zone entries stay within ADR 0029 on a cold launch (Haluna's first entry is 449 ms / 2.0 s on High and 697 ms / 2.3 s on Low).

## Options
1. Keep 1.35 s, and drop or simplify the palm frond material until it fits.
2. Raise the first-launch exception to cover a truly cold driver cache, bounded by the measurement.
3. Ship pre-built driver pipeline caches (not possible: they're driver- and GPU-specific).

## Decision
**Option 2.** On a **cold first launch only** (no project pipeline marker), and only **behind the boot card with the first-run cue showing**, a hidden frame may take up to **1.7 s** on the reference GPU (RX 9070 XT).
- Every other hidden frame still answers to 1 s, and every visible frame to 50 ms.
- Second and later launches have no exception.
- The first-run cue ("Preparing the graphics for first use. This happens only once.", M2-ARC-08) tells the player why the card may pause.

## Consequences
- **Gates:** the PC's cold-launch sweep checks ≤ 1.7 s for first-run hidden frames, and ≤ 1 s otherwise.
- **Min-spec:** M3-RND-02, the min-spec proxy, re-measures this. If min-spec exceeds about 3 s for one frame, revisit option 1 for the worst materials, or a lighter first-run material path.
- **The engine port:** the 4.7.2 port (ADR 0032) re-measures this. If 4.7 compiles a draw's pipelines asynchronously, this exception tightens back.
- **Number note:** two different ADRs are numbered 0033 on different branches (data-driven chapter flow and UI flair), and data-driven chapter flow also appears as 0035. The Lead resolves the numbering at merge; this ADR takes 0037 to stay clear of 0033–0036.
