class_name PellNameShell
extends RefCounted
## Pell's name-shell (M3-CHR-506, pell.md §3 and §4.1 #3): his GLB carries both states of the shell on its throat cord,
## `NameShellBlank` (the shell he has worn since he lost his name) and `NameShellCarved` (the spiral of notches carved
## after Ch9, from assets_src/characters/pell/motifs/pell_name.json). Exactly one is visible at a time; the blank one is
## the default. Scene owners call `apply` when the story flag changes; the cord (`NameShell`) stays visible in both.

const BLANK := &"NameShellBlank"
const CARVED := &"NameShellCarved"


## Shows the carved shell (`carved`) or the blank one under `root` (a Pell model or any scene holding one); returns
## how many shell meshes it found (2 for one Pell, 0 when there is none under root).
static func apply(root: Node, carved: bool) -> int:
	var found := 0
	for name: StringName in [BLANK, CARVED]:
		for node: Node in root.find_children(String(name), "Node3D", true, false):
			(node as Node3D).visible = (name == CARVED) == carved
			found += 1
	return found


## Whether the carved shell is the one showing under `root` (false when there is no Pell under it).
static func is_carved(root: Node) -> bool:
	for node: Node in root.find_children(String(CARVED), "Node3D", true, false):
		return (node as Node3D).visible
	return false
