# 0174: Act I's small new SFX ship in plain git while LFS uploads are blocked; the budget rises to 73 MiB

- **Status:** accepted (audio, on the Lead's 2026-10-30 direction)
- **Date:** 2026-10-30
- **Roles affected:** audio, lead (repository size)
- **Author role:** audio
- **Amends:** [0173](0173-act1-final-audio-in-lfs.md) for small files; **raises** the cap of
  [0171](0171-audio-budget-72-mib-act1-complete.md).

## Context
M3-AUD-864 adds 58 small Act I files: Kerrid's and Liss's Swell finishers and 28 cutscene foley kinds in two
variants. Together they are 0.69 MiB, and none is near 5 MB. ADR 0173 sent new Act I audio to Git LFS. On 2026-10-29
the cloud environments' network policy began refusing `lfs.github.com`, so no LFS object can be uploaded, and
GitHub's pre-receive hook (GH008) refuses any push that names a missing object. The Lead directed that files under
5 MB leave the LFS paths: CLAUDE.md §8 and ADR 0039 require LFS only for binaries over 5 MB. Plain git had 0.17 MiB
of ADR 0171's 72 MiB left.

## Decision
- New Act I SFX under 5 MB ship as plain blobs at their normal paths (`assets/audio/sfx/...`) until LFS uploads work
  again.
- `tools/audio/targets.py` `TOTAL_BUDGET` is 73 MiB (+1 MiB, enough for these 58 files and a little Act I polish).
- Large new binaries still go to LFS (`assets/lfs/**`, ADR 0039). Nothing is migrated in either direction, and
  `.gitattributes` is untouched.

## Consequences
- The plain-git history grows by about 0.7 MiB.
- The next raise still waits on the storage decision that 0171 asked for.
