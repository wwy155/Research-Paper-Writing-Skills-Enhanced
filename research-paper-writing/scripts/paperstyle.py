#!/usr/bin/env python3
r"""Figure and table style schemes for the research-paper-writing skill.

Every scheme lives in SCHEMES below, so plots and tables always share one set
of colors. See references/figure-table-styles.md for when to use each scheme.

In Python (copy this file next to your plotting code):

    import paperstyle
    paperstyle.use("clean")                   # fonts, sizes, lines, grid, colors
    st = paperstyle.method_styles(ALL_METHODS, ours="Ours")
    ax.plot(x, y, label="Ours", **st["Ours"])  # same style for a method everywhere

From the command line:

    python3 paperstyle.py list
    python3 paperstyle.py tex clean > table-style.tex     # then \input{table-style}
    python3 paperstyle.py mplstyle clean > clean.mplstyle  # plt.style.use(...)
    python3 paperstyle.py preview clean preview.png        # needs matplotlib

Only the standard library is needed, except for use() and preview.
"""
import sys

# Checked with the dataviz palette validator on a white page:
# - colored slots (ours, baselines): OKLCH lightness 0.43-0.77, chroma >= 0.10,
#   contrast >= 3:1, and between neighboring slots normal-vision Delta E >= 15
#   and CVD Delta E >= 6 (>= 8 in soft and vivid; markers cover 6-8);
# - ours vs every other slot, greys included: normal >= 15, CVD >= 8;
# - greys: the validator's ordinal checks and contrast >= 3:1; they are told
#   apart by dash pattern and hollow markers, and the first grey clears the
#   last colored slot (normal >= 15, CVD >= 6).
# Table tints mix a palette color with white (ours row: 8-12%; vivid ranks:
# 70/60/25% of vermillion/orange/yellow, darkest = best); black text on
# every tint stays >= 7:1.
GREYS = ["#505050", "#6e6e6e", "#8e8e8e"]  # extra baselines, drawn dashed
TEXT, INK_2, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
SERIF = ["Times New Roman", "Times", "Nimbus Roman", "TeX Gyre Termes",
         "Liberation Serif", "DejaVu Serif"]
SANS = ["Helvetica", "Arial", "Nimbus Sans", "TeX Gyre Heros",
        "Liberation Sans", "DejaVu Sans"]

SCHEMES = {
    "clean": {
        "look": "Balanced and modern; the default for most papers.",
        "source": "dataviz reference hues",
        "ours": "#2a78d6",
        "baselines": ["#eb6834", "#4a3aa7", "#008300", "#e34948"],
        "others": GREYS,
        "font": "serif",
        "seq": "Blues", "div": "RdBu_r",
        "table": {"ours_row": "#eaf2fb"},
    },
    "soft": {
        "look": "Muted and quiet; suits dense figures and many panels.",
        "source": "Paul Tol muted",
        "ours": "#882255",
        "baselines": ["#cc6677", "#117733", "#999933"],
        "others": ["#6e6e6e", "#808080", "#949494"],  # lighter: #505050 collides with wine under CVD
        "font": "sans",
        "seq": "Purples", "div": "PuOr_r",
        "table": {"ours_row": "#f3e9ee"},
    },
    "vivid": {
        "look": "High contrast; colored rank cells in tables, as in many 3D vision papers.",
        "source": "Okabe-Ito",
        "ours": "#d55e00",
        "baselines": ["#009e73", "#0072b2", "#cc79a7"],
        "others": GREYS,
        "font": "sans",
        "seq": "Oranges", "div": "RdBu_r",
        "table": {"rank": ["#e28e4c", "#f0c566", "#fbf8d0"]},
    },
    "mono": {
        "look": "Grey baselines and one accent; survives black-and-white printing.",
        "source": "neutral greys and one Okabe-Ito accent",
        "ours": "#d55e00",
        "baselines": [],
        "others": ["#303030", "#505050", "#6e6e6e", "#949494"],
        "font": "serif",
        "seq": "Greys", "div": "RdGy_r",
        "table": {"ours_row": "#eeeeee"},
        "ours_hatch": "////",  # bars of ours stay distinct in black-and-white print
    },
}
MARKERS = ["s", "^", "D", "v", "P", "X", "<", ">"]
DASHES = ["--", "-.", ":", (0, (5, 1.5)), (0, (3, 1, 1, 1)), (0, (1, 1))]
_current = "clean"


