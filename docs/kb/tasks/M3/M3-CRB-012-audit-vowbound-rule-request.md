---
id: M3-CRB-012
title: "Request (creatures-b): placeholder_audit's Vowbound rule misses the game's own Vowbound actor path (false 'primitive' rows for ilun, kahre, virel)"
role: qa
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: creatures-b
---
## Goal
`tools/placeholder_audit.py` `check_battle` says a Vowbound has a body only when `game/data/ui/battle_sandbox.json`
`stand_ins.<id>.scene` is set. The game resolves a Vowbound's model another way: its `game/data/creatures/creatures.json`
row with `"vowbound": true` and a `scene` (CreatureModels.vowbound_creature, M3-CRE-638; BattleStage.stand_in_spec).
So the inventory lists **ilun, kahre and virel as "drawn as a primitive"** although every battle shot renders their
models (creatures-b self-rendered battle_vowbound_out and battle_choreo_vowbound_rise @ 7305540a, and the big14 gate's
own out PNG shows the manta). This is what keeps M3-HER-1143 open and the Lead re-queuing Ilun.

## The patch (tested in creatures-b's tree: the three rows go, `tools/tests/test_placeholder_audit.py` OK)
```diff
diff --git a/tools/placeholder_audit.py b/tools/placeholder_audit.py
index df885dfa..49cad754 100644
--- a/tools/placeholder_audit.py
+++ b/tools/placeholder_audit.py
@@ -257,8 +257,12 @@ def check_battle(root: Path = ROOT) -> list[Item]:
             out.append(Item("game/data/battle/enemies.json#%s" % fid, "foe %s fights as a primitive stand-in (no model)" % fid, ch, owner, "high", "battle_body"))
         elif not res_to_path(model, root).exists():
             out.append(Item(model.removeprefix("res://"), "foe %s's model scene is missing" % fid, ch, owner, "high", "battle_body"))
+    creature_rows = (_json(root / "game/data/creatures/creatures.json").get("creatures", {})) or {}
     for vid in vowbound:
         scene = str((sandbox.get(vid, {}) or {}).get("scene", ""))
+        own = creature_rows.get(vid, {}) or {}
+        if scene == "" and own.get("vowbound"):  # the game's own rule: CreatureModels.vowbound_creature (M3-CRE-638)
+            scene = str(own.get("scene", ""))
         if scene == "" or not res_to_path(scene, root).exists():
             out.append(Item("game/data/battle/vowbound.json#%s" % vid, "Vowbound %s is drawn as a primitive (no actor scene)" % vid, None, OWNER_BOSS, "high", "battle_body"))
     for hero in PARTY:
```
A unit test case for it (a Vowbound with only a creatures.json row is not a placeholder) is worth adding with it.

## Review log
