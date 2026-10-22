# 0011 — Stay on Godot 4.6.3 although 4.7 is stable (revisits ADR 0001)

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** all
- **Author role:** Lead (task M1-ARC-04)

## Context
ADR 0001 pinned 4.6.3 and asked us to re-check 4.7's status. The godotengine.org "Maintenance release: Godot 4.7.1" article confirms that **4.7 is stable**, and secondary sources report that 4.7.2 is out. However, under ADR 0008 our only working gate runs the Ubuntu-archive build. The archive pool currently ships only `godot 4.4.1` and `4.6.3+ds-2`, so a 4.7 pin would leave us with **no runnable engine anywhere** (GitHub Actions has never run; the sandbox can't reach GitHub releases).

## Options
1. Upgrade to 4.7.2 now: an unverifiable gate, and every test and screenshot baseline stops running.
2. Stay on 4.6.3 and upgrade when a 4.7.x build is reachable by the gate.

## Decision
Stay on **4.6.3**. Upgrade as soon as either (a) the Ubuntu archive ships `godot 4.7.x` (re-check `pool/universe/g/godot/` at the start of each Lead session) or (b) GitHub Actions runs. The upgrade is then a single ADR plus re-approved screenshot baselines.

## Consequences
- Avoid relying on 4.7-only features. Keep scenes and resources free of 4.7-format changes.
- The longer we wait, the bigger the migration. Content is still small (M1), so the cost is low now. This ADR is revisited at the M1 milestone review at the latest.
