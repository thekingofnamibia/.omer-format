#!/usr/bin/env python3
"""
.omer file format — encoder / decoder / CLI converter.

Usage:
    python3 omer_format.py encode input.png output.omer [--title "My Photo"]
    python3 omer_format.py decode input.omer output.png
    python3 omer_format.py info input.omer

See OMER_SPEC.md for the full byte-level format definition.
"""

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

from PIL import Image

MAGIC = b"OMER"
VERSION = 1

COMPRESSION_NONE = 0
COMPRESSION_ZLIB = 1


def encode(image_path: str, output_path: str, title: str | None = None) -> None:
    img = Image.open(image_path)

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.mode or img.mode == "P" else "RGB")

    channels = 4 if img.mode == "RGBA" else 3
    width, height = img.size
    raw = img.tobytes()  # row-major, tightly packed

    compressed = zlib.compress(raw, level=9)
    if len(compressed) < len(raw):
        pixel_data = compressed
        compression = COMPRESSION_ZLIB
    else:
        pixel_data = raw
        compression = COMPRESSION_NONE

    meta = {
        "title": title or Path(image_path).stem,
        "source_format": img.format or "unknown",
    }
    meta_bytes = json.dumps(meta).encode("utf-8")

    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<B", VERSION))
        f.write(struct.pack("<I", width))
        f.write(struct.pack("<I", height))
        f.write(struct.pack("<B", channels))
        f.write(struct.pack("<B", compression))
        f.write(struct.pack("<I", len(meta_bytes)))
        f.write(meta_bytes)
        f.write(struct.pack("<I", len(pixel_data)))
        f.write(pixel_data)

    ratio = len(pixel_data) / len(raw) * 100
    print(f"Encoded {image_path} -> {output_path}")
    print(f"  {width}x{height}, {channels} channels, "
          f"{'zlib' if compression else 'raw'} "
          f"({len(pixel_data)} bytes, {ratio:.1f}% of raw {len(raw)} bytes)")


def decode(omer_path: str, output_path: str | None = None):
    with open(omer_path, "rb") as f:
        data = f.read()

    if data[0:4] != MAGIC:
        raise ValueError(f"Not a valid .omer file (bad magic bytes: {data[0:4]!r})")

    version = data[4]
    if version != VERSION:
        raise ValueError(f"Unsupported .omer version: {version}")

    width, = struct.unpack_from("<I", data, 5)
    height, = struct.unpack_from("<I", data, 9)
    channels = data[13]
    compression = data[14]
    meta_len, = struct.unpack_from("<I", data, 15)

    offset = 19
    meta_bytes = data[offset:offset + meta_len]
    meta = json.loads(meta_bytes.decode("utf-8"))
    offset += meta_len

    pixel_len, = struct.unpack_from("<I", data, offset)
    offset += 4
    pixel_data = data[offset:offset + pixel_len]

    if compression == COMPRESSION_ZLIB:
        raw = zlib.decompress(pixel_data)
    elif compression == COMPRESSION_NONE:
        raw = pixel_data
    else:
        raise ValueError(f"Unknown compression method: {compression}")

    mode = "RGBA" if channels == 4 else "RGB"
    img = Image.frombytes(mode, (width, height), raw)

    if output_path:
        img.save(output_path)
        print(f"Decoded {omer_path} -> {output_path} ({width}x{height})")

    return img, meta


def info(omer_path: str) -> None:
    with open(omer_path, "rb") as f:
        data = f.read()

    if data[0:4] != MAGIC:
        print("Not a valid .omer file")
        sys.exit(1)

    version = data[4]
    width, = struct.unpack_from("<I", data, 5)
    height, = struct.unpack_from("<I", data, 9)
    channels = data[13]
    compression = data[14]
    meta_len, = struct.unpack_from("<I", data, 15)
    meta = json.loads(data[19:19 + meta_len].decode("utf-8"))

    print(f"File:        {omer_path}")
    print(f"Version:     {version}")
    print(f"Dimensions:  {width} x {height}")
    print(f"Channels:    {channels} ({'RGBA' if channels == 4 else 'RGB'})")
    print(f"Compression: {'zlib' if compression else 'none'}")
    print(f"Metadata:    {meta}")
    print(f"File size:   {len(data)} bytes")


def main():
    parser = argparse.ArgumentParser(description="Convert to/from .omer image format")
    sub = parser.add_subparsers(dest="command", required=True)

    p_enc = sub.add_parser("encode", help="Convert an image (png/jpg/etc.) to .omer")
    p_enc.add_argument("input")
    p_enc.add_argument("output")
    p_enc.add_argument("--title", default=None)

    p_dec = sub.add_parser("decode", help="Convert a .omer file back to png/jpg/etc.")
    p_dec.add_argument("input")
    p_dec.add_argument("output")

    p_info = sub.add_parser("info", help="Print header/metadata of a .omer file")
    p_info.add_argument("input")

    args = parser.parse_args()

    if args.command == "encode":
        encode(args.input, args.output, args.title)
    elif args.command == "decode":
        decode(args.input, args.output)
    elif args.command == "info":
        info(args.input)


if __name__ == "__main__":
    main()
