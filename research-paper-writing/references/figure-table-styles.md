# Figure and Table Style Schemes

Read this file before you create or restyle any plot, diagram, or table. Pick one scheme for the whole paper and use it everywhere. Every value below comes from `scripts/paperstyle.py`, the single source of truth; regenerate from it instead of copying hex codes by hand.

## Choose a Scheme

1. If the user has named a scheme, use it.
2. Otherwise, the first time you create or restyle a figure or table, ask with the ask-user tool (`AskUserQuestion` in Claude Code). Offer the four schemes below as options, with `clean` first as the recommended default. If the venue question is still open, ask both in the same call.
3. Record the choice in a comment at the top of the main `.tex` file, e.g., `% Figure and table scheme: clean`, so later sessions keep it.
4. Never mix schemes in one paper.

## The Four Schemes

| Scheme | Look | Ours | Colored baselines, in order | Font | Tables | Heatmaps |
|---|---|---|---|---|---|---|
| `clean` (default) | Balanced and modern | `#2a78d6` blue | `#eb6834`, `#4a3aa7`, `#008300`, `#e34948` | Serif (Times) | Best bold, second underlined, ours row `#eaf2fb` | `Blues`, `RdBu_r` |
| `soft` | Muted and quiet; dense figures | `#882255` wine | `#cc6677`, `#117733`, `#999933` | Sans (Helvetica) | Best bold, second underlined, ours row `#f3e9ee` | `Purples`, `PuOr_r` |
| `vivid` | High contrast; 3D vision style | `#d55e00` vermillion | `#009e73`, `#0072b2`, `#cc79a7` | Sans (Helvetica) | First, second, third cells `#e28e4c`, `#f0c566`, `#fbf8d0` | `Oranges`, `RdBu_r` |
| `mono` | Survives black-and-white print | `#d55e00` vermillion | none: greys `#303030`, `#505050`, `#6e6e6e`, `#949494` | Serif (Times) | Best bold, second underlined, ours row `#eeeeee` | `Greys`, `RdGy_r` |

In `clean` and `vivid`, baselines beyond the colored slots take the greys `#505050`, `#6e6e6e`, `#8e8e8e`; in `soft`, the lighter `#6e6e6e`, `#808080`, `#949494`. Greys are drawn dashed with hollow markers. Show the strongest baselines in color. If a plot has more baselines than slots, drop the weakest ones or split the plot into panels.

## Apply a Scheme

Plots (matplotlib). Copy `scripts/paperstyle.py` next to the figure code once, so the project does not depend on the skill folder:

```python
import matplotlib.pyplot as plt
import paperstyle

paperstyle.use("clean")  # fonts, 9 pt text, line widths, grid, color cycle, PDF output
METHODS = ["Ours", "4D-GS", "Deformable 3DGS", "D-NeRF"]  # every method in the paper, in table order
ST = paperstyle.method_styles(METHODS, ours="Ours")       # build once, reuse in every figure

fig, ax = plt.subplots()  # 3.25 x 2.2 in: one CVPR column
for m in ["D-NeRF", "4D-GS", "Ours"]:  # a figure may show a subset; colors stay fixed
    ax.plot(x[m], psnr[m], label=m, **ST[m])
ax.set_xlabel("Training time (min)")
ax.set_ylabel("PSNR (dB)")
ax.legend()
fig.savefig("figures/psnr_vs_time.pdf")
```

`python3 paperstyle.py mplstyle clean > clean.mplstyle` writes the same settings as a style file for `plt.style.use`. `python3 paperstyle.py preview clean preview.png` draws a sample.

Tables (LaTeX). Generate the colors and macros, then `\input` them in the preamble:

```bash
python3 <this skill's directory>/scripts/paperstyle.py tex clean > table-style.tex
```

