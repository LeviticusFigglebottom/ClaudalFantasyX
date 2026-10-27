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
           "shell_shrine_interior", "ilun_summon", "saltgrass_causeway", "lamp_diver", "sefir_theme", "the_ebbing",
           "tidecup_match", "terraces_of_ash", "corrow_seawall", "hullgnaw", "spar_wraith", "oruvel", "pilgrims_wake",
           "tamsule", "iskarra_vigil", "brightwater_ferry", "brine_shoals", "ashcrown", "coilspire",
           "tamsule_bell_galleries", "stillguard_inquisitor", "ossa_fen", "reedhollow", "sunken_vey", "lowlight",
           "keth_pass", "quellan",
           "ansedra", "lamp_archive", "peace_wedding", "unlamped", "pale_rim", "drowned_choir")
AMBIENCE_BUDGET = int(2.5 * 1024 * 1024)  # the M2-AUD-05 field beds together
# Per-job budgets for later "ambience_loop" jobs (each job's beds together; the M2-AUD-05 job keeps AMBIENCE_BUDGET).
AMBIENCE_JOB_BUDGETS = {"assets_src/sfx/causeway_ambience.py": int(1.2 * 1024 * 1024),
                        "assets_src/sfx/act1_ambience.py": int(3.0 * 1024 * 1024),  # M2-AUD-13: two q1 beds; M3-AUD-16: six
                        "assets_src/sfx/prologue_ambience.py": int(0.6 * 1024 * 1024)}  # M3-AUD-817: one q1 bed
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
    ("assets_src/music/the_ebbing.py", "assets/audio/music", ["the_ebbing.ogg"], "music"),
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
        "whistle_start.ogg", "whistle_short.ogg", "whistle_end.ogg", "naming_rite.ogg"]
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
    # M2-AUD-14: the menus track's pages (Items, Formation, Customize, the zone map's pan)
    ("assets_src/sfx/menu_page_sfx.py", "assets/audio/sfx",
     [f"{u}.ogg" for u in ("ui_item_use", "ui_item_sort", "ui_formation_pick", "ui_formation_swap",
                           "ui_customize_open", "ui_craft", "ui_map_pan")], "sfx"),
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
]
M1_JOBS = 5  # the first JOBS rows are M1's audio (SIZE_BUDGET)


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
    args = ap.parse_args()

    self_test()  # BS.1770 meter sanity (48 kHz coefficients, 997 Hz reference)

    jobs = [j for j in JOBS if not args.only or args.only in j[0]]
    rows, total, new_total, amb_total, ok = [], 0, 0, 0, True
    amb_jobs: dict = {}
    for src, rel_dir, files, kind in jobs:
        m1 = JOBS.index((src, rel_dir, files, kind)) < M1_JOBS
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
            looped = kind in ("music_loop", "ambience_loop")
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
    if not args.only:
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
