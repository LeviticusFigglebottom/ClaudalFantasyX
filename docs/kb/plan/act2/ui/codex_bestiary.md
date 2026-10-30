---
draft: pre-gate
---
# Act II codex and bestiary

The ui-menus track holds the codex's narrative seat (M3-NAR-01). The rules from Act I hold:
- each entry is 2–4 sentences, sincere, in the voice guide's register;
- nothing past its unlock beat;
- no Act III term before Act III;
- `codex.json` rows with a flag unlock; read flags `codex_<id>_read` (flags.tres).

**Exists today (M3-UI-207):** world (Kirru, Ullari) and 14 places, from Ossa Fen to the Drowned Choir. Narrative review is
pending.

## Codex: new entries

### World (6)
| Id | Unlock (flag) | Says | Keys |
|---|---|---|---|
| `farewell_tide` | `ch10_farewell_tide_seen` | The Kirru's rite for their dead: the song, the turned backs, the motes going up. | `CODEX_FAREWELL_TIDE_TITLE`, `_BODY` |
| `name_shells` | `ch10_reached_reedhollow` | What a Kirru name-shell is, and what a blank one means (the bible's answer: a name, not a keepsake; N-27). | `CODEX_NAME_SHELLS_*` |
| `keth` | `ch12_reached_quellan` | Ullari knot-writing: cords that keep what was said. | `CODEX_KETH_*` |
| `conclave` | `ch13_started` | The five who sit above the Order, as Ansedra speaks of them (no "revenant", ADR 0016). | `CODEX_CONCLAVE_*` |
| `heresy` | `ch14_declared_heretics` | What the Order means by heretic, and what follows (shrines, shops). | `CODEX_HERESY_*` |
| `the_hush` | `ch16_choir_memory_seen` | What the Hush really does, in the plainest words the beat allows. | `CODEX_THE_HUSH_*` |

### People (8)
| Id | Unlock | Keys |
|---|---|---|
| `tobin` | `ch13_met_tobin` | `CODEX_TOBIN_*` (gains a second body at `ch14_tobin_died`: `CODEX_TOBIN_BODY_AFTER`) |
| `merel` | `ch13_met_merel` | `CODEX_MEREL_*` (`_BODY_AFTER` at `ch14_merel_taken`) |
| `malcor_venn` | `ch14_started` | `CODEX_MALCOR_VENN_*` |
| `liss_father` | `ch15_reached_hollowmere` | `CODEX_<NAME>_*` (Narrative names him in the beat sheet) |
| `kirru_eldest` | `ch10_reached_reedhollow` | `CODEX_KIRRU_ELDEST_*` |
| `corran` | `ch13_bound_ethren` | `CODEX_CORRAN_*` (Ysolde's account; the veil-fall is Act III's) |
| `wenna` | `ch11_liss_found_marks` | `CODEX_WENNA_*` (only what her marks say) |
| `ama` | `ch12_ama_keth_read` | `CODEX_AMA_*` |

**Changed by beat (in place, a second body key):**
- Kerrid at `ch15_kerrid_revealed` (see kerrid.md);
- Sefir at `ch16_sefir_tempts` (`CODEX_SEFIR_BODY_CH16`);
- Pell at `ch11_nhoa_bound` (`CODEX_PELL_BODY_CH11`: Ressa).

### Vowbound (4, a new category or under World; Narrative decides)
| Id | Unlock | Keys |
|---|---|---|
| `nhoa` | `ch11_nhoa_bound` | `CODEX_NHOA_*` |
| `hesk` | `ch12_hesk_bound` | `CODEX_HESK_*` |
| `ethren` | `ch13_ethren_bound` | `CODEX_ETHREN_*` |
| `kesh` | `ch16_kesh_bound` | `CODEX_KESH_*` |

If they get their own category: `CODEX_CAT_VOWBOUND`, `CODEX_CAT_VOWBOUND_DESC`; Act I's Ilun, Kahre and Virel move in
(three entries, `CODEX_ILUN_*` etc.). That is my recommendation: the summons are the act's spine.

### Records (5, open in the document reader)
`archive_ledger`, `cantor_roll`, `corran_line` (Ch13), `wenna_marks_2` (Ch11), `ama_keth` (Ch12): each
`CODEX_<ID>_TITLE` plus its `RECORD_<ID>_<NN>` sentences (screens.md §1). Found by `CodexRecordSpot` (M3-NAR-01).

**Codex loc keys:** about 25 titles + 25 bodies + 4 after-bodies + 2 category keys ≈ **56**, plus the record sentences.

## Bestiary

- **Regulars (10):** names and lore exist (`ENEMY_*`, `LORE_*` for tannin_archer, root_crab, fen_leech, gallery_ray,
  rime_urchin, ridge_lynx, cord_moth, scree_crawler, glass_skate, rim_crawler). Portraits exist. Gap (M3-UI-208): their
  `model` links in enemies.json.
- **New rows (8):**
  - Ch11: `conduit_crawler` (a boss add, plan default);
  - bosses: `mangrove_drowner`, `lamp_engine`, `avalanche_ram`, `malcor_venn` (a person: "people" rows show his portrait,
    as Moll's does), `wakefin`, `abiding_guard`;
  - the flat-engine part: no row, it shows under Malcor Venn's page.
  - Keys: `ENEMY_<ID>` and `LORE_<ID>` for each: **14**.
- **The Listen marks:** each page lists which abilities Pell can hear (screens.md §4).
- **People in the bestiary** follow Moll's precedent (creature_portraits.json `people`): Malcor Venn and the Abiding
  guard show a person's portrait, never a creature's.
