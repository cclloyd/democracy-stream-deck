#!/usr/bin/env python3
"""
Batch convert SVG -> PNG using ImageMagick, preserving folder structure.

Usage:
  python convert_im.py
  python convert_im.py --size 256x256
  python convert_im.py --force
  python convert_im.py --input dsdultra/assets/svg --output dsdultra/assets/png
  python convert_im.py --density 384

Notes:
- Requires ImageMagick installed and available as either:
  - 'magick' (preferred/newer) or
  - 'convert' (legacy).
- Default behavior fits the SVG within WxH (contain), centers it, and adds transparent
  padding (extent) to produce exactly WxH PNGs.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
import shutil
import os


def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def find_imagemagick() -> Tuple[str, bool]:
    """
    Returns (binary, uses_subcommand).
    - If 'magick' is found, returns ('magick', True) to use 'magick convert ...'
    - Else if 'convert' is found, returns ('convert', False)
    - Else raises RuntimeError
    """
    magick = which("magick")
    if magick:
        return magick, True
    convert_bin = which("convert")
    if convert_bin:
        return convert_bin, False
    raise RuntimeError(
        "ImageMagick not found. Ensure 'magick' or 'convert' is on your PATH."
    )


def parse_size(size_str: str) -> Tuple[int, int]:
    try:
        w, h = size_str.lower().split("x", 1)
        w_i, h_i = int(w), int(h)
        if w_i <= 0 or h_i <= 0:
            raise ValueError
        return w_i, h_i
    except Exception:
        raise argparse.ArgumentTypeError("Size must be like WIDTHxHEIGHT, e.g., 256x256")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def up_to_date(src: Path, dst: Path) -> bool:
    try:
        return dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime
    except Exception:
        return False


def convert_svg_to_png_im(
    im_bin: str,
    use_subcmd: bool,
    src: Path,
    dst: Path,
    width: int,
    height: int,
    density: int,
) -> None:
    """
    Convert with ImageMagick:
    - Set density for sharper vector rasterization.
    - Transparent background.
    - Resize to fit within WxH (contain).
    - Center and pad with transparency to exact WxH.
    - Strip metadata.
    """
    cmd = []
    if use_subcmd:
        cmd = [im_bin, "convert"]
    else:
        cmd = [im_bin]

    cmd += [
        "-density", str(density),
        "-background", "none",
        "-colorspace", "sRGB",
        str(src),
        "-filter", "Lanczos",
        "-resize", f"{width}x{height}",
        "-gravity", "center",
        "-extent", f"{width}x{height}",
        "-strip",
        str(dst),
    ]

    # Ensure output directory exists
    ensure_dir(dst.parent)

    # On Windows, make sure the working dir exists and avoid shell=True.
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def convert_all(
    input_dir: Path,
    output_dir: Path,
    size: Tuple[int, int],
    force: bool,
    density: int,
) -> int:
    im_bin, use_subcmd = find_imagemagick()
    converted = 0

    for svg in input_dir.rglob("*.svg"):
        rel = svg.relative_to(input_dir)
        dst = output_dir / rel.with_suffix(".png")

        if not force and up_to_date(svg, dst):
            continue

        try:
            convert_svg_to_png_im(im_bin, use_subcmd, svg, dst, size[0], size[1], density)
            converted += 1
            print(f"Converted: {svg} -> {dst}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR converting {svg}:\n{e}\n{e.stderr.decode('utf-8', errors='ignore')}", file=sys.stderr)
        except Exception as e:
            print(f"ERROR converting {svg}: {e}", file=sys.stderr)

    return converted


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Convert SVGs to PNGs with ImageMagick.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("dsdultra/assets/svg"),
        help="Input directory containing SVGs (default: dsdultra/assets/svg)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dsdultra/assets/png"),
        help="Output directory for PNGs (default: dsdultra/assets/png)",
    )
    parser.add_argument(
        "--size",
        type=parse_size,
        default="256x256",
        help="Output size as WIDTHxHEIGHT, e.g., 256x256 (default: 256x256)",
    )
    parser.add_argument(
        "--density",
        type=int,
        default=384,
        help="Rasterization density (higher = sharper, default: 384)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reconvert even if the PNG exists and is newer than the SVG",
    )
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Input directory does not exist: {args.input}", file=sys.stderr)
        return 2

    ensure_dir(args.output)

    count = convert_all(args.input, args.output, args.size, args.force, args.density)
    print(f"Done. Converted {count} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())