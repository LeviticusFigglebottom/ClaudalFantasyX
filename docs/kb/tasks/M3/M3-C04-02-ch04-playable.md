---
id: M3-C04-02
title: Ch4 "The Pilgrim's Wake" playable (dialogue, flow, greybox levels, encounters, cutscenes)
role: cinematics
status: review
owner_session: "m2-slice subagent (C04 build)"
depends_on: [M3-C04-01, M3-ARC-01]
reviewer: narrative
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Build Ch4 from its beat sheet (`docs/kb/story/beats/act1_ch04.md`):
- the `.dlg` scripts under `game/data/dialogue/ch04/`;
- the chapter's flow in the M3-ARC-01 chapter data;
- greybox levels under `game/levels/ch04/` (or the night variant named in the sheet), built for env-art's kit to swap in later;
- the encounters, with combat data and `sim.py` bands;
- the cutscenes.

Use env-art, audio and creature swap-in notes as they land.

## Acceptance criteria
- [x] The chapter plays headless from its entry to its exit in an integration test, like `test_fp_thread`.
- [x] Every line goes through a loc key or a `#line:` tag; flags are declared in `flags.tres`; `validate_data` and `dlgc --check` are clean.
- [ ] Each boss and encounter has a `sim.py --check` band, and the combat reviewer has seen it. (Bands in; combat to review, two logged exceptions.)
- [x] Each greybox level has a `place_at` root and its spawns, and an entry in `locations.json`.
- [x] PLAYTEST notes for the chapter.

## Notes
**2026-10-24, m2-slice subagent (C04 build), to review.** Reviewers: **narrative** (lines and staging, SPEC §12.3) and **combat** (the bands and the two logged exceptions). Handoff: `docs/kb/handoffs/2026-10-24-cinematics-14.md`.

What's built:
- **Chapter flow:** `game/data/flow/chapters/ch04.json`, listed in chapters.json, played by ZoneStory over two greybox zones under `game/levels/ch04/` (root `Ch04Zone`, extending Ch01Zone, with flag-driven `states`).
- **Dialogue:** 25 scripts in `game/data/dialogue/ch04/`, C4-01 to C4-15, about 1,090 words (dialogue_stats), including "The Long Way Round"'s lyric (about 60 words).
- **Battles:** five encounters (the leech ambush, the bottle-hermit lesson, the Spar-Wraith, two random lineups), three enemies and eight skills, with sim bands.
- **Tests:** `tests/integration/test_ch04_thread.gd` (entry to exit, plus the B11 gate and the "Not tonight" / asked-after branch), `tests/unit/test_ch04_battles.gd`, `tests/unit/test_ch04_zones.gd`, `tools/tests/test_ch04_validate.py`.

Decisions:
1. **Haluna's night is a stand-in greybox location, `ch04/haluna_wake`**, not a hook in HalunaStory. HalunaStory isn't data-driven, and ADR 0035 says new chapters use ZoneStory; a hook would put Ch4 on the slice's code path. The slice is untouched (test_fp_thread and test_haluna_* are green). The block moves to `ch02/haluna` with Haluna's move to ZoneStory.
2. **The end card isn't wired yet.** Ch4 currently exits to the end card (Ch5's `ch05/pemakar` isn't on this branch), so pointing the end card into Ch4 now would loop. Ch4 is reached at its own location (locations.json and two F5 teleports), and both hand-offs are M3-C04-04.
3. **The ferry is never attacked (ADR 0017 (d)).** The hulls are never joined, and the random fights run only while aboard the derelict; the test walks 500 m on the ferry and nothing fires.
4. **Ysolde joins in reserve.** The field party is Rhen, Asha and Toma with Ysolde in reserve, so the swap prompt is true. The hermit's battle step seats her in reserve whatever the formation.
5. **Two battle prompts in sequence:** a small view-only addition to BattleBossHud (`turn_prompt_hero` / `turn_prompt_key`): the swap prompt opens the hermit fight, and Read shows on Ysolde's first turn.
6. **A breath before the Spar-Wraith** (a full heal, as Ch1 before Hullgnaw): its band assumes a full party, and the party can't go back to the ferry's shrine.
7. **"Reflects fire"** is played as fire-immune glass (the engine has no reflect), and the leech's "fragile once it has struck" as evasion (no engine rule). Both are combat questions (M3-C04-06).

For narrative to check (new text):
- the three earlier Velamir Cantors' names (Mara, Ilse, Teodra), said by Osu;
- two Canticle lines ("The water keeps what it is given, and gives back what it keeps." / "Go down to the level, and be still.");
- the fisher's wife's name, Nalu;
- the lyric.

C4-04 (206 words) and C4-06 (159) are under the sheet's budgets (300 and 260); the chapter is about 1,090 words against the sheet's ~1,300 typical path. Narrative may want to add.

Gaps:
- No save shrine in a greybox zone: the ferry's shrine rests the party, nothing more.
- No party-formation menu or Ysolde party-join card yet.
- Battle barks are spoken before the fight.
- No in-battle bestiary prompt.
- Audio cues and SFX are placeholders (M3-C04-05).
- The creature models aren't seated in battle (M3-C04-06).
- The kits and the real Haluna wake-night dressing are M3-C04-03.

Follow-ups filed: M3-C04-03 (environment), M3-C04-04 (cinematics: the hand-offs), M3-C04-05 (audio), M3-C04-06 (combat with character art: the creatures and the rulings).

## Review log
