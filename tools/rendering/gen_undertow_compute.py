#!/usr/bin/env python3
"""Generates the compute storm body's uniform block from the spatial body's uniforms (M2-RND-01).

The raymarch (game/shaders/undertow/undertow_body_march.gdshaderinc) runs in two places: the spatial body
(uniforms declared with hints and defaults in undertow_common_uniforms / undertow_body_uniforms) and the
compute body (undertow_body_compute*.glsl, a CompositorEffect), which needs the same names as members
of one std140 uniform block. This script reads the uniform declarations, the one source of truth, and writes:

- game/shaders/undertow/undertow_compute_params.glslinc: the std140 block, members in declaration order;
- game/vfx/undertow/undertow_compute_layout.gd: UndertowComputeLayout, each member's type, byte offset
  and the declaration's default, which UndertowBodyEffect packs into the buffer;
- game/shaders/undertow/undertow_body_compute_flat.glslinc: undertow_body_compute.glslinc with its
  includes resolved, which the compute variants include;
- game/shaders/undertow/undertow_body*_compute.glsl: the compute variants, one per spatial tier variant.

Usage:
    python3 tools/rendering/gen_undertow_compute.py          # write both files
    python3 tools/rendering/gen_undertow_compute.py --check  # exit 1 when either is stale (tested)
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHADERS = ROOT / "game" / "shaders" / "undertow"
SOURCES = (SHADERS / "undertow_common_uniforms.gdshaderinc", SHADERS / "undertow_body_uniforms.gdshaderinc")
COMMON = SHADERS / "undertow_common.gdshaderinc"
OUT_GLSL = SHADERS / "undertow_compute_params.glslinc"
OUT_GD = ROOT / "game" / "vfx" / "undertow" / "undertow_compute_layout.gd"
# Godot's .glsl importer expands one level of #include only, so the compute variants include a
# flattened copy of the compute body: every nested include resolved once, in order.
COMPUTE_BODY = SHADERS / "undertow_body_compute.glslinc"
OUT_FLAT = SHADERS / "undertow_body_compute_flat.glslinc"
# The spatial tier variants, each with a compute twin of the same macros: undertow_body.gdshader ->
# undertow_body_compute.glsl. Each twin carries the flattened body's hash, so editing any file it
# includes changes the twin itself, and Godot re-imports it (the importer tracks the .glsl only).
VARIANTS = ("undertow_body", "undertow_body_medium", "undertow_body_ultra")
INCLUDE_RE = re.compile(r'^\s*#include\s+"res://([^"]+)"\s*$')

# Members the spatial body gets from Godot rather than from its uniforms:
# - hymn_sun_direction: the global uniform (globals.gdshaderinc), filled from ShaderGlobals;
# - the view (filled per frame on the render thread by UndertowBodyEffect): the inverse projection, the
#   camera's world transform, and the sizes in pixels of the output and of the depth buffer it reads.
EXTRA = (
    ("vec3", "hymn_sun_direction", None, "vec3(0.0, 1.0, 0.0)"),
    ("mat4", "view_inv_projection", None, None),
    ("mat4", "view_camera", None, None),
    ("vec2", "view_out_size", None, None),
    ("vec2", "view_depth_size", None, None),
)

UNIFORM_RE = re.compile(
    r"^\s*uniform\s+(?:highp\s+|mediump\s+|lowp\s+)?(\w+)\s+(\w+)\s*(?:\[(\w+)\])?\s*(?::([^=;]*))?(?:=\s*([^;]+))?;",
    re.M,
)
DEFINE_RE = re.compile(r"^#define\s+(\w+)\s+(\d+)\s*$", re.M)
# std140: (base alignment, size) in bytes; arrays of vec4 have a 16-byte stride.
STD140 = {"float": (4, 4), "int": (4, 4), "vec2": (8, 8), "vec3": (16, 12), "vec4": (16, 16), "mat4": (16, 64)}
# Uniforms with the source_color hint: Godot converts their Color from sRGB to linear before the
# spatial shader sees it, so the packer must too.
SRGB: set[str] = set()
SAMPLERS = ("sampler2D", "sampler3D", "isampler2D", "usampler2D", "sampler2DArray")


Field = tuple[str, str, "int | None", "str | None"]
Row = tuple[str, str, int, "int | None", "str | None"]


def parse() -> list[Field]:
    """(type, name, array length or None, default text or None) for every non-sampler uniform."""
    defines = {k: int(v) for k, v in DEFINE_RE.findall(COMMON.read_text(encoding="utf-8"))}
    out: list[Field] = []
    for src in SOURCES:
        text = re.sub(r"//[^\n]*", "", src.read_text(encoding="utf-8"))
        for typ, name, arr, hints, default in UNIFORM_RE.findall(text):
            if typ in SAMPLERS:
                continue
            if typ not in STD140:
                raise SystemExit(f"{src.name}: uniform {name}: type {typ} has no std140 rule here")
            n = None
            if arr:
                n = int(arr) if arr.isdigit() else defines[arr]
                if typ != "vec4":
                    raise SystemExit(f"{src.name}: uniform {name}: only vec4 arrays are packed")
            if "source_color" in hints:
                SRGB.add(name)
            out.append((typ, name, n, default.strip() if default else None))
    for typ, name, n, default in EXTRA:
        out.append((typ, name, n, default))
    return out


def layout(fields: list[Field]) -> tuple[list[Row], int]:
    rows = []
    off = 0
    for typ, name, n, default in fields:
        align, size = STD140[typ]
        if n is not None:
            align, size = 16, 16 * n
        off = (off + align - 1) // align * align
        rows.append((typ, name, off, n, default))
        off += size
    return rows, (off + 15) // 16 * 16


def gd_default(typ: str, default: str | None) -> str:
    if default is None:
        zero = {"float": "0.0", "int": "0", "vec2": "Vector2.ZERO", "vec3": "Vector3.ZERO", "vec4": "Vector4.ZERO"}
        return zero.get(typ, "Projection.IDENTITY")
    if typ == "float":
        return repr(float(default))
    if typ == "int":
        return str(int(default))
    args = default[default.index("(") + 1 : default.rindex(")")] if "(" in default else default
    nums = [float(x) for x in args.split(",")]
    if typ == "vec3":
        nums = nums * 3 if len(nums) == 1 else nums
        return "Vector3(%s)" % ", ".join(repr(x) for x in nums)
    if typ == "vec4":
        nums = nums * 4 if len(nums) == 1 else nums
        return "Vector4(%s)" % ", ".join(repr(x) for x in nums)
    raise SystemExit(f"no default rule for {typ}")


def flatten(path: Path, seen: set[Path], generated: dict[Path, str]) -> list[str]:
    """path's lines with each `#include "res://..."` replaced by that file, flattened (each file once)."""
    out: list[str] = []
    text = generated[path] if path in generated else path.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = INCLUDE_RE.match(line)
        if m is None:
            out.append(line)
            continue
        inc = ROOT / m.group(1)
        if inc in seen:
            continue
        seen.add(inc)
        out.append(f"// ---- {m.group(1)} ----")
        out += flatten(inc, seen, generated)
        out.append(f"// ---- end {m.group(1)} ----")
    return out


