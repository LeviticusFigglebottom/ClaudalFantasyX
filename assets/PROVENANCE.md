# Asset Provenance

Every file under `assets/` must have exactly one row here (SPEC §2, §13.6).
`tools/validate_data.py` fails CI on any asset without a row.

Rules:
- `source` is a path under `assets_src/` or `tools/` that regenerates the asset.
- `command` is the exact command that regenerates it from a clean checkout.
- `license` is `original` for agent-authored work. Third-party licenses are allowed ONLY for
  fonts (SIL OFL) and code; any other exception needs an ADR and a flag to the human.

| path | source | command | role | date | license |
|---|---|---|---|---|---|
