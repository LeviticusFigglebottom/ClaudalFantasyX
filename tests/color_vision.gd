class_name TestColorVision
extends RefCounted
## Colour-vision helpers for tests (M2-UI-11, M2-UI-30): Machado et al. (2009) simulation matrices
## on linear RGB, Oklab (Björn Ottosson) for perceptual distance, and the WCAG contrast ratio.


## `c` (sRGB) as seen through `m` (a 3x3 matrix on linear RGB), returned in linear RGB.
static func sim(c: Color, m: Array) -> Color:
	var l := c.srgb_to_linear()
	var v := [l.r, l.g, l.b]
	var out: Array[float] = []
	for row: Array in m:
		out.append(clampf(float(row[0]) * v[0] + float(row[1]) * v[1] + float(row[2]) * v[2], 0.0, 1.0))
	return Color(out[0], out[1], out[2])


## Linear RGB -> Oklab.
static func oklab(lin: Color) -> Vector3:
	var l := pow(0.4122214708 * lin.r + 0.5363325363 * lin.g + 0.0514459929 * lin.b, 1.0 / 3.0)
	var m := pow(0.2119034982 * lin.r + 0.6806995451 * lin.g + 0.1073969566 * lin.b, 1.0 / 3.0)
	var s := pow(0.0883024619 * lin.r + 0.2817188376 * lin.g + 0.6299787005 * lin.b, 1.0 / 3.0)
	return Vector3(
		0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
		1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
		0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
	)


## WCAG contrast ratio of two opaque sRGB colours.
static func contrast(a: Color, b: Color) -> float:
	var la := luma(a)
	var lb := luma(b)
	return (maxf(la, lb) + 0.05) / (minf(la, lb) + 0.05)


static func luma(c: Color) -> float:
	var l := c.srgb_to_linear()
	return 0.2126 * l.r + 0.7152 * l.g + 0.0722 * l.b
