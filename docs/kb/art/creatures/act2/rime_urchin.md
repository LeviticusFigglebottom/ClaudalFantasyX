# Rime urchin (`rime_urchin`), Ch11

**Where:** Sunken Vey, where the deep's cold wells up. **Kind:** reef beast. **Role:** an ice counter: striking it
in melee chills the striker (pick magic or reach).

**The idea:** a long-spined sea urchin from the cold well-water, its spines furred with rime. It moves slowly on
its tube feet, and its spines turn toward whatever touches it. The one exaggeration: **the rime**, which grows on
its spines even underwater.

**Silhouette:** a 0.9 m sphere bristling with spines twice its radius, the spines longest on top; it sits on a
plinth of ice it has made.

**Palette:** test `abyss_navy`; spines `deep_teal_shadow` going `salt_glass` and `foam_white` where the rime is;
tube feet `bone`; weak point (the mouth underneath, glimpsed when it rolls) `spawn_wound`.

**Clips:** `idle` (the spines sway in rows like a field in wind); `attack` (it rolls and the spines stab: contact
0.5 s of 1.1 s); `cast` (the spines all point at the target and frost blooms along them); `hit` (the spines clench;
peak near 0.1 s); `ko` (the spines droop and it settles, the rime melting). Budget ≤ 9k triangles (the spines are
the cost). Rig: body, spine-field bones (eight sectors).
