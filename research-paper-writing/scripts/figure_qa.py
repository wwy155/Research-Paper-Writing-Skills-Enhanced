#!/usr/bin/env python3
r"""Check paper figures for layout defects, and record the result for check_tex.py.

Draw every figure at its printed width, export it to PDF, and check it:

    python3 figure_qa.py figures/make_figures.py        # runs the script; checks every figure it saves
    python3 figure_qa.py figures/teaser.png fig/x.pdf    # checks finished files (photos, renders, diagrams)

Options: --print-width IN   width the figure is printed at (default: the figure's own width)
         --caption-pt PT    caption font size of the venue (default 9)

For figures drawn with matplotlib it reports:
  ERROR  the legend covers data; text overlaps other text, the legend, or another panel;
         content lies outside the figure, or data lies outside the axis range (cut off);
         text smaller than 6 pt.
  WARN   text smaller than the caption font or much larger; lines or markers too thin, thick,
         small, or large; markers cut in half at the axis edge; data filling under half of an
         axis range; an empty figure margin; a panel title that states a conclusion; a missing
         legend or axis label; bars that do not start at zero; a plot saved as a raster image;
         a file saved with bbox_inches="tight" wider than the figure.
For finished files: Type 3 fonts and the page width of a PDF, the resolution and white
borders of an image.

Each checked file gets an entry in <its folder>/.figure-qa/record.json, with its SHA-1 so that
check_tex.py notices later changes, and a PNG preview in the same folder. Open the preview and
look at it: no script sees everything. Exit status 1 if any ERROR remains, 2 on a usage error.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import traceback

ERROR, WARN = "ERROR", "WARN"
TOOL = "figure_qa 1"
CLAIM = re.compile(r"\b(?:outperform\w*|beats?|surpass\w*|superior|better|worse|best|worst|highest|lowest|fastest|"
                   r"slowest|sharpest|exceeds?|dominates?|wins?|keeps?|preserves?|recovers?|matches|achieves?|"
                   r"improves?|reduces?|degrades?|fails?|blurs?|grows?|helps?|scales?|stays?|remains?)\b", re.I)
TITLE_CLAIM = re.compile(r"^(?:\(?[a-z]\)\s*)?(?:ours|our\b|only\b|the (?:gain|lead|improvement|advantage|"
                         r"difference)\b)|\b(?:is|are|comes? from|cuts?|holds?|wins?|loses?|fails?)\b", re.I)
VECTOR_EXTS, RASTER_EXTS = (".pdf", ".svg", ".eps", ".ps"), (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")


# ---------------------------------------------------------------- matplotlib figures

def _np():
    import numpy as np
    return np


def _box(artist, r):
    np = _np()
    try:
        bb = artist.get_window_extent(r)
    except Exception:
        return None
    if bb is None or not np.all(np.isfinite([bb.x0, bb.y0, bb.x1, bb.y1])) or bb.width <= 0 or bb.height <= 0:
        return None
    return bb


def _shrink(bb, px):
    from matplotlib.transforms import Bbox
    return Bbox([[bb.x0 + px, bb.y0 + px], [bb.x1 - px, bb.y1 - px]])


def _overlap(a, b, px=1.0):
    """Two boxes overlap by more than px pixels in both directions."""
    return min(a.x1, b.x1) - max(a.x0, b.x0) > px and min(a.y1, b.y1) - max(a.y0, b.y0) > px


def _short(text, n=24):
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n - 1] + "..."


def _panel(ax, fig):
    title = ax.get_title() or ax.get_title(loc="left")
    return f"panel '{_short(title, 30)}'" if title else f"panel {fig.axes.index(ax) + 1}"


def _series(ax):
    """Data artists drawn in data coordinates: [(name, kind, artist, display points)].
    Panels with hidden axes (images, diagrams, table mock-ups) have none."""
    np = _np()
    out = []
    if not ax.axison:
        return out
    for line in ax.get_lines():
        if not line.get_visible() or line.get_transform() is not ax.transData:
            continue  # axhline, axvline, and other reference lines are not data
        xy = np.asarray(line.get_xydata(), float).reshape(-1, 2)
        xy = xy[np.isfinite(xy).all(axis=1)]
        if len(xy):
            out.append((line.get_label(), "line", line, ax.transData.transform(xy)))
    for coll in ax.collections:
        if not coll.get_visible():
            continue
        offsets = np.asarray(coll.get_offsets(), float).reshape(-1, 2)
        if len(offsets) and coll.get_offset_transform() is ax.transData and type(coll).__name__ == "PathCollection":
            offsets = offsets[np.isfinite(offsets).all(axis=1)]
            if len(offsets):
                out.append((coll.get_label(), "scatter", coll, ax.transData.transform(offsets)))
        elif coll.get_transform() is ax.transData:
            pts = [p.vertices for p in coll.get_paths() if len(p.vertices)]
            if pts:
                xy = np.concatenate(pts)
                xy = xy[np.isfinite(xy).all(axis=1)]
                if len(xy):
                    out.append((coll.get_label(), "area", coll, ax.transData.transform(xy)))
    for patch in ax.patches:
        if patch.get_visible() and type(patch).__name__ == "Rectangle" and patch.get_data_transform() is ax.transData:
            x, y, w, h = patch.get_x(), patch.get_y(), patch.get_width(), patch.get_height()
            corners = np.array([[x, y], [x + w, y + h]], float)
            if np.isfinite(corners).all() and (w or h):
                out.append((patch.get_label(), "bar", patch, ax.transData.transform(corners)))
    return out


NOUNS = {"line": "a line", "scatter": "a scatter series", "area": "a shaded area", "bar": "a bar"}


def _name(label, kind):
    return f"'{_short(label)}'" if label and not label.startswith("_") else NOUNS[kind]


def _hits_box(kind, artist, pts, box, dpi):
    """Does this data artist draw anything inside box (display pixels)?"""
    np = _np()
    from matplotlib.path import Path
    if kind == "bar":
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        return min(hi[0], box.x1) - max(lo[0], box.x0) > 1 and min(hi[1], box.y1) - max(lo[1], box.y0) > 1
    if kind == "area":
        return any(Path(artist.get_transform().transform(p.vertices)).intersects_bbox(box, filled=True)
                   for p in artist.get_paths() if len(p.vertices))
    if kind == "scatter":
        sizes = artist.get_sizes()
        radius = (np.sqrt(sizes.max()) / 2 if len(sizes) else 3) * dpi / 72
        grown = _shrink(box, -radius)
        return bool(np.any((pts[:, 0] > grown.x0) & (pts[:, 0] < grown.x1) & (pts[:, 1] > grown.y0) &
                           (pts[:, 1] < grown.y1)))
    marker = artist.get_marker()
    if marker not in (None, "None", "", " ", "none"):
        radius = artist.get_markersize() / 2 * dpi / 72
        grown = _shrink(box, -radius)
        if np.any((pts[:, 0] > grown.x0) & (pts[:, 0] < grown.x1) & (pts[:, 1] > grown.y0) & (pts[:, 1] < grown.y1)):
            return True
    if artist.get_linestyle() not in ("None", "", " ", "none") and len(pts) > 1:
        return Path(pts).intersects_bbox(box, filled=False)
    return False


def _texts(fig, r):
    """Visible texts with their boxes: [(text, box, owner axes or None, role)]."""
    out, seen = [], set()

    def add(t, owner, role):
        if t is None or id(t) in seen or not t.get_visible() or not t.get_text().strip():
            return
        seen.add(id(t))
        bb = _box(t, r)
        if bb is not None:
            out.append((t, bb, owner, role))

    for ax in fig.axes:
        if not ax.get_visible():
            continue
        axbox = ax.get_window_extent(r)
        for t in (ax.title, getattr(ax, "_left_title", None), getattr(ax, "_right_title", None)):
            add(t, ax, "title")
        if ax.axison:
            add(ax.xaxis.label, ax, "x label")
            add(ax.yaxis.label, ax, "y label")
            for t in ax.get_xticklabels(which="both"):
                bb = _box(t, r) if t.get_visible() and t.get_text().strip() else None
                if bb is not None and axbox.x0 - 1 <= (bb.x0 + bb.x1) / 2 <= axbox.x1 + 1:
                    out.append((t, bb, ax, "x tick label"))
            for t in ax.get_yticklabels(which="both"):
                bb = _box(t, r) if t.get_visible() and t.get_text().strip() else None
                if bb is not None and axbox.y0 - 1 <= (bb.y0 + bb.y1) / 2 <= axbox.y1 + 1:
                    out.append((t, bb, ax, "y tick label"))
        for t in ax.texts:
            add(t, ax, "label")
    for t in list(fig.texts) + [getattr(fig, a, None) for a in ("_suptitle", "_supxlabel", "_supylabel")]:
        add(t, None, "figure title" if t is getattr(fig, "_suptitle", None) else "figure text")
    return out


def _legends(fig, r):
    out = []
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            bb = _box(leg, r)
            if bb is not None:
                out.append((leg, bb, ax))
    for leg in fig.legends:
        if leg.get_visible():
            bb = _box(leg, r)
            if bb is not None:
                out.append((leg, bb, None))
    return out


def _is_categorical(labels):
    texts = [t.get_text().replace("−", "-").replace("$", "").strip() for t in labels if t.get_text().strip()]
    numeric = sum(1 for s in texts if re.fullmatch(r"[-+]?[\d.,]+(?:[eE][-+]?\d+)?%?|10\^\{?[-\d]+\}?|\\mathdefault\{.*\}", s))
    return bool(texts) and numeric < len(texts)


def check_figure(fig, print_width=None, caption_pt=9.0, tight=False):
    """Layout checks on a matplotlib figure; returns [(level, message)]."""
    np = _np()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    dpi = fig.dpi
    width_in, height_in = fig.get_size_inches()
    scale = print_width / width_in if print_width else 1.0
    figbox = fig.bbox
    issues = []

    def add(level, msg):
        if (level, msg) not in issues:
            issues.append((level, msg))

    if print_width and width_in > print_width * 1.05:
        add(WARN, f"Drawn {width_in:.2f} in wide but printed at {print_width:.2f} in: all text shrinks to "
                  f"{scale:.0%}. Draw it at the printed width")
    texts = _texts(fig, r)
    legends = _legends(fig, r)
    axes = [ax for ax in fig.axes if ax.get_visible()]
    axboxes = {ax: ax.get_window_extent(r) for ax in axes}

    # Content outside the figure: cut off, or a wider file with bbox_inches="tight".
    if not tight:
        for t, bb, owner, role in texts:
            if bb.x0 < figbox.x0 - 1 or bb.y0 < figbox.y0 - 1 or bb.x1 > figbox.x1 + 1 or bb.y1 > figbox.y1 + 1:
                add(ERROR, f"The {role} '{_short(t.get_text())}' extends past the figure edge and is cut off: "
                           "use constrained layout or make room")
        for leg, bb, owner in legends:
            if bb.x0 < figbox.x0 - 1 or bb.y0 < figbox.y0 - 1 or bb.x1 > figbox.x1 + 1 or bb.y1 > figbox.y1 + 1:
                add(ERROR, "The legend extends past the figure edge and is cut off")

    # Text on text, text on legends, and text running into another panel.
    for i in range(len(texts)):
        t1, b1, o1, r1 = texts[i]
        for j in range(i + 1, len(texts)):
            t2, b2, o2, r2 = texts[j]
            if _overlap(_shrink(b1, 0.5), _shrink(b2, 0.5)):
                if r1 == r2 and r1.endswith("tick label") and o1 is o2:
                    add(ERROR, f"The {r1}s of {_panel(o1, fig)} overlap ('{_short(t1.get_text(), 12)}', "
                               f"'{_short(t2.get_text(), 12)}'): use fewer ticks, shorter labels, or rotate them")
                else:
                    add(ERROR, f"The {r1} '{_short(t1.get_text())}' overlaps the {r2} '{_short(t2.get_text())}'")
        for leg, lb, lo in legends:
            if _overlap(_shrink(b1, 0.5), lb):
                add(ERROR, f"The legend covers the {r1} '{_short(t1.get_text())}'")
        for ax in axes:
            if ax is not o1 and _overlap(_shrink(b1, 0.5), axboxes[ax], 2) and not (o1 and ax in o1.child_axes):
                add(ERROR, f"The {r1} '{_short(t1.get_text())}' runs into {_panel(ax, fig)}")

    # Panels on panels, legends on panels and on data.
    for i, a1 in enumerate(axes):
        for a2 in axes[i + 1:]:
            if _overlap(axboxes[a1], axboxes[a2], 2):
                add(ERROR, f"{_panel(a1, fig).capitalize()} and {_panel(a2, fig)} overlap")
    for leg, lb, owner in legends:
        for ax in axes:
            if owner is not None and ax is not owner:
                if _overlap(lb, axboxes[ax], 2):
                    add(ERROR, f"The legend of {_panel(owner, fig)} covers {_panel(ax, fig)}")
                continue
            inside = _shrink(lb, 1.5)
            for name, kind, artist, pts in _series(ax):
                if _hits_box(kind, artist, pts, inside, dpi):
                    add(ERROR, f"The legend covers data of {_name(name, kind)} in {_panel(ax, fig)}: move it to an "
                               "empty corner or above the plot")

    for ax in axes:
        series = _series(ax)
        box = axboxes[ax]
        panel = _panel(ax, fig)
        # Data outside the axis range is not drawn; markers on the edge are cut in half.
        for name, kind, artist, pts in series:
            if kind == "area":
                continue
            out = (pts[:, 0] < box.x0 - 0.5) | (pts[:, 0] > box.x1 + 0.5) | (pts[:, 1] < box.y0 - 0.5) | \
                  (pts[:, 1] > box.y1 + 0.5)
            if kind == "bar":
                lo, hi = pts.min(axis=0), pts.max(axis=0)
                if hi[1] > box.y1 + 0.5 or hi[0] > box.x1 + 0.5:
                    whose = f" of {_name(name, kind)}" if name and not name.startswith("_") else ""
                    add(ERROR, f"A bar{whose} in {panel} is cut off by the axis limit")
                if lo[1] < box.y0 - 0.5 or lo[0] < box.x0 - 0.5:
                    add(WARN, f"Bars in {panel} do not start at zero: a bar's length must show its value")
            elif out.any():
                add(ERROR, f"{int(out.sum())} of {len(pts)} points of {_name(name, kind)} in {panel} lie outside the "
                           "axis range and are not drawn: widen the limits or plot only the shown range")
            elif kind == "line" and artist.get_marker() not in (None, "None", "", " ", "none") and artist.get_clip_on():
                rad = artist.get_markersize() / 2 * dpi / 72 * 0.6
                edge = (pts[:, 0] < box.x0 + rad) | (pts[:, 0] > box.x1 - rad) | (pts[:, 1] < box.y0 + rad) | \
                       (pts[:, 1] > box.y1 - rad)
                if edge.any():
                    add(WARN, f"Markers of {_name(name, kind)} in {panel} sit on the axis edge and are cut in half: "
                              "add a margin to the limits")
        # Too much empty space inside the panel: the data fills under half of an axis range.
        pts = [p for _, kind, _, p in series if kind != "area"]
        if pts and not ax.images:
            allp = np.concatenate(pts)
            frac = ax.transAxes.inverted().transform(allp).clip(0, 1)
            if len(np.unique(allp.round(1), axis=0)) >= 2:
                for k, (axis, lim) in enumerate((("x", ax.get_xlim()), ("y", ax.get_ylim()))):
                    span = frac[:, k].max() - frac[:, k].min()
                    if span < 0.5 and not (axis == "x" and _is_categorical(ax.get_xticklabels())) and \
                            not (axis == "y" and _is_categorical(ax.get_yticklabels())):
                        add(WARN, f"The data fills only {span:.0%} of the {axis} range of {panel} "
                                  f"({lim[0]:.3g} to {lim[1]:.3g}): tighten the limits")
        # Sizes of lines and markers at print size.
        for name, kind, artist, _ in series:
            if kind == "line":
                lw = artist.get_linewidth() * scale
                if artist.get_linestyle() not in ("None", "", " ", "none") and not 0.5 <= lw <= 3.5:
                    add(WARN, f"Line of {_name(name, kind)} is {lw:.1f} pt wide: use 0.8-2.5 pt")
                if artist.get_marker() not in (None, "None", "", " ", "none"):
                    ms = artist.get_markersize() * scale
                    if not 2.5 <= ms <= 12:
                        add(WARN, f"Markers of {_name(name, kind)} are {ms:.1f} pt: use 3-9 pt")
            elif kind == "scatter" and len(artist.get_sizes()):
                d = float(np.sqrt(np.median(artist.get_sizes()))) * scale
                if not 2.5 <= d <= 14:
                    add(WARN, f"Scatter markers of {_name(name, kind)} are {d:.1f} pt across: use 3-10 pt")
        # Titles describe what the panel shows; the caption carries the conclusion.
        for loc in ("center", "left", "right"):
            title = ax.get_title(loc=loc)
            if title and (CLAIM.search(title) or TITLE_CLAIM.search(title)):
                add(WARN, f"The title '{_short(title, 40)}' states a conclusion: name what the panel shows "
                          "('PSNR vs. views'), and put the conclusion in the caption")
        # Legends and axis labels.
        labeled = [s for s in series if s[0] and not s[0].startswith("_")]
        if len(labeled) >= 2 and ax.get_legend() is None and not fig.legends and not ax.texts:
            add(WARN, f"{panel.capitalize()} has {len(labeled)} labeled series but no legend or direct labels")
        if series and ax.axison and not ax.images:
            for axis in ("x", "y"):
                get = (lambda a: a.get_xlabel()) if axis == "x" else (lambda a: a.get_ylabel())
                shared = ax.get_shared_x_axes() if axis == "x" else ax.get_shared_y_axes()
                sup = getattr(fig, "_supxlabel" if axis == "x" else "_supylabel", None)
                has = any(get(s).strip() for s in shared.get_siblings(ax)) or (sup is not None and sup.get_text().strip())
                ticks = ax.get_xticklabels() if axis == "x" else ax.get_yticklabels()
                if not has and not _is_categorical(ticks):
                    add(WARN, f"The {axis} axis of {panel} has no label: name the quantity and its unit")
        # Direct labels and annotations sitting on top of data.
        for t, bb, owner, role in texts:
            if owner is ax and role == "label":
                for name, kind, artist, pts in series:
                    if _hits_box(kind, artist, pts, _shrink(bb, 1), dpi):
                        add(WARN, f"The label '{_short(t.get_text())}' sits on data of {_name(name, kind)} in "
                                  f"{panel}: move it to empty space")
                        break

    # Font sizes at print size.
    small, large = {}, {}  # role -> (smallest or largest size, panels)
    for t, bb, owner, role in texts:
        pt = t.get_fontsize() * scale
        name = _panel(owner, fig) if owner is not None else "the figure"
        if pt < caption_pt - 1.5:
            size, panels = small.get(role, (pt, set()))
            small[role] = (min(size, pt), panels | {name})
        elif pt > caption_pt + 3:
            size, panels = large.get(role, (pt, set()))
            large[role] = (max(size, pt), panels | {name})

    def where(panels):
        return f" in {next(iter(panels))}" if len(panels) == 1 else f" in {len(panels)} panels"

    for role, (pt, panels) in small.items():
        if pt < 6:
            add(ERROR, f"The {role}s{where(panels)} are {pt:.1f} pt at print size: too small to read; use "
                       f"{caption_pt:g} pt")
        else:
            add(WARN, f"The {role}s{where(panels)} are {pt:.1f} pt at print size, smaller than the {caption_pt:g} pt "
                      "caption")
    for role, (pt, panels) in large.items():
        add(WARN, f"The {role}s{where(panels)} are {pt:.1f} pt at print size: too large next to the "
                  f"{caption_pt:g} pt caption")
    for leg, lb, owner in legends:
        for t in leg.get_texts():
            pt = t.get_fontsize() * scale
            if pt < caption_pt - 1.5:
                add(WARN, f"Legend text is {pt:.1f} pt at print size, smaller than the {caption_pt:g} pt caption")
                break

    # Empty margins around the figure.
    try:
        tb = fig.get_tightbbox(r)
        margins = {"left": tb.x0, "bottom": tb.y0, "right": width_in - tb.x1, "top": height_in - tb.y1}
        for side, m in margins.items():
            dim = width_in if side in ("left", "right") else height_in
            if m > max(0.15, 0.07 * dim):
                add(WARN, f"Empty margin of {m:.2f} in on the {side}: use constrained layout or a smaller figure")
    except Exception:
        pass
    return issues


# ---------------------------------------------------------------- files

def sha1(path):
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()


def _raster_checks(path, print_width):
    issues = []
    try:
        import matplotlib.image as mimage
        img = mimage.imread(path)
    except Exception as e:  # noqa: BLE001
        return [(WARN, f"Could not read the image ({e.__class__.__name__}): open it and look at it")]
    np = _np()
    h, w = img.shape[:2]
    if print_width:
        dpi = w / print_width
        if dpi < 300:
            issues.append((WARN, f"{w} px wide: {dpi:.0f} dpi at {print_width:.2f} in; use at least 300 dpi"))
    rgb = img[..., :3] if img.ndim == 3 else img[..., None]
    if rgb.dtype.kind in "ui":
        rgb = rgb / np.iinfo(rgb.dtype).max
    white = (rgb >= 0.97).all(axis=-1)
    if img.ndim == 3 and img.shape[2] == 4:
        white |= img[..., 3] <= (0.03 if img.dtype.kind == "f" else 8)
    rows, cols = ~white.all(axis=1), ~white.all(axis=0)
    if rows.any() and cols.any():
        top, bottom = int(rows.argmax()), int(rows[::-1].argmax())
        left, right = int(cols.argmax()), int(cols[::-1].argmax())
        for side, px, dim in (("top", top, h), ("bottom", bottom, h), ("left", left, w), ("right", right, w)):
            if px > 0.06 * dim:
                issues.append((WARN, f"White border of {px / dim:.0%} on the {side}: crop it"))
    else:
        issues.append((ERROR, "The image is blank"))
    return issues


def _pdf_checks(path, print_width):
    issues = []
    with open(path, "rb") as fh:
        data = fh.read()
    if b"/Type3" in data or b"/Subtype /Type3" in data:
        issues.append((ERROR, "Type 3 fonts: set pdf.fonttype to 42 and save again"))
    m = re.search(rb"/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]", data)
    if m and print_width:
        w = (float(m.group(3)) - float(m.group(1))) / 72
        if w > print_width * 1.05:
            issues.append((WARN, f"The PDF is {w:.2f} in wide but printed at {print_width:.2f} in: all text shrinks "
                                 f"to {print_width / w:.0%}"))
    return issues


def render_pdf(path, out_png):
    """First page of a PDF as PNG, with PyMuPDF or poppler's pdftoppm."""
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
    if pymupdf:
        try:
            with pymupdf.open(path) as doc:
                doc[0].get_pixmap(dpi=150).save(out_png)
            return os.path.isfile(out_png)
        except Exception:  # noqa: BLE001
            pass
    if not shutil.which("pdftoppm"):
        return False
    stem = out_png[:-4]
    try:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", "1", "-l", "1", "-singlefile", path, stem],
                       check=True, capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return False
    return os.path.isfile(out_png)


