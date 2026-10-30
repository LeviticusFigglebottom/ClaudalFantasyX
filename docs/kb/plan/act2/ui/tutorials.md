---
draft: pre-gate
---
# Act II first-time tips and battle prompts

Act I's rule holds:
- a field tip shows once per save (`tutorial_tips.json`, its seen flag in flags.tres);
- a battle prompt belongs to one scripted fight (`encounters.json` `prompt_key`, or `turn_prompt_hero` and
  `turn_prompt_key`);
- a prompt names no binding; a tip names the bindings of the device in use (InputNames).

Each line is one or two sentences, sincere, and says what to do, not why the game wants it (SPEC pillar 1).

## Battle prompts (encounters.json)

| Fight | Kind | Key | Line (draft) |
|---|---|---|---|
| `ch10_fen_roots` | prompt | `TUT_CH10_ROOTED` | Roots hold whoever they catch. A rooted hero cannot be swapped out until they break free. |
| `ch10_fen_leeches` | prompt | `TUT_CH10_DRAIN` | The leeches heal on what they take. Strike them before they feed. |
| `ch10_fen_archers` (Pell's first fight) | turn prompt, `pell` | `TUT_CH10_LISTEN` | Listen, and Pell learns what he hears. It costs him this turn. |
| `mangrove_drowner` | prompt | `TUT_DROWNER_ROOTS` | Each root it is held by shows on the timeline. Break them and it comes loose. |
| `lamp_engine` | prompt | `TUT_LAMP_ENGINE_CRAWLERS` | The crawlers mend what you break. Stop them first. |
| `ch12_pass_moths` | prompt | `TUT_CH12_UNRAVEL` | Cord moths unpick the help you've woven. Strike them before your wards are gone. |
| `avalanche_ram` | prompt | `TUT_RAM_FIELD` | Every charge brings more snow down. The field shows what the next one costs. |
| Ch14 court steps (set piece) | prompt | `TUT_CH14_HOLD_STEPS` | Hold the steps until Merel cuts the barge loose. |
| `malcor_venn` phase 1 | turn prompt, `liss` | `TUT_MALCOR_ENGINE` | The flat-engine slows you with every pulse. Liss can break it. |
| `wakefin` | prompt | `TUT_WAKEFIN_DARK` | In the dark, listen. The timeline still shows what it means to do. |
| Ch16 Abiding guard / Kesh | prompt | `TUT_CH16_CYCLE` | It changes its element on a rhythm. The timeline shows the next one. |
| Ch16 storm's waking (set piece) | prompt | `TUT_CH16_HOLD_LINE` | Kerrid holds the line. Keep him standing. |

**Loc keys (12):** the keys in the table.

## Field tips (tutorial_tips.json)

| Tip | Raised by | Seen flag | Keys | Body (draft) |
|---|---|---|---|---|
| Seven heroes | flag `ch10_party_of_seven` (the first field after Ch9) | `tut_seven_seen` | `TIP_SEVEN_TITLE`, `TIP_SEVEN_BODY` | Three fight; four wait. Choose who stands in the line under Formation in the field menu. |
| Records | flag `ch13_archive_read` | `tut_records_seen` | `TIP_RECORDS_TITLE`, `TIP_RECORDS_BODY` | Found records are kept in the codex under Records. Open one to read it again. |
| Dark shrines | near tag `shrine`, after `ch14_declared_heretics` | `tut_dark_shrine_seen` | `TIP_DARK_SHRINE_TITLE`, `TIP_DARK_SHRINE_BODY` | The Order's shrines refuse heretics now. The Kirru and the Saltwrights still keep theirs. |
| A new Swell mode | flag `<mode>_unlocked` (Progression names it) | `tut_swell_mode_seen` | `TIP_SWELL_MODE_TITLE`, `TIP_SWELL_MODE_BODY` | A new way to fill the Swell. Choose it under Swell in the field menu. |

**Loc keys (8):** the keys in the table. **Flags (4):** the seen flags, declared in flags.tres at the gate.

## Not taught by a prompt (on purpose)

- **The document reader** teaches itself: its help line counts the hands left to find (screens.md §1).
- **The Vowbound** of Act II: Ch4's prompt taught calling; each new one is a new Call in its caller's Skills.
- **Kerrid's reveal** changes no mechanic (kerrid.md).
