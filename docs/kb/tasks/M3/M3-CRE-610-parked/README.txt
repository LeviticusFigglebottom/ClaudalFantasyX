M3-CRE-610 (FieldNpc: villagers that idle, talk, turn to the player and walk routes), parked as patches.

They depend on hero-integration's game/hero_motion (HeroLocomotion, HeroMotion, HeroIdleMicro), which is not yet on
the integration branch. Built and tested on a local merge of origin/claude/hero-integration (tip a95f5208): field_npc
10/0, hero 35/0, field_ 71/0, the npc_stage_field shot approved after viewing.

To land them, after hero-integration merges into claude/creatures:
    git am docs/kb/tasks/M3/M3-CRE-610-parked/*.patch
then delete this folder in the same push.
