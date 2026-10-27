# Act II variants (M3-CRE-620)

A variant is a slice or Act I creature's rig and clips with a new materials.json, new proportions in its build
parameters where the base allows them, and a creatures.json row: SPEC §5's palette variant with new behaviour.

| Id | Base | Where | What changes | Behaviour (proposal) |
|---|---|---|---|---|
| `root_crab` | `reef_crab` | Ossa Fen (Ch10) | Bark-brown carapace (`timber_weathered`, `laterite`) spotted with grey lichen (`overcast_slate`), longer climbing legs; the house-coral is mangrove bark and a knot of roots | **Roots** one hero (no swap) for two turns; the defender |
| `fen_leech` | `sail_leech` | Ossa Fen (Ch10) | Ribbon-flat and longer; back `lacquer_black` wet, underside a faint tannin-amber (`dusk_gold` darkened); no canvas | A drainer: heals by what it takes |
| `scree_crawler` | `slag_tortoise` | the Cloudloom approach (Ch12) | Frost-split scree on the shell (`overcast_slate`, `salt_glass` rime) instead of slag; a shaggier skin | Armour break again, with a frost counter on contact |
| `rim_crawler` | `tide_crawler` | the Pale Rim (Ch16) | Bleached chalky carapace (`mortar_white` over `lacquer_black` in the joints), wounds dimmer | The swarm, in the open: no wall to hold |

Variants that rebuild a base mesh (the root crab's legs, the fen leech's length) need a parameter in the base's
build, so the base job lists them; the others need only a materials.json (as the wall crab and the wreck crab do).
