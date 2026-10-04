#!/usr/bin/env python3
r"""Look at every page of a compiled paper at the highest resolution, and record that you did, for check_tex.py.

After every compile, render the pages and look at them:

    python3 page_qa.py main.pdf                         # checks the pages and writes images to look at
    python3 page_qa.py main.pdf --confirm K7QF H3XA ...  # after viewing: the code printed on each image
    python3 page_qa.py --reference refs/paperA.pdf       # a style-reference paper: sheets to read, no checks

It reports:
  ERROR  a blank band of 60 pt (5 lines) or more inside a column; a column that starts or ends
         60 pt or more away from the text block, on a page that does not end a part (main text,
         references, Appendix); an empty column; content that runs into the margin.
  WARN   the same from 34 pt (3 lines); stretched space of 12 pt or more between lines of body
         text; a figure narrower than 70% of its column; paragraphs whose last line fills less
         than 60% of the column (A1.2).

It writes images to .page-qa/<pdf name>/ next to the PDF, in color, each at the highest dpi that
an image viewer keeps without shrinking it (--max-px pixels and --max-edge on the long side):
every main-text page in four overlapping quarters (about 200 dpi on a Letter page), every other
page in two halves (about 150 dpi), and every figure or table that a tile edge cuts, whole, at up
to 300 dpi. Problems are boxed in red (ERROR) or orange (WARN), and each image carries a code.
Open every image at full size and look at every part: no script sees everything. Fix what you
see, recompile, and run it again; pages that look as they did when you viewed them get no new
images. When the pages look right, confirm with the codes; check_tex.py reports a PDF whose
images were not all viewed.

Rendering uses PyMuPDF (pip install pymupdf), poppler's pdftoppm, Ghostscript, or mutool; the
images need numpy, matplotlib, and Pillow. Exit status 1 if any ERROR remains, 2 on a usage error.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile

ERROR, WARN = "ERROR", "WARN"
TOOL = "page_qa 2"
DPI = 150                 # analysis resolution; 1 px = 0.48 pt
PT = 72.0 / DPI
MAX_PX, MAX_EDGE = 1_150_000, 1568   # the largest image a model's viewer keeps without shrinking it
OVERLAP = 0.03            # tiles overlap by 3% of the page, so nothing hides at a tile edge
FLOAT_DPI = 300           # figures and tables cut by a tile edge are shown whole, at up to this dpi
BAND = 44                 # pixels above each image for its label and code
INK = 235                 # gray level (of 255) below which a pixel is ink, light table shading included
GAP_WARN, GAP_ERROR = 34.0, 60.0   # blank band in pt: about 3 and 5 lines of 10 pt text
STRETCH = 12.0            # blank pt between two lines of body text that means LaTeX stretched the column
CODE_CHARS = "ACDEFHJKMNPRTUVWXY34679"
REFS = re.compile(r"^\s*(?:\d+\.?\s*)?(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*$")
APPENDIX = re.compile(r"^\s*(?:Appendix|APPENDIX|Appendices|Supplementary Materials?|Supplemental Materials?|"
                      r"[A-H]\.?\s{1,3}[A-Z][A-Za-z]+)")


def _np():
    import numpy
    return numpy


def sha1(path):
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()


def _pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        try:
            import fitz
            return fitz
        except ImportError:
            return None


def render(pdf):
    """Every page as a grayscale uint8 array at DPI, and the renderer's name."""
    np = _np()
    mu = _pymupdf()
    if mu:
        pages = []
        with mu.open(pdf) as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=DPI, colorspace=mu.csGRAY, alpha=False)
                a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[..., 0]
                pages.append(a.copy())
        return pages, "PyMuPDF"
    with tempfile.TemporaryDirectory() as tmp:
        stem = os.path.join(tmp, "p")
        for name, cmd in (("pdftoppm", ["pdftoppm", "-gray", "-png", "-r", str(DPI), pdf, stem]),
                          ("Ghostscript", ["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pnggray",
                                           f"-r{DPI}", f"-sOutputFile={stem}-%04d.png", pdf]),
                          ("mutool", ["mutool", "draw", "-q", "-r", str(DPI), "-c", "gray", "-o", stem + "-%04d.png",
                                      pdf])):
            if not shutil.which(cmd[0]):
                continue
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=600)
            except (OSError, subprocess.SubprocessError):
                continue
            files = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
            if files:
                import matplotlib.image as mimage
                out = []
                for f in files:
                    img = mimage.imread(os.path.join(tmp, f))
                    if img.ndim == 3:
                        img = img[..., :3].mean(axis=2)
                    if img.dtype.kind == "f":
                        img = img * 255
                    out.append(np.clip(img, 0, 255).astype(np.uint8))
                return out, name
    return [], None


