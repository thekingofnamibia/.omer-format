# .omer File Format Specification (v1)

A simple, real, binary image container format. "OMER" = magic signature.

## Layout

| Offset | Size      | Field           | Notes                                      |
|--------|-----------|-----------------|---------------------------------------------|
| 0      | 4 bytes   | Magic           | ASCII `"OMER"` (0x4F 0x4D 0x45 0x52)        |
| 4      | 1 byte    | Version         | Format version, currently `1`               |
| 5      | 4 bytes   | Width           | uint32, little-endian, pixels               |
| 9      | 4 bytes   | Height          | uint32, little-endian, pixels               |
| 13     | 1 byte    | Channels        | `3` = RGB, `4` = RGBA                       |
| 14     | 1 byte    | Compression     | `0` = raw, `1` = zlib                       |
| 15     | 4 bytes   | Metadata length | uint32, little-endian, bytes of UTF-8 JSON  |
| 19     | N bytes   | Metadata        | UTF-8 JSON blob (title, author, date, etc.) |
| 19+N   | 4 bytes   | Pixel data length | uint32, little-endian, bytes that follow  |
| 23+N   | M bytes   | Pixel data      | Raw or zlib-compressed row-major pixels     |

Pixel data, once decompressed, is tightly packed row-major pixels,
`width * height * channels` bytes, one byte per channel, no padding,
no alpha premultiplication.

## Design choices & why

- **Magic bytes first**: lets any tool (including the Unix `file` command,
  if you add a rule for it) identify a `.omer` file by sniffing the header,
  the same way PNG/JPEG do.
- **Version byte early**: so a future v2 decoder can detect and handle v1
  files without guessing.
- **Metadata as JSON**: flexible and human-inspectable without needing a
  binary schema — you can `strings` a `.omer` file and read the metadata.
- **Optional zlib compression**: keeps files small for photos without
  requiring a full codec; falls back to raw storage if compression doesn't
  help (e.g. already-noisy image data).

## Minimal example (conceptual)

```
4F 4D 45 52          "OMER"
01                   version 1
20 00 00 00          width = 32
20 00 00 00          height = 32
03                   channels = RGB
01                   compression = zlib
1A 00 00 00          metadata length = 26
{"title":"test.png"}  <- 26 bytes of JSON (example)
xx xx xx xx          pixel data length
... compressed pixel bytes ...
```

This is a teaching/demo format — good for learning how real image formats
like PNG or BMP are structured, not intended to compete with them on
compression efficiency (PNG's DEFLATE + filtering beats plain zlib on
photos).
