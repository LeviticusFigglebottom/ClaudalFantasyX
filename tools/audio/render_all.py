#!/usr/bin/env python3
"""Regenerate every synthesized audio asset, deterministically.

    python3 tools/audio/render_all.py                 # render + verify
    python3 tools/audio/render_all.py --determinism   # also render a second copy to a temp
                                                      # dir and compare SHA-256 byte-for-byte
    python3 tools/audio/render_all.py --only battle   # just the jobs whose source path matches

All randomness uses fixed seeds; Vorbis is encoded with ffmpeg's bit-exact
flags, so the same numpy + ffmpeg/libvorbis versions give identical bytes.
After rendering, each .ogg is decoded back and its loudness re-measured, so
the numbers printed are for the shipped files, not the float mix.

Looping cues ("music_loop") also write a sidecar <name>.loop.json and carry
LOOPSTART / LOOPLENGTH Vorbis comments (in samples). Verification decodes
each loop and checks its exact length, the tags, and the continuity of the
wrap seam, and copies the loop settings into the Godot .import file if one
exists (re-run `godot --headless --path . --import` afterwards).
Requires: python3, numpy, ffmpeg with libvorbis (ffprobe for the tag check).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.analysis import loop_seam_report  # noqa: E402
from synth.loudness import integrated_lufs, momentary_max_lufs, self_test, true_peak_dbtp  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

SIZE_BUDGET = 16 * 1024 * 1024       # all shipped audio for the M2 slice (mix.md §5)
NEW_AUDIO_BUDGET = 4 * 1024 * 1024   # the three M1-AUD-02 cues together
M1_AUD_02 = ("hush_theme_v2", "battle_standard.", "temple_trial")
# M2-AUD-03's cues, held to the music targets (-16 +- 0.5 LUFS, true peak <= -1 dBTP). drownbell_p1 is one stem of a
# stack measured whole by its source (the full stack is -16; stem 1 alone is quieter by design, mix.md §2).
M2_CUES = ("haluna_village", "haluna_night", "battle_standard_v2", "hush_first_verse", "hush_coda", "haluna_dawn",
           "shell_shrine_interior", "ilun_summon", "saltgrass_causeway", "lamp_diver", "sefir_theme", "the_ebbing", "the_ebbing_release",
           "tidecup_match", "terraces_of_ash", "corrow_seawall", "hullgnaw", "spar_wraith", "oruvel", "pilgrims_wake",
           "tamsule", "iskarra_vigil", "brightwater_ferry", "brine_shoals", "ashcrown", "coilspire",
           "tamsule_bell_galleries", "stillguard_inquisitor", "ossa_fen", "reedhollow", "sunken_vey", "lowlight",
           "keth_pass", "quellan",
           "ansedra", "lamp_archive", "peace_wedding", "unlamped", "pale_rim", "drowned_choir")
# M3-AUD-820: the Ch4 and Ch7 scene cues
M2_CUES += ("hearer_hum", "ysolde_theme", "name_board_home", "the_long_way_round", "oruvel_theme", "tavi_kell")
M2_CUES += ("tidecup_after", "tidecup_crowd", "virel_bound", "virel_summon", "corrow_aftermath")  # M3-AUD-822
M2_CUES += ("rhen_current_hum", "going_under", "corrow_night", "dawn_road")  # M3-AUD-819
M2_CUES += ("lanternfall", "hush_second_verse", "kerrid_stair", "kahre_summon", "liss_theme", "raid",
             "shoals_dusk")  # M3-AUD-821
AMBIENCE_BUDGET = int(2.5 * 1024 * 1024)  # the M2-AUD-05 field beds together
# Per-job budgets for later "ambience_loop" jobs (each job's beds together; the M2-AUD-05 job keeps AMBIENCE_BUDGET).
AMBIENCE_JOB_BUDGETS = {"assets_src/sfx/causeway_ambience.py": int(1.2 * 1024 * 1024),
                        "assets_src/sfx/act1_ambience.py": int(3.0 * 1024 * 1024),  # M2-AUD-13: two q1 beds; M3-AUD-16: six
                        "assets_src/sfx/prologue_ambience.py": int(0.6 * 1024 * 1024),  # M3-AUD-817: one q1 bed
                        "assets_src/sfx/act1_walla_ambience.py": int(1.2 * 1024 * 1024)}  # M3-AUD-864: two q1 layers
AMBIENCE_LUFS, AMBIENCE_MAX_TP = -26.0, -5.0  # mix.md §2: ambience loops at -26 LUFS, rendered at <= -6 dBFS


def _source_files(path: str) -> list[str]:
    """A source's own FILES list (M3-AUD-14: 194 creature files named from its table, not copied here)."""
    spec = importlib.util.spec_from_file_location("files_of_" + os.path.basename(path)[:-3], os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.FILES)


