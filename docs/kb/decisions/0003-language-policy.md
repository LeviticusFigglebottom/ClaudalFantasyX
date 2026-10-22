# 0003 — Language policy: typed GDScript first

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** all engineering roles
- **Author role:** Lead

## Context
SPEC §4.1 says GDScript is primary and statically typed, with C# or GDExtension only for proven hot paths.

## Decision
- All runtime code is **typed GDScript**: `class_name`, typed vars, typed arrays, and return types. Untyped `Variant` is allowed only at JSON and Dictionary boundaries, and it must be cast immediately.
- Pure logic (battle engine, Lattice, save migrations) is plain `RefCounted` classes that run headless and can be tested without scenes.
- A C# or GDExtension module needs its own ADR with profiler evidence (a captured frame or headless benchmark showing GDScript can't meet budget). The candidates we expect are the balancing simulator's inner loop and maybe Lattice pathfinding on the Expert board. No GDExtension is planned for M1.
- Python 3.13 is the tooling language (validators, pipelines, audio DSP, balancing reports), and lives under `tools/`.
- Linting: gdtoolkit 4.5 (`gdlint`, `gdformat -l 120`), enforced in CI.

## Consequences
Logic stays portable to a native module later if profiling demands it. Tool code must not become runtime code: Godot never imports Python.
