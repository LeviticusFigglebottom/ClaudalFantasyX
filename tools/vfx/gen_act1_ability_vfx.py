#!/usr/bin/env python3
"""ADR 0041 (Act I at final quality): every Act I ability gets its own battle VFX, not only its element's generic hit.

Writes the abilities below into game/data/vfx/battle/effects.json (`effects` and `map.skills` / `map.items`), keeping
every other entry as it is. BattleVfx plays an ability's own effect once per target, on top of the element hit, the
heal and the status effects (docs/kb/tech/battle_vfx.md). Colours are palette.json swatches only (the test checks each
hex against its swatch name).

Art rules kept here (color_script.md, decisions_log):
  - glimmer_lift (released, rising gold) is only for release; nobody's attack uses it.
  - Undertow-spawn wounds are spawn_wound / glimmer_held, sinking or sideways, never rising.
  - Lamps burn oil (oil_lamp, dusk_gold), never glimmer. Vowbound light is glimmer_bound: steady, no drift.
The skills aimed at the stair (`ward`: grip_the_stair, rope_dive, hand_closes) play at the arena's StairHead_ward mark
(M3-BPR-1325, BattleVfx.entry_mark); their motion is BattleChoreo's push reaction on the climb.

Usage: python3 tools/vfx/gen_act1_ability_vfx.py [--check]   (--check: exit 1 if the file would change)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EFFECTS = ROOT / "game/data/vfx/battle/effects.json"
PALETTE = ROOT / "docs/kb/art/palette.json"
SW = {k: v["hex"] for k, v in json.loads(PALETTE.read_text())["swatches"].items()}


def layer(a: str, b: str, amount: int, life: float, explos: float, vel: tuple, spread: float, gravity: tuple,
          size: tuple, direction: tuple = (0, 1, 0), radius: float = 0.15, turb: float = 0.0,
          energy: float = 1.15) -> dict:
    return {"color": SW[a], "color_end": SW[b], "swatches": [a, b], "amount": amount, "lifetime_s": life,
            "explosiveness": explos, "velocity_m_s": list(vel), "spread_deg": spread, "gravity": list(gravity),
            "size_m": list(size), "energy": energy, "emission_radius_m": radius, "turbulence": turb,
            "direction": list(direction)}


def core(a: str, b: str, size: float = 1.0, life: float = 0.18) -> dict:
    return layer(a, b, 2, life, 1.0, (0.0, 0.05), 0, (0, 0, 0), (size, size * 1.3), radius=0.02, energy=1.2)


# --- motifs: each returns layers. No impact core of their own: the element hit (or the heal, the status) already
# plays one, and a second stacked on it read as a soft blob in the first self-render. -------------------------------
def slash(a, b, n=40, side=1.0):  # a quick lateral spray of sparks across the target
    return [layer(a, b, n + 10, 0.4, 0.95, (2.0, 3.6), 18, (0, -2.0, 0), (0.12, 0.26), (side, 0.25, 0), 0.15, energy=1.4)]


def heavy(a, b, dust_a, dust_b, n=50):  # a heavy blow: a big core, chunks, and dust kicked out low
    return [layer(a, b, n + 10, 0.6, 0.95, (1.4, 3.0), 70, (0, -7.0, 0), (0.14, 0.3), radius=0.2, energy=1.4),
            layer(dust_a, dust_b, 30, 0.9, 0.9, (0.8, 1.6), 85, (0, -0.6, 0), (0.22, 0.46), radius=0.3, turb=0.3)]


def burst(a, b, n=45, rise=-2.5):  # a round impact
    return [layer(a, b, n + 10, 0.55, 0.92, (1.0, 2.2), 180, (0, rise, 0), (0.13, 0.29), energy=1.4)]


def spray(a, b, n=55):  # water thrown up and falling
    return [layer(a, b, n + 10, 0.7, 0.9, (1.5, 3.0), 50, (0, -6.0, 0), (0.12, 0.26), radius=0.2, energy=1.4)]


def shards(a, b, n=24):  # few, larger pieces falling
    return [layer(a, b, n + 6, 0.8, 0.95, (1.2, 2.4), 60, (0, -6.5, 0), (0.18, 0.36), radius=0.15, energy=1.4)]


def rise(a, b, n=36, life=1.1, radius=0.35):  # slow upward motes (a blessing, a stance)
    return [layer(a, b, n, life, 0.3, (0.4, 0.9), 25, (0, 0.4, 0), (0.15, 0.3), radius=radius, turb=0.3, energy=1.4)]


def sink(a, b, n=32, radius=0.35):  # motes settling down over the target (a hex, a smother)
    return [layer(a, b, n, 1.0, 0.4, (0.2, 0.5), 30, (0, -1.4, 0), (0.16, 0.32), (0, -1, 0), radius, 0.2, energy=1.4)]


def ring(a, b, n=40, radius=0.75):  # a ring lifting from the feet (a guard, a ward)
    return [layer(a, b, n, 0.9, 0.85, (0.05, 0.15), 5, (0, 0.5, 0), (0.16, 0.3), radius=radius, energy=1.4)]


def charge(a, b, n=40):  # gathering: motes drawn in and up around the body
    return [layer(a, b, n, 1.0, 0.0, (0.1, 0.3), 40, (0, 1.0, 0), (0.13, 0.26), radius=1.0, turb=0.4, energy=1.3)]


def column(a, b, n=60):  # a column straight up from the feet (a flame, a bolt)
    return [layer(a, b, n + 10, 0.6, 0.9, (2.5, 4.5), 8, (0, -1.0, 0), (0.13, 0.28), radius=0.15, energy=1.4)]


def fx(at: str, layers: list, note: str) -> dict:
    return {"kind": "particles", "anchor": "target", "at": at, "layers": layers, "note": note}


# --- the Act I abilities -----------------------------------------------------------------------------------------
SKILLS = {
    # The party (characters.json kits; Ch8's set-piece skills).
    "quick_hit": fx("chest", slash("foam_white", "cold_blue_stone", 30), "Rhen: a quick light cut, foam-white going slate."),
    "undertow_cut": fx("chest", slash("lagoon_teal", "deep_teal_shadow", 50, -1.0) + sink("deep_teal_shadow", "abyss_navy", 18),
                       "Rhen: a cut that drags down like the undertow: teal spray pulled under."),
    "mend": fx("chest", rise("turquoise_shallow", "foam_white", 30), "Asha: shallow water lifting off the wound (water, not glimmer)."),
    "hasten": fx("feet", [layer("sky_horizon_noon", "foam_white", 30, 0.6, 0.6, (2.5, 4.0), 10, (0, -0.5, 0), (0.05, 0.12), radius=0.3)],
                 "Asha: quick pale streaks rising past the ally."),
    "ward": fx("feet", ring("reef_blue", "sky_horizon_noon"), "Asha: a ring of reef-blue light lifting around the ally."),
    "shell_breaker": fx("chest", shards("tortoiseshell", "bone", 26) + burst("bone", "coral_stone_weathered", 20),
                        "Toma: shell plates cracking off the target."),
    "hold_the_stair": fx("feet", ring("indigo_dye", "sea_blue_cloth", 44), "Toma (Ch8): he sets his shield over the stair."),
    "stand_firm": fx("feet", ring("bone", "sand_cloth", 30), "Toma (Ch8): feet set, dust settling."),
    "challenge": fx("head", burst("ember_orange", "dusk_gold", 24, 1.0), "Toma (Ch8): the challenge, a spark at the foe's head."),
    "stand_fast": fx("feet", ring("sand_cloth", "bone", 26), "Ch8: a hero braces on the wall-walk."),
    "ember": fx("chest", column("ember_orange", "dusk_gold", 40), "Ysolde: a small flame climbing the target."),
    "frost": fx("chest", shards("moon_blue", "salt_glass", 26), "Ysolde: cold blue shards of rime falling."),
    "slow_hex": fx("head", sink("indigo_dye", "tattoo_ink", 34), "Ysolde: ink-dark motes settling over the target."),
    "fluke_cleave": fx("chest", heavy("cold_blue_stone", "bone", "sand_wet", "timber_weathered", 40),
                       "Kerrid: the anchor-fluke bites: iron chips and splinters."),
    "snub_line": fx("chest", slash("sand_cloth", "timber_weathered", 34, -1.0), "Kerrid: the line snubbed hard: rope fibres snapping."),
    "anchor_fall": fx("ground", heavy("cold_blue_stone", "bone", "sand_dry", "laterite", 60), "Kerrid: the anchor comes down: dust and stone."),
    "reel_shot": fx("chest", slash("brass", "foam_white", 26), "Liss: the line strikes home, brass bright."),
    "flash_housing": fx("head", [core("oil_lamp", "sun_noon", 1.4, 0.3)] + burst("oil_lamp", "dusk_gold", 30, 0.5),
                        "Liss: the lamp housing's flash in the foe's eyes (oil light; capped by particles, not a screen flash)."),
    "hoist_haul": fx("chest", rise("sand_cloth", "bone", 24, 0.8), "Liss (Ch8): the hoist hauls a group up."),
    # Swells (lamp_dive and shallows_verse are rendering's own).
    "return_tide": fx("ground", spray("turquoise_shallow", "foam_white", 70), "Toma's Swell: the tide thrown back out from the stair."),
    "written_light": fx("chest", [layer("starlight", "salt_glass", 50, 0.9, 0.5, (0.6, 1.4), 15, (0, 0.2, 0), (0.04, 0.1),
                                        (1, 0.3, 0), 0.4)] + burst("starlight", "lit_ceramic", 20),
                        "Ysolde's Swell: written strokes of pale light across each foe (not glimmer)."),
    "floodnet": fx("chest", [layer("glimmer_bound", "lagoon_teal", 40, 1.2, 0.6, (0.05, 0.2), 90, (0, 0, 0), (0.06, 0.12), radius=0.6)],
                   "Ilun's Swell: a steady net of bound threads over each foe (bound light: no drift)."),
    "last_strike": fx("chest", column("starlight", "moon_blue", 70), "Kahre's Swell: raw lightning down onto the foe."),
    "flare_line": fx("chest", burst("ember_orange", "dusk_gold", 40, 1.2), "Virel's Swell: the kite-string burning, a flare on each foe."),
    # Vowbound skills.
    "brine_lash": fx("chest", spray("turquoise_shallow", "foam_white", 60) + slash("lagoon_teal", "foam_white", 30),
                     "Ilun: a lash of brine."),
    "tidal_ward": fx("feet", ring("lagoon_teal", "turquoise_shallow", 50), "Ilun: water rising in a ring around itself."),
    "forge_bolt": fx("chest", column("starlight", "ember_orange", 50), "Kahre: a forge-hot bolt."),
    "kite_flare": fx("head", burst("oil_lamp", "ember_orange", 26, -0.8), "Virel: a kite's flare drifting down on the foe."),
    # Act I creatures (enemies.json): by family, tinted by the creature.
    "pinch": fx("chest", slash("tortoiseshell", "sand_wet", 26), "A crab's pinch: dark shell grit."),
    "scuttle_claw": fx("chest", slash("coral_stone_weathered", "sand_wet", 26, -1.0), "A scuttler's claw."),
    "tide_claw": fx("chest", slash("spawn_wound", "glimmer_held", 28, -1.0), "A tide crawler's claw: the Undertow's light, sideways."),
    "limpet_clamp": fx("chest", burst("cold_blue_stone", "bone", 22), "A limpet clamps down."),
    "skim_bite": fx("chest", spray("foam_white", "turquoise_shallow", 30), "A skipper's bite out of the shallows."),
    "shoal_nip": fx("chest", spray("foam_white", "lagoon_teal", 20), "A wickfry's nip."),
    "hound_bite": fx("chest", burst("bone", "sand_wet", 26), "The Order's hound bites."),
    "gnaw": fx("chest", heavy("spawn_wound", "glimmer_held", "deep_teal_shadow", "abyss_navy", 50), "Hullgnaw's gnaw: the spawn's wound-light, sinking."),
    "dive_rake": fx("chest", slash("cumulus_lit", "cumulus_shadow", 30), "A gull's raking dive: pale feathers."),
    "wing_peck": fx("chest", slash("cumulus_shadow", "storm_slate", 22), "A squall wing pecks."),
    "ash_rake": fx("chest", slash("volcanic_stone", "storm_slate", 34), "An ashwing rakes: ash streaks."),
    "spar_stab": fx("chest", slash("timber_weathered", "bone", 26), "The spar-wraith's spar: splinters."),
    "glass_jab": fx("chest", shards("salt_glass", "lit_ceramic", 18), "The bottle hermit's glass."),
    "rib_lash": fx("chest", slash("spawn_wound", "deep_teal_shadow", 30), "Hullgnaw's ribs lash."),
    "haft_strike": fx("chest", burst("brass", "bone", 22), "The Inquisitor's haft."),
    "shell_ram": fx("chest", heavy("cold_blue_stone", "bone", "volcanic_stone", "storm_slate", 34), "A slag tortoise rams."),
    "ladle_swing": fx("chest", heavy("ember_orange", "dusk_gold", "volcanic_stone", "storm_slate", 46), "The Cinder Matron's ladle: molten slag."),
    "hood_slam": fx("chest", heavy("bronze_patina", "brass", "sand_wet", "timber_weathered", 40), "The Drownbell's hood comes down."),
    "crust_slam": fx("chest", heavy("spawn_wound", "glimmer_held", "cold_blue_stone", "storm_slate", 50), "The Reach's crust slams."),
    # Black oil on a dark tower vanished in the arena self-render: lamp-lit glints ride on it (oil light, not glimmer).
    "oil_slap": fx("chest", spray("lacquer_black", "volcanic_stone", 30) + slash("oil_lamp", "dusk_gold", 24),
                   "An oil slug slaps: black oil."),
    "sail_drop": fx("head", sink("gauze_white", "sand_cloth", 28), "A sail leech drops over the target."),
    "pounce": fx("chest", heavy("bone", "sand_wet", "sand_dry", "laterite", 34), "The hound pounces."),
    "brine_spit": fx("chest", spray("lagoon_teal", "foam_white", 40), "A crab spits brine."),
    "lure_glow": fx("head", [layer("sea_glow", "glimmer_held", 56, 0.9, 0.5, (0.2, 0.5), 60, (0, -0.4, 0), (0.16, 0.32), radius=0.45,
                                   energy=1.6)],
                    "The lantern eel's lure: a cold glow."),
    "spark_spit": fx("chest", burst("starlight", "moon_blue", 30, -1.5), "A vein sparker spits sparks."),
    "glass_flare": fx("chest", burst("oil_lamp", "dusk_gold", 30, 0.8), "The hermit's bottle flares."),
    "brine_iron": fx("chest", burst("ember_orange", "salt_glass", 34, -1.0), "The Inquisitor's brine-iron: a salt burn."),
    "smother": fx("head", sink("lacquer_black", "volcanic_stone", 34) + sink("oil_lamp", "dusk_gold", 14),
                  "An oil slug smothers."),
    "wing_dust": fx("head", sink("volcanic_stone", "storm_slate", 30), "Ash shaken from a wing over each foe."),
    "housing_glare": fx("head", burst("oil_lamp", "sun_noon", 20, 0.4), "A wreck crab's lamp-housing glare."),
    "polyp_mend": fx("chest", sink("glimmer_held", "spawn_wound", 24), "A polyp's held motes mend its ally (sinking, never rising)."),
    "shroud_sweep": fx("chest", slash("cumulus_shadow", "storm_slate", 30, -1.0), "The spar-wraith's shroud sweeps the party."),
    "undertow_pull": fx("feet", sink("deep_teal_shadow", "abyss_navy", 30), "The Reach pulls at the party's footing."),
    # Gathers and stances on themselves (charges read on stage too: BattleTelegraph).
    "gnaw_coil": fx("chest", charge("spawn_wound", "deep_teal_shadow"), "Hullgnaw coils."),
    "pull_in": fx("chest", charge("cold_blue_stone", "storm_slate", 30), "A slag tortoise pulls into its shell."),
    "bank_the_fire": fx("chest", charge("ember_orange", "dusk_gold"), "The Cinder Matron banks her fire."),
    "shell_wall": fx("feet", ring("lacquer_red_deep", "brass", 36), "The Inquisitor's red shell armour closes."),
    "reach_for_stair": fx("chest", charge("spawn_wound", "glimmer_held", 30), "A crawler reaches for the stair."),
    "close_the_hand": fx("chest", charge("spawn_wound", "abyss_navy", 50), "The Reach's hand closes."),
    "breach_gather": fx("chest", charge("glimmer_held", "abyss_navy", 60), "The Breach gathers."),
    "recrust_gather": fx("chest", charge("volcanic_stone", "ember_orange", 40), "The Matron's crust re-forms."),
    "lines_taut": fx("chest", charge("sand_cloth", "timber_weathered", 30), "The Spar-Wraith's lines go taut."),
    "climb_up": fx("feet", rise("sand_cloth", "bone", 20, 0.8), "The Climb: a group goes up the stair."),
    # M3-BPR-1325: aimed at the stair (the Climb, a ward entry with no fighter), played at the arena's StairHead_ward mark.
    "grip_the_stair": fx("feet", slash("spawn_wound", "glimmer_held", 34) + sink("deep_teal_shadow", "abyss_navy", 18),
                         "A crawler grips the stair head: wound-light clawing sideways, the climbers falter."),
    "rope_dive": fx("chest", [layer("sand_cloth", "cumulus_shadow", 40, 0.5, 0.95, (2.5, 4.0), 20, (0, -3.0, 0), (0.06, 0.14),
                                    (1.0, -0.4, 0), 0.2, energy=1.3)],
                    "A squall wing dives the hand-line: spray and rope fibre whipped down across the stair."),
    "hand_closes": fx("chest", sink("abyss_navy", "storm_slate", 70, 0.9) + burst("spawn_wound", "deep_teal_shadow", 30, -1.0),
                      "The storm's hand closes on the stair head: the dark comes down whole, wound-light crushed out."),
    "surge_ebb": fx("feet", sink("deep_teal_shadow", "sea_glow", 20), "The Surge ebbs."),
    "rouse_polyp": fx("chest", charge("glimmer_held", "spawn_wound", 30), "The Drownbell rouses a polyp."),
    "surge_crawler": fx("feet", spray("deep_teal_shadow", "sea_glow", 30), "The Surge throws up a crawler."),
    "surge_wing": fx("feet", spray("storm_slate", "sea_glow", 30), "The Surge throws up a squall wing."),
    "storm_call_sound": fx("head", charge("moon_blue", "storm_slate", 30), "Pell sounds the storm-call."),
    "storm_call": fx("chest", column("starlight", "moon_blue", 40), "Pell's storm-call strikes and drives a foe off."),
    # The Act I bosses' phase skills (enemies.json phase rows).
    "thrash": fx("chest", heavy("spawn_wound", "deep_teal_shadow", "sand_wet", "timber_weathered", 40), "Hullgnaw thrashes in its ribs."),
    "haul": fx("chest", heavy("timber_weathered", "bone", "sand_cloth", "timber_weathered", 50), "The Spar-Wraith hauls its spar down on a foe."),
    "sea_lash": fx("chest", spray("lagoon_teal", "foam_white", 50), "The Spar-Wraith lashes the party with the sea."),
    "slag_pour": fx("chest", spray("ember_orange", "dusk_gold", 60) + sink("volcanic_stone", "storm_slate", 20),
                    "The Cinder Matron pours slag over the party."),
    "torch_hulk": fx("head", sink("volcanic_stone", "lacquer_black", 40), "The Inquisitor torches the hulk: smoke over each foe."),
    "breach": fx("chest", heavy("spawn_wound", "glimmer_held", "deep_teal_shadow", "abyss_navy", 60), "The Breach: the wall gives under the Reach."),
    # Her bulk is ~2.9 m: the default 0.75 m ring closed inside her and never showed (M3-C05-06 sweep).
    "recrust": fx("feet", ring("volcanic_stone", "ember_orange", 60, 1.6), "The Cinder Matron's crust closes over her."),
    "flood_surge": fx("chest", spray("turquoise_shallow", "lagoon_teal", 60), "The Drownbell's flood surges over each foe."),
    "undertow_surge": fx("feet", sink("deep_teal_shadow", "abyss_navy", 40), "The Drownbell's undertow drags at each foe's feet."),
}

# The Act I bosses' set pieces (boss_vfx.json `bosses`, kind set_piece; BattleBossSetPiece plays them on the boss):
# `gather` each turn of a charge it gathers, `phases` on a phase change, `ko` when it falls. The Drownbell keeps its own
# rig (BattleBossVfx). Spawns release the dead they held when they fall: glimmer_lift rising (color_script rule 1).
BOSS_EFFECTS = {
    "boss_hullgnaw_coil": fx("chest", charge("spawn_wound", "deep_teal_shadow", 60), "Hullgnaw draws itself in: its wound-light gathers."),
    "boss_hullgnaw_breaking": fx("chest", shards("bone", "timber_weathered", 40) + slash("spawn_wound", "glimmer_held", 40),
                                 "Hullgnaw's ribs break: bone and timber fall, the wound-light leaks out sideways."),
    "boss_spawn_release": fx("chest", [layer("glimmer_lift", "glimmer_lift_hi", 80, 2.2, 0.4, (0.4, 1.0), 30, (0, 0.6, 0),
                                             (0.12, 0.24), radius=0.8, turb=0.4)],
                             "A spawn falls: the dead it held are let go, rising (released glimmer, color_script rule 1)."),
    "boss_wraith_lines": fx("chest", charge("sand_cloth", "cumulus_shadow", 50), "The Spar-Wraith's lines draw taut."),
    "boss_wraith_hauled": fx("chest", shards("timber_weathered", "sand_cloth", 40) + sink("gauze_white", "cumulus_shadow", 30),
                             "The Spar-Wraith is hauled down: spars fall, its shroud tears and settles."),
    "boss_matron_recrust": fx("chest", charge("volcanic_stone", "ember_orange", 50), "The Cinder Matron's crust re-forms."),
    "boss_matron_pour": fx("chest", column("ember_orange", "dusk_gold", 70) + rise("volcanic_stone", "storm_slate", 30),
                           "The Matron turns to pouring: the ladle runs molten, smoke climbs."),
    "boss_matron_fall": fx("chest", sink("ember_orange", "volcanic_stone", 60), "The Cinder Matron's fire banks for good: embers settle."),
    "boss_inquisitor_torch": fx("chest", column("oil_lamp", "ember_orange", 50) + rise("volcanic_stone", "lacquer_black", 40),
                                "The Inquisitor torches the hulk: flame and smoke at his side."),
    "boss_reach_gather": fx("chest", charge("spawn_wound", "abyss_navy", 70), "The Reach gathers itself against the wall."),
    "boss_reach_dark": fx("head", sink("storm_slate", "night_sky", 80), "The storm-dark comes down over the wall-head."),
    "boss_reach_breach": fx("chest", slash("spawn_wound", "glimmer_held", 70) + burst("abyss_navy", "deep_teal_shadow", 40, -1.0),
                            "The Breach: the Reach's crust parts and its wound-light floods out sideways."),
}
BOSS_ROWS = {
    "hullgnaw": {"gather": "boss_hullgnaw_coil", "phases": {"breaking": "boss_hullgnaw_breaking"}, "ko": "boss_spawn_release"},
    "spar_wraith": {"gather": "boss_wraith_lines", "phases": {"hauled_down": "boss_wraith_hauled"}, "ko": "boss_spawn_release"},
    "cinder_matron": {"gather": "boss_matron_recrust", "phases": {"pour": "boss_matron_pour"}, "ko": "boss_matron_fall"},
    "stillguard_inquisitor": {"phases": {"torch_the_hulk": "boss_inquisitor_torch"}},
    "undertows_reach": {"gather": "boss_reach_gather", "phases": {"dark": "boss_reach_dark", "breach": "boss_reach_breach"}},
}
BOSS_VFX = ROOT / "game/data/vfx/battle/boss_vfx.json"
BOSS_SOUNDS = {"boss_spawn_release": "ko_release", "boss_matron_fall": "ko_release"}

ITEMS = {
    "bitterleaf": fx("chest", rise("palm_green", "saltgrass", 24), "Bitterleaf: a clean green lift (cleanse)."),
    "brine_eyewash": fx("head", rise("salt_glass", "foam_white", 22), "Brine eyewash: clear water at the eyes (cleanse)."),
    "drag_net": fx("chest", [layer("sand_cloth", "timber_weathered", 30, 0.8, 0.9, (0.8, 1.6), 70, (0, -5.0, 0), (0.05, 0.1), radius=0.4)],
                   "The drag net thrown over a foe (delay)."),
    "quiet_tea": fx("chest", rise("reef_blue", "sky_horizon_noon", 24), "Quiet tea: calm blue rising (MP)."),
    "relighting_wick": fx("chest", [core("oil_lamp", "dusk_gold", 1.0, 0.4)] + rise("oil_lamp", "dusk_gold", 28),
                          "A relighting wick: a small oil flame lit again (revive; oil light, never glimmer)."),
    "smelling_salts": fx("head", burst("salt_glass", "foam_white", 18, 0.5), "Smelling salts (cleanse)."),
    "throat_honey": fx("chest", rise("gold_leaf", "sand_dry", 20), "Throat honey (cleanse)."),
    "tidewash_salve": fx("chest", rise("turquoise_shallow", "salt_glass", 24), "Tidewash salve (cleanse)."),
}

# M3-BPR-422: the Swell finishers of the Act I heroes whose techniques combat has not written yet (Kerrid M3-C05-06,
# Liss M3-C06-05). BattleVfx plays map.swell_by_hero[hero] for any of that hero's skills marked "swell" with no
# map.skills row, so they play the moment the technique lands. The motion is BattleChoreo's swing / reel styles.
SWELL_BY_HERO = {
    "kerrid": ("swell_weighted_swing", fx("knee", [layer("brass", "cold_blue_stone", 70, 0.55, 0.95, (3.0, 5.0), 22, (0, -3.0, 0),
                                                         (0.12, 0.26), (-1.0, 0.12, 0), 0.25, energy=1.4)]
                                       + heavy("sand_wet", "storm_slate", "sand_dry", "cumulus_shadow", 40),
                                       "Kerrid's Swell (the weighted swing): one flat, low sweep of iron across the "
                                       "foe at knee height, wet sand thrown out with it; never overhead, so it reads "
                                       "apart from Toma's blow.")),
    "liss": ("swell_reel_stop", fx("chest", ring("brass", "glimmer_bound", 36) + burst("salt_glass", "glimmer_bound", 50, -1.0),
                                   "Liss's Swell (the reel-stop): the gadget's parts lock (a brass ring closing) and "
                                   "it goes off on the foe in a salt-glass flash; its light is bound glimmer, steady.")),
}
SWELL_SOUNDS = {"swell_weighted_swing": "hit_none", "swell_reel_stop": "status_apply"}

# M3-BPR-424: the end-of-turn ticks (BattleEngine.turn_ended / turn_lost; BattleVfx.play_ticks), by cause in map.ticks:
# poison and regen each turn, a Doom count and Doom falling, a turn lost to Sleep or Stop. Regen is water rising (never
# glimmer); Doom sinks dark (never a release); a Zombie's regen hurts and plays the poison tick.
TICKS = {
    "poison": ("tick_poison", fx("chest", [layer("palm_green", "foliage_shadow", 30, 0.8, 0.55, (0.3, 0.8), 45, (0, 0.5, 0),
                                                 (0.1, 0.2), radius=0.3, turb=0.3, energy=1.4)],
                                 "Poison takes its turn's toll: sick green welling out of the fighter.")),
    "regen": ("tick_regen", fx("chest", rise("turquoise_shallow", "foam_white", 24, 0.9),
                               "Regen mends a little: shallow water lifting off (water, not glimmer).")),
    # The dark alone vanished on the night terrace (self-render): cold pale motes fall with it, so it reads on any arena.
    "doom_tick": ("tick_doom", fx("head", sink("night_sky", "abyss_navy", 20) + sink("moon_blue", "night_sky", 10),
                                  "A Doom count falls: a little dark settling.")),
    "doom": ("tick_doom_fall", fx("chest", sink("abyss_navy", "night_sky", 64, 0.5) + sink("moon_blue", "storm_slate", 26, 0.5),
                                  "Doom comes due: the dark comes down whole.")),
    "sleep": ("tick_sleep", fx("head", [layer("moon_blue", "starlight", 14, 1.4, 0.2, (0.1, 0.3), 30, (0, 0.25, 0),
                                              (0.08, 0.16), radius=0.25, turb=0.2, energy=1.3)],
                               "A turn lost to Sleep: slow pale motes drifting over the sleeper.")),
    "stop": ("tick_stop", fx("feet", ring("salt_glass", "cold_blue_stone", 48, 1.05),
                             "A turn lost to Stop: a still ring of salt-glass.")),
}
TICK_SOUNDS = {"tick_poison": "status_apply", "tick_regen": "heal", "tick_doom": "status_apply",
               "tick_doom_fall": "ko_release", "tick_sleep": "status_apply", "tick_stop": "status_apply"}


SFX = ROOT / "game/data/audio/battle_sfx.json"
SWELL = ROOT / "game/data/battle/swell.json"
# Low anchors on the body's near face (BattleVfx.anchor: only `feet` stays centred, for rings). A ground impact at a big
# body's feet spawned inside it: the Cinder Matron hid Kerrid's sweep and Anchor Fall (the finisher self-render).
ANCHOR_HEIGHTS = {"ground": 0.05, "knee": 0.25}


def _stand_in_sounds(data: dict, sfx: dict) -> None:
    """Every effect needs a sound row (audio's battle_sfx.json `vfx`, checked by validate_data). Until audio gives
    these effects their own (request M3-BPR-420), each new one borrows an existing row: a damage skill its element's
    hit, a heal or a stand-up the heal, anything else the status sound. A repeat within repeat_ms plays as a softer
    layer, so a borrowed hit under the element hit only thickens it. Audio's own rows are never changed."""
    skills = {r["id"]: r for r in json.loads((ROOT / "game/data/battle/skills.json").read_text())["skills"] if isinstance(r, dict)}
    elements = data["map"]["elements"]
    for table in ("skills", "items"):
        for sid, eid in data["map"][table].items():
            if eid in sfx["vfx"]:
                continue
            row = skills.get(sid, {})
            if table == "skills" and row.get("kind") in ("physical", "magical") and float(row.get("power", 0) or 0) > 0:
                borrowed = sfx["vfx"].get(elements.get(row.get("element", "none"), "hit_none"), "hit_none")
            elif row.get("kind") == "heal" or any(m in eid for m in ("mend", "ward", "stand", "hold", "climb")) or table == "items":
                borrowed = sfx["vfx"]["heal"]
            else:
                borrowed = sfx["vfx"]["status_apply"]
            sfx["vfx"][eid] = borrowed


# A Vowbound taking and leaving the field (BattleVfx plays these on BattleVowbound.called / departed). Bound light is
# steady: glimmer_bound, no drift; a fall is not a release, so nothing rises gold.
EVENTS = {
    # Sized for the Vowbound's real bodies (Ilun 5.1 x 3.2 m, Virel 2.4 x 3.6, Kahre 1.6 x 2.8; M3-BPR-424's self-render):
    # at a capsule's 0.75 m the ring hid under Ilun's middle and the rising motes bunched into a blob over its back.
    "vowbound_call": fx("feet", ring("glimmer_bound", "lagoon_teal", 90, 1.6) + rise("glimmer_bound", "salt_glass", 44, 1.4, 1.1),
                        "A Vowbound answers: a steady ring of bound light lifting around it."),
    "vowbound_dismiss": fx("chest", sink("glimmer_bound", "deep_teal_shadow", 56, 0.9), "A Vowbound leaves: its bound light settles."),
    "vowbound_fell": fx("chest", sink("glimmer_bound", "abyss_navy", 80, 0.9), "A Vowbound falls: its bound light sinks (not a release)."),
}
# Each event's sound: audio's own Vowbound rows (the same sounds its `events` fallbacks play).
EVENT_SOUNDS = {"vowbound_call": "vowbound_call", "vowbound_dismiss": "vowbound_dismiss", "vowbound_fell": "vowbound_fell"}


def main() -> int:
    text = EFFECTS.read_text()
    data = json.loads(text)
    sk = {s["id"] for s in json.loads((ROOT / "game/data/battle/skills.json").read_text())["skills"] if isinstance(s, dict)}
    it_raw = json.loads((ROOT / "game/data/items/items.json").read_text())["items"]
    it = {i["id"] for i in it_raw} if isinstance(it_raw, list) else set(it_raw)
    missing = sorted([s for s in SKILLS if s not in sk] + [i for i in ITEMS if i not in it])
    if missing:
        print("unknown ids:", missing)
        return 1
    for table, entries in (("skills", SKILLS), ("items", ITEMS)):
        for sid, eff in entries.items():
            mapped = data["map"][table].get(sid)
            if mapped is not None and data["effects"].get(mapped, {}).get("note") != eff["note"]:
                continue  # rendering's own mapping wins
            # Never overwrite one of rendering's effects (the Drownbell's aimed polyp_mend): ours takes a suffix.
            own = data["effects"].get(sid)
            eid = sid if own is None or own.get("note") == eff["note"] else sid + "_hit"
            data["effects"][eid] = eff
            data["map"][table][sid] = eid
    for eid, eff in EVENTS.items():
        data["effects"][eid] = eff
        data["map"]["events"][eid] = eid
    for eid, eff in BOSS_EFFECTS.items():
        data["effects"][eid] = eff
    data["map"]["ticks"] = {}
    for cause, (eid, eff) in TICKS.items():
        data["effects"][eid] = eff
        data["map"]["ticks"][cause] = eid
    data["map"]["swell_by_hero"] = {}
    swell_heroes = {h["id"]: h["techniques"] for h in json.loads(SWELL.read_text())["swell"]["heroes"]}
    for hero, (eid, eff) in SWELL_BY_HERO.items():
        data["effects"][eid] = eff
        data["map"]["swell_by_hero"][hero] = eid
        for tech in swell_heroes.get(hero, []):  # M3-C05-06 / M3-C06-05: the techniques now exist; map them by id
            data["map"]["skills"][tech] = eid
    data["anchor_heights"].update(ANCHOR_HEIGHTS)
    out = json.dumps(data, indent=2) + "\n"
    boss_text = BOSS_VFX.read_text()
    boss = json.loads(boss_text)
    for bid, row in BOSS_ROWS.items():
        boss["bosses"][bid] = dict({"kind": "set_piece", "_note": "M3-BPR-420/M3-HER-1148 (ADR 0041): "
                                    "BattleBossSetPiece plays gather (each turn of a charge), phases and ko on the boss; "
                                    "effects.json ids (tools/vfx/gen_act1_ability_vfx.py)."}, **row)
    boss_out = json.dumps(boss, indent=2) + "\n"
    sfx_text = SFX.read_text()
    sfx = json.loads(sfx_text)
    _stand_in_sounds(data, sfx)
    for eid, key in EVENT_SOUNDS.items():
        sfx["vfx"].setdefault(eid, sfx["events"][key])
    for eid in BOSS_EFFECTS:
        sfx["vfx"].setdefault(eid, sfx["vfx"][BOSS_SOUNDS.get(eid, "status_apply")])
    for eid, key in TICK_SOUNDS.items():
        sfx["vfx"].setdefault(eid, sfx["vfx"][key])
    for eid, key in SWELL_SOUNDS.items():
        sfx["vfx"].setdefault(eid, sfx["vfx"][key])
    sfx_out = json.dumps(sfx, indent=2) + "\n"
    if "--check" in sys.argv:
        return 0 if out == text and sfx_out == sfx_text and boss_out == boss_text else 1
    EFFECTS.write_text(out)
    SFX.write_text(sfx_out)
    BOSS_VFX.write_text(boss_out)
    print("effects.json: %d skills, %d items" % (len(SKILLS), len(ITEMS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
