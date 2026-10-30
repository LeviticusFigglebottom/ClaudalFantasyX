# Ridge lynx (`ridge_lynx`), Ch12

**Where:** Keth Pass. **Kind:** beast. **Role:** a quick pouncer that strikes the **back row** first (formation
matters).

**The idea:** a high-pass lynx in its thick winter coat. Ordinary, hungry, beautiful: the first foe in Act II that
is only an animal in a hard winter. The one exaggeration: **the pounce** (it clears the front row in one leap).

**Silhouette:** a long-legged cat, 0.75 m at the shoulder, with big snowshoe paws, a short tail, ear tufts and a
ruff. It crouches low before the leap, and that crouch is the telegraph.

**Palette:** coat `overcast_slate` going `cumulus_shadow` on the belly, faint `lacquer_black` spots; ear tufts and
tail tip `lacquer_black`; eyes `dusk_gold`; dry snow on the ruff tips and settled along the back, scree grit in the paws (snow `#E8E6DF`, no frost or rime: ADR 0015, ADR 0204 §2, M4-CRE-670); weak point (an old wound on the
flank where a herder's sling caught it) `spawn_wound`, small.

**Clips:** `idle` (tail flick, ears turn, a breath that steams); `attack` (the crouch, then the leap over the
front row: contact 0.7 s of 1.4 s); `cast` (a yowl that shakes the snow off the rocks); `hit` (it twists aside;
peak near 0.1 s); `ko` (it limps two steps and lies down in the snow). Budget ≤ 8k triangles. Rig: a quadruped
(spine 4, neck 2, head, jaw, four legs of 3, tail 3).

**Polish for the battle read (M3-CRE-645, from the approved PC render fce2e82).** The first muzzle, an ellipsoid, read
short and pug-like at review distance. What changed, within the 8k budget (6,988 to 7,304 triangles; the bones, clip
names and contact times are unchanged):
- **A wedge muzzle:** a lofted, squared section from the brow to a blunt front about 4 cm further out, narrowing from
  above and from the side, coat on top and pale below.
- **A cat's nose and mouth:** a dark nose leather (a rounded triangle, broad at the top), pale full whisker pads with
  rows of dark whisker spots, four pale snow-white whiskers a side swept back along the cheek, a dark mouth line from
  the nose down between the pads and back under them, and a longer chin.
- **The ear tufts** are kept as they were.
- **The KO:** the head turns a little less than the neck as it lies down (its yaw on the head bone halved), so the
  longer muzzle lies on the snow, not in it.
- The weak point is unchanged: the one small sling-wound slit on the camera-side flank (ADR 0151).

## Leg shaping (2026-10-30, ADR 0205)
The legs read as plain rounded cylinders up close. Each is now flatter side to side (0.8 of its depth) and shaped
along its length: the shoulder's or haunch's muscle at the top, a forearm or gaskin swelling below the elbow or
stifle, a slim wrist or hock, and the pastern widening into the snowshoe paw. The tube starts inside the torso, so no
rim shows where the leg meets the body. The four toes stand up out of the pad's fur as knuckles, creased where they
meet. 7,544 triangles (budget 8k).
