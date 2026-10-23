# MPFB2 / MakeHuman CC0 data (vendored subset)

Source: https://github.com/makehumancommunity/mpfb2 at commit `b1a2dc98776da9d1eea751b159d42cf61778fe2e`.
Decision record: [ADR 0021](../../../docs/kb/decisions/0021-mpfb2-topology-donor.md).

- `data/` holds **asset data only**, which MPFB2 releases under **CC0 1.0** (`LICENSE.md` section C, `LICENSE.ASSETS.md`, both verbatim here).
- MPFB2's program code is GPLv3. **None of it is in this repository**, and nothing here imports it. Our readers are in `assets_src/characters/base_body/mpfb_data.py`.
- Reproduce or verify the set with `python3 tools/fetch_mpfb2.py` (fetch) or `python3 tools/fetch_mpfb2.py --check` (offline). `MANIFEST.json` lists every file with the sha256 of the upstream file and of the stored file. Files over 5 MB are stored gzip-compressed (`.gz` appended).
- Do not edit these files by hand. Change the list in `tools/fetch_mpfb2.py` and re-run it.
