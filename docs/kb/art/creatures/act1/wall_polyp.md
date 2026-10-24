# Wall-polyp (`wall_polyp`), Ch8 the seawall

**Idea.** A variant of the [spawn-polyp](../spawn_polyp.md) rooted on the seawall's stones, the healer behind the
tide crawlers. Per m2-slice's act1_ch08 §9 it clings to the **Watchers**, the wall's carved humming faces (closed
eyes, open mouths): it sits on a broken piece of the wall whose middle block carries a fragment of one. The polyp's
shell has grown over the Watcher's brow, black roots creep out of its open stone mouth and down its chin, and the
mouth glows with the polyp's light, as if the Watcher were humming it. Burning the polyp off (it is fire-weak:
Ysolde's answer) scars the face, so killing it costs something.

**Silhouette and palette.** About 1.25 m across and 0.9 m to the tallest mouth. The same language as the spawn-polyp,
flatter and wider: the lacquer shell (`lacquer_black` to `abyss_navy`, wet clearcoat) is clamped over the top of the
Watcher's block and draped down its edges, with flat lacquer roots poured over its sides onto the two lower blocks
and down its back. Five lit tube-mouths (`spawn_wound`) lean out over the stone's front edge toward the party. The
blocks are the wall's grey laterite (`coral_stone_weathered` toward `storm_slate`, stained `laterite`, old
`mortar_white` on the joints); the carved panel is kept cleaner so the face reads. At battle distance: a lit black
anemone on a block with a face.

**Clips.** The spawn-polyp's (imported from its build module, which is not edited): `idle` (the current through the
mouths), `attack` (the lash, contact 0.46 s), `cast` (the mend, release 0.6 s), `hit`, `ko` (the mouths curl and
close). It is rooted: the stones never move. Budget ≤ 8k (one per wave); built at 7.8k.

**Build.** `assets_src/creatures/wall_polyp/build_wall_polyp.py` imports `build_spawn_polyp`, re-proportions its
shell and tubes, lifts it onto the block and drapes the shell's edge (a clamped limpet), then adds the blocks, the
Watcher panel and the roots. Its Blender job lists the spawn-polyp's folder in its `sources`.
