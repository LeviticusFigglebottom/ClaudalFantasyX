# Act I on the real GPU: what reads unfinished or wrong (pc-gpu, ADR 0041)

The PC runs Act I on an RX 9070 XT (Windows 10, Godot 4.6.3 official, Vulkan) at the High preset, 2560×1440. It lists
only what shows on the real GPU or reads unfinished there: GI and lighting, shaders, the water, LOD pop, z-fighting, the
Undertow, and hitches over 33 ms. Lavapipe gate drift is not listed here. Each row names its owner per ADR 0041's split:

- env-art: the Prologue to Ch4 zones;
- env-art-b: the Ch5–9 zones and the arenas;
- creatures: enemies and villagers;
- creatures-b: bosses and Vowbound;
- characters: the party and named NPCs;
- battle-presentation: VFX;
- slice-polish: the slice cutscenes;
- act1-chapters: placement and flow;
- ui-menus;
- audio.

Pass A captures every manifest shot through `tools/gpu_bench/capture_preset.tscn` at High ×2.667. Pass B is the walk:

```
slice_sweep.tscn -- --walk=res://tools/gpu_bench/act1_walk.json --preset=high --res=2560x1440 --budget --stills=<dir>
```

It covers the title, New Game into the Prologue, each chapter as F8 starts it (its arrival story plays), every spawn of
every zone, one battle per arena and every Act I boss intro. Contact sheets go on `gpu/act1-qa-<n>` under
`docs/kb/qa/gpu/act1/`.

**Status:** each row is `open` until the owner fixes it, then `fixed @ <sha>` once the PC has seen the fix on the GPU.

## Findings

| # | Where (shot or walk segment) | What reads wrong on the GPU | Owner | Status | Pass |
|---|---|---|---|---|---|

## Frame-time budget per zone (ADR 0029/0037, the walk with --budget)

| Segment | gpu med / p99 ms | frame p99 / max ms | hitches > 33 ms | hidden max ms | visible max ms | Budget |
|---|---|---|---|---|---|---|
