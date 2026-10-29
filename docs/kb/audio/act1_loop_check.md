# Act I loops by ear's proxy (M3-AUD-861; the Lead's 04:44 ask)

`python3 tools/audio/act1_loop_check.py --md` (run `git lfs pull` first). It covers every music loop and ambience bed an
Act I zone plays. Each is decoded from the shipped file and measured the way render_all.py gates a render:
- the seam at the sidecar's loop point, as jump and spectral flux against the file's median;
- integrated loudness and true peak, against its targets.py rule;
- each zone's bed level against its music.

Run on 2026-10-28 after big14 and the M3-AUD-861 work: **41 files, 0 problems.**
- **Seams:** the worst jump is ×3.68 (shell_shrine_interior), against the click threshold of 10. The worst flux is
  ×2.84 (brine_shoals), against 3.
- **Music:** every Act I zone loop is at −16.0 ±0.15 LUFS.
- **Beds:** every bed is at −26 ±0.3.
- **Balance:** each bed sits 9.7–10.1 LU under its music, as mix.md asks (about 10).

It measures; it doesn't listen. A seam that is clean by these numbers can still be audible as a musical join. Those
are the listening notes' job (listening_notes.md).

| Zone | What | LUFS | TP dBTP | Seam jump | Seam flux | |
|---|---|---|---|---|---|---|
| haluna | music haluna_village | -16.02 | -1.72 | x0.38 | x2.40 | ok |
| haluna | music haluna_night | -16.00 | -3.56 | x0.37 | x1.31 | ok |
| shell_shrine | music shell_shrine_interior | -15.99 | -3.28 | x3.68 | x1.09 | ok |
| oruvel | music oruvel | -16.03 | -1.96 | x0.47 | x1.75 | ok |
| oruvel_underway | music lamp_diver | -16.05 | -3.02 | x3.33 | x0.59 | ok |
| haluna_wake | music haluna_night | -16.00 | -3.56 | x0.37 | x1.31 | ok |
| brightwater_ferry | music brightwater_ferry | -16.03 | -2.50 | x0.53 | x1.64 | ok |
| pemakar | music terraces_of_ash | -16.07 | -1.68 | x2.38 | x2.68 | ok |
| ashcrown | music ashcrown | -16.02 | -3.45 | x0.51 | x0.27 | ok |
| brine_shoals | music brine_shoals | -16.04 | -1.56 | x0.72 | x2.84 | ok |
| tamsule | music tamsule | -16.03 | -1.66 | x0.14 | x0.52 | ok |
| tamsule_bell_galleries | music tamsule_bell_galleries | -16.00 | -4.48 | x0.26 | x0.39 | ok |
| corrow_night | music corrow_night | -16.03 | -4.16 | x0.21 | x0.51 | ok |
| saltgrass_causeway | music saltgrass_causeway | -16.15 | -1.37 | x1.17 | x0.90 | ok |
| tidecup_match | music tidecup_match | -16.05 | -1.86 | x0.08 | x0.90 | ok |
| corrow | music corrow_seawall | -16.05 | -1.49 | x0.27 | x0.19 | ok |
| coilspire | music coilspire | -16.03 | -1.53 | x0.22 | x0.29 | ok |
| prologue | music prologue_dusk | -16.00 | -2.57 | x0.20 | x0.52 | ok |
| prologue | bed iskarra_dusk | -26.05 | -11.29 | x0.59 | x0.63 | ok |
| haluna | bed haluna_day | -25.89 | -12.96 | x0.33 | x1.08 | ok |
| haluna | bed surf | -25.99 | -8.85 | x0.68 | x0.48 | ok |
| haluna | bed haluna_night | -26.10 | -12.46 | x1.90 | x1.74 | ok |
| haluna | bed dock | -26.13 | -11.54 | x1.81 | x0.86 | ok |
| shell_shrine | bed shrine_interior | -26.11 | -14.46 | x1.90 | x0.75 | ok |
| tamsule | bed tamsule_port | -26.12 | -13.36 | x1.79 | x0.74 | ok |
| tamsule_bell_galleries | bed tamsule_bell | -26.11 | -11.19 | x0.12 | x1.22 | ok |
| pemakar | bed pemakar_terraces | -25.74 | -13.48 | x1.29 | x0.92 | ok |
| ashcrown | bed ashcrown | -26.16 | -13.09 | x1.76 | x1.00 | ok |
| brine_shoals | bed brine_shoals | -26.15 | -8.56 | x0.76 | x0.81 | ok |
| corrow_night | bed corrow_seawall | -26.05 | -11.38 | x1.83 | x1.08 | ok |
| saltgrass_causeway | bed causeway_wind | -25.85 | -13.43 | x1.83 | x1.36 | ok |
| saltgrass_causeway | bed tidepools | -26.21 | -5.26 | x2.70 | x1.53 | ok |
| oruvel_underway | bed drowned_tower | -26.14 | -13.33 | x1.09 | x1.42 | ok |
| first_verse | bed shrine_interior | -26.11 | -14.46 | x1.90 | x0.75 | ok |
| haluna_wake | bed haluna_night | -26.10 | -12.46 | x1.90 | x1.74 | ok |
| haluna_wake | bed surf | -25.99 | -8.85 | x0.68 | x0.48 | ok |
| haluna_wake | bed dock | -26.13 | -11.54 | x1.81 | x0.86 | ok |
| corrow | bed corrow_seawall | -26.05 | -11.38 | x1.83 | x1.08 | ok |
| oruvel | bed oruvel_raft | -26.17 | -10.86 | x3.54 | x1.15 | ok |
| brightwater_ferry | bed brightwater_deck | -25.93 | -15.49 | x0.94 | x1.18 | ok |
| coilspire | bed coilspire_flues | -26.12 | -12.24 | x1.82 | x0.83 | ok |

- ashcrown: bed 10.1 LU under the music
- brightwater_ferry: bed 9.9 LU under the music
- brine_shoals: bed 10.1 LU under the music
- coilspire: bed 10.1 LU under the music
- corrow: bed 10.0 LU under the music
- corrow_night: bed 10.0 LU under the music
- haluna: bed 9.9 LU under the music
- haluna_wake: bed 10.0 LU under the music
- oruvel: bed 10.1 LU under the music
- oruvel_underway: bed 10.1 LU under the music
- pemakar: bed 9.7 LU under the music
- prologue: bed 10.1 LU under the music
- saltgrass_causeway: bed 9.7 LU under the music
- shell_shrine: bed 10.1 LU under the music
- tamsule: bed 10.1 LU under the music
- tamsule_bell_galleries: bed 10.1 LU under the music

41 file(s), 0 problem(s)