def page_layout(pdf, n):
    """Per page: text lines as dicts (x0, y0, x1, y1 in pixels, size, bold, text), and the boxes of images and
    vector plots in pixels, as (kind, box).
    Lines have no boxes (None) when only pdftotext is available, and the list is None without any text tool."""
    s = DPI / 72.0
    mu = _pymupdf()
    if mu:
        texts, images = [], []
        with mu.open(pdf) as doc:
            for page in doc:
                lines = []
                for b in page.get_text("dict").get("blocks", []):
                    for line in b.get("lines", []):
                        spans = [sp for sp in line.get("spans", []) if sp.get("text", "").strip()]
                        if not spans:
                            continue
                        chars = sum(len(sp["text"]) for sp in spans)
                        size = max(spans, key=lambda sp: len(sp["text"]))["size"]
                        bold = sum(len(sp["text"]) for sp in spans if sp.get("flags", 0) & 16) > chars / 2
                        x0, y0, x1, y1 = line["bbox"]
                        lines.append({"x0": x0 * s, "y0": y0 * s, "x1": x1 * s, "y1": y1 * s, "size": size,
                                      "bold": bold, "chars": chars,
                                      "text": " ".join(" ".join(sp["text"] for sp in spans).split())})
                texts.append(sorted(lines, key=lambda d: (d["y0"], d["x0"])))
                boxes = [("image", tuple(v * s for v in info["bbox"])) for info in page.get_image_info()]
                plots = [c for c in page.cluster_drawings() if c.height >= 30] if hasattr(page, "cluster_drawings") \
                    else []
                boxes += [("plot", (c.x0 * s, c.y0 * s, c.x1 * s, c.y1 * s)) for c in plots]
                boxes += [("table", tuple(v * s for v in t)) for t in table_boxes(page, plots, lines, s)]
                images.append(boxes)
        return texts, images
    if shutil.which("pdftotext"):
        texts = []
        for k in range(1, n + 1):
            try:
                out = subprocess.run(["pdftotext", "-f", str(k), "-l", str(k), pdf, "-"], capture_output=True,
                                     text=True, timeout=120).stdout
            except (OSError, subprocess.SubprocessError):
                return None, [[] for _ in range(n)]
            texts.append([{"y0": None, "text": line.strip()} for line in out.split("\n") if line.strip()])
        return texts, [[] for _ in range(n)]
    return None, [[] for _ in range(n)]


def table_boxes(page, plots, lines, s):
    """Tables and algorithms, in pt: two or more horizontal rules of the same width outside plots,
    with their caption."""
    rules = set()
    for d in page.get_drawings():
        r = d["rect"]
        if r.height <= 1.5 and r.width >= 40 and not any(c.contains(r) for c in plots):
            rules.add((round(r.x0), round(r.y0), round(r.x1)))
    groups = []
    for x0, y, x1 in sorted(rules, key=lambda t: t[1]):
        g = next((g for g in groups if abs(g[0] - x0) <= 4 and abs(g[2] - x1) <= 4 and y - g[3] <= 150), None)
        if g:
            g[3], g[4] = y, g[4] + 1
        else:
            groups.append([x0, y, x1, y, 1])
    out = []
    for x0, y0, x1, y1, n in groups:
        if n < 2:
            continue
        for d in lines:   # the caption above or below
            top, bottom = d["y0"] / s, d["y1"] / s
            if re.match(r"(?:Table|Tab\.|Algorithm)\s*\d", d["text"]) and (0 <= y0 - bottom <= 60 or 0 <= top - y1 <= 30):
                y0, y1 = min(y0, top), max(y1, bottom)
                x0, x1 = min(x0, d["x0"] / s), max(x1, d["x1"] / s)
        out.append((x0, y0 - 2, x1, y1 + 2))
    return out


def visual_lines(lines):
    """Texts of the page's lines from top to bottom, with pieces on the same line joined, such as a
    section number and its title."""
    if not lines or lines[0].get("y0") is None:   # pdftotext: join a lone section number to its title
        out = []
        for d in lines:
            if out and len(out[-1]) <= 3 and re.fullmatch(r"[A-Z0-9.]+", out[-1]):
                out[-1] += " " + d["text"]
            else:
                out.append(d["text"])
        return out
    out, last = [], None
    for d in sorted(lines, key=lambda d: (round(d["y0"] / 4), d["x0"])):
        if last and abs(d["y0"] - last["y0"]) <= 3 / PT and 0 <= d["x0"] - last["x1"] <= 20 / PT:
            out[-1] += " " + d["text"]
        else:
            out.append(d["text"])
        last = d
    return out


def parts(texts, n):
    """Pages that end a part (main text, references, Appendix), the page and y of the References
    heading, and the first page of an Appendix that starts on a new page."""
    ends = {n - 1}
    refs_page = refs_y = app_page = None
    if texts is None:
        return ends, refs_page, refs_y, app_page
    for p, lines in enumerate(texts):
        hit = next((d for d in lines if REFS.match(d["text"])), None)
        if hit:
            refs_page, refs_y = p, hit["y0"]
            break
    for p in range(1 if refs_page is None else refs_page + 1, n):
        first = next((t for t in visual_lines(texts[p]) if len(t) > 2), "")
        if APPENDIX.match(first):
            app_page = p
            ends.add(p - 1)
            break
    return ends, refs_page, refs_y, app_page


def runs(mask):
    """(start, end) of each run of True values; end is exclusive."""
    np = _np()
    d = np.diff(np.concatenate(([0], mask.astype(np.int8), [0])))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _dilate_x(mask, r):
    """True where the row has a True value within r pixels."""
    np = _np()
    c = np.cumsum(np.pad(mask, ((0, 0), (r + 1, r))).astype(np.int32), axis=1)
    return (c[:, 2 * r + 1:] - c[:, :-(2 * r + 1)]) > 0


def margin_bands(inks):
    """Rows of a running header or footer: the first or last ink run of a page, set apart by a gap,
    that recurs at the same height on at least 40% of the pages."""
    np = _np()
    found = []
    for ink in inks:
        rows = ink.any(axis=1)
        r = runs(rows)
        h = len(rows)
        cand = []
        if len(r) >= 2:
            if r[0][1] < 0.12 * h and r[1][0] - r[0][1] >= 8 / PT:
                cand.append(r[0])
            if r[-1][0] > 0.88 * h and r[-1][0] - r[-2][1] >= 8 / PT:
                cand.append(r[-1])
        found.append(cand)
    out = np.zeros(max(len(i) for i in inks), dtype=bool)
    for cand in found:
        for a, b in cand:
            hits = sum(1 for other in found if any(abs(a - c) <= 3 / PT and abs(b - d) <= 3 / PT for c, d in other))
            if hits >= max(2, 0.4 * len(inks)):
                out[max(0, a - int(1.5 / PT)):b + int(1.5 / PT)] = True
    return out


