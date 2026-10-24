#!/usr/bin/env bash
# M1-QA-10: isolated repro of the Godot 4.6.3 RenderingDevice vertex-format race (see M1-ARC-17).
# Usage: tools/dev/rd_vertex_format_race/run.sh forced [WORKDIR]   # deterministic, under gdb
#        tools/dev/rd_vertex_format_race/run.sh plain  [WORKDIR]   # free-running stress, no gdb
# forced: downloads the Ubuntu debug symbols for the pinned godot build (~450 MB, debuginfod) and
# patchelf (pip) into WORKDIR (default $TMPDIR/rd_vertex_format_race), makes a copy of godot whose
# ELF interpreter points at the sysroot so gdb treats it as the main program, and runs race_force.py.
# Exit 0 = the race reproduced (4.6.3); exit 1 = the error line was never reached (a fixed engine).
# Takes ~10 min: every engine pipeline compile is checked against a conditional breakpoint.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
mode="${1:-forced}"
work="${2:-${TMPDIR:-/tmp}/rd_vertex_format_race}"
cache="$HOME/.cache/hymn/godot-4.6.3+ds-2"
render="${HYMN_GODOT_RENDER:-$cache/godot-render}"
sysroot="$cache/sysroot"
build_id="f7bcf5186cd245063b93392f28d2764e5f38dc94"
mkdir -p "$work/xdg"
export XDG_DATA_HOME="$work/xdg" LP_NUM_THREADS="${LP_NUM_THREADS:-2}"
log="$work/race_$mode.log"

if [ "$mode" = "plain" ]; then
  "$render" --path "$here" --audio-driver Dummy --rendering-driver vulkan -- --mode=fast --formats=100000 > "$log" 2>&1 || true
  grep -E "QA10|vertex input location|vertex_formats" "$log" | sort | uniq -c
  exit 0
fi

dbg="$work/dbg"
mkdir -p "$dbg"
if [ ! -s "$dbg/godot.debug" ]; then
  curl -sSf --max-time 900 -o "$dbg/godot.debug" "https://debuginfod.ubuntu.com/buildid/$build_id/debuginfo"
fi
pe="$work/pe/x/patchelf-0.19.1.0.data/scripts/patchelf"
if [ ! -x "$pe" ]; then
  python3 -m pip download --no-deps -q -d "$work/pe" patchelf==0.19.1.0
  python3 -I -m zipfile -e "$work/pe"/patchelf-0.19.1.0-*.whl "$work/pe/x"
  chmod +x "$pe"
fi
cp "$sysroot/usr/bin/godot" "$dbg/godot-patched"
"$pe" --set-interpreter "$sysroot/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2" "$dbg/godot-patched"
libpath="$sysroot/usr/lib/x86_64-linux-gnu:$sysroot/lib/x86_64-linux-gnu:$sysroot/usr/lib/x86_64-linux-gnu/pulseaudio"
# The render wrapper's environment (Vulkan ICD, Xvfb, fonts), with gdb on the patched copy as its last line.
sed "s|^\"\$LOADER\" --library-path \"\$LIBPATH\" \"\$SYSROOT/usr/bin/godot\" \"\$@\"\$|gdb -q -batch -iex 'set startup-with-shell off' -iex 'set environment LD_LIBRARY_PATH=$libpath' -x '$here/race_force.py' --args '$dbg/godot-patched' \"\$@\"|" \
  "$render" > "$work/godot-render-gdb"
chmod +x "$work/godot-render-gdb"
grep -q "^gdb " "$work/godot-render-gdb" || { echo "could not derive the gdb wrapper from $render"; exit 2; }
QA10_DBG_DIR="$dbg" "$work/godot-render-gdb" --path "$here" --audio-driver Dummy --rendering-driver vulkan \
  -- --mode=forced --formats=5000 > "$log" 2>&1 || true
grep -E "^QA10|^ERROR: Shader vertex input|received signal|^\\$[0-9]+ = " "$log" | cut -c1-160 | uniq -c
if grep -q "^ERROR: Shader vertex input location (0) not provided" "$log"; then
  echo "race reproduced (log: $log)"
  exit 0
fi
echo "race NOT reproduced (log: $log)"
exit 1