# (module source, output dir, output file names, kind)
JOBS = [
    ("assets_src/music/hush_theme_sketch.py", "assets/audio/music", ["hush_theme_sketch.ogg"], "music"),
    ("assets_src/sfx/ui_sfx.py", "assets/audio/sfx",
     ["ui_cursor.ogg", "ui_confirm.ogg", "ui_cancel.ogg", "text_blip.ogg"], "sfx"),
    ("assets_src/music/hush_theme_v2.py", "assets/audio/music", ["hush_theme_v2.ogg"], "music"),
    ("assets_src/music/battle_standard.py", "assets/audio/music",
     ["battle_standard.ogg", "battle_standard.loop.json"], "music_loop"),
    ("assets_src/music/temple_trial.py", "assets/audio/music",
     ["temple_trial.ogg", "temple_trial.loop.json"], "music_loop"),
    ("assets_src/music/shell_shrine_interior.py", "assets/audio/music",
     ["shell_shrine_interior.ogg", "shell_shrine_interior.loop.json"], "music_loop"),
    ("assets_src/sfx/shrine_sfx.py", "assets/audio/sfx/shrine",
     ["shrine_stone_turn_1.ogg", "shrine_stone_turn_2.ogg", "shrine_stone_turn_3.ogg", "shrine_pour.ogg",
      "shrine_spill.ogg", "shrine_drain.ogg", "shrine_side_drain.ogg", "shrine_door.ogg", "shrine_charm.ogg"], "sfx"),
    ("assets_src/sfx/shrine_pool_fill.py", "assets/audio/sfx/shrine",
     ["shrine_pool_fill.ogg", "shrine_pool_fill.loop.json"], "music_loop"),
    ("assets_src/sfx/battle_sfx.py", "assets/audio/sfx",
     ["battle/hit_none_1.ogg", "battle/hit_none_2.ogg", "battle/hit_none_3.ogg", "battle/hit_fire_1.ogg",
      "battle/hit_fire_2.ogg", "battle/hit_fire_3.ogg", "battle/hit_ice_1.ogg", "battle/hit_ice_2.ogg",
      "battle/hit_ice_3.ogg", "battle/hit_lightning_1.ogg", "battle/hit_lightning_2.ogg",
      "battle/hit_lightning_3.ogg", "battle/hit_water_1.ogg", "battle/hit_water_2.ogg", "battle/hit_water_3.ogg",
      "battle/hit_holy_1.ogg", "battle/hit_holy_2.ogg", "battle/lamp_dive.ogg", "battle/shallows_verse.ogg",
      "battle/read.ogg", "battle/heal.ogg", "battle/status_apply.ogg", "battle/ko_release.ogg",
      "battle/bell_release.ogg", "battle/stinger_ambush.ogg", "battle/stinger_ambush_soft.ogg",
      "battle/stinger_preemptive.ogg", "battle/drownbell_toll.ogg", "battle/drownbell_toll_soft.ogg",
      "battle/toll_gather.ogg", "battle/rim_crack_1.ogg", "battle/rim_crack_2.ogg", "battle/rim_crack_3.ogg",
      "battle/rim_break.ogg", "battle/polyp_rise.ogg", "battle/polyp_mend.ogg", "battle/floodnet.ogg",
      "battle/flood.ogg", "battle/flood_soft.ogg", "battle/vowbound_call.ogg", "battle/vowbound_dismiss.ogg",
      "battle/victory.ogg", "battle/defeat.ogg", "battle/escape.ogg", "drownbell_toll.ogg"], "sfx"),
    ("assets_src/music/haluna_village.py", "assets/audio/music",
     ["haluna_village.ogg", "haluna_village.loop.json"], "music_loop"),
    ("assets_src/music/haluna_night.py", "assets/audio/music",
     ["haluna_night.ogg", "haluna_night.loop.json"], "music_loop"),
    ("assets_src/music/battle_standard_v2.py", "assets/audio/music",
     ["battle_standard_v2.ogg", "battle_standard_v2.loop.json"], "music_loop"),
    ("assets_src/music/drownbell.py", "assets/audio/music",
     ["drownbell_p1.ogg", "drownbell_p1.loop.json", "drownbell_p2.ogg", "drownbell_p2.loop.json"], "music_loop"),
    ("assets_src/music/hush_first_verse.py", "assets/audio/music", ["hush_first_verse.ogg"], "music"),
    ("assets_src/music/hush_coda.py", "assets/audio/music", ["hush_coda.ogg"], "music"),
    ("assets_src/music/haluna_dawn.py", "assets/audio/music", ["haluna_dawn.ogg"], "music"),
    ("assets_src/music/ilun_summon.py", "assets/audio/sfx", ["ilun_summon.ogg"], "music"),
    ("assets_src/music/saltgrass_causeway.py", "assets/audio/music",
     ["saltgrass_causeway.ogg", "saltgrass_causeway.loop.json"], "music_loop"),
    ("assets_src/music/lamp_diver.py", "assets/audio/music", ["lamp_diver.ogg", "lamp_diver.loop.json"], "music_loop"),
    ("assets_src/music/sefir_theme.py", "assets/audio/music", ["sefir_theme.ogg", "sefir_theme.loop.json"], "music_loop"),
    ("assets_src/music/the_ebbing.py", "assets/audio/music", ["the_ebbing.ogg", "the_ebbing_release.ogg"], "music"),
    ("assets_src/sfx/act1_ambience.py", "assets/audio/ambience",
     [f"{b}{ext}" for b in ("tamsule_port", "tamsule_bell", "brine_shoals", "pemakar_terraces", "ashcrown",
                           "corrow_seawall") for ext in (".ogg", ".loop.json")], "ambience_loop"),
    ("assets_src/sfx/field_ambience.py", "assets/audio/ambience",
     [f"{b}{ext}" for b in ("haluna_day", "haluna_night", "surf", "dock", "shrine_interior", "wind")
      for ext in (".ogg", ".loop.json")], "ambience_loop"),
    ("assets_src/sfx/field_sfx.py", "assets/audio/sfx",
     [f"step_{s}_{v:02d}.ogg" for s in ("sand", "stone", "wood") for v in range(1, 6)]
     + [f"{u}.ogg" for u in ("ui_menu_open", "ui_menu_close", "ui_page", "ui_buy", "ui_inn_rest", "ui_error",
                             "ui_vowbound_open")], "sfx"),
    ("assets_src/sfx/voice_blips.py", "assets/audio/sfx/voice",
     [f"blip_{t}_{v}.ogg" for t in ("soft", "bright", "low", "breathy", "child") for v in (1, 2, 3)], "sfx"),
    # M3-AUD-06. "sfx_set": one-shots and loops together; a file with a .loop.json in the list is checked as a loop.
    ("assets_src/sfx/underwater_sfx.py", "assets/audio",
     [f"ambience/{b}{ext}" for b in ("underwater_deep", "drowned_tower") for ext in (".ogg", ".loop.json")]
     + [f"sfx/dive/{s}.ogg" for s in ("dive_entry", "dive_surface", "dive_bubble_burst", "dive_stroke_1",
                                      "dive_stroke_2", "dive_stroke_3", "dive_stroke_4")]
     + ["sfx/dive/dive_lantern_hum.ogg", "sfx/dive/dive_lantern_hum.loop.json"], "sfx_set"),
    ("assets_src/sfx/reefball_sfx.py", "assets/audio/sfx/reefball",
     [f"ball_{k}_{v}.ogg" for k, n in (("kick", 3), ("push", 2), ("catch", 2), ("shot", 2)) for v in range(1, n + 1)]
     + ["ball_score.ogg", "sphere_enter.ogg", "sphere_exit.ogg", "sphere_swim_1.ogg", "sphere_swim_2.ogg",
        "sphere_swim_3.ogg", "crowd_cheer_1.ogg", "crowd_cheer_2.ogg", "crowd_groan.ogg", "crowd_gasp.ogg",
        "whistle_start.ogg", "whistle_short.ogg", "whistle_end.ogg", "naming_rite.ogg", "float_ring_bell.ogg"]
     + [f"crowd_{b}{ext}" for b in ("murmur", "excited") for ext in (".ogg", ".loop.json")], "sfx_set"),
    ("assets_src/music/tidecup_match.py", "assets/audio/music",
     ["tidecup_match.ogg", "tidecup_match.loop.json"], "music_loop"),
    ("assets_src/music/terraces_of_ash.py", "assets/audio/music",
     ["terraces_of_ash.ogg", "terraces_of_ash.loop.json"], "music_loop"),
    ("assets_src/music/corrow_seawall.py", "assets/audio/music",
     ["corrow_seawall.ogg", "corrow_seawall.loop.json"], "music_loop"),
    ("assets_src/music/hullgnaw.py", "assets/audio/music", ["hullgnaw.ogg", "hullgnaw.loop.json"], "music_loop"),
    ("assets_src/music/spar_wraith.py", "assets/audio/music",
     ["spar_wraith.ogg", "spar_wraith.loop.json"], "music_loop"),
    # M3-AUD-09: boss stems (like the Drownbell's, each stem alone is quieter; the stack is checked by
    # tools/tests/test_audio_loudness.py)
    ("assets_src/music/cinder_matron.py", "assets/audio/music",
     [f"cinder_matron_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/undertows_reach.py", "assets/audio/music",
     [f"undertows_reach_p{i}{ext}" for i in (1, 2, 3) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/sfx/causeway_ambience.py", "assets/audio/ambience",
     [f"{b}{ext}" for b in ("causeway_wind", "tidepools") for ext in (".ogg", ".loop.json")], "ambience_loop"),
    ("assets_src/music/oruvel.py", "assets/audio/music", ["oruvel.ogg", "oruvel.loop.json"], "music_loop"),
    ("assets_src/music/pilgrims_wake.py", "assets/audio/music",
     ["pilgrims_wake.ogg", "pilgrims_wake.loop.json"], "music_loop"),
    ("assets_src/music/tamsule.py", "assets/audio/music", ["tamsule.ogg", "tamsule.loop.json"], "music_loop"),
    ("assets_src/music/iskarra_vigil.py", "assets/audio/music", ["iskarra_vigil.ogg"], "music"),
    ("assets_src/music/brightwater_ferry.py", "assets/audio/music",
     ["brightwater_ferry.ogg", "brightwater_ferry.loop.json"], "music_loop"),
    ("assets_src/music/brine_shoals.py", "assets/audio/music",
     ["brine_shoals.ogg", "brine_shoals.loop.json"], "music_loop"),
    # M3-AUD-15: the M3 menus' UI sounds (Lattice, Equip, map, tips, title)
    ("assets_src/sfx/menu_sfx.py", "assets/audio/sfx",
     [f"{u}.ogg" for u in ("ui_lattice_node", "ui_lattice_unlock", "ui_lattice_step", "ui_equip", "ui_unequip",
                           "ui_map_open", "ui_map_close", "ui_map_tick", "ui_map_marker", "ui_tip",
                           "ui_title_confirm", "ui_title_swell")], "sfx"),
    # M3-AUD-13: the battle choreography's whooshes, weapon accents, footfalls, KO, Swell, toll, flood, Vowbound
    ("assets_src/sfx/choreo_sfx.py", "assets/audio/sfx",
     [f"choreo/{k}_{v}.ogg" for k, c in (("whoosh_melee", 3), ("whoosh_heavy", 2), ("whoosh_cast", 2),
                                          ("whoosh_throw", 2), ("whoosh_guard", 2), ("accent_hooks", 3),
                                          ("accent_staff", 2), ("accent_spear", 3), ("accent_shield", 2),
                                          ("accent_book", 2), ("accent_focus", 2), ("accent_cleaver", 2),
                                          ("accent_claw", 3), ("accent_teeth", 2), ("accent_bell_hood", 2),
                                          ("accent_guard", 2), ("step_sand", 4), ("ko_collapse", 2))
      for v in range(1, c + 1)]
     + [f"choreo/{s}.ogg" for s in ("swell_rhen", "swell_asha", "swell_toma", "swell_ysolde", "toll_wave",
                                    "flood_surge")]
     + ["choreo/flood_brace_1.ogg", "choreo/flood_brace_2.ogg"]
     + [f"choreo/{s}.ogg" for s in ("vowbound_beckon", "vowbound_rise", "vowbound_rise_long", "vowbound_sink",
                                    "vowbound_fall")], "sfx"),
    # M3-AUD-18: stings on the battle presentation's announcements (the tide line, the bark, boss intros)
    ("assets_src/sfx/battle_stings.py", "assets/audio/sfx",
     [f"battle/sting_{s}.ogg" for s in ("tideline", "bark", "boss", "boss_soft", "boss_bell", "boss_bell_soft")],
     "sfx"),
    # M3-AUD-14: creature voices and movement (the file list is the source's own, like battle_sfx's)
    ("assets_src/sfx/creature_sfx.py", "assets/audio/sfx/creatures", _source_files("assets_src/sfx/creature_sfx.py"),
     "sfx"),
    # M3-AUD-831: the Act II creatures (the Ch10-12 bosses, the Wakefin, the Ch10-11 regulars), into the same folder
    ("assets_src/sfx/act2_creature_sfx.py", "assets/audio/sfx/creatures",
     _source_files("assets_src/sfx/act2_creature_sfx.py"), "sfx"),
    # M2-AUD-14: the menus track's pages (Items, Formation, Customize, the zone map's pan)
    ("assets_src/sfx/menu_page_sfx.py", "assets/audio/sfx",
     [f"{u}.ogg" for u in ("ui_item_use", "ui_item_sort", "ui_formation_pick", "ui_formation_swap",
                           "ui_customize_open", "ui_craft", "ui_map_pan")], "sfx"),
    # M3-AUD-838: the `charge` choreography style (the Avalanche Ram's run, M3-BPR-410)
    ("assets_src/sfx/charge_sfx.py", "assets/audio/sfx/choreo", _source_files("assets_src/sfx/charge_sfx.py"), "sfx"),
    # M3-AUD-846: Ilun the Vowbound's voice and his layers on the summon (creatures and choreo folders)
    ("assets_src/sfx/vowbound_sfx.py", "assets/audio/sfx", _source_files("assets_src/sfx/vowbound_sfx.py"), "sfx"),
    # M3-AUD-861 (ADR 0173): Act I's last borrowed and silent foes, in Git LFS
    ("assets_src/sfx/act1_final_creature_sfx.py", "assets/lfs/audio/sfx/creatures",
     _source_files("assets_src/sfx/act1_final_creature_sfx.py"), "sfx"),
    ("assets_src/sfx/act1_skill_sfx.py", "assets/lfs/audio/sfx/battle", _source_files("assets_src/sfx/act1_skill_sfx.py"),
     "sfx"),
    ("assets_src/sfx/act1_boss_stings.py", "assets/lfs/audio/sfx/battle",
     _source_files("assets_src/sfx/act1_boss_stings.py"), "sfx"),
    ("assets_src/sfx/act1_ability_sfx.py", "assets/lfs/audio/sfx", _source_files("assets_src/sfx/act1_ability_sfx.py"),
     "sfx"),
    ("assets_src/sfx/act1_final_ambience.py", "assets/lfs/audio/ambience",
     _source_files("assets_src/sfx/act1_final_ambience.py"), "sfx_set"),
    # M3-AUD-864: Act I's cutscene clips that still played nothing (CutsceneAudio, cutscene_foley.json `anim`)
    ("assets_src/sfx/act1_cutscene_foley.py", "assets/audio/sfx/cutscene",
     _source_files("assets_src/sfx/act1_cutscene_foley.py"), "sfx"),
    ("assets_src/sfx/act1_swell_finisher_sfx.py", "assets/audio/sfx/battle",
     _source_files("assets_src/sfx/act1_swell_finisher_sfx.py"), "sfx"),
    # M4-A2P-093 (ADR 0175): Act II's ambience beds, plain git under assets/audio/act2/
    ("assets_src/sfx/act2_ambience.py", "assets/audio/act2/ambience", _source_files("assets_src/sfx/act2_ambience.py"),
     "sfx_set"),
    ("assets_src/sfx/act2_hero_foley.py", "assets/audio/act2/sfx/foley", _source_files("assets_src/sfx/act2_hero_foley.py"),
     "sfx"),
    ("assets_src/sfx/act2_variant_creature_sfx.py", "assets/audio/act2/sfx/creatures",
     _source_files("assets_src/sfx/act2_variant_creature_sfx.py"), "sfx"),
    ("assets_src/sfx/act2_skill_sfx.py", "assets/audio/act2/sfx/battle", _source_files("assets_src/sfx/act2_skill_sfx.py"),
     "sfx"),
    ("assets_src/sfx/act2_boss_stings.py", "assets/audio/act2/sfx/battle",
     _source_files("assets_src/sfx/act2_boss_stings.py"), "sfx"),
    ("assets_src/sfx/act2_ability_sfx.py", "assets/audio/act2/sfx/battle",
     _source_files("assets_src/sfx/act2_ability_sfx.py"), "sfx"),
    ("assets_src/sfx/act2_cutscene_sfx.py", "assets/audio/sfx",
     _source_files("assets_src/sfx/act2_cutscene_sfx.py"), "sfx"),
    ("assets_src/sfx/act2_ui_sfx.py", "assets/audio/sfx", _source_files("assets_src/sfx/act2_ui_sfx.py"), "sfx"),
    ("assets_src/sfx/act1_foley_detail_sfx.py", "assets/audio/sfx", _source_files("assets_src/sfx/act1_foley_detail_sfx.py"),
     "sfx"),
    ("assets_src/sfx/act1_struck_sfx.py", "assets/audio/sfx/choreo", _source_files("assets_src/sfx/act1_struck_sfx.py"), "sfx"),
    ("assets_src/sfx/act1_walla_ambience.py", "assets/audio/ambience",
     [f"{b}{ext}" for b in ("corrow_town", "haluna_mourners") for ext in (".ogg", ".loop.json")], "ambience_loop"),
    # M4-A2P-090 (ADR 0175): Act II scene cues, plain git under assets/audio/act2/music/
    ("assets_src/music/act2/farewell_tide.py", "assets/audio/act2/music",
     ["farewell_tide.ogg", "farewell_tide.loop.json", "farewell_tide_release.ogg"], "music_loop"),  # M4-CIN-1301
    ("assets_src/music/act2/peace_wedding_break.py", "assets/audio/act2/music", ["peace_wedding_break.ogg"], "music"),
    ("assets_src/music/act2/lagoon_escape.py", "assets/audio/act2/music", ["lagoon_escape.ogg"], "music"),
    ("assets_src/music/act2/kerrid_at_sea.py", "assets/audio/act2/music", ["kerrid_at_sea.ogg"], "music"),
    ("assets_src/music/act2/hollowmere_answers.py", "assets/audio/act2/music", ["hollowmere_answers.ogg"], "music"),
    ("assets_src/music/act2/sefir_go_home.py", "assets/audio/act2/music", ["sefir_go_home.ogg"], "music"),
    ("assets_src/music/act2/act2_break.py", "assets/audio/act2/music", ["act2_break.ogg"], "music"),
    ("assets_src/music/act2/kesh_memory.py", "assets/audio/act2/music", ["kesh_memory.ogg"], "music"),
    # M5-A3P-1950 (ADR 0208): Act III's score, plain git under assets/audio/act3/music/ (the Unbinding themes)
    ("assets_src/music/act3/the_letting.py", "assets/audio/act3/music",
     ["the_letting.ogg", "the_letting.loop.json", "the_letting_release.ogg"], "music_loop"),
    ("assets_src/music/act3/release_sting.py", "assets/audio/act3/music", ["release_sting.ogg"], "music"),
    ("assets_src/music/act3/unbinding_swell.py", "assets/audio/act3/music", ["unbinding_swell.ogg"], "music"),
    # M5-A3P-1951: the finale (Ch21 H01-H06)
    ("assets_src/music/act3/heart.py", "assets/audio/act3/music",
     [f"{c}{ext}" for c in ("heart_approach", "heart_rest") for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/act3/kesh_first_voice.py", "assets/audio/act3/music",
     ["kesh_first_voice.ogg", "kesh_first_voice.loop.json"], "music_loop"),
    ("assets_src/music/act3/sefir_finale.py", "assets/audio/act3/music",
     [f"{c}{ext}" for c in ("sefir_warden", "sefir_heart") for ext in (".ogg", ".loop.json")], "music_loop"),
    # M4-A2P-092 (ADR 0175): the people bosses' stems
    ("assets_src/music/act2/malcor_venn.py", "assets/audio/act2/music",
     [f"malcor_venn_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/act2/abiding_guard.py", "assets/audio/act2/music",
     [f"abiding_guard_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/act2/court_steps.py", "assets/audio/act2/music",
     [f"court_steps_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    # M4-A2P-091: Act II zone loops new in plain git (ADR 0175)
    ("assets_src/music/act2/cloudloom.py", "assets/audio/act2/music", ["cloudloom.ogg", "cloudloom.loop.json"],
     "music_loop"),
    ("assets_src/music/act2/sanctum_of_the_level.py", "assets/audio/act2/music",
     ["sanctum_of_the_level.ogg", "sanctum_of_the_level.loop.json"], "music_loop"),
    ("assets_src/music/act2/vowbound_stings.py", "assets/audio/act2/music/stings",
     _source_files("assets_src/music/act2/vowbound_stings.py"), "sfx_set"),
    ("assets_src/music/act2/battle_heretic.py", "assets/audio/act2/music", ["battle_heretic.ogg", "battle_heretic.loop.json"],
     "music_loop"),
    ("assets_src/music/prologue_dusk.py", "assets/lfs/audio/music", ["prologue_dusk.ogg", "prologue_dusk.loop.json"], "music_loop"),
    # M3-AUD-832: the UI track's new screens (menu motion, the title's reveal, save slots, shrine travel, Reefball HUD)
    ("assets_src/sfx/screen_sfx.py", "assets/audio/sfx", _source_files("assets_src/sfx/screen_sfx.py"), "sfx"),
    # M3-AUD-19: Act I temple and dungeon music (Ch5 Ashcrown, Ch8 Coilspire, Ch7 the Tamsule Bell's galleries)
    ("assets_src/music/ashcrown.py", "assets/audio/music", ["ashcrown.ogg", "ashcrown.loop.json"], "music_loop"),
    ("assets_src/music/coilspire.py", "assets/audio/music", ["coilspire.ogg", "coilspire.loop.json"], "music_loop"),
    ("assets_src/music/tamsule_bell_galleries.py", "assets/audio/music",
     ["tamsule_bell_galleries.ogg", "tamsule_bell_galleries.loop.json"], "music_loop"),
    # M3-AUD-20: the Ch6 boss, the Stillguard Inquisitor and the raid-hound
    ("assets_src/music/stillguard_inquisitor.py", "assets/audio/music",
     ["stillguard_inquisitor.ogg", "stillguard_inquisitor.loop.json"], "music_loop"),
    # M3-AUD-802: the field heroes' footsteps by surface and gait, halts, turns, cloth and gear foley
    ("assets_src/sfx/hero_foley.py", "assets/audio/sfx/foley", _source_files("assets_src/sfx/hero_foley.py"), "sfx"),
    # M3-AUD-814: villagers' chat turns and work, gulls, crabs and fish (LifeAudio)
    ("assets_src/sfx/life_sfx.py", "assets/audio/sfx/life", _source_files("assets_src/sfx/life_sfx.py"), "sfx"),
    # M3-AUD-816: battle impact tiers and the KO slow-mo swell (ImpactAudio)
    ("assets_src/sfx/impact_sfx.py", "assets/audio/sfx/battle", _source_files("assets_src/sfx/impact_sfx.py"), "sfx"),
    # M3-AUD-817: cutscene foley (CutsceneAudio) and the prologue's room tone
    ("assets_src/sfx/cutscene_foley.py", "assets/audio/sfx/cutscene", _source_files("assets_src/sfx/cutscene_foley.py"),
     "sfx"),
    ("assets_src/sfx/prologue_ambience.py", "assets/audio/ambience", ["iskarra_dusk.ogg", "iskarra_dusk.loop.json"],
     "ambience_loop"),
    # M3-AUD-818: Act I's cutscene `@sfx` cues (the sequencer plays assets/audio/sfx/<id>.ogg)
    ("assets_src/sfx/act1_cutscene_sfx.py", "assets/audio/sfx", _source_files("assets_src/sfx/act1_cutscene_sfx.py"),
     "sfx"),
    # M3-AUD-825: the Ashcrown strike trial (AshcrownAudio)
    ("assets_src/sfx/ashcrown_sfx.py", "assets/audio/sfx/ashcrown", _source_files("assets_src/sfx/ashcrown_sfx.py"),
     "sfx"),
    # M3-AUD-804: Act II sketches (Ch10 Ossa Fen and Reedhollow, Ch11 Sunken Vey and Lowlight, Ch12 Keth Pass and Quellan)
    ("assets_src/music/ossa_fen.py", "assets/audio/music", ["ossa_fen.ogg", "ossa_fen.loop.json"], "music_loop"),
    ("assets_src/music/reedhollow.py", "assets/audio/music", ["reedhollow.ogg", "reedhollow.loop.json"], "music_loop"),
    ("assets_src/music/sunken_vey.py", "assets/audio/music", ["sunken_vey.ogg", "sunken_vey.loop.json"], "music_loop"),
    ("assets_src/music/lowlight.py", "assets/audio/music", ["lowlight.ogg", "lowlight.loop.json"], "music_loop"),
    ("assets_src/music/keth_pass.py", "assets/audio/music", ["keth_pass.ogg", "keth_pass.loop.json"], "music_loop"),
    ("assets_src/music/quellan.py", "assets/audio/music", ["quellan.ogg", "quellan.loop.json"], "music_loop"),
    # M3-AUD-805: Act II sketches II (Ch13 Ansedra and the Lamp Archive, Ch14 the wedding, Ch15, Ch16)
    ("assets_src/music/ansedra.py", "assets/audio/music", ["ansedra.ogg", "ansedra.loop.json"], "music_loop"),
    ("assets_src/music/lamp_archive.py", "assets/audio/music", ["lamp_archive.ogg", "lamp_archive.loop.json"], "music_loop"),
    ("assets_src/music/peace_wedding.py", "assets/audio/music", ["peace_wedding.ogg", "peace_wedding.loop.json"], "music_loop"),
    ("assets_src/music/unlamped.py", "assets/audio/music", ["unlamped.ogg", "unlamped.loop.json"], "music_loop"),
    ("assets_src/music/pale_rim.py", "assets/audio/music", ["pale_rim.ogg", "pale_rim.loop.json"], "music_loop"),
    ("assets_src/music/drowned_choir.py", "assets/audio/music", ["drowned_choir.ogg", "drowned_choir.loop.json"], "music_loop"),
    # M3-AUD-820: the Ch4 and Ch7 scene and cutscene cues (the scripts' `@music <id>`)
    ("assets_src/music/hearer_hum.py", "assets/audio/music", ["hearer_hum.ogg", "hearer_hum.loop.json"], "music_loop"),
    ("assets_src/music/ysolde_theme.py", "assets/audio/music", ["ysolde_theme.ogg", "ysolde_theme.loop.json"],
     "music_loop"),
    ("assets_src/music/name_board_home.py", "assets/audio/music", ["name_board_home.ogg"], "music"),
    ("assets_src/music/the_long_way_round.py", "assets/audio/music", ["the_long_way_round.ogg"], "music"),
    ("assets_src/music/oruvel_theme.py", "assets/audio/music", ["oruvel_theme.ogg"], "music"),
    ("assets_src/music/tavi_kell.py", "assets/audio/music", ["tavi_kell.ogg"], "music"),
    # M3-AUD-822: Ch7 and Ch8's scripted `@music` cues (the Tidecup's aftermath and crowd, Virel, the seawall waves)
    ("assets_src/music/tidecup_after.py", "assets/audio/music", ["tidecup_after.ogg"], "music"),
    ("assets_src/music/tidecup_crowd.py", "assets/audio/music", ["tidecup_crowd.ogg", "tidecup_crowd.loop.json"], "music_loop"),
    ("assets_src/music/virel_bound.py", "assets/audio/music", ["virel_bound.ogg"], "music"),
    ("assets_src/music/virel_summon.py", "assets/audio/sfx", ["virel_summon.ogg"], "music"),
    ("assets_src/music/corrow_aftermath.py", "assets/audio/music",
     ["corrow_aftermath.ogg", "corrow_aftermath.loop.json"], "music_loop"),
    ("assets_src/music/seawall_hold.py", "assets/audio/music",
     [f"seawall_hold_p{i}{ext}" for i in (1, 2, 3) for ext in (".ogg", ".loop.json")], "music_loop"),
    # M3-AUD-819: Act I's scripted cues (Ch1 the hum, going under, the Rising's stems; Ch9 the night and the road)
    ("assets_src/music/rhen_current_hum.py", "assets/audio/music", ["rhen_current_hum.ogg"], "music"),
    ("assets_src/music/going_under.py", "assets/audio/music", ["going_under.ogg"], "music"),
    ("assets_src/music/undertow_rising.py", "assets/audio/music",
     [f"undertow_rising_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/corrow_night.py", "assets/audio/music", ["corrow_night.ogg", "corrow_night.loop.json"],
     "music_loop"),
    ("assets_src/music/dawn_road.py", "assets/audio/music", ["dawn_road.ogg", "dawn_road.loop.json"], "music_loop"),
    # M3-AUD-821: Act I's scripted Ch5-Ch6 cues (lanternfall, the second verse, Kerrid's motif, Kahre's sting, Liss's
    # theme, the raid, the shoals at night)
    ("assets_src/music/lanternfall.py", "assets/audio/music", ["lanternfall.ogg", "lanternfall.loop.json"], "music_loop"),
    ("assets_src/music/hush_second_verse.py", "assets/audio/music", ["hush_second_verse.ogg"], "music"),
    ("assets_src/music/kerrid_stair.py", "assets/audio/music", ["kerrid_stair.ogg"], "music"),
    ("assets_src/music/kahre_summon.py", "assets/audio/sfx", ["kahre_summon.ogg"], "music"),
    ("assets_src/music/liss_theme.py", "assets/audio/music", ["liss_theme.ogg", "liss_theme.loop.json"], "music_loop"),
    ("assets_src/music/raid.py", "assets/audio/music", ["raid.ogg", "raid.loop.json"], "music_loop"),
    ("assets_src/music/shoals_dusk.py", "assets/audio/music", ["shoals_dusk.ogg", "shoals_dusk.loop.json"], "music_loop"),
]
M1_JOBS = 5  # the first JOBS rows are M1's audio (SIZE_BUDGET)

# M3-AUD-839: Act II's final cues (assets_src/music/act2/ -> assets/audio/music/act2/). That path is Git LFS (ADR
# 0039), and LFS isn't live in the cloud yet, so these render only with --act2 and are never committed until the Lead
# announces it: the default run, the size budget and the tests don't expect them. Composers append rows here.
ACT2_FINALS: list[tuple] = [
    ("assets_src/music/act2/ossa_fen.py", "assets/audio/music/act2", ["ossa_fen.ogg", "ossa_fen.loop.json"],
     "music_loop"),
    ("assets_src/music/act2/reedhollow.py", "assets/audio/music/act2", ["reedhollow.ogg", "reedhollow.loop.json"],
     "music_loop"),
    ("assets_src/music/act2/sunken_vey.py", "assets/audio/music/act2", ["sunken_vey.ogg", "sunken_vey.loop.json"],
     "music_loop"),
    ("assets_src/music/act2/ansedra.py", "assets/audio/music/act2", ["ansedra.ogg", "ansedra.loop.json"], "music_loop"),
    ("assets_src/music/act2/lamp_archive.py", "assets/audio/music/act2", ["lamp_archive.ogg", "lamp_archive.loop.json"], "music_loop"),
    ("assets_src/music/act2/peace_wedding.py", "assets/audio/music/act2", ["peace_wedding.ogg", "peace_wedding.loop.json"], "music_loop"),
    ("assets_src/music/act2/lowlight.py", "assets/audio/music/act2", ["lowlight.ogg", "lowlight.loop.json"], "music_loop"),
    ("assets_src/music/act2/keth_pass.py", "assets/audio/music/act2", ["keth_pass.ogg", "keth_pass.loop.json"], "music_loop"),
    ("assets_src/music/act2/quellan.py", "assets/audio/music/act2", ["quellan.ogg", "quellan.loop.json"], "music_loop"),
    ("assets_src/music/act2/unlamped.py", "assets/audio/music/act2", ["unlamped.ogg", "unlamped.loop.json"], "music_loop"),
    ("assets_src/music/act2/pale_rim.py", "assets/audio/music/act2", ["pale_rim.ogg", "pale_rim.loop.json"], "music_loop"),
    ("assets_src/music/act2/drowned_choir.py", "assets/audio/music/act2", ["drowned_choir.ogg", "drowned_choir.loop.json"], "music_loop"),
    ("assets_src/music/act2/avalanche_ram.py", "assets/audio/music/act2",
     [f"avalanche_ram_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/act2/wakefin.py", "assets/audio/music/act2",
     [f"wakefin_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/act2/mangrove_drowner.py", "assets/audio/music/act2",
     [f"mangrove_drowner_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/act2/lamp_engine.py", "assets/audio/music/act2",
     [f"lamp_engine_p{i}{ext}" for i in (1, 2) for ext in (".ogg", ".loop.json")], "music_loop"),
]
ACT2_DIR = "assets/audio/music/act2"
# M3-AUD-852: Act III's cues (act3_plan.md), the same way: assets_src/music/act3/ -> assets/audio/music/act3/ (Git LFS,
# ADR 0039), rendered only with --act3 and never committed until LFS is live.
ACT3_FINALS: list[tuple] = [
    ("assets_src/music/act3/hollowmere.py", "assets/audio/music/act3", ["hollowmere.ogg", "hollowmere.loop.json"], "music_loop"),
    ("assets_src/music/act3/dace_ledger.py", "assets/audio/music/act3", ["dace_ledger.ogg"], "music"),
    ("assets_src/music/act3/the_kite.py", "assets/audio/music/act3", ["the_kite.ogg", "the_kite.loop.json"], "music_loop"),
    ("assets_src/music/act3/kite_maiden_flight.py", "assets/audio/music/act3", ["kite_maiden_flight.ogg"], "music"),
    ("assets_src/music/act3/iskarra_ruins.py", "assets/audio/music/act3", ["iskarra_ruins.ogg", "iskarra_ruins.loop.json"], "music_loop"),
    ("assets_src/music/act3/iskarra_spire.py", "assets/audio/music/act3", ["iskarra_spire.ogg", "iskarra_spire.loop.json"], "music_loop"),
    ("assets_src/music/act3/hesper_and_ilsabet.py", "assets/audio/music/act3",
     [f"hesper_and_ilsabet_s{i}{ext}" for i in (0, 1) for ext in (".ogg", ".loop.json")], "music_loop"),
    ("assets_src/music/act3/kerrid_last_night.py", "assets/audio/music/act3", ["kerrid_last_night.ogg"], "music"),
]
ACT3_DIR = "assets/audio/music/act3"
# M3-AUD-859: Act III's SFX the same way (plain git has about 0.5 MiB of its budget left): assets_src/sfx/act3/ ->
# assets/audio/sfx/act3/, rendered with --act3 too and held for LFS.
ACT3_SFX: list[tuple] = [
    ("assets_src/sfx/act3/kite_foley.py", "assets/audio/sfx/act3", _source_files("assets_src/sfx/act3/kite_foley.py"),
     "sfx_set"),
]
ACT3_SFX_DIR = "assets/audio/sfx/act3"


def _load(path):
    spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(path))[0],
                                                  os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _render_job(src, out_dir, files, kind):
    mod = _load(src)
    if kind in ("music", "music_loop"):
        mod.render(os.path.join(out_dir, files[0]), verbose=False)
    else:
        mod.render(out_dir, verbose=False)


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _vorbis_tags(path: str) -> dict:
    probe = shutil.which("ffprobe")
    if not probe:
        return {}
    out = subprocess.run([probe, "-v", "error", "-show_entries", "stream_tags", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    tags = {}
    for st in json.loads(out).get("streams", []):
        tags.update({k.upper(): v for k, v in st.get("tags", {}).items()})
    return tags


def _check_loop(ogg: str, y) -> list[str]:
    """Verify a looping cue against its sidecar. Returns a list of problems."""
    problems = []
    with open(os.path.splitext(ogg)[0] + ".loop.json", encoding="utf-8") as f:
        meta = json.load(f)
    S, L, total = meta["loop_start_samples"], meta["loop_length_samples"], meta["total_samples"]
    if len(y) != total or S + L != total:
        problems.append(f"length {len(y)} != sidecar total {total} (start {S} + length {L})")
    tags = _vorbis_tags(ogg)
    if tags and (tags.get("LOOPSTART") != str(S) or tags.get("LOOPLENGTH") != str(L)):
        problems.append(f"Vorbis tags {tags.get('LOOPSTART')}/{tags.get('LOOPLENGTH')} != sidecar {S}/{L}")
    seam = loop_seam_report(y, S)
    print(f"  loop {os.path.basename(ogg)}: start {S}, length {L} ({L / 44100:.2f} s), "
          f"seam jump x{seam['jump_ratio']:.2f}, flux x{seam['flux_ratio']:.2f}, tags {'ok' if tags else 'n/a'}")
    if seam["flux_ratio"] > 3.0:
        problems.append(f"seam spectral flux {seam['flux_ratio']:.2f}x the median (click or gap?)")
    _sync_import(ogg, meta)
    return problems


def _sync_import(ogg: str, meta: dict) -> None:
    """Copy loop settings into Godot's .import file (if Godot has imported the file already)."""
    imp = ogg + ".import"
    if not os.path.isfile(imp):
        return
    with open(imp, encoding="utf-8") as f:
        txt = f.read()
    want = {"loop": "true", "loop_offset": repr(float(meta["loop_offset_seconds"])),
            # beat_count stays 0: with bpm and beat_count both set, Godot 4.6's Ogg playback loops after
            # beat_count beats counted from the *file start* (audio_stream_ogg_vorbis.cpp, beat_length_frames),
            # not from loop_offset, so a cue with an intro would wrap early by the intro's length. The sidecar keeps
            # the musical beat count for tools; the engine loops at the file's end.
            "bpm": repr(float(meta["bpm"])), "beat_count": "0",
            "bar_beats": str(int(meta["bar_beats"]))}
    new = txt
    for k, v in want.items():
        new = re.sub(rf"(?m)^{k}=.*$", f"{k}={v}", new)
    if new != txt:
        with open(imp, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"  updated {os.path.relpath(imp, ROOT)} (re-run godot --headless --path . --import)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--determinism", action="store_true", help="render twice and compare bytes")
    ap.add_argument("--only", default="", help="only the jobs whose source path contains this text")
    ap.add_argument("--act2", action="store_true", help="Act II's final cues (ACT2_FINALS, Git LFS) instead of JOBS")
    ap.add_argument("--act3", action="store_true", help="Act III's cues and SFX (ACT3_FINALS, ACT3_SFX: Git LFS) instead of JOBS")
    args = ap.parse_args()

    self_test()  # BS.1770 meter sanity (48 kHz coefficients, 997 Hz reference)

    lfs = args.act2 or args.act3
    jobs = [j for j in (ACT2_FINALS if args.act2 else ACT3_FINALS + ACT3_SFX if args.act3 else JOBS)
            if not args.only or args.only in j[0]]
    rows, total, new_total, amb_total, ok = [], 0, 0, 0, True
    amb_jobs: dict = {}
    for src, rel_dir, files, kind in jobs:
        m1 = not lfs and JOBS.index((src, rel_dir, files, kind)) < M1_JOBS
        out_dir = os.path.join(ROOT, rel_dir)
        print(f"rendering {src} ...", flush=True)
        _render_job(src, out_dir, files, kind)
        for f in files:
            p = os.path.join(out_dir, f)
            if not os.path.isfile(p):
                print(f"MISSING {p}")
                ok = False
                continue
            size = os.path.getsize(p)
            total += size if m1 else 0
            if kind == "ambience_loop" and src in AMBIENCE_JOB_BUDGETS:
                amb_jobs[src] = amb_jobs.get(src, 0) + size
            elif kind == "ambience_loop":
                amb_total += size
            if f.startswith(M1_AUD_02):
                new_total += size
            if f.endswith(".json"):
                rows.append((os.path.join(rel_dir, f), size, None, None, None, None, _sha(p)))
                continue
            # a loop job may carry a one-shot beside its loop (farewell_tide_release): only a file with its own
            # .loop.json sidecar is checked as a loop
            looped = kind in ("music_loop", "ambience_loop") and os.path.isfile(os.path.splitext(p)[0] + ".loop.json")
            one_shot = kind == "sfx"
            if kind == "sfx_set":
                looped = os.path.splitext(f)[0] + ".loop.json" in files
                one_shot = not looped
            y = read_audio(p, channels=1 if kind == "sfx" else 2)
            if kind == "sfx_set" and np.array_equal(y[:, 0], y[:, 1]):
                y = read_audio(p, channels=1)  # a mono file measures as mono (as test_audio_loudness does)
            if looped:
                for prob in _check_loop(p, y):
                    print(f"FAIL {f}: {prob}")
                    ok = False
            rows.append((os.path.join(rel_dir, f), size, len(y) / 44100,
                         None if one_shot else integrated_lufs(y), momentary_max_lufs(y), true_peak_dbtp(y),
                         _sha(p)))

    print()
    print(f"{'file':48} {'bytes':>8} {'sec':>6} {'I LUFS':>7} {'Mmax':>7} {'TPdB':>6}  sha256[:12]")
    for path, size, sec, il, mm, tp, sha in rows:
        if sec is None:
            print(f"{path:48} {size:8d} {'':>6} {'':>7} {'':>7} {'':>6}  {sha[:12]}")
            continue
        ils = f"{il:7.2f}" if il is not None else "      -"
        print(f"{path:48} {size:8d} {sec:6.2f} {ils} {mm:7.2f} {tp:6.2f}  {sha[:12]}")
        held = (path.startswith("assets/audio/music") or path.endswith("ilun_summon.ogg")) and os.path.basename(
            path).startswith(M1_AUD_02 + M2_CUES)
        if il is not None and held and (abs(il + 16.0) > 0.5 or tp > -1.0):
            print(f"FAIL {path}: outside -16 +- 0.5 LUFS, or true peak above -1 dBTP")
            ok = False
        if path.startswith("assets/audio/ambience") and (abs(il - AMBIENCE_LUFS) > 0.5 or tp > AMBIENCE_MAX_TP):
            print(f"FAIL {path}: outside {AMBIENCE_LUFS} +- 0.5 LUFS, or true peak above {AMBIENCE_MAX_TP} dBTP")
            ok = False
    if amb_total:
        print(f"ambience beds {amb_total / 1048576:.2f} MiB, budget {AMBIENCE_BUDGET / 1048576:.1f} MiB")
        if amb_total > AMBIENCE_BUDGET:
            print("FAIL: ambience beds over their size budget")
            ok = False
    for src, size in amb_jobs.items():
        print(f"{os.path.basename(src)} beds {size / 1048576:.2f} MiB, budget {AMBIENCE_JOB_BUDGETS[src] / 1048576:.1f} MiB")
        if size > AMBIENCE_JOB_BUDGETS[src]:
            print(f"FAIL: {src}'s beds over their size budget")
            ok = False
    if lfs:
        size = sum(r[1] for r in rows)
        print(f"{'Act II finals' if args.act2 else 'Act III cues'} {size} bytes ({size / 1048576:.2f} MiB): Git LFS (ADR "
              "0039), outside the plain-git budget")
    elif not args.only:
        print(f"total {total} bytes ({total / 1048576:.2f} MiB), budget {SIZE_BUDGET / 1048576:.0f} MiB; "
              f"M1-AUD-02 cues {new_total / 1048576:.2f} MiB, budget {NEW_AUDIO_BUDGET / 1048576:.0f} MiB")
        if total > SIZE_BUDGET or new_total > NEW_AUDIO_BUDGET:
            print("FAIL: over size budget")
            ok = False

    if args.determinism:
        with tempfile.TemporaryDirectory() as td:
            for src, rel_dir, files, kind in jobs:
                _render_job(src, td, files, kind)
                for f in files:
                    a, b = _sha(os.path.join(ROOT, rel_dir, f)), _sha(os.path.join(td, f))
                    same = a == b
                    ok &= same
                    print(f"determinism {f}: {'identical' if same else 'DIFFERENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
