---
id: M2-RND-11
title: Rendering fixes from review-sweep-R (first-run tests, warm compute pipelines at exit, Undertow literals, Ultra reflection)
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M1-RND-27, M1-RND-29, M2-RND-05]
milestone: M2
request-from: "lead"
---
## Goal
These are the should-fixes review-sweep-R left on M1-RND-27, M1-RND-29 and M2-RND-05. None of them blocks. Items 1–3
are headless (cloud). Items 4 and 5 need the PC GPU.

## Acceptance criteria
- [ ] **First-run tests (RND-29).** The only first-run test today is the headless guard plus an interrupted run.
      Nothing checks what a first run does. Add tests to `test_shader_prewarm.gd` with a temporary registry whose
      `first_run_marker` is under the test's tmp dir. They should show that a `resident_only` + `first_run` stage
      lists the non-resident entries and harvests `first_run_scenes`; that `_finish` writes the marker with
      `first_run_key(preset)`; and that `needs_first_run` is false on a matching key and true on another preset's
      key. Factor out the headless early-return so the key logic can be tested headless.
- [ ] **Warm compute pipelines at exit (RND-27).** `UndertowBodyEffect._warm` is a static Dictionary of RD shader
      and pipeline RIDs, and nothing frees it. That's the same kind of exit-time leftover that M1-RND-29's gate fix
      removed for resident resources. Free them on exit (an owner node under the tree root, as
      `ShaderPrewarm.ResidentHolder` does, or an explicit release the router calls), and check that a headless run
      has no RID leak warnings at exit.
- [ ] **Literals in `undertow_events.gd` (RND-05; CLAUDE.md §3, no magic numbers).** Move these to named constants or
      to `undertow.json`: the 0.6 bolt-site height bias and the `2.39996323` golden angle (`bolt_sites`), the
      `threshold * 0.25` bolt hide level, the `0.5 +` sea-reach base in `bolt_ends`, and the `2147483647.0` seed
      scale (`_strike`).
- [ ] **RND-05 findings 2 and 3, unfiled (PC).** Ultra, the top tier, reflects the storm's impostor while Medium and
      High reflect the body's own pixels, so Ultra's sea looks worse than High's. Either give Ultra a reflection
      source, or record in undertow.md why it can't have one, and get Art's acceptance through M2-ART-03.
      The sky dome's missing overcast toward the storm: record it in undertow.md's open items, with this task's id.
- [ ] **A lead for M2-ENV-05 (PC, measure only).** In the RND-29 table, Haluna's entry takes 1.26–1.33 s on a
      **first** launch, after the first-run harvest, and 2.4–3.25 s on the second (Low is over 3 s). The harvest
      seems to leave Haluna's resources loaded. Measure whether harvesting Haluna's SceneState on every boot (or
      holding what it loads) brings the second launch under 3 s, and give the numbers to M2-ENV-05.

## Notes
- Source: review-sweep-R (2026-10-24).

## Review log
