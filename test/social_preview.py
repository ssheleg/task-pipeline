#!/usr/bin/env python3
"""Check the committed GitHub social-preview asset without image dependencies."""

from pathlib import Path
import struct

path = Path("docs/assets/social-preview.png")
data = path.read_bytes()
signature = b"\x89PNG\r\n\x1a\n"
if not data.startswith(signature):
    raise SystemExit(f"{path}: not a PNG")
if len(data) >= 1_000_000:
    raise SystemExit(f"{path}: {len(data)} bytes, GitHub requires under 1 MB")
if data[12:16] != b"IHDR":
    raise SystemExit(f"{path}: IHDR is not the first chunk")
width, height = struct.unpack(">II", data[16:24])
if (width, height) != (1200, 630):
    raise SystemExit(f"{path}: {width}x{height}, expected 1200x630")
print(f"OK: {path} is {width}x{height}, {len(data)} bytes")

