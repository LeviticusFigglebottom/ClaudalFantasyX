# The Lattice: Data, Rules, Authoring

Owner: Progression & Economy. Spec: SPEC §6.4 and pillar 5 ("growth you can see"). Formulas: [formulas.md § Progression](formulas.md#progression).

The Lattice is a shared board of nodes that every character walks across. Each hero starts at their own spot. Walking costs **movement points** earned in battle, and nodes are activated with consumable **Facets**. This page covers the data model, the headless logic, the editor tool, and the first board section. The 3D presentation (depth, glow, parallax starfield) is M2.

## Files

| Path | What it is |
|---|---|
| `tools/lattice_editor/sections/standard.lat` | **Source** of the standard board. Edit this file. |
| `tools/lattice_editor/lattice_editor.py` | Builds, checks, and previews boards (`build`, `check`, `svg`, `stats`). |
| `game/data/progression/lattice_standard.json` | **Generated** board (nodes and edges). Never hand-edit it; a test fails if it drifts from the source. |
| `game/data/progression/facets.json` | Board rules and the Facet table. Hand-edited. |
| `game/progression/*.gd` | Headless logic: `LatticeNode`, `LatticeBoard`, `LatticeRules`, `FacetInventory`, `LatticeTraveler`, `LatticeProgress`, `ProgressionFormulas`. |
| `tools/validate_data.py` | `check_progression`, `lattice_errors`, and `facets_errors`, run in CI. |

## Data model

### Board (`lattice_<id>.json`)

```json
{"board": {"id": "standard", "name_key": "LATTICE_STANDARD", "source": "tools/lattice_editor/sections/standard.lat"},
 "nodes": [{"id": "rh_01", "type": "stat", "stat": "agility", "value": 2, "x": -11, "y": 0, "region": "rhen"}, ...],
 "edges": [["rhen_start", "rh_01"], ...]}
```

| `type` | Extra fields | Meaning |
|---|---|---|
| `start` | `character` | Where that character begins. It counts as activated by them. At most one per character. |
| `stat` | `stat`, `value` | A flat bonus to one battle stat: `hp mp strength magic defense magic_defense agility accuracy evasion luck`. `level` is not a Lattice stat. |
| `ability` | `skill` | Grants a skill from `game/data/battle/skills.json`. |
| `gate` | `gate_level` | Blocks movement until opened with a Key Facet of exactly that level (1..`max_gate_level`). |
| `empty` | (none) | Walkable, nothing to activate. Reserved for the late-game rewrite items. |

All nodes carry `id`, `type`, integer `x`/`y` (lattice units; the 3D scene picks the world scale), and an optional `region` used for colour and grouping. Edges are undirected pairs. The validator rejects fields that don't belong to the node's type.

### Facets and rules (`facets.json`)

| Facet item | Type | Activates |
|---|---|---|
| `facet_power` | Power | stat nodes for `hp`, `strength`, `defense` |
| `facet_mind` | Mind | stat nodes for `mp`, `magic`, `magic_defense` |
| `facet_speed` | Speed | stat nodes for `agility`, `accuracy`, `evasion` |
| `facet_fortune` | Fortune | stat nodes for `luck` |
| `facet_ability` | Ability | ability nodes |
| `facet_key_1` to `facet_key_4` | Key | gates of level 1 to 4 |

`rules`: `move_cost` (1), `move_cost_activated` (0), `facets_per_activation` (1), `keys_per_gate` (1), and `max_gate_level` (4). Every Lattice stat must belong to exactly one Facet, and every gate level needs a Key Facet. The validator enforces both.

Facets are ordinary items. They live in `GameStateData.inventory` under their item id, and `FacetInventory` wraps that dictionary in place.

## Rules (what `LatticeProgress` does)

1. **Joining.** `add_character(id)` puts the hero on their start node. The game calls it when the hero joins the party; a hero with no start on the board can't join it.
2. **Moving.** A hero steps to an **adjacent** node. It costs `move_cost` (1) movement point, or `move_cost_activated` (0) if **anyone** has activated that node (start nodes and opened gates count). This follows the genre convention: walking well-trodden ground is free, and breaking new ground costs. Closed gates can't be entered. `cheapest_path()` finds the cheapest route (0-1 BFS) for "walk there" UI; it never plans through a closed gate.
3. **Activating.** A hero activates the node they **stand on** by spending `facets_per_activation` Facets of the matching type. Activation costs no movement. Each hero activates separately: Rhen activating `rh_01` doesn't give Asha its bonus, but it does make the node free for her to walk over.
4. **Gates.** A hero standing **next to** a gate opens it with `keys_per_gate` Key Facets of exactly its level. An opened gate stays open for everyone and then costs `move_cost_activated` to enter.
5. **Earning.** After a victory, call `award_battle(id, xp)` with each hero's entry from `BattleEngine.xp_awards()`. LP equals the credited XP and converts to movement points by the Progression formulas (thresholds grow every 10 points earned, and the bank caps at 99 without losing LP).
6. **Applying.** `apply_to(combatant)` adds every activated stat bonus and ability skill onto a combatant **freshly built** from `characters.json`. It adds, so call it once per combatant. HP and MP bonuses raise both the max and the current value. Skills the hero already knows are not duplicated.

Every action returns `RESULT_OK` or an `ERR_*` StringName (`no_movement_points`, `gate_closed`, `no_facet`, ...), and `activate_error()` / `open_gate_error()` answer without changing anything. The UI can always show **what an action costs and why it's blocked** (pillar 4).

### Saving

`LatticeProgress.to_dict()` is stored as plain data in `GameStateData.lattice`, as `{board, characters: {id: {position, activated[], movement_points, lattice_points, movement_earned}}, opened_gates[]}`. Rebuild it with `LatticeProgress.from_dict(state.lattice, LatticeBoard.load_board(id), LatticeRules.load_file())`. Save version 2 added the field; the v1→v2 migration writes empty progress on the standard board. `from_dict` drops node ids that the board no longer has (with a warning) and moves a lost position back to the start, so a board edit never bricks a save. It can still cost a player an activation, though: see the gotchas below.

## The first section (standard board, vertical slice)

87 nodes and 94 edges cover Rhen, Asha, and Toma. Preview it with `python3 tools/lattice_editor/lattice_editor.py svg`, which writes `tools/lattice_editor/out/lattice_standard.svg` (gitignored).

```
                                   [Asha pocket: L2 · Stilling Bell · Mending Chorus]
                                         \
              bridge (Hasten | L1 | Quick Hit)   ASHA start
             /                          \       /   \ ring
 [Rhen pocket]  RHEN start ─ring─ spine ─ L1 ─ ... ─ HUB (Luck+3) ─ empty ─ Breakwater ─ L3 ─┐
   L2 · Lantern Flare · Slipstream   \                  /                                     │
              bridge (Shell Breaker | L1 | Undertow Cut)   TOMA start      east bridge (Brace | L1 | Ward)
                                         /   \ ring
                                   [Toma pocket: L2 · Challenge · Shield Wall]
```

- **Three petals around a hub.** Each hero's start sits mid-line. **Ahead**, toward the hub, runs their niche spine, cut by a **level-1 gate**. **Behind** the start is a mastery pocket behind a **level-2 gate**, which holds their two strongest skills. A small ring of side nodes around each early spine gives a real choice of route.
- **Cross-over bridges** join each pair of petals' early rings. On your own side of a bridge you can learn your neighbour's signature skill before any gate; this is the visible cross-over. The bridge's middle is a level-1 gate into the neighbour's petal.
- **Hub spur.** An empty node (for later rewrite items), the shared heavy strike Breakwater, and a **level-3 gate** onto the east bridge. Section 2 (M2) attaches beyond the hub.

| Hero | Niche (story sheet) | Spine stats | Abilities on their path |
|---|---|---|---|
| Rhen | Fast striker, turn manipulation | AGI, ACC, EVA, STR, LCK | Kick Off the Wall (rank 1), Undercut (delay 1); pocket: Lantern Flare (Darkness), Slipstream (self Haste) |
| Asha | Healer, white mage | MAG, MP, MDF | Veil (Shell), Lull (Regen); pocket: Stilling Bell (Silence), Mending Chorus (party heal) |
| Toma | Tank, defender | HP, DEF, STR, MDF | Brace (self Protect), Sunder (Power Break); pocket: Challenge (Provoke), Shield Wall (party Protect) |

Before any gate, each hero has about 16 nodes to explore. That is roughly five or six sandbox-sized fights of movement points.

## Authoring (`.lat` format)

One command per line. `#` starts a comment when it begins the line or follows whitespace and is followed by a space; `#1` is a gate token.

```
board standard name_key=LATTICE_STANDARD
region rhen                                  # applies to the nodes that follow
start rhen_start rhen @ -12 0                # start <id> <character> @ <x> <y>
node hub luck+3 @ 0 0                        # node <id> <token> @ <x> <y>
walk rh from rhen_start E: agility+2 @kick_off #1 _ >N strength+1 -> hub
walk xra from rn_02 NE step=2: evasion+1 @hasten keep_me=#1
link a b                                     # an extra edge
```

- **Tokens:** `<stat>+<n>` is a stat node, `@<skill>` an ability, `#<level>` a gate, and `_` an empty node. `>DIR` turns the walk (`E W N S NE NW SE SW`; y grows downward). `-> <id>` must come last and links the walk's final node to an existing node, which closes loops.
- **Layout is automatic.** Each walk node sits one `step` (default 1) from the previous one along the current direction. `check` fails on overlapping nodes and on nodes lying on another edge, and warns about crossing edges.
- **Ids:** walk nodes are named `<walk>_<nn>` (`rh_01`, `rh_02`, ...). Write `myid=<token>` to pin a name.
- Workflow: edit the `.lat` → `build` → `svg` and look → `check` → commit the `.lat` and the JSON together. `tools/tests/test_lattice_editor.py` fails CI if the JSON is stale.

## Extending

- **New section:** add walks to `standard.lat` that start from existing nodes (the hub spur's L3 gate is the intended seam), or put them in a new region. Append; don't reorder.
- **New board** (for example Expert): write `sections/expert.lat` with `board expert ...` and build it. The validator picks up every `lattice_*.json` automatically, and `LatticeBoard.load_board(&"expert")` loads it.
- **New skill on the board:** add the row to `skills.json` and its `name_key` to `strings.csv` first. The validator rejects ability nodes with unknown skills.
- **New stat or Facet:** the stat must be a `BattleCombatant` field. Add it to `LatticeProgress._add_stat`, to `STAT_KEYS` in the validator, and to exactly one Facet's `stats`.
- **New node type** (for example a rewritable slot): add it to `LatticeNode`, `LATTICE_NODE_TYPES`/`LATTICE_NODE_FIELDS` in the validator, `_payload` in the editor, and the rules above, with tests.

## Gotchas

- **Node ids are save data.** Renaming or renumbering a node after it ships silently drops that activation from saves. Inserting a token mid-walk renumbers every later node in that walk, so append to the end, start a new walk, or pin ids with `id=token`. Before release, a board change that drops ids needs a save migration.
- **Gates must be the only way in.** A `-> link` or a bridge that touches a pocket bypasses its gate. Check the SVG, and remember that the reachability check treats gates as passable on purpose.
- **Keys match exactly.** A level-2 Key can't open a level-1 gate. That keeps Key economy readable; if playtests hate it, change it in `LatticeRules.facet_for` and in this page together.
- **`apply_to` adds.** Calling it twice doubles the bonuses. Build a fresh combatant for each battle.
- Movement points (the Lattice) and `mp` (battle mana) are different things. Code says `movement_points`.
- `Challenge` inflicts Provoke, which the engine doesn't implement yet (M1-CMB-02). The node is deep in Toma's L2 pocket, so it won't be reached before Combat ships Provoke.

## Expert mode (later, M3+)

SPEC §6.4 asks for an Expert board with an open layout, chosen at the start of a new game. Plan:

- A separate `sections/expert.lat` → `lattice_expert.json` sharing `facets.json`. The board id is saved in `GameStateData.lattice.board`, so the choice persists.
- Open layout: all starts around one central ring, fewer gates, and every hero can reach every niche with similar effort. Keep the same skills and roughly the same stat totals so balance is comparable.
- The new-game flow picks the board once. Switching boards mid-game is not supported, since the node ids differ.
- The validator and editor already handle any number of boards. Pathfinding on a much larger open board is the one hot path ADR 0003 names as a possible native module, so benchmark it before porting anything.
- Late-game "rewrite" items (SPEC §6.4) turn `empty` nodes into stat nodes. This needs a per-save overlay of node overrides in `LatticeProgress`, and it is not built yet.
