#!/usr/bin/env python3
r"""Plot forms for the most common messages of ML papers, drawn with paperstyle.

Write the message first, pick its form in references/figure-table-styles.md
("Pick the Form for the Message"), then copy this file and paperstyle.py next
to your figure code and call the matching function with your own data:

    import matplotlib.pyplot as plt
    import paperstyle, figure_forms as ff
    paperstyle.use("clean")
    st = paperstyle.method_styles(ALL_METHODS, ours="Ours")  # every method, table order
    fig, ax = plt.subplots()                                   # one column: 3.25 x 2.2 in
    ff.tradeoff(ax, st, {"Ours": (110, 33.6), "Method A": (2, 33.1)},
                r"Speed (FPS) $\uparrow$", r"PSNR (dB) $\uparrow$")
    fig.savefig("figures/tradeoff.pdf")

The functions draw no legend, so one legend can serve all panels of a figure. Titles name
what a panel shows; the conclusion goes in the caption. Check the saved figure with figure_qa.py.
From the command line, draw every form with illustrative data:

    python3 figure_forms.py clean figure-forms.png   # needs matplotlib
"""
import sys

import paperstyle

OURS = "Ours"
LOSS = "#8e8e8e"  # bars where ours loses: grey, so the gains carry the accent


def _log_x(ax):
    """Log x-axis with plain tick labels (0.1, 1, 10), not powers of ten."""
    from matplotlib.ticker import FuncFormatter, NullFormatter
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())