def columns(inks, body):
    """Text columns as (left, right) pixel ranges, found from where ink falls on all pages, and narrow
    strips of ink outside them, such as line numbers in a review copy."""
    np = _np()
    w = min(i.shape[1] for i in inks)
    prof = np.mean([i[body[:i.shape[0]], :w].mean(axis=0) for i in inks], axis=0)
    k = max(3, int(6 / PT))
    smooth = np.convolve(prof, np.ones(k) / k, mode="same")
    if smooth.max() <= 0:
        return [(0, w - 1)], []
    merged = []
    for a, b in runs(smooth > 0.3 * smooth.max()):
        if merged and a - merged[-1][1] < 4 / PT:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    cols = [(a, b - 1) for a, b in merged if b - a >= 0.2 * w] or [(merged[0][0], merged[-1][1] - 1)]
    rulers = [(a, b) for a, b in runs(smooth > 0.05 * smooth.max()) if b - a < 0.06 * w
              and all(b < c0 or a > c1 for c0, c1 in cols)]
    return cols, rulers


def refine(cols, inks, keep):
    """Exact column edges: where most text lines start and end."""
    np = _np()
    out = []
    for c, (l, r) in enumerate(cols):
        lo = max(l - int(14 / PT), 0) if c == 0 else (cols[c - 1][1] + l) // 2
        hi = r + int(14 / PT) if c == len(cols) - 1 else (r + cols[c + 1][0]) // 2
        starts, ends = [], []
        for ink in inks:
            sub = ink[:, lo:hi]
            for a, b in runs(sub.any(axis=1) & keep[:ink.shape[0]]):
                if 4 / PT <= b - a <= 16 / PT:
                    xs = np.flatnonzero(sub[a:b].any(axis=0))
                    starts.append(xs[0] + lo)
                    ends.append(xs[-1] + lo)
        out.append((int(np.percentile(starts, 10)), int(np.percentile(ends, 90))) if len(ends) >= 20 else (l, r))
    return out


