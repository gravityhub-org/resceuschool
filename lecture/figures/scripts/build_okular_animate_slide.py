#!/usr/bin/env python3
"""Build Okular-playable full-slide GIF pages and splice into lecture1.pdf.

Typst freezes GIF embeds to the first frame. Okular plays LaTeX ``animate``
widgets, so we compile those and replace the Typst placeholder pages.

Deck layout (two ``figure-slide``s):
  1. nested sampling (marker: David Yallup)
  2. Laplace approximation (page immediately after)
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image

LECTURE = Path(__file__).resolve().parents[2]
FIG = LECTURE / "figures"
MEDIA = FIG / "media"
NESTED_GIF = FIG / "external" / "nested_sampling.gif"
LAPLACE_GIF = FIG / "laplace_approximation.gif"
NESTED_DIR = MEDIA / "nested_sampling_frames"
LAPLACE_DIR = MEDIA / "laplace_approximation_frames"
ANIM_PDF = FIG / "nested_laplace_okular.pdf"

PAGE_W_MM = 297.0
PAGE_H_MM = 167.0625
TITLE = r"How to get from a detector to merging black hole?"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, check=True, cwd=cwd)


def export_gif_frames(
    gif: Path,
    out_dir: Path,
    *,
    max_width: int,
    target_fps: float = 8.0,
    min_hold_s: float = 0.0,
) -> int:
    """Write f-0.png … expanding each GIF frame to ``target_fps`` for animate.sty."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("f-*.png"):
        old.unlink()

    reader = imageio.get_reader(gif)
    meta = reader.get_meta_data()
    raw_frames = list(reader)
    n = len(raw_frames)
    dur = meta.get("duration", None)
    if isinstance(dur, (list, tuple)) and len(dur) == n:
        durations_s = [float(d) / (1000.0 if d > 10 else 1.0) for d in dur]
    elif isinstance(dur, (int, float)) and dur is not None:
        d = float(dur)
        d_s = d / 1000.0 if d > 10 else d
        durations_s = [d_s] * n
    else:
        durations_s = [max(min_hold_s, 1.0 / target_fps)] * n

    out_i = 0
    for frame, d_s in zip(raw_frames, durations_s):
        im = Image.fromarray(np.asarray(frame))
        if im.width > max_width:
            h = int(round(im.height * (max_width / im.width)))
            im = im.resize((max_width, h), Image.Resampling.LANCZOS)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        hold = max(min_hold_s, d_s)
        n_rep = max(1, int(round(hold * target_fps)))
        for _ in range(n_rep):
            im.save(out_dir / f"f-{out_i}.png")
            out_i += 1
    return out_i


def _slide_page_tex(
    *,
    frames_subdir: str,
    n_last: int,
    credit: str | None,
    newpage: bool,
) -> str:
    """One full-bleed figure-slide page (title + large animated figure)."""
    credit_tex = ""
    if credit:
        credit_tex = (
            r"\\[1.5mm]{\color{slidemuted}\fontsize{9.5}{11}\selectfont "
            + credit
            + "}"
        )
    pagebreak = r"\newpage" if newpage else ""
    # Fill remaining slide body (Typst figure-slide style): light panel + contain.
    return (
        r"""
{\fontsize{26}{30}\bfseries TITLE\par}
\vspace{2.2mm}
{\color{slideaccent}\rule{\linewidth}{2pt}}
\vspace{2.5mm}

\noindent
\begin{minipage}[t][\dimexpr\textheight-2.3cm\relax][t]{\linewidth}
\centering
\colorbox{figpanel}{%
  \begin{minipage}[c][\dimexpr\textheight-2.8cm\relax][c]{\dimexpr\linewidth-2mm\relax}
  \centering
  \animategraphics[
    autoplay,loop,poster=first,
    width=\linewidth,
    height=\dimexpr\textheight-3.2cm\relax,
    keepaspectratio
  ]{8}{FRAMES/f-}{0}{NLAST}%
  \end{minipage}%
}\par
CREDIT
\end{minipage}
PAGEBREAK
"""
        .replace("TITLE", TITLE)
        .replace("FRAMES", frames_subdir)
        .replace("NLAST", str(n_last))
        .replace("CREDIT", credit_tex)
        .replace("PAGEBREAK", pagebreak)
    )


