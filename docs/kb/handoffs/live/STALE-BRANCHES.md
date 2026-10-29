# Stale branches safe to delete (checked 2026-10-28 by the Lead)

Cloud sessions can't delete remote branches (the git proxy returns 403). Delete these in GitHub's branches UI, or from the PC with `git push origin --delete <name>`.

**Keep:**
- every `claude/<track>` branch and the integration branch `claude/undertow-lead-handoff-ze8rrn`;
- `claude/undertow-lead-handoff-423ixt` (frozen, referenced in the docs);
- `gpu/gate-big*-shots`, `gpu/act1-qa-*` and `gpu/pc-gpu-paused-1027` (QA and gate history);
- `lead/gate-big15`, `lead/gate-big16`, `lead/gate-ft-beach` and `lead/gate-big13-shots` until big16 is merged;
- `claude/gate-runner-a` and `claude/gate-runner-b` (unreviewed).

## Fully merged into the integration branch
- `claude/first-playable`
- `claude/menus`
- `claude/new-session-mj8c3c`
- `gpu/adr-0029-prewarm-followups`
- `gpu/arc-03-remeasure`
- `gpu/env-03-vegetation`
- `gpu/env-03-vegetation-v2`
- `gpu/fp-10-keylight-check`
- `gpu/gate-big8-rnd910`
- `gpu/hero-materials-resident`

## Superseded staging
- `lead/gate-big14` (contained in gpu/gate-big14-shots and big15/16)
- `lead/gate-lfs-probe` (the ADR 0039 probe)

## Retired render-request outputs (the PC/cloud render queue, replaced by self-rendering on 10-28)
- `gpu/render-act1-chapters-180510e`
- `gpu/render-act1-chapters-5112837`
- `gpu/render-act1-chapters-77a6a77`
- `gpu/render-act1-chapters-8daa0c6`
- `gpu/render-act1-chapters-b30c2cf`
- `gpu/render-act1-chapters-c0ee523`
- `gpu/render-act1-chapters-eeaf91b`
- `gpu/render-battle-presentation-25dcea2`
- `gpu/render-battle-presentation-60b6267`
- `gpu/render-battle-presentation-680cd88`
- `gpu/render-battle-presentation-c1d1e3e`
- `gpu/render-battle-presentation-db0819b`
- `gpu/render-characters-038d565`
- `gpu/render-characters-7f56d64`
- `gpu/render-characters-dc93a5d`
- `gpu/render-creatures-10f21a1`
- `gpu/render-creatures-2112578`
- `gpu/render-creatures-44080e1`
- `gpu/render-creatures-b5e05d2`
- `gpu/render-creatures-b99be56`
- `gpu/render-creatures-fce2e82`
- `gpu/render-env-art-179069d`
- `gpu/render-env-art-1a42247`
- `gpu/render-env-art-22a5de1`
- `gpu/render-env-art-43492e8`
- `gpu/render-env-art-599b241`
- `gpu/render-env-art-71f19fb`
- `gpu/render-env-art-854e6a9`
- `gpu/render-env-art-8770a06`
- `gpu/render-env-art-94fe8f7`
- `gpu/render-env-art-95be611`
- `gpu/render-env-art-a0d2549`
- `gpu/render-env-art-ba16d48`
- `gpu/render-env-art-fd630bb`
- `gpu/render-hero-integration-1b84b89`
- `gpu/render-hero-integration-b2453cf`
- `gpu/render-hero-integration-d443039`
- `gpu/render-m2-slice-17b0601`
- `gpu/render-m2-slice-4ce8a48`
- `gpu/render-m2-slice-8b25b3b`
- `gpu/render-m2-slice-fdec3cc`
- `gpu/render-ui-121362b`
- `gpu/render-ui-17325e0`
- `gpu/render-ui-26755f9`
- `gpu/render-ui-5317c0e`
- `gpu/render-ui-6454c06`
- `gpu/render-ui-99623a0`
- `gpu/render-ui-a195cd3`
- `lead/gate-render-battle-presentation-5a5b4fe`
- `lead/gate-render-battle-presentation-60cbb21`
- `lead/gate-render-battle-presentation-ed3a458`
- `lead/gate-render-characters-ee3bd33`
- `lead/gate-render-creatures-3b0e44b`
- `lead/gate-render-env-art-191e5e8`
- `lead/gate-render-env-art-1e14af8`
- `lead/gate-render-env-art-60eee2f`
- `lead/gate-render-env-art-8be2adc`
- `lead/gate-render-env-art-ab58f89`
- `lead/gate-render-env-art-c770380`
- `lead/gate-render-env-art-c990e2c`
- `lead/gate-render-env-art-f39cdde`
- `lead/gate-render-env-art-fca9987`
- `lead/gate-render-hero-integration-1c9bf8b`
- `lead/gate-render-hero-integration-7a8bff7`
- `lead/gate-render-m2-slice-ead04ba`
- `lead/gate-render-ui-34d6e51`
- `lead/gate-render-ui-da7891c`