def rc(scheme):
    """matplotlib rcParams for a scheme (plain values, no matplotlib import)."""
    s = SCHEMES[scheme]
    colors = [s["ours"]] + s["baselines"] + s["others"]
    params = {
        # Draw each plot at its printed width and include it at that width,
        # so text stays at the caption size (A2.2). One CVPR column: 3.25 in.
        "figure.figsize": (3.25, 2.2),
        "figure.dpi": 150,
        "figure.constrained_layout.use": True,
        "savefig.dpi": 300,
        "savefig.format": "pdf",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 9,
        "axes.titlesize": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "text.color": TEXT,
        "axes.labelcolor": TEXT,
        "axes.edgecolor": INK_2,
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.5,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "lines.linewidth": 1.4,
        "lines.markersize": 5,
        "legend.frameon": False,
        "legend.handlelength": 1.8,
        "patch.force_edgecolor": True,
        "patch.edgecolor": "#ffffff",
        "patch.linewidth": 0.8,
        "image.cmap": s["seq"],
        "color_cycle": colors,  # turned into axes.prop_cycle below
        "marker_cycle": (["o"] + MARKERS)[:len(colors)],
    }
    if s["font"] == "serif":
        params.update({"font.family": "serif", "font.serif": SERIF, "mathtext.fontset": "stix"})
    else:
        params.update({"font.family": "sans-serif", "font.sans-serif": SANS,
                       "mathtext.fontset": "stixsans"})
    return params


def use(scheme="clean"):
    """Apply a scheme to matplotlib; returns the scheme dict."""
    global _current
    import matplotlib as mpl
    from cycler import cycler
    params = rc(scheme)
    colors, markers = params.pop("color_cycle"), params.pop("marker_cycle")
    params["axes.prop_cycle"] = cycler(color=colors, marker=markers)
    mpl.rcParams.update(params)
    _current = scheme
    return SCHEMES[scheme]


def method_styles(methods, ours="Ours", scheme=None):
    """Line and marker style for every method, fixed for the whole paper.

    Pass ALL methods of the paper, in table order, every time, even when a
    figure shows only some of them: a method keeps its color and marker in
    every figure (A2.3). "ours" gets the accent, a thicker line, and the top
    layer; baselines take the colored slots in order, then dashed greys.
    """
    s = SCHEMES[scheme or _current]
    slots = [(c, False) for c in s["baselines"]] + [(c, True) for c in s["others"]]
    base = [m for m in methods if m != ours]
    if len(base) > len(slots):
        raise ValueError(f"{len(base)} baselines but {len(slots)} slots in '{scheme or _current}': "
                         "show the strongest baselines only, or split the plot into panels")
    styles = {}
    if ours in methods:
        styles[ours] = {"color": s["ours"], "marker": "o", "linestyle": "-",
                        "linewidth": 2.0, "zorder": 3}
    for i, (m, (color, grey)) in enumerate(zip(base, slots)):
        styles[m] = {"color": color, "marker": MARKERS[i % len(MARKERS)],
                     "linestyle": DASHES[i % len(DASHES)] if grey else "-",
                     "linewidth": 1.2 if grey else 1.4,
                     "markerfacecolor": "white" if grey else color, "zorder": 2}
    return styles


def tex(scheme):
    """LaTeX colors and table macros for a scheme (paste or \\input in the preamble)."""
    s = SCHEMES[scheme]
    h = lambda c: c.lstrip("#").upper()
    lines = [f"% Figure and table style '{scheme}', generated by paperstyle.py; regenerate, do not edit.",
             "\\usepackage{xcolor,colortbl,booktabs}",
             f"\\definecolor{{psours}}{{HTML}}{{{h(s['ours'])}}}"]
    lines += [f"\\definecolor{{psbase{i}}}{{HTML}}{{{h(c)}}}"
              for i, c in enumerate(s["baselines"] + s["others"], 1)]
    t = s["table"]
    if "rank" in t:
        for name, c in zip(("first", "second", "third"), t["rank"]):
            lines.append(f"\\definecolor{{ps{name}}}{{HTML}}{{{h(c)}}}")
        macros = {"best": "\\cellcolor{psfirst}#1", "second": "\\cellcolor{pssecond}#1",
                  "third": "\\cellcolor{psthird}#1"}
        row = ""
    else:
        lines.append(f"\\definecolor{{psoursrow}}{{HTML}}{{{h(t['ours_row'])}}}")
        macros = {"best": "\\textbf{#1}", "second": "\\underline{#1}", "third": "#1"}
        row = "\\rowcolor{psoursrow}"
    lines.append("% \\best, \\second, \\third must start their table cell; \\oursrow starts the row of ours.")
    for name, body in macros.items():
        lines.append(f"\\providecommand{{\\{name}}}{{}}\\renewcommand{{\\{name}}}[1]{{{body}}}")
    lines.append(f"\\providecommand{{\\oursrow}}{{}}\\renewcommand{{\\oursrow}}{{{row}}}")
    return "\n".join(lines) + "\n"


