"""Minimal PNG reader/writer on numpy + zlib (no Pillow), for screenshot regression (M1-QA-01).

Reads what Godot's Image.save_png writes: 8- or 16-bit, non-interlaced, greyscale / grey+alpha /
RGB / RGBA (plus 8-bit palette for good measure), all five scanline filters. Writes 8-bit RGB or
greyscale with filter 0. Returns arrays shaped (height, width, channels), dtype uint8 or uint16.
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np

SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}  # PNG colour type -> samples per pixel


class PngError(ValueError):
    pass


def _chunks(data: bytes):
    if data[:8] != SIGNATURE:
        raise PngError("not a PNG file")
    pos = 8
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if len(body) != length:
            raise PngError("truncated chunk")
        yield kind, body
        pos += 12 + length
        if kind == b"IEND":
            return
    raise PngError("missing IEND")


def _paeth_row(row: bytearray, prev: bytes, bpp: int) -> None:
    for i in range(len(row)):
        a = row[i - bpp] if i >= bpp else 0
        b = prev[i]
        c = prev[i - bpp] if i >= bpp else 0
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        if pa <= pb and pa <= pc:
            pred = a
        elif pb <= pc:
            pred = b
        else:
            pred = c
        row[i] = (row[i] + pred) & 0xFF


def _avg_row(row: bytearray, prev: bytes, bpp: int) -> None:
    for i in range(len(row)):
        a = row[i - bpp] if i >= bpp else 0
        row[i] = (row[i] + ((a + prev[i]) >> 1)) & 0xFF


def _unfilter(raw: bytes, height: int, stride: int, bpp: int) -> np.ndarray:
    out = np.zeros((height, stride), dtype=np.uint8)
    prev = np.zeros(stride, dtype=np.uint8)
    for y in range(height):
        start = y * (stride + 1)
        ftype = raw[start]
        line = np.frombuffer(raw, dtype=np.uint8, count=stride, offset=start + 1)
        if ftype == 0:
            cur = line.copy()
        elif ftype == 1:  # Sub: running sum per byte lane, mod 256
            lanes = line.astype(np.uint32)
            pad = (-stride) % bpp
            lanes = np.concatenate([lanes, np.zeros(pad, np.uint32)]).reshape(-1, bpp)
            cur = (np.cumsum(lanes, axis=0) & 0xFF).astype(np.uint8).reshape(-1)[:stride]
        elif ftype == 2:  # Up
            cur = line + prev
        elif ftype in (3, 4):
            buf = bytearray(line.tobytes())
            (_avg_row if ftype == 3 else _paeth_row)(buf, prev.tobytes(), bpp)
            cur = np.frombuffer(bytes(buf), dtype=np.uint8)
        else:
            raise PngError(f"bad filter type {ftype} on row {y}")
        out[y] = cur
        prev = out[y]
    return out


def decode(data: bytes) -> np.ndarray:
    header = None
    palette = None
    idat = bytearray()
    for kind, body in _chunks(data):
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = np.frombuffer(body, dtype=np.uint8).reshape(-1, 3)
        elif kind == b"IDAT":
            idat += body
    if header is None:
        raise PngError("missing IHDR")
    width, height, depth, ctype, _comp, _filt, interlace = header
    if interlace:
        raise PngError("interlaced PNGs are not supported")
    if ctype not in CHANNELS or depth not in (8, 16) or (ctype == 3 and depth != 8):
        raise PngError(f"unsupported PNG: colour type {ctype}, bit depth {depth}")
    chans = CHANNELS[ctype]
    bpp = chans * depth // 8
    rows = _unfilter(zlib.decompress(bytes(idat)), height, width * bpp, bpp)
    if depth == 16:
        img = rows.view(">u2").astype(np.uint16).reshape(height, width, chans)
    else:
        img = rows.reshape(height, width, chans)
    if ctype == 3:
        if palette is None:
            raise PngError("palette image without PLTE")
        img = palette[img[:, :, 0]]
    return img


def read(path: Path | str) -> np.ndarray:
    return decode(Path(path).read_bytes())


def encode(img: np.ndarray) -> bytes:
    """8-bit greyscale (H, W) / (H, W, 1) or RGB (H, W, 3) -> PNG bytes (filter 0)."""
    arr = np.ascontiguousarray(img, dtype=np.uint8)
    if arr.ndim == 2:
        arr = arr[:, :, None]
    height, width, chans = arr.shape
    ctype = {1: 0, 3: 2, 4: 6}[chans]
    raw = np.concatenate([np.zeros((height, 1), np.uint8), arr.reshape(height, width * chans)], axis=1)

    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, ctype, 0, 0, 0)
    return SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw.tobytes(), 9)) + chunk(b"IEND", b"")


def write(path: Path | str, img: np.ndarray) -> None:
    Path(path).write_bytes(encode(img))
