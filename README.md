# .omer

A small, real binary image format — built as a learning project, not a
PNG replacement. Includes a full spec, a Python encoder/decoder, and a
browser-based viewer that can also convert images to `.omer` directly —
no install required.

## What's in here

- **`OMER_SPEC.md`** — the byte-level format spec (header, metadata, pixel data)
- **`omer_viewer.html`** — standalone app: view `.omer` files *and* convert regular photos into `.omer`, all in the browser
- **`omer_format.py`** — Python CLI for the same conversions, useful for scripting/batch jobs
- **`sample.omer`** — a small test file to try the viewer with

## Format at a glance

A `.omer` file has:
1. Magic bytes (`OMER`) + version, so it's identifiable like PNG/JPEG
2. Width, height, channel count (RGB or RGBA)
3. A JSON metadata block (title, source format, etc.)
4. Pixel data, optionally zlib-compressed

Full byte-level details in [OMER_SPEC.md](./OMER_SPEC.md).

The Python encoder and the browser's JavaScript encoder both write this
same format, and each can read files the other produced — a `.omer` built
in the browser decodes pixel-perfectly with the Python tool, and vice versa.

## Quick start (no installs, just the browser)

Open `omer_viewer.html` — just double-click it, it opens in any browser.
It has two tabs:

- **View .omer** — drag a `.omer` file onto it to see the decoded image,
  its metadata, and its header info. You can save the result back out as
  a PNG.
- **Convert to .omer** — drag a regular photo onto it (jpg, png, bmp,
  webp, gif&hellip;), optionally edit the title, and click "Download .omer".
  Conversion happens entirely client-side — the file never leaves your
  computer.

Try the **View** tab first with `sample.omer` to see it working.

## Using the Python CLI instead

Useful if you want to batch-convert a folder, or automate this as part of
a script.

Requires Python 3 and Pillow:
```
pip install pillow
```

### Converting images to .omer

```
python omer_format.py encode photo.jpg photo.omer --title "My Photo"
```

The `--title` flag is optional — if you skip it, the filename is used.

The encoder uses Pillow, so it reads pretty much any common image type:

```
python omer_format.py encode photo.jpg      photo.omer
python omer_format.py encode graphic.png    graphic.omer
python omer_format.py encode old_scan.bmp   scan.omer
python omer_format.py encode animation.gif  frame.omer
python omer_format.py encode picture.webp   picture.omer
python omer_format.py encode scan.tiff      scan.omer
```

A few things to know:
- **GIF** — only the *first frame* is converted (`.omer` is a still-image
  format, it doesn't support animation). Same applies to the browser converter.
- **Transparency** — images with an alpha channel are automatically saved
  as 4-channel RGBA `.omer` files instead of 3-channel RGB. Both the
  Python and browser encoders detect this automatically.
- **Filenames with spaces** — wrap them in quotes:
  `python omer_format.py encode "my photo.jpg" photo.omer`

### Converting a whole folder at once

The CLI only handles one file per command, but you can loop over a folder.

PowerShell:
```powershell
Get-ChildItem *.jpg | ForEach-Object {
    python omer_format.py encode $_.Name ($_.BaseName + ".omer")
}
```

macOS/Linux:
```bash
for f in *.jpg; do
    python omer_format.py encode "$f" "${f%.*}.omer"
done
```

### Converting .omer back to a normal image

```
python omer_format.py decode photo.omer photo.png
```

Pick whatever output extension you want (`.png`, `.jpg`, `.bmp`, etc.) —
Pillow saves in that format automatically based on the extension you give it.

### Inspecting a .omer file

```
python omer_format.py info photo.omer
```

Prints the dimensions, channel count, compression method, embedded
metadata, and file size — without decoding the full image.

## Why

Mostly to understand how image container formats like PNG actually work
under the hood, by building a minimal one end-to-end: header, metadata,
compression, and real encoders/decoders on both the Python and JS side —
matching bit-for-bit.
