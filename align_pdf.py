#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter, Transformation
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(
        "Manjka paket 'pypdf'. Aktiviraj venv in namesti odvisnosti:\n"
        "  .\\.venv\\Scripts\\Activate.ps1\n"
        "  python -m pip install -r requirements.txt"
    ) from exc

MM_TO_PT = 72.0 / 25.4


def mm_to_pt(value_mm: float) -> float:
    return value_mm * MM_TO_PT


def align_pdf(
    foreground_pdf: Path,
    background_pdf: Path,
    output_pdf: Path,
    x_offset_mm: float = 0.0,
    y_offset_mm: float = 0.0,
    scale: float = 1.0,
    mode: str = "background",
) -> None:
    fg_reader = PdfReader(str(foreground_pdf))
    bg_reader = PdfReader(str(background_pdf))
    writer = PdfWriter()

    if not bg_reader.pages:
        raise ValueError("Ozadje nima nobene strani.")

    bg_page_template = bg_reader.pages[0]
    tx = mm_to_pt(x_offset_mm)
    ty = mm_to_pt(y_offset_mm)
    transform = Transformation().scale(scale).translate(tx=tx, ty=ty)

    for fg_page in fg_reader.pages:
        out_page = copy.deepcopy(fg_page)
        transformed_bg = copy.deepcopy(bg_page_template)
        transformed_bg.add_transformation(transform)

        if mode == "background":
            out_page.merge_page(transformed_bg, over=False)
        else:
            out_page.merge_page(transformed_bg, over=True)

        writer.add_page(out_page)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as f:
        writer.write(f)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dodaj UPN ozadje/stampo na PDF z nastavljivim zamikom in skaliranjem."
    )
    parser.add_argument("--input", default="2026_izpis.pdf", help="Vhodni PDF.")
    parser.add_argument("--overlay", default="ozadje_UPN.pdf", help="PDF z UPN obrazcem (1. stran).")
    parser.add_argument("--output", default="2026_poravnano.pdf", help="Izhodni PDF.")
    parser.add_argument("--x-mm", type=float, default=0.0, help="Zamik po X osi v mm (+ desno, - levo).")
    parser.add_argument("--y-mm", type=float, default=0.0, help="Zamik po Y osi v mm (+ gor, - dol).")
    parser.add_argument("--scale", type=float, default=1.0, help="Skala ozadja, npr. 0.998 ali 1.002.")
    parser.add_argument(
        "--mode",
        choices=["background", "stamp"],
        default="background",
        help="background = pod vsebino, stamp = cez vsebino.",
    )
    args = parser.parse_args()

    align_pdf(
        foreground_pdf=Path(args.input),
        background_pdf=Path(args.overlay),
        output_pdf=Path(args.output),
        x_offset_mm=args.x_mm,
        y_offset_mm=args.y_mm,
        scale=args.scale,
        mode=args.mode,
    )
    print(f"Ustvarjeno: {args.output}")


if __name__ == "__main__":
    main()
