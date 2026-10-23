# Playtest: the First Playable (Windows)

This is a rough but complete thread through the first minutes of *Hymn of the Undertow*. Most of what you see is placeholder: capsules stand in for people (Asha is the only real model, and she has no animations yet), the Shell Shrine is grey stone primitives, and the music uses the three prototype cues in place of the scenes' own. **The point is to feel the flow.** Please note anything that confuses you, drags, or feels wrong.

## What you play (about 10–15 minutes)

1. **Title.** Choose **New Game**.
2. **Prologue.** A dead city at dusk, with one line of Rhen's narration.
3. **Cutscene A, "The Girl on the Beach".** Rhen wakes in the shallows at Haluna. There are two choices; both are fine.
4. **Haluna, free to walk.** Talk to the three villagers (at the market, the chapel court and the dock). Each one has a line that hints at what a "Cantor" is.
5. **First battle.** Walking up the beach path toward the village starts a fight against a reef crab and a lantern eel, with Rhen and Asha (Toma in reserve). Win it, and you return to the beach path.
6. **Save** at the shrine: the glowing teal stone with a shell canopy, near the beach palms. Resting there heals the party and opens the save menu.
7. **The causeway head.** Once you have saved, walk north along the beach, past the dock, to the causeway head at its far end. This plays **Cutscene B, "The First Verse"**, at the Shell Shrine at sunset.
8. **End card.** Press accept to return to the title. **Continue** loads your save.

## Running it

### Option A: the Godot editor (recommended)

1. Download **Godot 4.6.3 stable**, the standard build (not .NET), for Windows: <https://godotengine.org/download/archive/4.6.3-stable/>. Unzip it anywhere. There is no installer.
2. Get the project: clone the repository, or download the `claude/first-playable` branch as a ZIP from GitHub and unzip it.
3. Run `Godot_v4.6.3-stable_win64.exe`. In the Project Manager, click **Import**, choose the repository's `project.godot`, and click **Import & Edit**.
4. **The first open imports every asset, which takes a few minutes.** Wait until the progress bar at the bottom of the editor finishes.
5. Press **F5** (or the ▶ "Run Project" button at the top right). The game starts at the title.

To close the game, press **Alt+F4**, or click ■ Stop in the editor. **F8** also stops it from the editor.

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
| Battle menus | Up / Down / Left / Right, Enter, Escape | D-pad, A, B |

In battle, the timeline on the right shows who acts next. Highlighting a command previews how it changes the order. Swap brings Toma in from the reserve.

Debug keys (editor runs only): **F1** lists the debug pages. **F4** shows the story flags and **F5** teleports. They're useful if you get stuck.

## Known placeholders and limits

- People are capsules, apart from Asha, who stands in a rest pose because she has no animations yet. Asha's face does change: her expression follows each line's emotion, and her mouth moves as her text appears. Body animations are still missing.
- The music is a prototype stand-in: the hush theme sketch plays on the beach and in Haluna, the temple cue plays at the shrine, and the hush theme v2 plays for the verse. Nobody has signed off on any of them.
- The glimmer motes in the cutscenes are simple glowing dots, not the real particle effect.
- Haluna uses the art team's mood-test scene, with simple collision added. The camera mostly follows Rhen from behind; only a few spots use composed shots.
- Cutscene B ends with the bell tolling and a call to battle. **The Drownbell boss isn't built yet**, so the end card comes next.
- Entering Haluna freezes for about a second and a half behind the black fade while the village builds itself. That's expected for now.
- After a lost battle you return past the trigger, so the fight can be skipped by walking on. Walking back down to the beach and up again offers it once more.

## Reporting

Write a line per issue: what you did, what you saw, and what you expected. Screenshots help (Windows + Shift + S). Small impressions count too: "this part felt long" is useful.
