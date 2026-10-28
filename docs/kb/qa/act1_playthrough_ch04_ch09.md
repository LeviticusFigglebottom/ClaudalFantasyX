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

- Second pass (viewed again in the re-rendered stills): Garo faces the camera in P07 and P09_garo, Kerrid at the inn
  gate (P06N), Toma's face in the raid (W07) and on the barge (W12_crate), Tavi on the prow (R06), the moorings above
  the water (R09), N12 off the moon onto the raft, the wall-walk shots W12/W13 on the party; **ch08_captain staged as
  ADR 0022 (c) pins it** (Kerrid, Marra and the climbers at the flooded stair foot before the scene; W15 above the
  flood's water, W16 on Marra); Ch9's road D03 moved onto the road behind the line (it stood beyond the parapet).
- Third pass: R08 lifted off the waterline onto the moorings and the people on them; W07 and W07_storm moved
  west of the gate (the old views sat inside the gate leaves, which have no collision) so the party is front-lit
  with the gate behind; F08_key from the north, the side the great key is turned from, and Asha placed at the
  wheel (`great_key_asha`) before ch08_beacon_opened; N09 frames the mourner whole until the kneel exists.

## Field POIs (2026-10-28)
Every zone map POI of Ch4–Ch9 (69) rendered at the field's default view (GreyboxZone's hub orbit, orbit_yaw 0,
7.5 m back, 6 m up) through the zone's shot rig. Where the orbit saw a wall, a roof, a sail or the beacon, the layout
now has a pan-follow camera volume, each camera picked from rendered previews (interiors placed with
`tools/act1/shot_check`'s solver):
- Ch4 wake: Haluna's own CameraVolumes (Ch04Zone rebuilds ch02/haluna's from its scene: the lane, market, dock,
  chapel) plus Neme's door (c48cba476). The ferry: bow, waist and aft deck off her beam (775a44dd0).
- Ch5 Pemakar's harbour, clear of the moored sail (e66297f98). Ch7 Tamsule's stilt lane. Ch8 Corrow's wall-gate.
  Coilspire: the keeper's hut, a volume per tier on the spire's axis, the gallery's two halves. Ch9: the road gate,
  the milestone and the wall head from the wall's inner side (3e43e1e71; test `test_ch08_coilspire_camera`).
- Read well as they are: the Brine Shoals' flats, Tamsule's quay, market and galleries, Corrow's town and mole,
  Ch9's strand, landing and Stillguard row, the Coilspire's headland path, Pemakar's terraces.
- Pacing: a scan of every Ch4–Ch9 scene for long holds without a line found only holds the beats pin (ch08_wall_falls'
  seven cuts with no word, rule 4; ch09_the_stair's one 15 s shot, ADR 0022 (f); the Ebbing's held inputs).
- Balance: the playthrough showed no spike or trivial fight, so no sim run (the Lead's brief: only where it does).

## Walks and pacing (2026-10-28)
- **Walks on their paths (32d59e75d):** M3-CIN-1221's `via=` landed in slice-polish's b2d39f8cc, so
  `act1_walk_vias.patch`'s 36 cues are in. `act1_cutscene_walks_known.json` is empty. The dawn causeway is staged
  on the real Haluna: Asha at her shell, Ysolde gone at dawn, C01 down the path behind the three, and holds that
  fit the walk.
- **Pacing (d212b0413, 3c3839c84):** the sequencer lets a running walk finish before a scene ends, so a walk longer
  than its script held a frame, a black screen or a locked field camera. `tools/act1/cutscene_stills` with
  `STILLS_TIMING=1` (headless) prints each scene's TAIL and the walks it waits on. Its plan now runs in story
  order, ordered by the flags each group needs and raises; arrive rows and same-zone `go`s reload the zone with
  the story's flags; a beat's player stands on its trigger. Before the fixes the worst tails were
  ch04_shell_is_set 45 s in black, ch08_landfall 45 s, ch08_cut_rope's black tail, ch07_into_tamsule 37 s with
  the camera released, ch08_wall_falls 32 s, ch06_raid, ch06_smoke 65 s and ch04_dock_in_the_dark (Asha
  arriving after the talk). Every scene now ends within about 11 s of its last step, and the tail is a visible
  walk ending (Kerrid's exit up the mole stair, Toma's run to the shield line). ch08_stuck_key's 14 s is the
  harness: its beat fires from the seized key's `flue` payload, so the player isn't stood on it.
- The galleries' after_the_bell plays first in the plan because its flag comes from the Reefball match, not a
  flow (a harness limit; the scene itself is staged right).

## Open, act1-chapters (cameras and staging)
| Ch | Scene / shot | What reads wrong |
|---|---|---|
| 4 | ch04_name_board D06, ch04_seventh_terrace D01, F05; ch04_spar_wraith D05 | waits on the grade (M3-ENV-1228): re-previewed 2026-10-28, every view of the stern reads near-black, so framing can't be judged. F05, D01 and D05 have their subject (the hull, the wraith's motes); D06 aims at y 1.7 above the kit's name-board (it hangs on the transom at -9.24, 0.85, 21.04): re-aim it once the grade lands |
| 5 | Ashcrown's tier POIs (quench, tier_1–4) | the orbit frames a dark shaft (tier_1 sits inside a banner); still greybox, so its volumes wait for its kit (M3-ARC-1216) |
| 4, 5 | the derelict alongside the ferry; Pemakar's harbour at night | the orbit and the new harbour volume read near-black: the grades (M3-ENV-1228, M3-ENV-1229) |
| 9 | ch09_the_ebbing N09 | framed on the standing mourner; the open hand on the shingle needs the kneeling mourners (character, M3-C09-08 §5: no villager cast has a kneel clip yet, only Toma's `kneel_palms_flat`) |

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