def spanning(ink, gutter, boxes):
    """Rows of content that crosses the gap between two columns: the title, wide figures and tables."""
    np = _np()
    h, w = ink.shape
    out = np.zeros(h, dtype=bool)
    if not gutter:
        return out
    g0, g1 = gutter
    third = max((g1 - g0) // 3, 1)
    r = int(5 / PT)
    off = max(g0 - 2 * r, 0)
    band = ink[:, off:min(g1 + 2 * r, w)]
    closed = ~_dilate_x(~_dilate_x(band, r), r)
    cross = closed[:, g0 + third - off:g1 - third - off].any(axis=1)
    for a, b in runs(ink.any(axis=1)):
        if cross[a:b].any():
            out[a:b] = True
    mid = (g0 + g1) / 2
    for _, (x0, y0, x1, y1) in boxes:
        if x0 < mid < x1:
            out[int(max(y0, 0)):int(min(y1, h))] = True
    return out


def figure_groups(boxes, cols, gutter):
    """Images and plots side by side merged into one figure: (kind, box, column index or None if it
    spans the columns, the width it is measured against)."""
    def where(box):
        x0, _, x1, _ = box
        if gutter and x0 < (gutter[0] + gutter[1]) / 2 < x1:
            return None
        mid = (x0 + x1) / 2
        return min(range(len(cols)), key=lambda c: abs((cols[c][0] + cols[c][1]) / 2 - mid))
    groups = []
    for kind, box in sorted(boxes, key=lambda kb: (kb[1][1], kb[1][0])):
        c = where(box)
        for g in groups:
            gx0, gy0, gx1, gy1 = g[1]
            overlap = min(gy1, box[3]) - max(gy0, box[1])
            if g[2] == c and overlap >= 0.5 * min(gy1 - gy0, box[3] - box[1]):
                g[1] = (min(gx0, box[0]), min(gy0, box[1]), max(gx1, box[2]), max(gy1, box[3]))
                break
        else:
            groups.append([kind, box, c])
    ref = "text width" if len(cols) == 1 else "column width"
    return [(k, b, c, "text width" if c is None else ref) for k, b, c in groups]


def with_caption(box, lines):
    """A figure's box (pixels) grown to hold its caption: a 'Figure N' line just below it, and the lines
    that follow it closely."""
    x0, y0, x1, y1 = box
    near = 30 / PT
    for i, d in enumerate(lines):
        if not re.match(r"(?:Figure|Fig\.)\s*\d", d["text"]) or d["x1"] < x0 or d["x0"] > x1:
            continue
        if 0 <= d["y0"] - y1 <= near:
            cap = [d]
            for e in lines[i + 1:]:
                if 0 <= e["y0"] - cap[-1]["y1"] <= 6 / PT and e["x1"] >= d["x0"] and e["x0"] <= max(d["x1"], x1):
                    cap.append(e)
                elif e["y0"] - cap[-1]["y1"] > 6 / PT:
                    break
            x0, y0 = min([x0] + [c["x0"] for c in cap]), min([y0] + [c["y0"] for c in cap])
            x1, y1 = max([x1] + [c["x1"] for c in cap]), max([y1] + [c["y1"] for c in cap])
            break
    return x0, y0, x1, y1


def body_size(texts):
    """The font size of the body text: the size that most characters have."""
    counts = {}
    for lines in texts or []:
        for d in lines:
            if d.get("size"):
                key = round(d["size"] * 2) / 2
                counts[key] = counts.get(key, 0) + d["chars"]
    return max(counts, key=counts.get) if counts else None


def analyze(pdf):
    np = _np()
    pages, renderer = render(pdf)
    if not pages:
        return None, None, [(ERROR, "View", 0, "No renderer: pip install pymupdf (or install poppler-utils), then "
                             "run page_qa.py again")], [], set()
    n = len(pages)
    if max(g.shape[1] for g in pages) * PT < 360:
        return pages, [[] for _ in pages], [(ERROR, "View", 0, "These pages are narrower than 5 in, so this is not "
                                             "the paper: run page_qa.py on the compiled paper")], [[] for _ in pages], \
            set()
    texts, images = page_layout(pdf, n)
    boxed = texts is not None and any(d.get("y0") is not None for lines in texts for d in lines)
    ends, refs_page, refs_y, app_page = parts(texts, n)
    inks = [g < INK for g in pages]
    bands = margin_bands(inks)
    for ink in inks:
        ink[bands[:ink.shape[0]]] = False
    cols, rulers = columns(inks, ~bands)
    for ink in inks:
        for a, b in rulers:
            ink[:, a:b] = False
    cols = refine(cols, inks, ~bands)
    gutter = (cols[0][1] + 1, cols[1][0] - 1) if len(cols) == 2 and cols[1][0] - cols[0][1] > 4 / PT else None
    names = [""] if len(cols) == 1 else [" left column", " right column"] if len(cols) == 2 else \
        [f" column {k + 1}" for k in range(len(cols))]
    spans = [spanning(ink, gutter, images[p]) for p, ink in enumerate(inks)]
    tops, bottoms = [[] for _ in cols], [[] for _ in cols]
    for ink, span in zip(inks, spans):
        for c, (l, r) in enumerate(cols):
            idx = np.flatnonzero(ink[:, l:r + 1].any(axis=1) | span)
            if len(idx):
                tops[c].append(idx[0])
                bottoms[c].append(idx[-1])
    block = [(np.percentile(t, 10) if t else 0, np.percentile(b, 90) if b else 0) for t, b in zip(tops, bottoms)]
    heights = [b - a for ink in inks for l, r in cols for a, b in runs(ink[:, l:r + 1].any(axis=1))
               if 4 / PT <= b - a <= 16 / PT]
    line_h = float(np.median(heights)) if heights else 9 / PT
    size = body_size(texts) if boxed else None

    issues, marks = [], [[] for _ in range(n)]
    if renderer and not boxed:
        issues.append((WARN, "View", 0, "No text positions: pip install pymupdf for the full check (part ends, "
                       "stretched spacing, narrow figures)"))

    def add(level, rule, p, msg, box, blank=True):
        issues.append((level, rule, p + 1, msg))
        marks[p].append((level, box, blank))

    for p, ink in enumerate(inks):
        h, w = ink.shape
        span = spans[p]
        in_image = np.zeros(h, dtype=bool)
        for kind, (x0, y0, x1, y1) in images[p]:
            if kind == "image" and x1 - x0 > 0.1 * w:
                in_image[int(max(y0, 0)):int(min(y1, h))] = True
        # Figures narrower than their column or the text width leave white space beside them.
        for kind, (x0, y0, x1, y1), c, ref in figure_groups([kb for kb in images[p] if kb[0] != "table"], cols,
                                                            gutter):
            l, r = cols[0][0] if c is None else cols[c][0], cols[-1][1] if c is None else cols[c][1]
            frac = (x1 - x0) / max(r - l, 1)
            a, b = int(max(y0, 0)), int(min(y1, h))
            beside = ink[a:b, l:r + 1].copy()
            beside[:, max(int(x0 - l - 6 / PT), 0):int(x1 - l + 6 / PT)] = False
            if frac < 0.7 and b - a > 0 and beside.any(axis=1).mean() < 0.3:
                add(WARN, "A1.6", p, f"A figure fills only {frac:.0%} of the {ref}, {y0 * PT:.0f} pt from the top: "
                    "widen it, or put panels side by side", (x0, y0, x1, y1), blank=False)
        part_end = p in ends
        for c, (l, r) in enumerate(cols):
            name = names[c]
            rows = ink[:, l:r + 1].any(axis=1) | span
            idx = np.flatnonzero(rows)
            if not len(idx):
                if not part_end:
                    add(ERROR, "A1.6", p, f"The{name or ' page'} is empty", (l, block[c][0], r, block[c][1]))
                continue
            top, bottom = idx[0], idx[-1]
            for a, b in runs(~rows[top:bottom + 1]):
                a, b = a + top, b + top
                gap = (b - a) * PT
                inside = in_image[a:b].mean()
                if gap >= GAP_WARN and inside < 0.9:
                    note = "; part of it is the white border of an image, so crop the image" if inside > 0.3 else ""
                    add(ERROR if gap >= GAP_ERROR else WARN, "A1.6", p, f"Blank band of {gap:.0f} pt in the"
                        f"{name or ' text'}, {a * PT:.0f}-{b * PT:.0f} pt from the top{note}", (l, a, r, b))
            short = (block[c][1] - bottom) * PT
            if short >= GAP_WARN and not part_end:
                level = ERROR if short >= GAP_ERROR and boxed else WARN
                hint = "" if boxed else " (fine if a new part, such as the Appendix, starts on the next page)"
                add(level, "A1.6", p, f"The{name or ' text'} ends {short:.0f} pt above the bottom of the text "
                    f"block{hint}", (l, bottom, r, block[c][1]))
            late = (top - block[c][0]) * PT
            if late >= GAP_WARN and p not in (0, app_page):
                add(ERROR if late >= GAP_ERROR else WARN, "A1.6", p, f"The{name or ' text'} starts {late:.0f} pt "
                    "below the top of the text block", (l, block[c][0], r, top))
            # Stretched space between lines of body text: LaTeX spread the column to fill it.
            if size:
                body = [d for d in texts[p] if abs(d["size"] - size) <= 0.3 and not d["bold"]
                        and d["x0"] >= l - 3 / PT and d["x1"] <= r + 3 / PT and d["x0"] <= l + 30 / PT
                        and not span[int(min((d["y0"] + d["y1"]) / 2, h - 1))]]
                body.sort(key=lambda d: d["y0"])
                for d0, d1 in zip(body, body[1:]):
                    a, b = int(d0["y1"]) + 1, int(d1["y0"]) - 1
                    gap = (d1["y0"] - d0["y1"]) * PT
                    if STRETCH <= gap < GAP_WARN and b > a and not rows[a:b].any():
                        add(WARN, "A1.6", p, f"Stretched space of {gap:.0f} pt between lines of text in the"
                            f"{name or ' text'}, {d0['y1'] * PT:.0f} pt from the top: LaTeX spread the column to fill "
                            "it. Reword, or move a float", (l, a, r, b))
        # Content in the margins or in the gap between columns.
        zones = []
        for c, (l, r) in enumerate(cols):
            left_end = 0 if c == 0 else (gutter[1] - (gutter[1] - gutter[0]) // 3 if gutter else cols[c - 1][1] + 1)
            right_end = w if c == len(cols) - 1 else (gutter[0] + (gutter[1] - gutter[0]) // 3 if gutter
                                                      else cols[c + 1][0])
            zones += [(left_end, l - int(3 / PT)), (r + int(3 / PT) + 1, right_end)]
        body_rows = np.zeros(h, dtype=bool)
        body_rows[int(min(t for t, _ in block)):int(max(b for _, b in block)) + 1] = True
        for a, b in zones:
            if b - a < 2:
                continue
            found = []
            for y0, y1 in runs(ink[:, a:b].any(axis=1) & ~span & body_rows):
                if (y1 - y0) * PT < 2:
                    continue
                if found and (y0 - found[-1][1]) * PT < 8:
                    found[-1][1] = y1
                else:
                    found.append([y0, y1])
            for y0, y1 in found:
                xs = np.flatnonzero(ink[y0:y1, a:b].any(axis=0))
                add(ERROR, "A1.1", p, f"Content runs into the margin, {y0 * PT:.0f}-{y1 * PT:.0f} pt from the top: "
                    "shorten or resize it", (a + xs[0], y0, a + xs[-1], y1), blank=False)
        # Short last lines of paragraphs (A1.2), outside the references.
        in_refs = refs_page is not None and refs_page <= p and (app_page is None or p < app_page)
        if in_refs and (p > refs_page or refs_y is None):
            continue
        shorts = 0
        for c, (l, r) in enumerate(cols):
            rows = ink[:, l:r + 1].any(axis=1) & ~span
            lines = [(a, b) for a, b in runs(rows) if b - a >= 1.5 / PT]
            if p == refs_page and refs_y is not None:
                lines = [(a, b) for a, b in lines if b < refs_y]
            ext = []
            for a, b in lines:
                xs = np.flatnonzero(ink[a:b, l:r + 1].any(axis=0))
                ext.append((l + xs[0], l + xs[-1]) if len(xs) else (r, l))
            gaps = [lines[i + 1][0] - lines[i][1] for i in range(len(lines) - 1)]
            text_gap = float(np.median(gaps)) if gaps else 3 / PT
            tol = 2.5 / PT
            for i, (a, b) in enumerate(lines):
                if i == 0 or not 0.5 * line_h <= b - a <= 1.6 * line_h:
                    continue
                x0, x1 = ext[i]
                pa, pb = lines[i - 1]
                prev_full = ext[i - 1][1] >= r - tol and 0.5 * line_h <= pb - pa <= 1.6 * line_h
                if not prev_full or a - pb > 1.6 * text_gap + 1 or x0 > l + tol or x1 >= r - tol:
                    continue
                if i + 1 < len(lines):
                    na, nb = lines[i + 1]
                    nx0 = ext[i + 1][0]
                    indented = l + 4 / PT <= nx0 <= l + 30 / PT
                    far = na - b > 1.6 * text_gap + 1
                    if not (indented or (far and nx0 <= l + tol)):
                        continue
                if (x1 - l) / max(r - l, 1) < 0.6:
                    shorts += 1
                    marks[p].append(("SHORT", (x0, b + 1, x1, b + 3), False))
        if shorts:
            issues.append((WARN, "A1.2", p + 1, f"{shorts} paragraph(s) end with a line under 60% of the column "
                           "width: reword them"))
    floats = [[b if k == "table" else with_caption(b, texts[p] if boxed else [])
               for k, b, _, _ in figure_groups(images[p], cols, gutter)] for p in range(n)]
    last_main = refs_page if refs_page is not None else n - 1
    quarter = {p for p in range(n) if p <= last_main}   # main-text pages; the others are viewed in halves
    return pages, marks, issues, floats, quarter


def qa_dir(pdf):
    d = os.path.join(os.path.dirname(os.path.abspath(pdf)), ".page-qa")
    os.makedirs(d, exist_ok=True)
    return d


def load_record(pdf):
    try:
        with open(os.path.join(qa_dir(pdf), "record.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_record(pdf, rec):
    with open(os.path.join(qa_dir(pdf), "record.json"), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)


def code_hash(code, salt):
    return hashlib.sha256((salt + code.strip().upper()).encode()).hexdigest()


def write_sheets(pdf, pages, marks, kind="Sheet"):
    """Sheets of up to 4 pages with the problems boxed and a code on each; returns their records."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    np = _np()
    out_dir = os.path.join(qa_dir(pdf), os.path.splitext(os.path.basename(pdf))[0])
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".png"):
            os.remove(os.path.join(out_dir, f))
    color = {ERROR: "#d62728", WARN: "#ff7f0e", "SHORT": "#ff7f0e"}
    ph = max(p.shape[0] for p in pages)
    pw = max(p.shape[1] for p in pages)
    sheets = []
    for s in range(0, len(pages), 4):
        group = list(range(s, min(s + 4, len(pages))))
        head, pad = 90, 20
        cols_n = 2 if len(group) > 1 else 1
        rows_n = 2 if len(group) > 2 else 1
        W, H = cols_n * pw + (cols_n + 1) * pad, rows_n * ph + (rows_n + 1) * pad + head
        canvas = np.full((H, W), 209, dtype=np.uint8)
        origin = {}
        for k, p in enumerate(group):
            ox, oy = pad + (k % 2) * (pw + pad), head + pad + (k // 2) * (ph + pad)
            g = pages[p]
            canvas[oy:oy + g.shape[0], ox:ox + g.shape[1]] = g
            origin[p] = (ox, oy)
        scale = min(1.0, 1560 / max(W, H))
        dpi = 100 * scale
        fig = plt.figure(figsize=(W / 100, H / 100), dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(canvas, cmap="gray", vmin=0, vmax=255, interpolation="antialiased")
        ax.set_xlim(0, W)
        ax.set_ylim(H, 0)
        ax.axis("off")
        code = "".join(secrets.choice(CODE_CHARS) for _ in range(4))
        salt = secrets.token_hex(8)
        first, last = group[0] + 1, group[-1] + 1
        label = f"pages {first}-{last}" if last > first else f"page {first}"
        ax.text(pad, head / 2, f"{kind} {s // 4 + 1}, {label}", fontsize=22 * 100 / 72, va="center", ha="left")
        ax.text(W - pad, head / 2, f"code {code}", fontsize=26 * 100 / 72, va="center", ha="right",
                family="monospace", weight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff2b3", edgecolor="black"))
        for p in group:
            ox, oy = origin[p]
            ax.text(ox + 8, oy + 8, f"p. {p + 1}", fontsize=16 * 100 / 72, color="#1f4e9a", va="top", ha="left",
                    weight="bold", bbox=dict(facecolor="white", edgecolor="#1f4e9a", pad=2))
            for level, (x0, y0, x1, y1), blank in marks[p]:
                lw = 2.5 if level != "SHORT" else 2.0
                d = -3 if blank and y1 - y0 > 12 else 3   # inside blank space, around content
                ax.add_patch(Rectangle((ox + x0 - d, oy + y0 - d), x1 - x0 + 2 * d, y1 - y0 + 2 * d, fill=False,
                                       edgecolor=color[level], linewidth=lw / scale))
        path = os.path.join(out_dir, f"sheet-{s // 4 + 1}.png")
        fig.savefig(path, dpi=dpi)
        plt.close(fig)
        sheets.append({"path": os.path.relpath(path, qa_dir(pdf)), "pages": [p + 1 for p in group],
                       "salt": salt, "code": code_hash(code, salt)})
    return sheets


class Clipper:
    """Renders parts of the PDF's pages in color, at any dpi."""

    def __init__(self, pdf):
        self.pdf, self.mu, self.cache = pdf, _pymupdf(), {}
        self.doc = self.mu.open(pdf) if self.mu else None

    def clip(self, p, rect, dpi):
        """Region (x0, y0, x1, y1 in pt) of page p as an RGB uint8 array."""
        np = _np()
        if self.doc is not None:
            pix = self.doc[p].get_pixmap(matrix=self.mu.Matrix(dpi / 72, dpi / 72), clip=self.mu.Rect(*rect),
                                         colorspace=self.mu.csRGB, alpha=False)
            return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3].copy()
        dpi = round(dpi)
        if (p, dpi) not in self.cache:
            self.cache = {(p, dpi): self._full(p, dpi)}
        s = dpi / 72
        return self.cache[(p, dpi)][int(rect[1] * s):int(rect[3] * s), int(rect[0] * s):int(rect[2] * s)]

    def _full(self, p, dpi):
        np = _np()
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "p.png")
            for cmd in (["pdftoppm", "-png", "-r", str(dpi), "-f", str(p + 1), "-l", str(p + 1), "-singlefile",
                         self.pdf, out[:-4]],
                        ["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m", f"-r{dpi}",
                         f"-dFirstPage={p + 1}", f"-dLastPage={p + 1}", f"-sOutputFile={out}", self.pdf],
                        ["mutool", "draw", "-q", "-r", str(dpi), "-o", out, self.pdf, str(p + 1)]):
                if not shutil.which(cmd[0]):
                    continue
                try:
                    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
                except (OSError, subprocess.SubprocessError):
                    continue
                if os.path.isfile(out):
                    import matplotlib.image as mimage
                    img = mimage.imread(out)
                    img = img[..., :3] if img.ndim == 3 else np.repeat(img[..., None], 3, axis=2)
                    return np.clip(img * 255 if img.dtype.kind == "f" else img, 0, 255).astype(np.uint8)
        raise RuntimeError("no renderer for page images")

    def close(self):
        if self.doc is not None:
            self.doc.close()


def fit_dpi(w_pt, h_pt, cap=None):
    """The highest dpi at which a w x h pt region, with the label band on top, fits the viewer
    (MAX_EDGE pixels on its long side, MAX_PX pixels in all) without being shrunk."""
    w, h = w_pt / 72, h_pt / 72
    dpi = min((MAX_EDGE - 2) / w, (MAX_EDGE - BAND - 2) / h, (MAX_PX / (w * h)) ** 0.5)
    while (w * dpi + 1) * (h * dpi + BAND + 1) > MAX_PX:
        dpi *= 0.99
    return min(dpi, cap) if cap else dpi


def _font(size):
    from PIL import ImageFont
    try:
        import matplotlib
        return ImageFont.truetype(os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans-Bold.ttf"),
                                  size)
    except Exception:  # noqa: BLE001
        return ImageFont.load_default()


def save_view(rgb, path, label, code, boxes):
    """Save one image to view: the region with its boxes, under a band with its label and code."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (rgb.shape[1], rgb.shape[0] + BAND), (230, 230, 230))
    img.paste(Image.fromarray(rgb), (0, BAND))
    d = ImageDraw.Draw(img)
    for color, (x0, y0, x1, y1), width in boxes:
        d.rectangle([x0, y0 + BAND, x1, y1 + BAND], outline=color, width=width)
    f = _font(int(BAND * 0.5))
    d.text((10, BAND / 2), label, fill=(0, 0, 0), font=f, anchor="lm")
    text = f"code {code}"
    tw = d.textlength(text, font=f)
    d.rectangle([img.width - tw - 28, 5, img.width - 6, BAND - 5], fill=(255, 242, 179), outline=(0, 0, 0))
    d.text((img.width - 17, BAND / 2), text, fill=(0, 0, 0), font=f, anchor="rm")
    img.save(path)


def page_tiles(w, h, n):
    """The n tiles of a w x h pt page, as (name, rect): quarters for 4, halves for 2, with overlap."""
    tw, th = (w / 2 + OVERLAP * w, h / 2 + OVERLAP * h) if n == 4 else (w, h / 2 + OVERLAP * h)
    spots = [("top left", 0, 0), ("top right", w - tw, 0), ("bottom left", 0, h - th),
             ("bottom right", w - tw, h - th)] if n == 4 else [("top", 0, 0), ("bottom", 0, h - th)]
    return [(name, (x, y, x + tw, y + th)) for name, x, y in spots]


def new_code():
    code, salt = "".join(secrets.choice(CODE_CHARS) for _ in range(4)), secrets.token_hex(8)
    return code, salt, code_hash(code, salt)


def write_views(pdf, pages, marks, floats, quarter, viewed, tiles=None):
    """Images to look at, at the highest dpi the viewer keeps: each page in tiles (quarters for the
    main text, halves for the rest), and each figure or table that a tile edge cuts, whole. Pages
    whose look is unchanged since they were viewed get none. Returns their records."""
    import hashlib as hl
    out_dir = os.path.join(qa_dir(pdf), os.path.splitext(os.path.basename(pdf))[0])
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".png"):
            os.remove(os.path.join(out_dir, f))
    color = {ERROR: (214, 39, 40), WARN: (255, 127, 14), "SHORT": (255, 127, 14)}
    clipper, views = Clipper(pdf), []
    try:
        for p, g in enumerate(pages):
            digest = hl.sha1(g.tobytes()).hexdigest()
            if digest in viewed:
                continue
            w, h = g.shape[1] * PT, g.shape[0] * PT
            here = page_tiles(w, h, tiles or (4 if p in quarter else 2))
            for name, rect in here:
                dpi = fit_dpi(rect[2] - rect[0], rect[3] - rect[1])
                rgb = clipper.clip(p, rect, dpi)
                k = dpi / 72
                boxes = []
                for level, (x0, y0, x1, y1), blank in marks[p]:
                    x0, y0, x1, y1 = [(v * PT - o) * k for v, o in zip((x0, y0, x1, y1), (rect[0], rect[1]) * 2)]
                    if x1 < 0 or y1 < 0 or x0 > rgb.shape[1] or y0 > rgb.shape[0]:
                        continue
                    pad = -4 if blank and y1 - y0 > 16 else 4
                    boxes.append((color[level], (x0 - pad, y0 - pad, x1 + pad, y1 + pad), 3 if level != "SHORT" else 2))
                code, salt, hashed = new_code()
                path = os.path.join(out_dir, f"p{p + 1:02d}-{name.replace(' ', '-')}.png")
                save_view(rgb, path, f"p. {p + 1}, {name}, {dpi:.0f} dpi", code, boxes)
                views.append({"path": os.path.relpath(path, qa_dir(pdf)), "page": p + 1, "part": name,
                              "dpi": round(dpi), "hash": digest, "salt": salt, "code": hashed})
            for i, (x0, y0, x1, y1) in enumerate(floats[p]):
                box = (x0 * PT - 6, y0 * PT - 6, x1 * PT + 6, y1 * PT + 6)
                if any(r[0] <= box[0] and r[1] <= box[1] and box[2] <= r[2] and box[3] <= r[3] for _, r in here):
                    continue   # one tile shows it whole
                box = (max(box[0], 0), max(box[1], 0), min(box[2], w), min(box[3], h))
                dpi = fit_dpi(box[2] - box[0], box[3] - box[1], cap=FLOAT_DPI)
                code, salt, hashed = new_code()
                path = os.path.join(out_dir, f"p{p + 1:02d}-float{i + 1}.png")
                save_view(clipper.clip(p, box, dpi), path, f"p. {p + 1}, figure or table {i + 1}, {dpi:.0f} dpi",
                          code, [])
                views.append({"path": os.path.relpath(path, qa_dir(pdf)), "page": p + 1, "part": f"float {i + 1}",
                              "dpi": round(dpi), "hash": digest, "salt": salt, "code": hashed})
    finally:
        clipper.close()
    return views


def report(pdf, issues, entry):
    errors = sum(1 for i in issues if i[0] == ERROR)
    print(f"{os.path.relpath(pdf)}: {errors} error(s), {len(issues) - errors} warning(s)")
    for level, rule, page, msg in sorted(issues, key=lambda i: (i[2], i[0] != ERROR)):
        print(f"  {level:5} [{rule}] p. {page}: {msg}" if page else f"  {level:5} [{rule}] {msg}")
    return errors


def _me():
    me = os.path.relpath(__file__)
    return os.path.abspath(__file__) if me.startswith("..") else me


def reference(pdf, rec):
    """A style-reference paper: overview sheets of its main pages (up to its references, at most 16), to see
    how it is built and what it shows where."""
    pages, _ = render(pdf)
    if not pages:
        print(f"{os.path.relpath(pdf)}: no renderer: pip install pymupdf (or install poppler-utils)")
        return 1
    texts, _ = page_layout(pdf, len(pages))
    refs_page = parts(texts, len(pages))[1]
    keep = pages[:min(len(pages) if refs_page is None else refs_page + 1, 16)]
    views = write_sheets(pdf, keep, [[] for _ in keep], kind="Reference sheet")
    rec[os.path.basename(pdf)] = {"sha1": sha1(pdf), "pages": len(keep), "issues": [], "images": views,
                                  "viewed": None, "tool": TOOL, "kind": "reference",
                                  "checked": datetime.datetime.now().isoformat(timespec="seconds")}
    save_record(pdf, rec)
    print(f"{os.path.relpath(pdf)}: {len(keep)} page(s) on {len(views)} sheet(s). Open every sheet and see how this "
          "paper is built: the order of its sections and what it shows where. Read its text as well. Decide what "
          "our paper shows from our story, never by copying this one:")
    for v in views:
        print(f"  {os.path.relpath(os.path.join(qa_dir(pdf), v['path']))}")
    print(f"Then run python3 {_me()} {os.path.relpath(pdf)} --confirm <the code on each sheet>")
    return 0


def main(argv=None):
    global MAX_PX, MAX_EDGE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", nargs="+", help="compiled PDF(s): the paper, and a separate supplementary file if any")
    ap.add_argument("--confirm", nargs="+", metavar="CODE", help="the code printed on each image you viewed")
    ap.add_argument("--reference", action="store_true", help="a style-reference paper: overview sheets to read, "
                    "without the layout checks")
    ap.add_argument("--tiles", type=int, choices=(2, 4), help="tiles per page for every page (default: 4 for the "
                    "main text, 2 for the rest)")
    ap.add_argument("--max-px", type=int, default=MAX_PX, help=f"pixels per image the viewer keeps (default "
                    f"{MAX_PX}); raise it if yours keeps larger images")
    ap.add_argument("--max-edge", type=int, default=MAX_EDGE, help=f"longest image side the viewer keeps (default "
                    f"{MAX_EDGE})")
    args = ap.parse_args(argv)
    MAX_PX, MAX_EDGE = args.max_px, args.max_edge
    for pdf in args.pdf:
        if not os.path.isfile(pdf):
            print(f"page_qa.py: no such file: {pdf}", file=sys.stderr)
            return 2
    if args.confirm:
        status = 0
        for pdf in args.pdf:
            rec = load_record(pdf)
            entry = rec.get(os.path.basename(pdf))
            if not entry or entry.get("sha1") != sha1(pdf):
                print(f"{os.path.relpath(pdf)}: changed since its images were written; run page_qa.py on it again")
                status = 1
                continue
            views = entry.get("images", entry.get("sheets", []))
            missing = [v for v in views if not any(code_hash(c, v["salt"]) == v.get("code", v.get("hash"))
                                                   for c in args.confirm)]
            if missing:
                print(f"{os.path.relpath(pdf)}: no matching code for {len(missing)} image(s), e.g., " + ", ".join(
                    os.path.join(".page-qa", v["path"]) for v in missing[:6]) + ". Open each of them and read the "
                    "code in its top right corner")
                status = 1
                continue
            entry["viewed"] = datetime.datetime.now().isoformat(timespec="seconds")
            entry["viewed_hashes"] = sorted(set(entry.get("viewed_hashes", [])) |
                                            {v["hash"] for v in views if v.get("hash")})
            save_record(pdf, rec)
            print(f"{os.path.relpath(pdf)}: recorded that all {len(views)} image(s) were viewed")
        return status
    errors = 0
    for pdf in args.pdf:
        rec = load_record(pdf)
        name = os.path.basename(pdf)
        old = rec.get(name) or {}
        if old.get("sha1") == sha1(pdf) and old.get("viewed"):
            print(f"{os.path.relpath(pdf)}: unchanged since you viewed it on {old['viewed']}")
            errors += report(pdf, [tuple(i) for i in old.get("issues", [])], old)
            continue
        if args.reference:
            errors += reference(pdf, rec)
            continue
        pages, marks, issues, floats, quarter = analyze(pdf)
        viewed = set(old.get("viewed_hashes", []))
        views = write_views(pdf, pages, marks, floats, quarter, viewed, args.tiles) if pages else []
        entry = {"sha1": sha1(pdf), "pages": len(pages or []), "issues": [list(i) for i in issues],
                 "images": views, "viewed": None, "viewed_hashes": sorted(viewed), "tool": TOOL, "kind": "paper",
                 "checked": datetime.datetime.now().isoformat(timespec="seconds")}
        if pages and not views:
            entry["viewed"] = entry["checked"]   # every page looks as it did when it was viewed
        rec[name] = entry
        save_record(pdf, rec)
        errors += report(pdf, issues, entry)
        if views:
            shown = sorted({v["page"] for v in views})
            same = len(pages) - len(shown)
            print(f"Now open all {len(views)} image(s) at full size and look at every part: white space, float "
                  "positions, text in the margins, overlaps, small or blurry text, and short last lines. No script "
                  "sees everything." + (f" {same} page(s) look as they did when you viewed them, so they have no "
                                        "images." if same else ""))
            for v in views:
                print(f"  {os.path.relpath(os.path.join(qa_dir(pdf), v['path']))}")
            print(f"Fix what you see, recompile, and run this again. When every page looks right, run "
                  f"python3 {_me()} {os.path.relpath(pdf)} --confirm <the code on each image>")
        elif pages:
            print("Every page looks as it did when you viewed it.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
