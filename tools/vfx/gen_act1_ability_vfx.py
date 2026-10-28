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
Not mapped on purpose: skills whose target is the stair (`ward`: grip_the_stair, rope_dive, hand_closes). The ward is
an entry with no fighter, so an effect would play at the VFX node's origin. Their own motion is
BattleChoreo's push reaction on the climb.

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


def rise(a, b, n=36, life=1.1):  # slow upward motes (a blessing, a stance)
    return [layer(a, b, n, life, 0.3, (0.4, 0.9), 25, (0, 0.4, 0), (0.15, 0.3), radius=0.35, turb=0.3, energy=1.4)]


def sink(a, b, n=32):  # motes settling down over the target (a hex, a smother)
    return [layer(a, b, n, 1.0, 0.4, (0.2, 0.5), 30, (0, -1.4, 0), (0.16, 0.32), (0, -1, 0), 0.35, 0.2, energy=1.4)]


def ring(a, b, n=40):  # a ring lifting from the feet (a guard, a ward)
    return [layer(a, b, n, 0.9, 0.85, (0.05, 0.15), 5, (0, 0.5, 0), (0.16, 0.3), radius=0.75, energy=1.4)]


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
    "anchor_fall": fx("feet", heavy("cold_blue_stone", "bone", "sand_dry", "laterite", 60), "Kerrid: the anchor comes down: dust and stone."),
    "reel_shot": fx("chest", slash("brass", "foam_white", 26), "Liss: the line strikes home, brass bright."),
    "flash_housing": fx("head", [core("oil_lamp", "sun_noon", 1.4, 0.3)] + burst("oil_lamp", "dusk_gold", 30, 0.5),
                        "Liss: the lamp housing's flash in the foe's eyes (oil light; capped by particles, not a screen flash)."),
    "hoist_haul": fx("chest", rise("sand_cloth", "bone", 24, 0.8), "Liss (Ch8): the hoist hauls a group up."),
    # Swells (lamp_dive and shallows_verse are rendering's own).
    "return_tide": fx("feet", spray("turquoise_shallow", "foam_white", 70), "Toma's Swell: the tide thrown back out from the stair."),
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
    "oil_slap": fx("chest", spray("lacquer_black", "volcanic_stone", 30), "An oil slug slaps: black oil."),
    "sail_drop": fx("head", sink("gauze_white", "sand_cloth", 28), "A sail leech drops over the target."),
    "pounce": fx("chest", heavy("bone", "sand_wet", "sand_dry", "laterite", 34), "The hound pounces."),
    "brine_spit": fx("chest", spray("lagoon_teal", "foam_white", 40), "A crab spits brine."),
    "lure_glow": fx("head", [layer("sea_glow", "glimmer_held", 30, 0.8, 0.5, (0.2, 0.5), 60, (0, -0.4, 0), (0.1, 0.2), radius=0.4)],
                    "The lantern eel's lure: a cold glow."),
    "spark_spit": fx("chest", burst("starlight", "moon_blue", 30, -1.5), "A vein sparker spits sparks."),
    "glass_flare": fx("chest", burst("oil_lamp", "dusk_gold", 30, 0.8), "The hermit's bottle flares."),
    "brine_iron": fx("chest", burst("ember_orange", "salt_glass", 34, -1.0), "The Inquisitor's brine-iron: a salt burn."),
    "smother": fx("head", sink("lacquer_black", "volcanic_stone", 34), "An oil slug smothers."),
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
    "surge_ebb": fx("feet", sink("deep_teal_shadow", "sea_glow", 20), "The Surge ebbs."),
    "rouse_polyp": fx("chest", charge("glimmer_held", "spawn_wound", 30), "The Drownbell rouses a polyp."),
    "surge_crawler": fx("feet", spray("deep_teal_shadow", "sea_glow", 30), "The Surge throws up a crawler."),
    "surge_wing": fx("feet", spray("storm_slate", "sea_glow", 30), "The Surge throws up a squall wing."),
    "storm_call_sound": fx("head", charge("moon_blue", "storm_slate", 30), "Pell sounds the storm-call."),
    "storm_call": fx("chest", column("starlight", "moon_blue", 40), "Pell's storm-call strikes and drives a foe off."),
}

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


SFX = ROOT / "game/data/audio/battle_sfx.json"


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
    "vowbound_call": fx("feet", ring("glimmer_bound", "lagoon_teal", 60) + rise("glimmer_bound", "salt_glass", 30, 1.4),
                        "A Vowbound answers: a steady ring of bound light lifting around it."),
    "vowbound_dismiss": fx("chest", sink("glimmer_bound", "deep_teal_shadow", 40), "A Vowbound leaves: its bound light settles."),
    "vowbound_fell": fx("chest", sink("glimmer_bound", "abyss_navy", 60), "A Vowbound falls: its bound light sinks (not a release)."),
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
    out = json.dumps(data, indent=2) + "\n"
    sfx_text = SFX.read_text()
    sfx = json.loads(sfx_text)
    _stand_in_sounds(data, sfx)
    for eid, key in EVENT_SOUNDS.items():
        sfx["vfx"].setdefault(eid, sfx["events"][key])
    sfx_out = json.dumps(sfx, indent=2) + "\n"
    if "--check" in sys.argv:
        return 0 if out == text and sfx_out == sfx_text else 1
    EFFECTS.write_text(out)
    SFX.write_text(sfx_out)
    print("effects.json: %d skills, %d items" % (len(SKILLS), len(ITEMS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
