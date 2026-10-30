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
    # at its head, rising: from the fight's frame the barge's rail hides the whole waterline beside the hull, so a ring
    # on the water (tried at the near face, then at the fin's feet, 10-30) was never seen; the fin dives as it sounds
    # large, slow and long-lived: at 12 m in the dark, the stock rise motes read as one dot (10-30)
    "sound_dive": fx("crest", [A1.layer("sea_glow", "lagoon_teal", 70, 2.4, 0.15, (0.3, 0.7), 20, (0, 0.2, 0), (0.3, 0.55),
                                       radius=1.0, turb=0.25, energy=2.2),
                              A1.layer("sea_glow", "abyss_navy", 30, 2.8, 0.1, (0.15, 0.35), 30, (0, 0.1, 0), (0.5, 0.8),
                                       radius=0.6, turb=0.2, energy=1.6)],
                     "The Wakefin sounds: it goes under and sea-glow rises off the water where its fin was, marking where it will come up (a glow, not a light)."),
    "wake_breach": fx("chest", spray("sea_glow", "deep_teal_shadow", 60),
                      "It breaches alongside and the fin sweeps the deck: black water lit from below."),
    "wake_wheel": fx("ground", spray("deep_teal_shadow", "sea_glow", 44),
                     "The circle closes: the wake rocks the barge under each of the party."),
}

# M4-A2P-061: the four Act II Vowbound (bound light, color_script rule 2: glimmer_bound, steady, never shed) and
# their Swell finishers. Their skill rows land with act1-chapters' vowbound.json (big21); until a skill exists in
# skills.json its row here is skipped, so this table can wait for them.
LAYER = A1.layer
VOWBOUND = {
    # Nhoa, the Rootlight (Ice). Her cold is the deep's, not a frozen surface (nhoa.md): deep teal and navy, no
    # crystals (ADR 0204 keeps ice out of Ch12-15).
    "silt_fall": fx("chest", sink("glimmer_bound", "deep_teal_shadow", 40, 0.45) + burst("deep_teal_shadow", "abyss_navy", 30, -1.0),
                    "Nhoa's Silt Fall: her motes sift down over the target like silt in deep water, and the deep's cold breaks on it."),
    "deep_well": fx("ground", ring("deep_teal_shadow", "abyss_navy", 44, 1.4) + sink("glimmer_bound", "deep_teal_shadow", 30, 0.6),
                    "Nhoa's Deep Well: the deep's cold wells up under each foe, a dark ring with her motes settling into it."),
    "nhoa_echo": fx("chest", burst("glimmer_bound", "abyss_navy", 40, -1.0),
                    "Nhoa's Echo: the last foe's blow, given back in her bound light."),
    "farewell_tide": fx("ground", spray("deep_teal_shadow", "abyss_navy", 60) + A1.rise("glimmer_lift", "glimmer_lift_hi", 40, 1.6, 0.6),
                        "Farewell-Tide (Nhoa's Swell): the deep's cold tide breaks over every foe, and motes rise off it: the only finisher whose light goes up (act2_plan 4.4; rule 1's released glimmer)."),
    # Hesk (Holy, cleanse, Regen): glimmer_bound held in gauze-white cords (hesk.md: one bound light colour).
    "knot_light": fx("chest", burst("glimmer_bound", "gauze_white", 44, -1.5) + slash("gauze_white", "glimmer_bound", 16),
                     "Hesk's Knot-Light: a lit knot opens on the target, the cord-ends snapping out white."),
    "cord_lift": fx("ground", ring("gauze_white", "glimmer_bound", 36, 0.9),
                    "Hesk's Cord-Lift: a ring of white cord rises around each ally and lifts their afflictions (a cleanse)."),
    "hesk_mending": fx("chest", sink("glimmer_bound", "gauze_white", 30, 0.5),
                       "Hesk's Mending: her light settles onto each ally, steady (Regen)."),
    "pass_cord": fx("chest", slash("glimmer_bound", "gauze_white", 70, 1.0) + burst("gauze_white", "glimmer_bound", 30, -1.0),
                    "Pass-Cord (Hesk's Swell): a line of shining knots runs across the field, a knot catching on each foe."),
    # Ethren (Glimmer, Slow and Stop, wards): stillness. The bound light shows at lacquer seams (ethren.md); his effects
    # barely move.
    "level_hand": fx("chest", [LAYER("glimmer_bound", "lacquer_black", 36, 0.9, 0.9, (0.05, 0.2), 180, (0, 0, 0), (0.14, 0.28), radius=0.35, energy=1.4)],
                     "Ethren's Level Hand: the air around the target goes level and still, held in bound light."),
    "hold_the_hour": fx("ground", ring("glimmer_bound", "lacquer_black", 40, 1.2) + sink("lacquer_red_deep", "lacquer_black", 20, 0.4),
                        "Ethren's Hold the Hour: a still ring closes on the target's footing (Stop)."),
    "lacquer_screen": fx("ground", ring("lacquer_red_deep", "glimmer_bound", 36, 1.0),
                         "Ethren's Lacquer Screen: a lacquered screen stands around each ally, bound light at its seams (a ward)."),
    "still_water": fx("ground", [LAYER("glimmer_bound", "abyss_navy", 60, 1.6, 0.95, (0.02, 0.08), 5, (0, 0, 0), (0.2, 0.36), radius=2.0, energy=1.4)]
                      + sink("glimmer_bound", "lacquer_black", 24, 0.6),
                      "Still Water (Ethren's Swell): the field goes flat and still under every foe, a wide ring that does not move."),
    # Kesh, the Seven (element cycling): each voice its element's colours, carried on bound light.
    "voice_water": fx("chest", spray("turquoise_shallow", "glimmer_bound", 50), "Kesh's water voice: sea water over each foe."),
    "voice_lightning": fx("chest", slash("starlight", "glimmer_bound", 40), "Kesh's lightning voice: a white seam across the target."),
    "voice_fire": fx("chest", burst("ember_orange", "glimmer_bound", 44, -2.0), "Kesh's fire voice: embers breaking on the target."),
    "voice_ice": fx("chest", shards("salt_glass", "moon_blue", 22), "Kesh's ice voice: rime over each foe."),
    "voice_holy": fx("chest", sink("glimmer_bound", "gauze_white", 30, 0.5), "Kesh's holy voice: light settling onto each ally."),
    "voice_glimmer": fx("chest", A1.rise("glimmer_lift", "glimmer_lift_hi", 36, 1.1, 0.4),
                        "Kesh's glimmer voice: released glimmer rising off each foe (rule 1)."),
    "the_seven": fx("chest", burst("turquoise_shallow", "glimmer_bound", 20, -1.5) + burst("ember_orange", "glimmer_bound", 20, -1.5)
                    + slash("starlight", "glimmer_bound", 20) + burst("glimmer_lift", "glimmer_lift_hi", 20, -0.5),
                    "The Seven (Kesh's Swell): every voice at once over every foe, water, fire, lightning and glimmer together."),
}

