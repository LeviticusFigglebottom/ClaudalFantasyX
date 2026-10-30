#!/usr/bin/env python3
"""ADR 0205 (Act II per track): every Act II foe's ability gets its own battle VFX, as Act I's did
(tools/vfx/gen_act1_ability_vfx.py, whose motifs and palette rules this reuses).

Writes the abilities below into game/data/vfx/battle/effects.json (`effects` and `map.skills`), keeping every other
entry as it is, and gives each new effect a stand-in sound row in battle_sfx.json until audio writes its own.

Act II rules kept here (ADR 0204, color_script.md):
  - No ice from Ch12 to Ch15: the scree crawler's slide is snow and grit (cold stone, mortar white, dry sand), never
    crystals. The Ch11 urchin's rime is ice (the Sunken Vey is before the rule).
  - Undertow-spawn wounds are spawn_wound / glimmer_held; nothing here uses glimmer_lift (release only).
  - A poison wound is sick green settling (foliage_shadow, palm_green), as Act I's poison tick.

Usage: python3 tools/vfx/gen_act2_ability_vfx.py [--check]   (--check: exit 1 if a file would change)
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("gen_act1_ability_vfx", HERE / "gen_act1_ability_vfx.py")
A1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A1)
fx, slash, heavy, burst, spray, shards, sink = A1.fx, A1.slash, A1.heavy, A1.burst, A1.spray, A1.shards, A1.sink
ring, charge = A1.ring, A1.charge

# The Act II regulars' skills (ch10..ch16 encounters). Their foes' plain `attack` keeps the element hit.
SKILLS = {
    # Ch10 Ossa Fen
    "leech_bite": fx("chest", burst("foliage_shadow", "palm_green", 30, -1.5) + sink("palm_green", "foliage_shadow", 18, 0.3),
                     "The fen leech bites: a dark wet spatter, then the sickness settling in (poison)."),
    "root_drag": fx("ground", heavy("timber_weathered", "laterite", "sand_wet", "foliage_shadow", 44),
                    "The root crab drags at the footing: splinters and wet fen mud thrown out low."),
    "tannin_jet": fx("chest", spray("timber_weathered", "sand_wet", 50),
                     "The tannin archer's jet: brown fen water, tea-dark, breaking over the target."),
    # Ch11 the Sunken Vey
    "glide_lash": fx("chest", slash("lagoon_teal", "foam_white", 40, -1.0),
                     "The gallery ray's lash: a flat sweep of sea water off its wing edge."),
    "rime_spine": fx("chest", shards("salt_glass", "moon_blue", 22) + sink("moon_blue", "cold_blue_stone", 14, 0.3),
                     "The rime urchin's spine: rime shards, then the cold slowing the target (Slow)."),
    # Ch12 Keth Pass (no ice, ADR 0204)
    "scree_slide": fx("ground", heavy("cold_blue_stone", "mortar_white", "sand_dry", "overcast_slate", 50),
                      "The scree crawler's slide: grit and wet snow tumbling at the target's feet (no ice: ADR 0204)."),
    "unravel": fx("chest", sink("sand_cloth", "faded_teal_cloth", 30, 0.45) + slash("bone", "sand_cloth", 16),
                  "The cord moth unravels a woven blessing: loose thread-ends pulled off and falling (a cleanse of buffs)."),
    # Ch16 the Pale Rim
    "skate_sting": fx("chest", slash("salt_glass", "palm_green", 30) + sink("palm_green", "foliage_shadow", 14, 0.25),
                      "The glass skate's sting: a needle of pale glass, then the poison settling."),
    # The Act II creature bosses (PROVISIONAL rows, 10-30; their sheets' attack and cast reads)
    "drowner_drag": fx("ground", spray("deep_teal_shadow", "foam_white", 50),
                       "The Mangrove Drowner hauls the footing: fen water dragged back along the roots."),
    "rising_water": fx("ground", spray("lagoon_teal", "deep_teal_shadow", 60),
                       "The Drowner's rising water climbs around each of the party (water, never glimmer)."),
    "root_stamp": fx("ground", heavy("timber_weathered", "laterite", "sand_wet", "foliage_shadow", 56),
                     "Risen on its root-feet, the Drowner stamps: splinters and fen mud."),
    "lamp_trim": fx("chest", slash("brass", "salt_glass", 36), "The Lamp Engine's scissor arm snips: brass sparks."),
    "lamp_gather": fx("chest", charge("glimmer_bound", "salt_glass", 44),
                      "The Lamp Engine gathers: every lamp turns to the party and brightens (bound light, steady)."),
    "lamp_flare": fx("chest", burst("glimmer_bound", "salt_glass", 44, -1.0),
                     "The lamps loose together: bound light in the eyes (capped by particles, not a screen flash)."),
    "core_pulse": fx("chest", burst("glimmer_bound", "lagoon_teal", 50, -1.5),
                     "The bared core pulses: a ring of steady bound light breaking over each of the party."),
    "horn_toss": fx("chest", slash("sand_cloth", "overcast_slate", 36), "The Avalanche Ram tosses its head: wet wool and grit."),
    "ram_charge_gather": fx("ground", ring("mortar_white", "sand_dry", 40, 1.2),
                            "The Ram paws the terrace, head low: snow kicked up around its feet (no ice, ADR 0204)."),
    "ram_charge": fx("ground", heavy("sand_cloth", "overcast_slate", "mortar_white", "sand_dry", 60),
                     "The Ram drives through: snow and grit thrown out low."),
    "ram_bellow": fx("head", sink("mortar_white", "overcast_slate", 40, 0.5),
                     "The bellow brings the snow down off the wall onto the party (wet snow, never ice)."),
    "fin_cut": fx("chest", slash("sea_glow", "abyss_navy", 40), "The Wakefin's blade cuts across the rail: a seam of sea-glow."),
    # feet, not ground: ground sits on the body's near face, which for a fin in the water is against the barge's hull
    "sound_dive": fx("feet", ring("sea_glow", "abyss_navy", 48, 1.6),
                     "The Wakefin sounds: the water darkens, then a ring of sea-glow marks where it will rise (a glow, not a light)."),
    "wake_breach": fx("chest", spray("sea_glow", "deep_teal_shadow", 60),
                      "It breaches alongside and the fin sweeps the deck: black water lit from below."),
    "wake_wheel": fx("ground", spray("deep_teal_shadow", "sea_glow", 44),
                     "The circle closes: the wake rocks the barge under each of the party."),
}


def main() -> int:
    text = A1.EFFECTS.read_text()
    data = json.loads(text)
    sk = {s["id"] for s in json.loads((A1.ROOT / "game/data/battle/skills.json").read_text())["skills"] if isinstance(s, dict)}
    missing = sorted(s for s in SKILLS if s not in sk)
    if missing:
        print("unknown ids:", missing)
        return 1
    for sid, eff in SKILLS.items():
        mapped = data["map"]["skills"].get(sid)
        if mapped is not None and data["effects"].get(mapped, {}).get("note") != eff["note"]:
            continue  # someone else's mapping wins
        own = data["effects"].get(sid)
        eid = sid if own is None or own.get("note") == eff["note"] else sid + "_hit"
        data["effects"][eid] = eff
        data["map"]["skills"][sid] = eid
    out = json.dumps(data, indent=2) + "\n"
    sfx_text = A1.SFX.read_text()
    sfx = json.loads(sfx_text)
    A1._stand_in_sounds(data, sfx)
    sfx_out = json.dumps(sfx, indent=2) + "\n"
    if "--check" in sys.argv:
        return 0 if out == text and sfx_out == sfx_text else 1
    A1.EFFECTS.write_text(out)
    A1.SFX.write_text(sfx_out)
    print("effects.json: %d Act II skills" % len(SKILLS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
