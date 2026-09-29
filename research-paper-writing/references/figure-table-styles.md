# Figures and Tables: Form and Style

Read this file before you create or restyle any plot, diagram, or table. First pick the form that shows the message, then style it with one scheme for the whole paper. Form comes before color: a plain chart of the right form beats a polished chart of the wrong one. Every style value below comes from `scripts/paperstyle.py`, the single source of truth; regenerate from it instead of copying hex codes by hand.

## Pick the Form for the Message

Decide what a figure must say before you decide what it looks like.

1. Write the message as one sentence with a number, e.g., "Ours keeps 70% accuracy at noise level 0.5, while every baseline falls below 45%." It becomes the caption's bold takeaway (A2.4). If you cannot write it, do not make the figure (A2.1).
2. Name the comparison inside the message: ours against which methods, and along which variable. The variable can be a cost, a data size, a difficulty level, a category, or an image region.
3. Pick the form from the table below. Make that comparison the most visible thing in the figure. Put the compared items next to each other on one shared axis, highlight ours, and let nothing else compete for attention.
4. Draw it at print size with real data or marked placeholders. Then test it: from the figure and its bold takeaway alone, can a reader confirm the message within five seconds? If not, change the form, not the colors.
5. Put numbers that readers will cite or compare against in a table. Put trends, trade-offs, and distributions in a plot. When both matter, plot in the main text and give the full table in the Appendix.
6. When you reproduce a figure of the closest work (Core Workflow step 2 in `SKILL.md`), keep its form so readers can compare the two papers. If that form breaks a rule in this file, e.g., a dual axis, keep the analysis and fix the form.

`scripts/figure_forms.py` draws the plot forms of the table with the chosen scheme: `tradeoff`, `curves`, `gain_bars`, `cdf`, and `sensitivity`. Copy it next to `paperstyle.py` and pass your own data. `python3 <this skill's directory>/scripts/figure_forms.py clean forms.png` renders its gallery, panels (a)-(f) in the table, with illustrative data; look at it before drawing your own.

| What you want to say | Form that shows it | Avoid |
|---|---|---|
| Ours beats the baselines on standard benchmarks. | Table: methods in rows, metrics with ↑ or ↓ in columns, best and second marked. | A bar chart of numbers that are already in a table. |
| Ours is better and cheaper (speed, memory, parameters, data). | Scatter: cost on a log x-axis, quality on y, one labeled point per method, ours alone in the best corner. Panel (a), `tradeoff`. | Two bar charts, one per measure; a dual-axis chart. |
| The gain grows, or holds, with scale (data, model size, compute, input views). | Lines: scale on a log x-axis, one line per method. Mark where ours matches the best result of a baseline. Panel (b), `curves`. | A table with one column per size. |
| Ours degrades least on harder inputs (noise, occlusion, sparsity, length). | Lines: difficulty on x, the metric on y, clean inputs at the left. Panel (c), `curves`. | Bars for each level; a table the reader must subtract. |
| The gain comes from specific cases (categories, difficulty bins, datasets). | Bars of ours minus the best baseline, sorted, starting at zero, losses in grey. Panel (d), `gain_bars`. Or the standard split of the benchmark, e.g., AP on small, medium, and large objects. | A long per-class table in the main text. |
| Ours fails less often, or less badly. | Cumulative error curve: the share of samples below each error. Panel (e), `cdf`. A box plot also works. | The mean alone, which hides the tail. |
| Ours is insensitive to a hyperparameter. | A line over its range (log x when the range spans factors), the default marked, the best baseline as a dashed reference. Panel (f), `sensitivity`. | A table of ten values. |
| Ours trains faster or more stably. | Training curves over iterations or wall-clock time, `curves`; the mean of several seeds with a shaded band (`ax.fill_between`). | One seed; only the final number. |
| Each component matters. | Ablation table: one row per variant, one column for the change from the full model. Add a qualitative row when a component fixes a visible artifact. | Bars that differ by a fraction of a unit. |
| Ours fixes a visible failure (artifacts, blur, wrong geometry). | Qualitative grid: inputs in rows, methods in table order and the ground truth in columns, zoom-in crops on the failure (Rule 10). | Full images too small to show the difference; only easy cases. |
| What the model learns or attends to. | Maps overlaid on the input (attention, error, depth) with a sequential colormap (Rule 7). | Rainbow colormaps; an embedding plot (t-SNE) without an observation. |
| How the method works. | Pipeline diagram (`references/method.md`, Rule 11). | A diagram of every layer. |
| The key idea, at first glance. | Teaser (Part D of `references/introduction.md`). | A teaser that repeats the pipeline figure. |

### Worked Examples

1. Message: "Ours matches the best PSNR at 50× the speed."
   - First idea: two bar charts, one for PSNR and one for FPS. The reader must pair bars across the panels to see the trade-off.
   - Better: one scatter with FPS on a log x-axis and PSNR on y; ours sits alone in the upper right (panel (a)). Caption: "**Ours matches the best PSNR at 50× the speed.** PSNR and FPS on [dataset], measured on one [GPU]."
2. Message: "Our lead grows as the input views get sparser."
   - First idea: one more column in the main table for the sparse setting.
   - Better: PSNR against the number of input views (3, 6, 9, 12, 24), one line per method. The gap visibly widens toward the left.
3. Message: "Without module X, floaters come back around thin structures."
   - First idea: only the ablation table, where a 0.3 dB drop reads as noise.
   - Better: keep the table and add one qualitative row with zoom-ins on thin structures: the full model against the variant without X.
4. Message: "Most of our gain is on small objects."
   - First idea: bars of overall AP for all methods, which repeat Table 1.
   - Better: the AP on small, medium, and large objects in the main table, or gain bars for each size (panel (d)).

### Forms to Avoid

- Pie and donut charts: angles are hard to compare. Use sorted bars or a table.
- 3D bars, 3D pies, and shadows: perspective distorts the values.
- Bars on a truncated axis: a bar's length encodes its value, so bars start at zero. For small differences between large values, plot the difference (panel (d)) or use a table.
- Radar charts: the shape depends on the order and scale of the axes. Use a table or grouped bars.
- Dual y-axes (Rule 6).
- A number on every point: label only the points the message is about.
- More than about six lines in one panel: grey out the lines that are not the point, or split them into panels with shared axes.
- A figure that repeats a table: cut one of them (A2.1).

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
