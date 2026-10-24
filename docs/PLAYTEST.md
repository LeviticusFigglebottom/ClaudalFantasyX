# Playtest: the First Playable (Windows)

This is a rough but complete thread through the first minutes of *Hymn of the Undertow*. Most of what you see is placeholder: capsules stand in for people (Asha is the only real model, and she has no animations yet), the Shell Shrine is grey stone primitives, and the music uses the three prototype cues in place of the scenes' own. **The point is to feel the flow.** Please note anything that confuses you, drags, or feels wrong.

## What you play (about 15–20 minutes)

1. **Title.** Choose **New Game**.
2. **Prologue.** A dead city at dusk, with one line of Rhen's narration.
3. **Cutscene A, "The Girl on the Beach".** Rhen wakes in the shallows at Haluna. There are two choices; both are fine.
4. **First battle.** Walking up the beach path toward the village starts a fight against a reef crab and a lantern eel, with Rhen and Asha (Toma in reserve). Win it, and the screen fades to **Neme's table**: noon, Rhen waking at Asha's aunt's door to far too much food. Flee it, and you're back on the beach below the path, with the fight still ahead. Lose it, and you can **Fight again** or **Return to last save** (your newest save; with none yet, this reads **Return to title**).
5. **Haluna, free to walk.** Four people, at the market, the chapel court, the dock and in the lane (a child skipping), each say something that hints at what a "Cantor" is. You overhear each one as you walk past, without stopping, and you can also talk to them.
   - In the lane, **Look** at the carved gull on a roof ridge.
   - **Optional, "Pila's Granddaughter":** Grandmother Osu washes the wake-shells at a wall at the causeway head (on the village side, left of where the causeway starts). Talk to her before you go on: it is the only time she's there, and a later scene remembers it.
   - **Escape** opens the field menu (bestiary, Swell fill modes) for Rhen, Asha and Toma.
6. **Save** at the shrine: the glowing teal stone with a shell canopy, on the third lane into the village (past the tide-wall lanes). Resting there heals the party and opens the save menu.
7. **The causeway head.** Once you have saved, walk north along the beach, away from the dock, to the causeway head at the beach's far end. (Before you've saved, Toma and Asha send you back to the shrine in town as you walk in; you keep walking.) **This leaves Haluna's day behind:** you come back only at night. Asha asks first: choose **Go now** to set off, or **Not yet** to step back with nothing lost (Osu, the barks and the lintel-gull are still there, and walking in again asks again). After Go now, Toma and Asha talk about the low tide, and you're inside the **Shell Shrine** for its trial.
   - **The trial:** three stone basins, seen from above. Water runs from the spring through whichever channel each basin's lip faces, and the channels carrying water light up. Use a basin (**E**) to turn it a quarter turn. Send the water into the big pool on the far side; when the pool fills, the door at the end sinks, and walking through it plays **Cutscene B, "The First Verse"**, at sunset. Stuck for a minute and a half? Toma gives one hint. **Optional:** route the water into the small sluice near the second basin to drain the side pool, and pick up what's in it. Cutscene B notices.
   - The room is grey placeholder blocks for now.