```latex
\input{table-style}  % preamble: loads xcolor, colortbl, booktabs; defines \best, \second, \third, \oursrow
...
\begin{table}[t]
  \caption{\textbf{Ours is the most accurate and the fastest.} Results on the D-NeRF dataset.}
  \label{tab:main}
  \centering
  \begin{tabular}{lccc}
    \toprule
    Method & PSNR$\uparrow$ & SSIM$\uparrow$ & FPS$\uparrow$ \\
    \midrule
    D-NeRF~\cite{dnerf} & 29.17 & \second{0.95} & 0.1 \\
    4D-GS~\cite{4dgs} & \second{34.05} & \best{0.98} & \second{82} \\
    \oursrow Ours & \best{35.12} & \best{0.98} & \best{120} \\
    \bottomrule
  \end{tabular}
\end{table}
```

`\best`, `\second`, and `\third` must start their cell, and `\oursrow` must start the row. In `vivid`, they color the cell and `\oursrow` does nothing; in the other schemes, `\third` leaves the number plain.

## Rules for Every Scheme

1. One method, one style: build the mapping once with `method_styles` from the full method list, in table order, and reuse it in every figure, so a method keeps its color, marker, and name everywhere (A2.3).
2. Ours: the accent color, a 2 pt solid line, filled circle markers, drawn on top. Baselines: 1.4 pt lines with their own markers. In `mono`, give the bars of ours `hatch="////"` so they stay distinct in black-and-white print.
3. Every line carries a marker, so identity never depends on color alone.
4. Draw each figure at its printed width and include it at that width (`width=\columnwidth` or `\linewidth`), so text stays at 9 pt, the caption size (A2.2). Typical widths: CVPR and ICCV 3.25 in per column and 6.875 in across; ICML 3.25 in and 6.75 in; ACL 3.03 in and 6.3 in; NeurIPS and ICLR 5.5 in; ECCV 4.8 in. Confirm with `\the\columnwidth` and `\the\textwidth` in the template. If the caption font is larger than 9 pt, raise the figure text to match.
5. Save plots and diagrams as vector PDF with embedded fonts (`paperstyle` sets `pdf.fonttype` to 42, A1.4). Use PNG or JPEG only for photos and renderings, at 300 dpi or more at print size.
6. One y-axis per panel. Never draw a dual-axis chart; put two measures in two panels.
7. Heatmaps: the scheme's sequential map for magnitudes, and its diverging map centered at 0 for signed differences. Depth and error maps: `magma` or `viridis`. Never `jet`, `turbo`, or `rainbow`.
8. Text stays black or dark grey: legend entries, labels, and numbers are never colored; the colored mark next to them carries identity.
9. A legend for two or more series, without a frame, placed where it hides no data (above the plot or in an empty corner). With four or fewer lines, direct labels next to the line ends also work.
10. Qualitative comparisons: methods in the same order as in the tables, names under the images, and zoom-in boxes drawn 1.5 pt wide in scheme colors, one color per region, repeated on the border of its crop.
11. Diagrams (teaser, pipeline): fill boxes with light tints (10-20%) of the scheme colors, give our new module a tint of the ours color with a 1 pt border in that color, draw arrows in dark grey `#52514e`, and keep text black.

## How the Colors Were Checked

Each palette passed the dataviz palette validator on a white page:

- Colored slots: OKLCH lightness 0.43-0.77, chroma of at least 0.10, contrast of at least 3:1, and between neighboring slots a normal-vision Delta E of at least 15 and a color-blind (protan and deutan) Delta E of at least 6, or 8 in `soft` and `vivid`. The markers of rule 3 cover the 6-8 pairs.
- Ours differs from every other slot, greys included, by a normal-vision Delta E of at least 15 and a color-blind Delta E of at least 8.
- Greys pass the validator's ordinal checks with a contrast of at least 3:1; dash patterns and hollow markers tell them apart.
- Black text on every table tint has a contrast of at least 7:1, and the `vivid` rank tints darken from third to first.
