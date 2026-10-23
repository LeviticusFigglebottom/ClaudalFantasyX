#!/usr/bin/env python3
"""Pre-integrated skin diffuse (Penner & Borshukov 2011) reference and the analytic fit used by
game/shaders/character/character_brdf.gdshaderinc (M1-RND-04).

The reference integrates a clamped cosine over a ring of radius R (the local curvature radius)
weighted by a sum-of-Gaussians diffusion profile:

    D(theta, R) = int cos+(theta + x) P(2 R sin(x / 2)) dx / int P(2 R sin(x / 2)) dx

P is the six-Gaussian skin profile published by d'Eon & Luebke (GPU Gems 3, ch. 14, table 14-1;
variances in mm^2 and per-channel weights), which is measured scientific data, not an asset.
`scatter_radius_mm` rescales the profile (art direction: Asha 2.5 mm => scale 2.5 / 1.0).

The shader cannot afford a 6-Gaussian convolution, and we do not want a LUT texture binding in
light(), so each channel is fitted with a normalised hyperbolic soft ramp:

    D_c(x, u) = s_c (x + sqrt(x^2 + q_c^2)) / (1 + sqrt(1 + q_c^2))
    q_c = a_c u + b_c u^2        (terminator softness)
    s_c = 1 + c_c u + d_c u^2    (lit-side energy that the profile moves into the shadow)

where x = N.L and u = profile_scale / R (dimensionless "scatter curvature"). A soft ramp is the
shape a Gaussian blur gives a clamped linear function, so one parameter per channel captures
most of the profile. Run:

    python3 assets_src/characters/shader_test/preintegrated_skin_fit.py [--png out.png]

It prints the fitted a..d per channel and the max / RMS error over the fitted domain. The constants
are pasted into HYMN_SKIN_PREINT_A.._D in character_brdf.gdshaderinc, and
tests/unit/test_character_shading.gd checks that the shader still carries exactly these values
(FIT_EXPECTED below). Re-run and update both together if the profile or the model changes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

# d'Eon & Luebke 2007, table 14-1: variance (mm^2), then R, G, B weights.
PROFILE = np.array(
    [
        [0.0064, 0.233, 0.455, 0.649],
        [0.0484, 0.100, 0.336, 0.344],
        [0.187, 0.118, 0.198, 0.000],
        [0.567, 0.113, 0.007, 0.007],
        [1.99, 0.358, 0.004, 0.000],
        [7.41, 0.078, 0.000, 0.000],
    ]
)

U_MAX = 2.0  # fitted domain of u = scale / R (2.5 mm scale: cheek ~0.06, nose ~0.3, ear rim ~1.2)
N_THETA = 181
N_U = 41
N_X = 4097  # integration samples over x in (-pi, pi]

# Constants as committed to the shader (rounded). The test compares against these.
FIT_EXPECTED = {
    "a": (0.2606, 0.0922, 0.0688),
    "b": (-0.0592, 0.0054, 0.0028),
    "c": (-0.0671, -0.0011, -0.0005),
    "d": (0.0064, -0.0135, -0.0072),
}
N_Q = 801  # grid for the per-row q search


def profile(r_mm: np.ndarray, channel: int) -> np.ndarray:
    v = PROFILE[:, 0][:, None]
    w = PROFILE[:, 1 + channel][:, None]
    g = np.exp(-(r_mm[None, :] ** 2) / (2.0 * v)) / (2.0 * np.pi * v)
    return (w * g).sum(axis=0)


def reference(theta: np.ndarray, u: np.ndarray) -> np.ndarray:
    """D[c, iu, itheta] for curvature parameter u (profile scale 1 mm, so R = 1 / u mm)."""
    x = np.linspace(-np.pi, np.pi, N_X)
    out = np.zeros((3, u.size, theta.size))
    for c in range(3):
        for iu, uu in enumerate(u):
            if uu <= 1e-6:
                out[c, iu] = np.maximum(np.cos(theta), 0.0)
                continue
            radius = 1.0 / uu
            w = profile(np.abs(2.0 * radius * np.sin(x / 2.0)), c)
            cosp = np.maximum(np.cos(theta[:, None] + x[None, :]), 0.0)
            out[c, iu] = (cosp * w[None, :]).sum(axis=1) / w.sum()
    return out


def model(ndl: np.ndarray, q: np.ndarray) -> np.ndarray:
    return (ndl + np.sqrt(ndl * ndl + q * q)) / (1.0 + np.sqrt(1.0 + q * q))


def fit_row(ndl: np.ndarray, target: np.ndarray, grid: np.ndarray) -> tuple[float, float]:
    """Best (q, s) for one (channel, u) row: exhaustive q grid, closed-form least-squares s."""
    h = model(ndl[None, :], grid[:, None])
    s = (h * target).sum(axis=1) / np.maximum((h * h).sum(axis=1), 1e-12)
    err = ((s[:, None] * h - target) ** 2).sum(axis=1)
    k = int(err.argmin())
    return float(grid[k]), float(s[k])


def evaluate(ndl: np.ndarray, u: float, a: float, b: float, c: float, d: float) -> np.ndarray:
    return (1.0 + c * u + d * u * u) * model(ndl, a * u + b * u * u)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", help="write a reference-vs-fit comparison image here")
    args = ap.parse_args(argv)
    theta = np.linspace(0.0, np.pi, N_THETA)
    u = np.linspace(0.0, U_MAX, N_U)
    ref = reference(theta, u)
    ndl = np.cos(theta)
    grid = np.linspace(0.0, 2.0, N_Q)
    coeffs = []
    fitted = np.zeros_like(ref)
    m = np.stack([u, u * u], axis=1)
    for c in range(3):
        rows = [fit_row(ndl, ref[c, iu], grid) for iu in range(u.size)]
        q = np.array([r[0] for r in rows])
        sc = np.array([r[1] for r in rows])
        # Least squares without a constant term: u = 0 must give exactly the clamped cosine.
        (a, b), *_ = np.linalg.lstsq(m, q, rcond=None)
        (cc, dd), *_ = np.linalg.lstsq(m, sc - 1.0, rcond=None)
        coeffs.append((float(a), float(b), float(cc), float(dd)))
        for iu in range(u.size):
            fitted[c, iu] = evaluate(ndl, u[iu], a, b, cc, dd)
    err = fitted - ref
    names = "RGB"
    for c in range(3):
        print(
            f"{names[c]}: a={coeffs[c][0]:.4f} b={coeffs[c][1]:.4f} c={coeffs[c][2]:.4f} d={coeffs[c][3]:.4f}  "
            f"max |err| = {np.abs(err[c]).max():.4f}  rms = {np.sqrt((err[c] ** 2).mean()):.4f}"
        )
    for k, name in enumerate("ABCD"):
        print(f"#define HYMN_SKIN_PREINT_{name} vec3(%.4f, %.4f, %.4f)" % tuple(c[k] for c in coeffs))
    if args.png:
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "screenshots"))
        import pngio  # noqa: E402  (repo-local PNG writer, no Pillow)

        # Left half: reference LUT (x = N.L from -1..1, y = u from 0 at the bottom); right: fit.
        def to_img(d: np.ndarray) -> np.ndarray:
            img = np.transpose(d, (1, 2, 0))[::-1, ::-1]  # u up, N.L left->right
            srgb = np.where(img <= 0.0031308, img * 12.92, 1.055 * np.power(np.clip(img, 0, 1), 1 / 2.4) - 0.055)
            return (np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)

        pngio.write(args.png, np.concatenate([to_img(ref), to_img(fitted)], axis=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