8. **The Drownbell.** The bell answers the verse. It's a two-phase boss, with Rhen, Asha and Toma and no reserve.
   - **Phase 1, the Toll:** watch the timeline. The bell gathers a toll that shoves everyone back, and the timeline shows it two turns out. Three fast strikes (Rhen's Attack or Quick Hit) break its rim and silence it.
   - **Phase 2, the Flood:** at about 40% health the water rises, and polyps heal the bell faster than you can cut them down. Asha's **Call** row brings in **Ilun**, the first Vowbound. The party steps back and he fights alone, his gauge filling as he drinks the flood. When it's full, his **Floodnet** clears the water. Dismiss him from his own menu, or he stays until he falls.

   Lose, and you can fight again or return to your last save.
9. **The dock at night.** Win, and you're back in Haluna after dark: moonlight, stars, a faintly glowing sea and oil lamps under the eaves. Rhen finds Asha at the end of the dock and asks to come with her. Talking to the villagers again now gives their night lines.
10. **End card.** Press accept to return to the title. **Continue** loads your save.

## Running it

### Option A: the Godot editor (recommended)

1. Download **Godot 4.6.3 stable**, the standard build (not .NET), for Windows: <https://godotengine.org/download/archive/4.6.3-stable/>. Unzip it anywhere. There is no installer.
2. Get the project: clone the repository, or download the integration branch (currently `claude/undertow-lead-handoff-423ixt`, with the latest art) as a ZIP from GitHub and unzip it.
3. Run `Godot_v4.6.3-stable_win64.exe`. In the Project Manager, click **Import**, choose the repository's `project.godot`, and click **Import & Edit**.
4. **The first open imports every asset, which takes a few minutes.** Wait until the progress bar at the bottom of the editor finishes.
5. Press **F5** (or the ▶ "Run Project" button at the top right). The game starts at the title.

To close the game, press **Alt+F4**, or click ■ Stop in the editor. **F8** also stops it from the editor.

**If it runs slowly:** on the title, choose **Settings**. Left and Right change the preset (try **Low**) or any single setting; each change is applied and kept at once. Escape goes back.

### Option B: an exported .exe

This needs the Godot 4.6.3 **export templates**: in the editor, open **Editor → Manage Export Templates → Download and Install**. Then open **Project → Export…**, select the **Windows Desktop** preset (already in the project), and click **Export Project**. The default output is `build/windows/hymn_of_the_undertow.exe`. Run the `.exe` next to its `.pck`.

## Controls

| Action | Keyboard | Controller |
|---|---|---|
| Move | WASD or arrow keys | Left stick |
| Walk slowly | hold Shift | Left shoulder |
| Talk, examine, use the shrine | E, Enter or Space | A / Cross |
| Turn the camera (open areas only) | Q / R | Right stick |
| Advance dialogue, confirm | Enter or Space | A / Cross |
| Choose an option | Up / Down, then Enter | D-pad, then A |
| Back, cancel | Escape | B / Circle |
| Skip a cutscene (it stops at each choice, so you still choose) | hold Escape for 1 s | hold B / Circle |
| Field menu (bestiary, Swell fill modes) | Escape in the field | B / Circle |
| Battle menus | Up / Down / Left / Right, Enter, Escape | D-pad, A, B |

In battle, the timeline on the right shows who acts next. Highlighting a command previews how it changes the order. Swap brings Toma in from the reserve. In the Drownbell fight, the panel at the top left says what the bell is building toward (the Toll and how many of its turns away it is), how many rim hits you've landed, and later how many polyps feed it.

Debug keys (editor runs only): **F1** lists the debug pages. **F4** shows the story flags and **F5** teleports. They're useful if you get stuck.

## Known placeholders and limits

- People are capsules, apart from Asha, who stands in a rest pose because she has no animations yet. Asha's face does change: her expression follows each line's emotion, and her mouth moves as her text appears. Body animations are still missing.
- The music is a prototype stand-in: the hush theme sketch plays on the beach and in Haluna, the temple cue plays at the shrine, and the hush theme v2 plays for the verse. Nobody has signed off on any of them.
- The glimmer motes in the cutscenes are simple glowing dots, not the real particle effect.
- Haluna's world is the art team's scene, now shipped with the zone, with simple collision added. The camera mostly follows Rhen from behind; only a few spots use composed shots.
- Osu's wall at the causeway head is a grey stand-in with shells (the real wake-shell wall piece is still to be placed), and the night has no colour grade of its own yet.
- Ilun is a placeholder shape, and his call has no cinematic yet. The bell and polyps are placeholder shapes too.
- Entering Haluna holds the black fade for about a second and a half while the village builds itself; the picture no longer freezes when it appears.
- In the field, Escape opens the field menu, which pauses the game. From it you can open the bestiary or choose each hero's Swell fill mode. Escape backs out a step at a time and then closes it. It doesn't open during a cutscene or a conversation. **E** also advances dialogue.

## Reporting

Write a line per issue: what you did, what you saw, and what you expected. Screenshots help (Windows + Shift + S). Small impressions count too: "this part felt long" is useful.