def render_flat(glsl: str) -> str:
    head = [
        "// GENERATED by tools/rendering/gen_undertow_compute.py. Do not edit.",
        "// Source: undertow_body_compute.glslinc with every #include resolved (Godot's .glsl importer",
        "// expands one level only).",
    ]
    body = flatten(COMPUTE_BODY, {COMPUTE_BODY}, {OUT_GLSL: glsl})
    return "\n".join(head + body) + "\n"


def render_twin(variant: str, flat: str) -> str:
    src = (SHADERS / f"{variant}.gdshader").read_text(encoding="utf-8")
    tier = variant.removeprefix("undertow_body").removeprefix("_").upper() or "HIGH"
    digest = hashlib.sha1(flat.encode("utf-8")).hexdigest()[:12]
    lines = [
        "#[compute]",
        "#version 450",
        "// GENERATED by tools/rendering/gen_undertow_compute.py. Do not edit.",
        f"// The storm body as a compute pass, {tier} tier (M2-RND-01): the compute twin of {variant}.gdshader,",
        "// with its tier macros. Body: undertow_body_compute.glslinc, flattened into",
        f"// undertow_body_compute_flat.glslinc (sha1 {digest}).",
    ]
    lines += [ln for ln in src.splitlines() if ln.startswith("#define ")]
    lines.append('#include "res://game/shaders/undertow/undertow_body_compute_flat.glslinc"')
    return "\n".join(lines) + "\n"


def render() -> tuple[str, str]:
    rows, size = layout(parse())
    sources = " and ".join(s.name for s in SOURCES)
    glsl = [
        "// GENERATED by tools/rendering/gen_undertow_compute.py. Do not edit.",
        "// Source: " + sources + ".",
        "// The compute storm body's uniforms (M2-RND-01): the spatial body's uniforms as one std140 block, so the",
        "// shared march (undertow_body_march.gdshaderinc) reads the same names. Packed by UndertowBodyEffect.",
        "",
        "layout(set = 0, binding = 0, std140) uniform UndertowParams {",
    ]
    for typ, name, off, n, _default in rows:
        decl = f"{typ} {name}[{n}]" if n is not None else f"{typ} {name}"
        glsl.append(f"\t{decl}; // offset {off}")
    glsl += ["};", ""]
    gd = [
        "# GENERATED by tools/rendering/gen_undertow_compute.py. Do not edit.",
        "# Source: " + sources + ".",
        "class_name UndertowComputeLayout",
        "extends RefCounted",
        "## The compute storm body's std140 uniform block (M2-RND-01): one row per member, in block order.",
        "## Row = [name, type, byte offset, array length (0 = not an array), the declaration's default,",
        "## true when it is a source_color (pack the Color converted from sRGB to linear, as Godot does)].",
        "",
        f"const SIZE := {size}",
        "const FIELDS: Array = [",
    ]
    for typ, name, off, n, default in rows:
        srgb = "true" if name in SRGB else "false"
        gd.append(f'\t["{name}", "{typ}", {off}, {n or 0}, {gd_default(typ, default)}, {srgb}],')
    gd += ["]", ""]
    return "\n".join(glsl), "\n".join(gd)


def main(argv: list[str]) -> int:
    glsl, gd = render()
    flat = render_flat(glsl)
    twins = [(SHADERS / f"{v}_compute.glsl", render_twin(v, flat)) for v in VARIANTS]
    if "--check" in argv:
        outs = [(OUT_GLSL, glsl), (OUT_GD, gd), (OUT_FLAT, flat)] + twins
        stale = [p for p, t in outs if not p.is_file() or p.read_text(encoding="utf-8") != t]
        for p in stale:
            print(f"stale: {p.relative_to(ROOT)} (run tools/rendering/gen_undertow_compute.py)")
        return 1 if stale else 0
    for p, t in [(OUT_GLSL, glsl), (OUT_GD, gd), (OUT_FLAT, flat)] + twins:
        p.write_text(t, encoding="utf-8", newline="\n")
        print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
