# Act I playthrough, Ch4–Ch9: what reads unfinished (act1-chapters, ADR 0041)

Source: `tools/act1/cutscene_stills` (each zone visit's chapter flow run in order on one zone instance, every cutscene
played in driven time, a still 0.8 s after every camera cue) and `tools/act1/shot_check` (each story camera's line of
sight and enclosure, with a solver for the nearest clear view). 60 scenes, 181 stills, viewed 2026-10-28 @ d150d529.
Owner per row: **act1-chapters** fixes cameras, staging, flow and encounters; the rest are filed to their owners.

## Fixed already (this session)
- Ch4 wake on Haluna: Neme and Toma left at home, Osu 26 m from the wall, close-ups on the dock (712bc98a).
- Six cutscene snaps (91f21337); Coilspire's ten story cameras inside rock, walls or the crown (d150d529); 16 blocked
  cameras on the derelict, Pemakar, the shoals, the galleries and Corrow moved clear (d150d529).
- Ch8's three field fights have arenas (41bc33e7).

## Open, act1-chapters (cameras and staging)
| Ch | Scene / shot | What reads wrong |
|---|---|---|
| 4 | ch04_name_board D06, ch04_seventh_terrace D01, F05; ch04_spar_wraith D05 | the derelict at night: dark frames with no subject (sea, rigging); the wraith reads only as its motes |
| 5 | ch05_smiths_question P07, release | Garo's back fills the frame; the release frames the ground |
| 5 | ch05_lanternfall_boats P09_garo | feet only |
| 5 | ch05_inn_gate P06N | Asha's side, cut at the head |
| 6 | ch06_barge W12_crate; ch06_raid W07; ch06_midday W02_share | legs only; the back of Toma's shield; a hull from inside |
| 7 | ch07_after_the_bell R06 | cut through a boat's hull |
| 7 | ch07_empty_moorings R08, R09 | at the waterline, the posts fill the frame |
| 8 | ch08_captain W15, W16; ch08_stranger_on_wall W13; ch08_hoist W12 | black or near-black: inside the wall or its shadow |
| 8 | ch08_wall_gate W07; ch08_run_back W07_storm | the gate as a black silhouette, no one in frame |
| 8 | ch08_storm_against_wind / ch08_beacon_opened F08_key | the wheel half behind the dark flue wall |
| 9 | ch09_the_ebbing N09; ch09_the_road_out P04 | feet / the road surface only |
| 9 | ch09_the_road_out D02, D03 | empty sky; the parapet's barrels only |
| 9 | ch09_the_ebbing N12 | the moon's bloom whites out the frame (aim off the moon) |

## Open, other owners (filed)
| Ch | What | Owner / task |
|---|---|---|
| 6 | Sefir is a capsule on the barge (W11, W12) | hero-integration, M3-HER-1225 |
| 6, 7, 8 | Liss is a capsule (camp, lantern, galleries R02K, Corrow) | characters, M3-CHR-03 / M3-C06-06 |
| 8, 9 | Kerrid is a capsule (W23, W24; Ch9 stair N13, road) | characters, M3-CHR-505 |
| 9 | Pell is a capsule on the strand and road (N17) | characters, M3-CHR-506 |
| 8 | The storm figure over the water is a cyan capsule (W22) | characters + rendering: new request M3-RND-28 |
| 8 | Virel is the greybox block in F07, F06_out (fills the frame) | creatures-b, M3-CRE-627 |
| 7, 8 | The weeping column; the storm wall | rendering, M3-RND-27 |
| 5 | Ashcrown is greybox: A02, A04, A10, A11, A12 frame bare walls and voids | env-art-b + steep stairs, M3-ARC-1216 |
| 4 | The derelict at night grades near-black (D01, D06, F05 read as nothing) | env-art (Prologue–Ch4), new request M3-ENV-1228 |
| 6, 8 | Brine Shoals' dusk camp and Corrow's storm read as silhouettes (W15, W07, W13) | env-art-b (Ch5–Ch9 grades), new request M3-ENV-1229 |
