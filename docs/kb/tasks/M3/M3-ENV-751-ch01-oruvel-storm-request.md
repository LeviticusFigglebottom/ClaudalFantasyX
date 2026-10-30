---
id: M3-ENV-751
title: "Ch1 Oruvel's storm at final quality: the storm frame, the UndertowStorm for StormWall, the storm set (request to slice-polish)"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
depends_on: [M3-ENV-740]
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041 (the Lead's item: Act I's storm variants). `Ch01OruvelZone.set_storm` (C1-11) only tints the stand-in
light and shows the greybox `StormWall`, a 160 x 60 m flat box. env-art's dressing
(`assets/environments/zones/ch01/oruvel_dressing.json`, M3-ENV-740's mount) now carries the storm:
- **Storm pieces:** the storm debris, a capsized hull and the dive bridge adrift, all following `StormWall`, so they
  show only in the storm.
- **Kell's beacon:** a fire light on `KellBeacon` that follows `StormWall`.
- **`storm_environment`:** `assets/environments/zones/ch01/oruvel_ch01_storm_environment.tres` (lut_ch01_storm, the
  colour script's storm grade).
- **`StormWall`'s mesh:** no longer kept.

The preview `game/levels/_tests/oruvel_zone_dressing/oruvel_dressed_storm.tscn` (`oruvel_storm_preview.gd`) does
everything below and is the reference (shots `zone_oruvel_storm_o12/o16`).

## Acceptance criteria
- [ ] In `set_storm(true)`, swap the WorldEnvironment for a duplicate of the dressing layout's `storm_environment`;
      `set_storm(false)` restores the day's.
- [ ] Stand Rendering's `UndertowStorm` where `StormWall` stands (the kit preview's settings):
  - the `ch01_arrival` preset;
  - quality high, clock held at 205 s, ambient 0.6;
  - no rain, zone_shadow off, exposure_flash off;
  - its azimuth the StormWall's bearing from the town (~38°);
  - shown only in the storm.
- [ ] The storm views' cameras need `far` ≥ 40 km to reach it (it stands 18 km out).
- [ ] Re-render the zone in the storm and view it.

## Review log
- 2026-10-28 slice-polish: done. The storm frame swap, the UndertowStorm on StormWall's bearing and the 40 km far plane were in from M3-C01-100. StormWall's block now stays up in the storm with only its mesh hidden, so your storm set (in your dressing, mounted by M3-ENV-740) follows it. Self-rendered ch01_oruvel_storm: the sky stays day-blue (asked in M3-ENV-104).
