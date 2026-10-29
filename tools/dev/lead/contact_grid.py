#!/usr/bin/env python3
"""Lead tool: stack a gate's *_sheet.jpg contact sheets six to an image, so the Lead can VIEW every drifted or new
shot quickly. Usage: python3 tools/dev/lead/contact_grid.py <gate-run dir with *_sheet.jpg> <out dir>"""
import glob
import os
import sys

from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
sheets = sorted(glob.glob(os.path.join(src, "*_sheet.jpg")))
W = 1500
for gi in range(0, len(sheets), 6):
    parts = []
    for p in sheets[gi : gi + 6]:
        im = Image.open(p).convert("RGB")
        im = im.resize((W, int(im.height * W / im.width)))
        c = Image.new("RGB", (W, im.height + 22), "white")
        c.paste(im, (0, 22))
        ImageDraw.Draw(c).text((4, 4), os.path.basename(p)[: -len("_sheet.jpg")], fill="black")
        parts.append(c)
    g = Image.new("RGB", (W, sum(p.height for p in parts)), "white")
    y = 0
    for p in parts:
        g.paste(p, (0, y))
        y += p.height
    g.save(os.path.join(out, f"g{gi // 6:02d}.jpg"), quality=80)
print(len(sheets), "sheets ->", out)
