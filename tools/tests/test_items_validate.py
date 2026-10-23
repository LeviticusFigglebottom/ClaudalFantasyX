"""Item, equipment, ability, Customize and shop checks in tools/validate_data.py (M1-PRG-02).
Run: python3 -m unittest discover -s tools/tests"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

ITEMS = "game/data/items/items.json"
EQUIP = "game/data/items/equipment.json"
ABIL = "game/data/items/abilities.json"
CUST = "game/data/items/customize.json"
SHOPS = "game/data/items/shops.json"


class ItemsValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        for rel in ("game", "assets", "tools/banned_terms.txt", "docs/kb/glossary.md"):
            src, dst = ROOT / rel, self.tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".godot"))
            elif src.exists():
                shutil.copy(src, dst)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def load(self, rel: str) -> dict:
        return json.loads((self.tmp / rel).read_text(encoding="utf-8"))

    def save(self, rel: str, doc: dict) -> None:
        (self.tmp / rel).write_text(json.dumps(doc), encoding="utf-8")

    def row(self, doc: dict, table: str, rid: str) -> dict:
        return next(r for r in doc[table] if r["id"] == rid)

    def edit(self, rel: str, table: str, rid: str, **changes: object) -> None:
        doc = self.load(rel)
        self.row(doc, table, rid).update(changes)
        self.save(rel, doc)

    def assert_error(self, needle: str) -> None:
        errs = vd.run(self.tmp).errors
        self.assertTrue(any(needle in e for e in errs), f"no error containing {needle!r} in {errs}")

    # -- the repo itself ------------------------------------------------------------------------

    def test_repo_items_are_clean(self) -> None:
        self.assertEqual(vd.run(self.tmp).errors, [])

    def test_repo_items_reach_the_loc_check(self) -> None:
        files = vd.load_json_files(self.tmp, vd.Report())
        keys = vd.check_items(files, vd.declared_flags_quiet(self.tmp), vd.Report())
        self.assertIn("ITEM_SALT_TONIC", keys)
        self.assertIn("ABILITY_FULL_NET_DESC", keys)
        self.assertIn("SHOP_HALUNA_MARKET", keys)

    # -- items.json -----------------------------------------------------------------------------

    def test_price_must_be_positive(self) -> None:
        self.edit(ITEMS, "items", "salt_tonic", price=0)
        self.assert_error("item 'salt_tonic': price must be a positive int")

    def test_key_items_have_no_price(self) -> None:
        self.edit(ITEMS, "items", "brass_lantern", price=50)
        self.assert_error("key items have no 'price'")

    def test_unknown_category(self) -> None:
        self.edit(ITEMS, "items", "salt_tonic", category="snack")
        self.assert_error("item 'salt_tonic': category must be one of")

    def test_facet_item_must_match_facets_json(self) -> None:
        self.edit(ITEMS, "items", "facet_power", facet="facet_muscle")
        self.assert_error("a facet item needs 'facet' equal to its id")

    def test_every_facet_needs_an_item_row(self) -> None:
        doc = self.load(ITEMS)
        doc["items"] = [r for r in doc["items"] if r["id"] != "facet_key_4"]
        self.save(ITEMS, doc)
        self.assert_error("Facet 'facet_key_4'")

    def test_battle_effect_schema(self) -> None:
        self.edit(ITEMS, "items", "salt_tonic", battle={"target": "single_ally", "rank": 2,
                                                       "effects": [{"type": "teleport"}]})
        self.assert_error("effect type must be one of")
        self.edit(ITEMS, "items", "salt_tonic", battle={"target": "everyone", "rank": 0,
                                                       "effects": [{"type": "heal_hp", "amount": -3}]})
        self.assert_error("battle.target must be one of")
        self.assert_error("battle.rank must be an int in 1..8")
        self.assert_error("heal_hp.amount must be a positive int")

    def test_battle_effect_unknown_status(self) -> None:
        self.edit(ITEMS, "items", "bitterleaf", battle={"target": "single_ally", "rank": 2,
                                                       "effects": [{"type": "cure", "statuses": ["hiccups"]}]})
        self.assert_error("unknown status 'hiccups'")

    def test_only_consumables_in_battle(self) -> None:
        self.edit(ITEMS, "items", "ember_coral", battle={"target": "single_foe", "rank": 2,
                                                        "effects": [{"type": "delay", "ranks": 1}]})
        self.assert_error("only consumables can be used in battle")

    # -- abilities.json -------------------------------------------------------------------------

    def test_ability_effect_fields(self) -> None:
        self.edit(ABIL, "abilities", "ember_edge", effect={"element": "plasma"})
        self.assert_error("'ember_edge': unknown element 'plasma'")
        self.edit(ABIL, "abilities", "ember_edge", effect={})
        self.assert_error("on_hit_element effect needs 'element'")

    def test_status_strike_needs_a_harmful_status(self) -> None:
        self.edit(ABIL, "abilities", "bitter_edge", effect={"status": "haste", "chance": 30, "duration": 3})
        self.assert_error("status_strike needs a harmful status, not 'haste'")

    def test_auto_status_needs_a_beneficial_status(self) -> None:
        self.edit(ABIL, "abilities", "standing_guard", effect={"status": "poison", "trigger": "always"})
        self.assert_error("auto_status needs a beneficial status")

    def test_low_hp_trigger_needs_threshold(self) -> None:
        self.edit(ABIL, "abilities", "low_tide_haste", effect={"status": "haste", "trigger": "low_hp"})
        self.assert_error("low_hp trigger needs hp_below_pct")

    def test_sleep_strike_may_not_be_permanent(self) -> None:
        self.edit(ABIL, "abilities", "drowse_edge", effect={"status": "sleep", "chance": 20, "duration": -1})
        self.assert_error("'sleep' may not be permanent")

    # -- equipment.json -------------------------------------------------------------------------

    def test_dangling_ability_in_equipment(self) -> None:
        self.edit(EQUIP, "equipment", "rhen_coral_hooks", abilities=["firestorm"])
        self.assert_error("'rhen_coral_hooks': unknown ability 'firestorm'")

    def test_slot_count_at_most_four(self) -> None:
        self.edit(EQUIP, "equipment", "rhen_coral_hooks", slots=5)
        self.assert_error("'rhen_coral_hooks': slots must be an int in 0..4")
        doc = self.load(EQUIP)
        doc["rules"]["max_slots"] = 6
        self.save(EQUIP, doc)
        self.assert_error("rules.max_slots must be an int in 1..4")

    def test_prefilled_abilities_fit_slots(self) -> None:
        self.edit(EQUIP, "equipment", "rhen_salvage_hooks", abilities=["ember_edge", "tide_edge"])
        self.assert_error("2 pre-filled abilities but only 1 slots")

    def test_ability_must_fit_the_piece(self) -> None:
        self.edit(EQUIP, "equipment", "rhen_coral_hooks", abilities=["ember_guard"])
        self.assert_error("ability 'ember_guard' does not fit a weapon piece")

    def test_equipment_price_positive(self) -> None:
        self.edit(EQUIP, "equipment", "toma_boarding_spear", price=-10)
        self.assert_error("'toma_boarding_spear': price must be a positive int")

    def test_unknown_character_in_gear_type(self) -> None:
        self.edit(EQUIP, "gear_types", "reef_hooks", character="tobin")
        self.assert_error("gear type 'reef_hooks': unknown character 'tobin'")

    def test_starting_gear_must_match_character(self) -> None:
        doc = self.load(EQUIP)
        doc["starting"]["rhen"]["weapon"] = "asha_vigil_staff"
        self.save(EQUIP, doc)
        self.assert_error("starting.rhen.weapon: 'asha_vigil_staff' is a asha weapon piece")

    def test_every_character_needs_starting_gear(self) -> None:
        doc = self.load(EQUIP)
        del doc["starting"]["ysolde"]
        self.save(EQUIP, doc)
        self.assert_error("character 'ysolde' has no starting gear")

    def test_equipment_id_must_not_clash_with_items(self) -> None:
        doc = self.load(EQUIP)
        self.row(doc, "equipment", "rhen_salvage_hooks")["id"] = "salt_tonic"
        self.save(EQUIP, doc)
        self.assert_error("id clashes with an item id")

    # -- customize.json -------------------------------------------------------------------------

    def test_recipe_dangling_refs(self) -> None:
        doc = self.load(CUST)
        doc["recipes"][0]["items"][0]["item"] = "dragon_tooth"
        doc["recipes"][1]["ability"] = "moonbeam"
        self.save(CUST, doc)
        self.assert_error("unknown item 'dragon_tooth'")
        self.assert_error("unknown ability 'moonbeam'")

    def test_recipe_cannot_spend_key_items_or_zero(self) -> None:
        doc = self.load(CUST)
        doc["recipes"][0]["items"] = [{"item": "brass_lantern", "count": 0}]
        self.save(CUST, doc)
        self.assert_error("key item 'brass_lantern' can't be spent")
        self.assert_error("count for 'brass_lantern' must be a positive int")

    def test_recipe_once_per_ability(self) -> None:
        doc = self.load(CUST)
        doc["recipes"].append(dict(doc["recipes"][0]))
        self.save(CUST, doc)
        self.assert_error("second recipe for 'ember_edge'")

    # -- shops.json -----------------------------------------------------------------------------

    def test_shop_unknown_stock(self) -> None:
        doc = self.load(SHOPS)
        doc["shops"][0]["stock"].append({"item": "moon_cheese"})
        doc["shops"][1]["stock"].append({"item": "salt_tonic"})
        self.save(SHOPS, doc)
        self.assert_error("unknown item 'moon_cheese' in stock")
        self.assert_error("unknown equipment 'salt_tonic' in stock")

    def test_shop_flags_must_be_declared(self) -> None:
        doc = self.load(SHOPS)
        doc["shops"][0]["requires_flag"] = "ch99_never_declared"
        doc["shops"][0]["stock"][0]["requires_flag"] = "ch98_nor_this"
        self.save(SHOPS, doc)
        self.assert_error("undeclared story flag 'ch99_never_declared'")
        self.assert_error("undeclared story flag 'ch98_nor_this'")

    def test_shop_cannot_sell_key_items(self) -> None:
        doc = self.load(SHOPS)
        doc["shops"][0]["stock"].append({"item": "net_float_charm"})
        self.save(SHOPS, doc)
        self.assert_error("key item 'net_float_charm' can't be sold")

    def test_sell_ratio_never_profits(self) -> None:
        doc = self.load(SHOPS)
        doc["rules"]["sell_ratio_num"] = 3
        self.save(SHOPS, doc)
        self.assert_error("sell ratio must be ints")

    # -- loc ------------------------------------------------------------------------------------

    def test_missing_loc_key(self) -> None:
        self.edit(ABIL, "abilities", "full_net", name_key="ABILITY_NOT_IN_CSV")
        self.assert_error("missing localization key 'ABILITY_NOT_IN_CSV'")

    # -- pure entry point -----------------------------------------------------------------------

    def test_items_errors_is_pure(self) -> None:
        refs = {k: set() for k in ("characters", "statuses", "harmful", "beneficial", "facets", "flags")}
        errs = vd.items_errors({}, refs)
        self.assertTrue(any("missing 'rules' object" in e for e in errs))
        self.assertTrue(any("missing top-level list 'recipes'" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