def qa_dir(path):
    d = os.path.join(os.path.dirname(os.path.abspath(path)), ".figure-qa")
    os.makedirs(d, exist_ok=True)
    return d


def load_record(path):
    try:
        with open(os.path.join(qa_dir(path), "record.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def record(path, issues, preview, mode):
    d = qa_dir(path)
    rec_path = os.path.join(d, "record.json")
    rec = load_record(path)
    rec[os.path.basename(path)] = {
        "sha1": sha1(path), "issues": [list(i) for i in issues], "preview": os.path.relpath(preview, d) if preview
        else None, "checked": datetime.datetime.now().isoformat(timespec="seconds"), "mode": mode, "tool": TOOL}
    with open(rec_path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)


def report(path, issues, preview):
    errors = sum(1 for level, _ in issues if level == ERROR)
    warns = len(issues) - errors
    look = f"; look at {os.path.relpath(preview)}" if preview else "; open it and look at it"
    print(f"{os.path.relpath(path)}: {errors} error(s), {warns} warning(s){look}")
    for level, msg in sorted(issues, key=lambda i: i[0] != ERROR):
        print(f"  {level:5} {msg}")
    return errors


def check_file(path, print_width):
    """Checks for a finished file that was not drawn here."""
    entry = load_record(path).get(os.path.basename(path))
    if entry and entry.get("mode") == "script" and entry.get("sha1") == sha1(path):
        print(f"{os.path.relpath(path)}: unchanged since its script was checked")
        preview = os.path.join(qa_dir(path), entry["preview"]) if entry.get("preview") else None
        return report(path, [tuple(i) for i in entry.get("issues", [])], preview)
    ext = os.path.splitext(path)[1].lower()
    preview = None
    if ext == ".pdf":
        issues = _pdf_checks(path, print_width)
        png = os.path.join(qa_dir(path), os.path.splitext(os.path.basename(path))[0] + ".png")
        if render_pdf(path, png):
            preview = png
            issues += [(lvl, msg) for lvl, msg in _raster_checks(png, None)]
        else:
            issues.append((WARN, "No preview (pip install pymupdf, or install poppler): open the PDF and look at it"))
    elif ext in RASTER_EXTS:
        issues = _raster_checks(path, print_width)
        preview = path
    else:
        issues = [(WARN, f"Unsupported file type '{ext}': export the figure to PDF")]
    record(path, issues, preview, "file")
    return report(path, issues, preview)


# ---------------------------------------------------------------- running a plotting script

def run_script(script, args, print_width, caption_pt):
    import matplotlib
    matplotlib.use("Agg", force=True)
    from matplotlib.figure import Figure
    original = Figure.savefig
    totals = {"errors": 0, "files": 0}

    def savefig(self, fname, *a, **kw):
        if not isinstance(fname, (str, os.PathLike)):
            return original(self, fname, *a, **kw)
        path = os.fspath(fname)
        fmt = kw.get("format") or os.path.splitext(path)[1][1:] or matplotlib.rcParams["savefig.format"]
        if not os.path.splitext(path)[1]:
            path = f"{path}.{fmt}"
        tight = kw.get("bbox_inches", matplotlib.rcParams["savefig.bbox"]) == "tight"
        issues = check_figure(self, print_width, caption_pt, tight)
        result = original(self, fname, *a, **kw)
        ext = os.path.splitext(path)[1].lower()
        if ext in RASTER_EXTS and not any(ax.images for ax in self.axes):
            issues.append((WARN, "A plot saved as a raster image: save plots and diagrams as vector PDF"))
        if tight:
            r = self.canvas.get_renderer()
            tb = self.get_tightbbox(r)
            w = self.get_size_inches()[0]
            if tb.width > w * 1.03:
                issues.append((WARN, f"Saved with bbox_inches='tight', the file is {tb.width:.2f} in wide instead of "
                                     f"{w:.2f} in: draw at the printed width with constrained layout instead"))
        if ext == ".pdf":
            issues += _pdf_checks(path, print_width)
        preview = os.path.join(qa_dir(path), os.path.splitext(os.path.basename(path))[0] + ".png")
        pkw = {k: v for k, v in kw.items() if k in ("bbox_inches", "pad_inches", "facecolor", "transparent")}
        original(self, preview, dpi=150, format="png", **pkw)
        record(path, issues, preview, "script")
        totals["errors"] += report(path, issues, preview)
        totals["files"] += 1
        return result

    Figure.savefig = savefig
    old_argv, old_path = sys.argv, list(sys.path)
    sys.argv = [script] + list(args)
    sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        if e.code not in (None, 0):
            print(f"figure_qa.py: {script} exited with status {e.code}", file=sys.stderr)
            return 2
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        print(f"figure_qa.py: {script} failed; fix it and run again", file=sys.stderr)
        return 2
    finally:
        sys.argv, sys.path[:] = old_argv, old_path
        Figure.savefig = original
    if not totals["files"]:
        print(f"figure_qa.py: {script} saved no figure (call fig.savefig with a file name)", file=sys.stderr)
        return 2
    return 1 if totals["errors"] else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+", help="a plotting script (.py, with its arguments) or finished figure files")
    ap.add_argument("--print-width", type=float, help="printed width in inches (default: the figure's own width)")
    ap.add_argument("--caption-pt", type=float, default=9.0, help="caption font size in pt (default 9)")
    args = ap.parse_args(argv)
    first = args.targets[0]
    if not os.path.isfile(first):
        print(f"figure_qa.py: no such file: {first}", file=sys.stderr)
        return 2
    if first.endswith(".py"):
        return run_script(first, args.targets[1:], args.print_width, args.caption_pt)
    errors = 0
    for path in args.targets:
        if not os.path.isfile(path):
            print(f"figure_qa.py: no such file: {path}", file=sys.stderr)
            return 2
        errors += check_file(path, args.print_width)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
