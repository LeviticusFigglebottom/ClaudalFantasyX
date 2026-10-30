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

## Salt-glass, not ice (the Lead, 2026-10-30; ADR 0015)
Nothing is frozen in Lowlight (ADR 0015: the cold is the deep's), so, as ADR 0204 §2 did for the Ch12 regulars, the
urchin has no ice. Its "rime" is a **salt crust** on the spines (`salt_glass` going to a pale salt, `salt_glass`
toward `bone`, faceted, with no `foam_white` frost). It sits on a **mound of salt-glass** it has grown, glossy and
clear-green with a bloom of salt on top: material slot `glass`, which replaces `ice`. In the KO it slumps onto the
mound; in the cast the salt crusts along the turned spines (the effect, M4-A2P-060). The lines above that say rime,
frost or ice are superseded. The ids (`rime_urchin`, `rime_spine`) and the skill's ice element are the encounter
data's (design); the name stays.