def tradeoff(ax, st, points, xlabel, ylabel, logx=True, nudge=None, ours=OURS):
    """Better and cheaper: one point per method, quality against cost.

    points maps a method to (cost, quality). Put cost on a log axis when it
    spans orders of magnitude. Ours should sit alone in the best corner.
    Points carry direct labels; nudge maps a method to a label offset in points.
    """
    nudge = nudge or {}
    for m, (x, y) in points.items():
        s = st[m]
        ax.plot(x, y, linestyle="none", marker=s["marker"], color=s["color"],
                markerfacecolor=s.get("markerfacecolor", s["color"]),
                markersize=8 if m == ours else 6, zorder=s["zorder"])
        ax.annotate(m, (x, y), textcoords="offset points", xytext=nudge.get(m, (6, 3)),
                    fontweight="bold" if m == ours else "normal")
    if logx:
        _log_x(ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def curves(ax, st, x, ys, xlabel, ylabel, logx=False):
    """A trend over a setting (data size, noise level, iterations): one line per method.

    ys maps a method to its values at x. Put x on a log axis for sizes that
    grow by factors (data, parameters, compute).
    """
    for m, y in ys.items():
        ax.plot(x, y, label=m, **st[m])
    if logx:
        _log_x(ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def gain_bars(ax, gains, xlabel, color, loss_color=LOSS):
    """Where the gain comes from: ours minus the best baseline for each group.

    gains maps a group (category, difficulty bin, dataset) to the gain. Bars
    are sorted, start at zero, and keep losses visible in grey.
    """
    items = sorted(gains.items(), key=lambda kv: kv[1])
    vals = [v for _, v in items]
    ax.barh([k for k, _ in items], vals, height=0.7,
            color=[color if v >= 0 else loss_color for v in vals])
    ax.axvline(0, color=paperstyle.INK_2, linewidth=0.8)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(xlabel)


def cdf(ax, st, samples, xlabel, logx=True, points=60):
    """Consistency and failures: the share of samples with an error at most x.

    samples maps a method to its per-sample errors. A curve further up and
    to the left is better; where it reaches 100% shows the tail of large errors.
    """
    import numpy as np
    values = {m: np.sort(np.asarray(v, dtype=float)) for m, v in samples.items()}
    both = np.concatenate(list(values.values()))
    lo, hi = (both[both > 0].min() if logx else both.min()), both.max()
    grid = np.geomspace(lo, hi, points) if logx else np.linspace(lo, hi, points)
    for m, v in values.items():
        share = np.searchsorted(v, grid, side="right") / len(v) * 100
        ax.plot(grid, share, label=m, markevery=max(1, points // 6), **st[m])
    if logx:
        _log_x(ax)
    ax.set_ylim(-4, 104)  # room for the markers at 0% and 100%
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Samples below this error (%)")


def sensitivity(ax, style, x, y, default, xlabel, ylabel, reference=None,
                reference_label="Best baseline", stable=None, logx=True):
    """Insensitive to a setting: ours over the range of one hyperparameter.

    style is the style of ours from method_styles. The dotted line marks the
    default; the dashed grey line is the best baseline, so the reader sees
    how far ours stays ahead; stable=(low, high) shades the range to point out.
    """
    if stable:
        ax.axvspan(*stable, color=style["color"], alpha=0.08, linewidth=0)
    if reference is not None:
        ax.axhline(reference, color=LOSS, linestyle="--", linewidth=1.2)
        ax.annotate(reference_label, (x[0], reference), textcoords="offset points",
                    xytext=(0, -11))
    ax.axvline(default, color=paperstyle.INK_2, linestyle=":", linewidth=1.0)
    ax.annotate("default", (default, 1), xycoords=("data", "axes fraction"),
                textcoords="offset points", xytext=(3, -10))
    ax.plot(x, y, **style)
    if logx:
        _log_x(ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def _title(ax, content, form):
    """What the panel shows in bold, as a paper's panel title would say; the message and form below it, in grey."""
    ax.set_title(content, loc="left", fontweight="bold", pad=16)
    ax.annotate(form, (0, 1), xycoords="axes fraction", textcoords="offset points",
                xytext=(0, 5), color=paperstyle.INK_2, style="italic")


def gallery(scheme, path):
    """Every form above with illustrative data, one column-wide panel each."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    s = paperstyle.use(scheme)
    methods = [OURS, "Method A", "Method B", "Method C"]
    st = paperstyle.method_styles(methods, ours=OURS, scheme=scheme)
    fig, axes = plt.subplots(3, 2, figsize=(6.875, 7.6))
    (a, b), (c, d), (e, f) = axes

    tradeoff(a, st, {OURS: (110, 33.6), "Method A": (2, 33.1), "Method B": (15, 31.2),
                     "Method C": (140, 29.0)},
             r"Speed (FPS, log scale) $\uparrow$", r"PSNR (dB) $\uparrow$",
             nudge={"Method C": (-18, 7)})
    a.set_xlim(0.8, 400)
    _title(a, "(a) PSNR vs. rendering speed",
           "Better and cheaper: scatter, cost on a log axis")

    frac = [1, 3, 10, 30, 100]
    curves(b, st, frac, {OURS: [62, 71, 78.5, 82, 84], "Method A": [52, 60, 68, 73.5, 77],
                         "Method B": [48, 57, 65, 71, 75], "Method C": [44, 53, 61, 67.5, 72]},
           "Training data used (%, log scale)", r"Accuracy (%) $\uparrow$", logx=True)
    b.axhline(77, color=LOSS, linestyle=":", linewidth=1.0, zorder=1)
    b.annotate("Method A at 100%", (1, 77), textcoords="offset points", xytext=(0, 3))
    b.set_xticks(frac, [str(v) for v in frac])
    _title(b, "(b) Accuracy vs. training data",
           "Scales with data: lines, size on a log axis")

    noise = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
    curves(c, st, noise, {OURS: [85, 84, 82, 79, 75, 70], "Method A": [84, 80, 72, 62, 52, 43],
                          "Method B": [82, 77, 69, 60, 51, 42], "Method C": [80, 73, 63, 53, 44, 36]},
           r"Input noise level $\sigma$", r"Accuracy (%) $\uparrow$")
    _title(c, "(c) Accuracy vs. input noise",
           "Robust to harder inputs: lines over difficulty")

    gain_bars(d, {"pole": 6.8, "fence": 5.1, "bicycle": 4.6, "traffic sign": 3.9,
                  "person": 1.5, "car": 0.6, "road": 0.1, "sky": -0.4},
              "IoU gain over the best baseline (points)", s["ours"])
    _title(d, "(d) IoU gain per category",
           "Where the gain comes from: sorted gain bars")

    rng = np.random.default_rng(0)
    errors = {m: rng.lognormal(np.log(med), sig, 2000) for m, med, sig in
              ((OURS, 0.7, 0.6), ("Method A", 1.1, 0.8), ("Method B", 1.4, 0.85),
               ("Method C", 1.7, 0.9))}
    cdf(e, st, errors, r"Rotation error ($^\circ$, log scale)")
    _title(e, "(e) Distribution of rotation errors",
           "Fewer failures: cumulative error curve")

    lam = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
    sensitivity(f, st[OURS], lam, [79, 81.5, 83.4, 83.8, 84.0, 83.9, 83.5, 81.8, 78.5], 1,
                r"Loss weight $\lambda$ (log scale)", r"Accuracy (%) $\uparrow$",
                reference=77, stable=(0.1, 10))
    f.set_ylim(75, 86)
    _title(f, r"(f) Accuracy vs. loss weight $\lambda$",
           "Insensitive to a setting: line, default marked")

    handles = [plt.Line2D([], [], **st[m]) for m in methods]
    try:
        fig.legend(handles, methods, loc="outside upper center", ncol=4)
    except ValueError:  # matplotlib older than 3.7
        fig.legend(handles, methods, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 1.0))
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main(argv):
    if len(argv) == 2 and argv[0] in paperstyle.SCHEMES:
        gallery(*argv)
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