def mplstyle(scheme):
    """The same settings as use(), as a .mplstyle file."""
    params = rc(scheme)
    colors = ", ".join(f"'{c.lstrip('#')}'" for c in params.pop("color_cycle"))
    markers = ", ".join(f"'{m}'" for m in params.pop("marker_cycle"))
    out = [f"# Figure style '{scheme}', generated by paperstyle.py; regenerate, do not edit."]
    for k, v in params.items():
        if isinstance(v, (list, tuple)):
            v = ", ".join(str(x) for x in v)
        elif isinstance(v, str) and v.startswith("#"):
            v = v.lstrip("#")
        out.append(f"{k}: {v}")
    out.append(f"axes.prop_cycle: cycler('color', [{colors}]) + cycler('marker', [{markers}])")
    return "\n".join(out) + "\n"


def preview(scheme, path):
    """Sample line plot, bar chart, and table mock-up in a scheme."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    s = use(scheme)
    slots = len(s["baselines"]) + len(s["others"])
    methods = ["Ours"] + [f"Method {c}" for c in "ABCDE"[:min(5, slots)]]
    st = method_styles(methods, ours="Ours", scheme=scheme)
    fig, axes = plt.subplots(1, 3, figsize=(6.875, 2.6), width_ratios=[1.15, 0.9, 1.15])
    x = np.array([1, 2, 4, 8, 16])
    ax = axes[0]
    for i, m in enumerate(methods):
        y = 30 + 2.2 * np.log2(x) - (0 if m == "Ours" else 0.9 + 0.55 * i)
        ax.plot(x, y, label=m, **st[m])
    ax.set_xscale("log", base=2)
    ax.set_xticks(x, [str(v) for v in x])  # plain labels, not powers of two
    ax.minorticks_off()
    ax.set_xlabel("Training time (min)")
    ax.set_ylabel("PSNR (dB)")
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(-0.02, 1.0), handlelength=1.6,
              columnspacing=0.6, handletextpad=0.4, borderaxespad=0.2)
    ax = axes[1]
    vals = [120, 82, 41, 95, 12, 3][:len(methods)]  # bars start at zero: a measure with a true zero
    bars = ax.bar(range(len(methods)), vals, color=[st[m]["color"] for m in methods])
    if s.get("ours_hatch"):
        bars[0].set_hatch(s["ours_hatch"])
    ax.set_xticks(range(len(methods)), [m.replace("Method ", "") for m in methods])
    ax.set_ylabel(r"Speed (FPS) $\uparrow$")
    ax = axes[2]
    ax.axis("off")
    rows = [("Method", "PSNR", "SSIM", "FPS"), ("Method A", "34.1", "0.975", "82"),
            ("Method B", "33.2", "0.981", "41"), ("Method C", "32.6", "0.964", "95"),
            ("Ours", "35.1", "0.978", "120")]
    t = s["table"]
    rank = {("PSNR", 4): 0, ("PSNR", 1): 1, ("PSNR", 2): 2, ("SSIM", 2): 0, ("SSIM", 4): 1,
            ("SSIM", 1): 2, ("FPS", 4): 0, ("FPS", 3): 1, ("FPS", 1): 2}
    xs, dy = [0.02, 0.44, 0.63, 0.84], 0.15
    for r, row in enumerate(rows):
        yy = 0.86 - r * dy
        if r == len(rows) - 1 and "ours_row" in t:
            ax.add_patch(plt.Rectangle((0, yy - dy / 2), 1, dy, color=t["ours_row"], lw=0, zorder=0))
        for c, cell in enumerate(row):
            k = rank.get((rows[0][c], r)) if r else None
            weight, text = "normal", cell
            if k is not None and "rank" in t:
                ax.add_patch(plt.Rectangle((xs[c] - 0.02, yy - dy / 2), 0.19 if c else 0.4, dy,
                                           color=t["rank"][k], lw=0, zorder=0))
            elif k == 0:
                weight = "bold"
            elif k == 1:
                text = r"$\underline{\mathrm{" + cell + "}}$"
            ax.text(xs[c], yy, text, va="center", fontsize=8, weight=weight)
    for yy, lw in ((0.86 + dy / 2, 0.9), (0.86 - dy / 2, 0.5), (0.86 - 4.5 * dy, 0.9)):
        ax.plot([0, 1], [yy, yy], color=TEXT, lw=lw, marker="", zorder=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.suptitle(f"{scheme}: {s['look']}", fontsize=9, x=0.01, ha="left")
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main(argv):
    if len(argv) >= 1 and argv[0] == "list":
        for name, s in SCHEMES.items():
            print(f"{name:6} ours {s['ours']}  baselines {' '.join(s['baselines'] + s['others'])}  {s['look']}")
        return 0
    if len(argv) == 2 and argv[0] in ("tex", "mplstyle") and argv[1] in SCHEMES:
        sys.stdout.write(tex(argv[1]) if argv[0] == "tex" else mplstyle(argv[1]))
        return 0
    if len(argv) == 3 and argv[0] == "preview" and argv[1] in SCHEMES:
        preview(argv[1], argv[2])
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