# Act II foes whose rows land later (act1-chapters' M4-A2P-022, on gate-big22): written once each skill exists.
FOES_PENDING = {
    # the conduit crawler (the Lamp Engine's tender): a Lit Age machine, its light bound and steady (rule 2)
    "brush_jab": fx("chest", slash("brass", "bronze_patina", 34), "The conduit crawler's brush arm jabs: brass grit and old patina."),
    "crawler_mend": fx("chest", charge("glimmer_bound", "brass", 36),
                       "The crawler relights a broken part of the engine: bound light drawn back into it, steady (no drift, no flicker)."),
    "crawler_tend": fx("ground", ring("brass", "glimmer_bound", 20, 0.6),
                       "The crawler tends the engine: a small brass ring at its feet; it pays the party no mind."),
}


def main() -> int:
    text = A1.EFFECTS.read_text()
    data = json.loads(text)
    sk = {s["id"] for s in json.loads((A1.ROOT / "game/data/battle/skills.json").read_text())["skills"] if isinstance(s, dict)}
    missing = sorted(s for s in SKILLS if s not in sk)
    if missing:
        print("unknown ids:", missing)
        return 1
    rows = dict(SKILLS)
    rows.update({sid: eff for sid, eff in {**VOWBOUND, **FOES_PENDING}.items() if sid in sk})  # each as its row lands
    for sid, eff in rows.items():
        mapped = data["map"]["skills"].get(sid)
        if mapped not in (None, sid, sid + "_hit") and data["effects"].get(mapped, {}).get("note") != eff["note"]:
            continue  # someone else's mapping wins (this tool's own ids are rewritten)
        own = data["effects"].get(sid)
        if mapped in (sid, sid + "_hit"):
            eid = mapped  # this tool's own effect: rewritten in place
        else:
            eid = sid if own is None or own.get("note") == eff["note"] else sid + "_hit"
        data["effects"][eid] = eff
        data["map"]["skills"][sid] = eid
    data["anchor_heights"]["crest"] = 1.0  # a body's top, on its middle (anchor_centred): not on its near face
    data["anchor_centred"] = sorted(set(data.get("anchor_centred", ["feet"])) | {"feet", "crest"})
    data["anchor_centred_doc"] = ("Anchor heights placed on the body's middle, not its near face (BattleVfx.anchor). crest: the "
                                  "Wakefin's near face is 1.9 m out, against the barge's hull; its Sound Dive rises at its crest.")
    out = json.dumps(data, indent=2) + "\n"
    sfx_text = A1.SFX.read_text()
    sfx = json.loads(sfx_text)
    A1._stand_in_sounds(data, sfx)
    sfx_out = json.dumps(sfx, indent=2) + "\n"
    if "--check" in sys.argv:
        return 0 if out == text and sfx_out == sfx_text else 1
    A1.EFFECTS.write_text(out)
    A1.SFX.write_text(sfx_out)
    pending = len(VOWBOUND) + len(FOES_PENDING)
    print("effects.json: %d Act II skills, %d of %d pending (Vowbound, later foes)" % (len(SKILLS), len(rows) - len(SKILLS), pending))
    return 0


if __name__ == "__main__":
    sys.exit(main())
