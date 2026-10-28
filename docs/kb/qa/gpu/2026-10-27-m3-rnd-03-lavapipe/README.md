# M3-RND-03 on lavapipe (PC, 2026-10-27): Sefir's tells on and off

These are lavapipe renders (WSL2, `LLVM 22.1.8, 256 bits`) of gpu/m3-rnd-03-sefir-tells @ 02d1fa52, captured by
tests/screenshots/capture.tscn from a complete import (exit 0 and the DONE line).
The 4 shots have no baselines yet. Approve them after viewing (`compare.py --update-baselines revenant_tells_*`).

- `revenant_tells_shadow.png` has both tells on, and `_off` has both off (the setup nodes switch RevenantTells).
  With them on, Sefir's shadow and his hand shadows have crisper edges than Asha's. A tighter contact line runs along his hem
  (`shadow_hem_on_off.png`, 4x). Elsewhere nothing changes: the twin pair cancels, so no area is lit twice. The black
  shadow that the spot-light version showed under capture.tscn is gone.
- `revenant_tells_reflection.png` and `_off` show the brine water. The on/off difference (`on_off_diff_x8.jpg`, difference
  times 8) sits on the edges of Sefir's reflection and at the waterline under the heroes. With the tell on, his reflection
  holds its outline where the ripples would break it. The test scene's small wave makes the difference subtle at this
  framing. It shows best on the GPU, in motion.
- Asha's reflection and shadow keep their soft look. The only changes near her come from Sefir's own shadow and reflection overlapping hers.

Owners to view: rendering (this track), env-art (M3-ENV-1000 depends on this), art.
