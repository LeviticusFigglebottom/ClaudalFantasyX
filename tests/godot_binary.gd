class_name GodotBinary
extends RefCounted
## The Godot a test launches in a child process (a probe whose scene change would replace the runner's scene).
## $GODOT when set (not exported by tools/ci_local.sh, so often unset); else this executable when it is Godot
## itself; else, when this process was started through the loader of tools/dev/fetch_godot.py's sysroot
## (`<root>/sysroot/.../ld-linux-x86-64.so.2`: OS.get_executable_path() names the loader, which takes no Godot
## option: big37's red), that build's wrapper `<root>/godot`; else `godot` on PATH.

const ENV := "GODOT"
const NAME_HINT := "godot"
const ON_PATH := "godot"
const SYSROOT_DIR := "/sysroot/"
const WRAPPER := "godot"


static func path() -> String:
	var env := OS.get_environment(ENV)
	if env != "":
		return env
	var exe := OS.get_executable_path()
	if exe.get_file().to_lower().contains(NAME_HINT):
		return exe
	var at := exe.find(SYSROOT_DIR)
	if at >= 0:
		var wrapper := exe.substr(0, at).path_join(WRAPPER)
		if FileAccess.file_exists(wrapper):
			return wrapper
	return ON_PATH
