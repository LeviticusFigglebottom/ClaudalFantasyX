---
id: M3-CRE-634
title: "Request to ui-menus: the bestiary portrait test should cover the creatures enemies use (the Act II creatures have no enemy yet)"
role: ui
status: review
owner_session: "claude/ui (ui-menus)"
reviewer: character
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
`tests/unit/test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row` requires a baked
bestiary portrait (tools/portraits manifest) for **every** creatures.json row. The creatures track built the Act II
roster (M3-CRE-620..628: 15 creatures) ahead of its encounters. None has an enemies.json row, so none can appear in
the bestiary, but the test fails for all 15 on claude/creatures after the big11 merge.

## Proposal (verified: the test is 4/0 with it on claude/creatures; your file, so not committed by creatures)
```diff
-	for id: Variant in rows:
-		assert_true(ids.has(str(id)), "creatures.json row %s has a portrait in the manifest" % id)
+	# The bestiary lists enemies: every creature an enemies.json `model` uses has a portrait. A creature no enemy uses
+	# yet (an Act II design built ahead of its encounters) gets one when its encounter lands.
+	var used := CreatureModels.models().values()
+	for id: Variant in rows:
+		if str((rows[id] as Dictionary).get("scene", "")) in used:
+			assert_true(
+				ids.has(str(id)), "creatures.json row %s (an enemy's model) has a portrait in the manifest" % id
+			)
```
When an Act II encounter adds its enemy rows, add those creatures to tools/portraits/portraits.json and file a PC
RENDER-REQUEST for the bake (rendering is the PC's). The dark ones carry `portrait.rim_energy` 2.8 /
`kick_energy` 1.8 in creatures.json (M3-CRE-618) if the bake wants to read them.

## Acceptance criteria
- [x] The test covers the creatures enemies use (or the manifest gains every Act II creature with a PC bake). Done the second way (5f9c71fd): every Act II creature and boss in the manifest is baked (`tools/portraits/render.sh`, self-rendered under TRACK-RULES 2026-10-28) with PROVENANCE rows, so the test stays strict. Every creature keeps a bestiary picture ready for the day its enemy row lands.
- [ ] claude/creatures is green on `--filter=creature` after merging it
- 2026-10-27, creatures: **one more case for the same fix.** creatures.json now has a Vowbound row (`ilun`, `"vowbound": true`, M3-CRE-638). The bestiary only logs foes, so it has no manifest entry, and the test now also reports "creatures.json row ilun has a portrait in the manifest". The ask is unchanged: limit the check to enemies.json foes, which also skips Vowbound rows (or skip rows with `vowbound: true`).
- 2026-10-27, creatures: superseded for Ilun. The Lead asked for his manifest row, so `ilun` is now in tools/portraits/portraits.json and the test no longer flags him. What's left in test_creature_portraits is only the 17 unbaked PNGs, and their bake is requested in the creatures live log.

## Review log