def write_tex(path: Path, n_nested: int, n_laplace: int) -> None:
    # Two pages: nested full slide, then Laplace full slide.
    body = _slide_page_tex(
        frames_subdir="nested",
        n_last=n_nested - 1,
        credit="Credit: David Yallup",
        newpage=True,
    ) + _slide_page_tex(
        frames_subdir="laplace",
        n_last=n_laplace - 1,
        credit=None,
        newpage=False,
    )

    path.write_text(
        r"""\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{animate}
\usepackage[
  paperwidth=PAGE_W_MMmm,
  paperheight=PAGE_H_MMmm,
  left=7mm,right=7mm,top=5mm,bottom=5mm
]{geometry}
\definecolor{slidebg}{HTML}{121212}
\definecolor{slideink}{HTML}{F2F2F2}
\definecolor{slidemuted}{HTML}{B8B8B8}
\definecolor{slideaccent}{HTML}{8EC8E8}
\definecolor{figpanel}{HTML}{FAFAFA}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\begin{document}
\pagecolor{slidebg}
\color{slideink}
BODY
\end{document}
"""
        .replace("PAGE_W_MM", f"{PAGE_W_MM}")
        .replace("PAGE_H_MM", f"{PAGE_H_MM}")
        .replace("BODY", body)
    )


def compile_animate_pdf(n_nested: int, n_laplace: int) -> None:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        shutil.copytree(NESTED_DIR, td_path / "nested")
        shutil.copytree(LAPLACE_DIR, td_path / "laplace")
        write_tex(td_path / "slide.tex", n_nested, n_laplace)
        for _ in range(2):
            run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "slide.tex",
                ],
                cwd=td_path,
            )
        shutil.copy(td_path / "slide.pdf", ANIM_PDF)
        pages = subprocess.check_output(
            ["pdfinfo", str(ANIM_PDF)], text=True
        )
        print(f"wrote {ANIM_PDF} ({pages.split('Pages:')[1].splitlines()[0].strip()} pages)")


def find_nested_page(typst_pdf: Path) -> int:
    """1-based page with the Yallup credit (nested-sampling figure-slide)."""
    info = subprocess.check_output(["pdfinfo", str(typst_pdf)], text=True)
    n = int(info.split("Pages:")[1].splitlines()[0].strip())
    for i in range(1, n + 1):
        text = subprocess.check_output(
            ["pdftotext", "-f", str(i), "-l", str(i), str(typst_pdf), "-"],
            text=True,
            errors="ignore",
        )
        if "David Yallup" in text:
            return i
    raise RuntimeError(f"nested-sampling splice page not found in {typst_pdf}")


def splice(typst_pdf: Path, dest: Path) -> None:
    """Replace nested page and the following Laplace page with animate pages 1–2."""
    nested_page = find_nested_page(typst_pdf)
    laplace_page = nested_page + 1
    info = subprocess.check_output(["pdfinfo", str(typst_pdf)], text=True)
    n = int(info.split("Pages:")[1].splitlines()[0].strip())
    if laplace_page > n:
        raise RuntimeError(
            f"expected Laplace figure-slide at page {laplace_page}, deck has {n}"
        )

    # pdftk preserves /AcroForm widgets (needed for Okular animation).
    parts: list[str] = []
    if nested_page > 1:
        parts.append(f"A1-{nested_page - 1}")
    parts.append("B1")  # nested animate
    parts.append("B2")  # laplace animate
    if laplace_page < n:
        parts.append(f"A{laplace_page + 1}-end")

    cmd = [
        "pdftk",
        f"A={typst_pdf}",
        f"B={ANIM_PDF}",
        "cat",
        *parts,
        "output",
        str(dest),
    ]
    run(cmd)
    print(
        f"spliced Okular animate pages at {nested_page}+{laplace_page}/{n} → {dest}"
    )


def build_animate() -> tuple[int, int]:
    if not LAPLACE_GIF.exists():
        raise SystemExit(
            f"missing {LAPLACE_GIF}; run laplace_approximation.py first"
        )
    n_nested = export_gif_frames(
        NESTED_GIF, NESTED_DIR, max_width=1400, target_fps=8.0, min_hold_s=0.0
    )
    n_laplace = export_gif_frames(
        LAPLACE_GIF, LAPLACE_DIR, max_width=1400, target_fps=8.0, min_hold_s=2.0
    )
    print(f"frames nested={n_nested} laplace={n_laplace}")
    compile_animate_pdf(n_nested, n_laplace)
    return n_nested, n_laplace


def main(argv: list[str] | None = None) -> None:
    import sys

    args = list(sys.argv[1:] if argv is None else argv)
    mode = args[0] if args else "all"

    typst_pdf = LECTURE / "lecture1.typst.pdf"
    final_pdf = LECTURE / "lecture1.pdf"

    if mode in ("all", "animate"):
        build_animate()
    if mode in ("all", "splice"):
        if not ANIM_PDF.exists():
            build_animate()
        if not typst_pdf.exists():
            raise SystemExit(f"missing {typst_pdf}; compile Typst first")
        splice(typst_pdf, final_pdf)


if __name__ == "__main__":
    main()
