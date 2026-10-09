# Figures: Informative, Good-Looking, Convincing

Read this file before you make any figure, and `references/table-types.md` before any table. A figure earns its place by showing something informative, such as a result, a comparison, a trend, a visual difference, how the method works, or what the model learns. It need not prove a claim of the story, since a paper has many figures and only a few claims. Above all, every figure must look good and convince.

## Make It Look Good

Reviewers judge a paper by its figures before they read a word.

- One look across the paper. Every figure uses the same fonts and line widths, and the same color and marker for each method.
- Text at least as large as the caption text at print size.
- Clean layouts, with aligned panels, shared axes and one legend for related panels, and no clutter or wasted space.
- Crisp output, with vector PDF for plots and drawn diagrams, and high-resolution images for generated figures, photos, and renders.
- Finished details, such as aligned boxes and straight arrows in diagrams, even gaps between panels, and labels that never overlap.

## Make It Convince

- Show the evidence directly. Put ours next to the baselines, on the same inputs, at the same scale.
- Lead the eye to the difference, with zoom-ins where ours is better and the key numbers where the eye lands.
- Use real data and honest axes (Figures That Hide the Message, below). One trick makes reviewers doubt every figure.
- Show enough cases that the effect cannot be luck, e.g., several scenes rather than one.
- Let it stand alone. From the figure and its caption, a reader sees the point within five seconds.

## Decide What to Show

1. Pick content that tells the reader something, such as an advantage of ours, a result reviewers expect, how the method works, what the model learns, or a non-obvious finding. Never draw a figure for decoration, or one that only repeats a table's numbers (A2.1).
2. Write what it shows in one sentence, with a number when it is a result, e.g., "Ours keeps 70% accuracy at noise level 0.5, while every baseline falls below 45%." It becomes the conclusion at the end of the caption (A2.4).
3. Choose the form that shows it most clearly and convincingly. The table below lists common choices. Use it as a starting point, never as a rule.
4. Add the figure to the figure plan (below) before drawing it. If its form already appears in two main-text figures, follow Vary the Forms.
5. Draw it with real data, export it to PDF, check it (Check Every Figure, below), and look at it at print size. Redraw it until it looks good and convinces.
6. Put numbers that readers will cite or compare in a table, and trends, trade-offs, and distributions in a plot. When both matter, plot in the main text and give the full table in the Appendix.

| What you want to show | A form that can show it |
|---|---|
| Ours beats the baselines on standard benchmarks. | SOTA comparison table (`references/table-types.md`). |
| Ours is better and cheaper (speed, memory, parameters, data). | Quality against cost, one point per method. |
| The gain grows, or holds, with scale (data, model size, input views). | Lines over the scale, one per method. |
| Ours degrades least on harder inputs (noise, occlusion, sparsity). | Lines over the difficulty level. |
| The gain comes from specific cases (categories, difficulty bins). | The gain per case, sorted. |
| Ours fails less often, or less badly. | The share of samples below each error, or a box plot. |
| Ours is insensitive to a hyperparameter. | A line over its range, with the default marked. |
| Ours trains faster or more stably. | Training curves over iterations or time. |
| Each component matters. | Ablation table, with a qualitative row when a component fixes a visible artifact. |
| Our module helps every method it is added to. | Plug-in table (`references/table-types.md`). |
| Ours fixes a visible failure (artifacts, blur, wrong geometry). | The same inputs for each method, with zoom-ins on the failure. |
| What the model learns or attends to. | Maps overlaid on the input. |
| The task or the data. | Example inputs and outputs, or dataset statistics. |
| How the method works. | Architecture figure, required in the Method and generated with `generate_image` (`references/method.md`). |
| The key idea, at first glance. | Teaser (Part D of `references/introduction.md`). |

### The Figure Plan

Keep one line per figure and per table at the top of the main `.tex` file. Write the line before making the figure or table, and update it when its message or form changes. The checker reads this block. It reports an ERROR for a main-text figure or table without a line. It warns about a form used in more than two figures, and about a table line that names no table type.

```latex
% Figure plan (label: message -> form):
% fig:teaser: ours matches the best PSNR at 50x the speed -> results teaser with FPS labels
% fig:arch: how the method works -> architecture diagram
% fig:qualitative: ours keeps thin structures that baselines blur -> qualitative grid with zoom-ins
% fig:views: [C2] our lead grows as the input views get sparser -> lines over the number of views
% fig:per_class: the gain comes from thin categories -> sorted gain bars
% tab:main: [C1] ours has the best PSNR on both datasets -> SOTA comparison table
% tab:ablation: [C3] each module helps; the deformation module the most -> ablation table
```

When a figure or table is the evidence for a claim of the story, start its message with that claim, e.g., `[C1]`, so every claim has evidence (`references/story.md`). Other figures need no tag. Name the form with one of these words, so the checker can count it: teaser, diagram, qualitative grid, scatter, lines, bars, cumulative curve, map, or table. Synonyms also work: pipeline, curves, histogram, box plot. For a table, name its type from `references/table-types.md`, e.g., SOTA comparison table or plug-in table. A figure whose panels use different forms names each, e.g., `lines over noise; sorted gain bars`.

### Vary the Forms

Readers skim the figures before the text. When several figures look alike, the paper reads like one result repeated.

1. In the main text, use one form for at most two figures, e.g., two line plots, two bar charts, or two qualitative grids.
2. When a third message needs the same form, merge it with a related figure. Use panels (a) and (b) with shared axes and one legend. Otherwise, move the weakest one to the Appendix, or use a table when exact numbers matter.
3. The Appendix has no such limit: per-scene grids and extra curves belong there.

### Worked Examples

1. Message: "Ours matches the best PSNR at 50× the speed."
   - First idea: two bar charts, one for PSNR and one for FPS. The reader must pair bars across the panels to see the trade-off.
   - Better: one plot of PSNR against FPS, where ours stands alone at the best corner. Caption: "PSNR versus rendering speed on [dataset], measured on one [GPU]. Ours matches the best PSNR at 50× the speed."
2. Message: "Our lead grows as the input views get sparser."
   - First idea: one more column in the main table for the sparse setting.
   - Better: PSNR against the number of input views (3, 6, 9, 12, 24), one line per method. The gap visibly widens toward the left.
3. Message: "Without module X, floaters come back around thin structures."
   - First idea: only the ablation table, where a 0.3 dB drop reads as noise.
   - Better: keep the table and add one qualitative row with zoom-ins on thin structures: the full model against the variant without X.
4. Message: "Most of our gain is on small objects."
   - First idea: bars of overall AP for all methods, which repeat Table 1.
   - Better: the AP on small, medium, and large objects in the main table, or the gain for each size, sorted.

### Figures That Hide the Message

- Pie charts: angles are hard to compare. Use sorted bars or a table.
- 3D bars and pies: perspective distorts the values.
- Bars on a truncated axis: a bar's length encodes its value, so bars start at zero. For small differences between large values, show the difference or use a table.
- Radar charts: the shape depends on the order and scale of the axes.
- Two y-axes in one panel: put two measures in two panels.
- A number on every point: label only the points the message is about.
- More than about six lines in one panel: split them into panels with shared axes.
- A figure that repeats a table's numbers: cut it, unless it reveals what the table cannot (A2.1).
- A title that states the conclusion: titles name what a panel shows ("PSNR vs. views"); the conclusion goes at the end of the caption.

## Write the Caption

A caption first says what the figure or table shows, then what each part shows, then what to conclude. The text explains why.

1. What it shows, in one sentence: "Qualitative comparison on the D-NeRF dataset." or "PSNR versus rendering speed on Mip-NeRF 360." You may set it in bold as a title.
2. For subfigures or panels, what each one shows: "(a) Lego. (b) Jumping Jacks." Add a reading aid only when the figure needs it, e.g., "Insets zoom into the boxed regions."
3. Then the conclusion, from the figure plan, in at most 2 sentences: "Ours keeps the thin structures that the baselines blur."
4. Keep the caption within 50 words, or 80 for a teaser or architecture figure. An architecture figure may describe its stages (a), (b), (c) and needs no conclusion.
5. Leave out how the figure or table was made and its formatting: "best in bold, second underlined", "ours is shaded", "plotted with Matplotlib", "↑ means higher is better". Readers know these conventions. Leave out analysis (it goes in the text) and significance tests (they go in the Appendix).
6. Titles inside a figure and subfigure captions name what is shown ("PSNR vs. views", "Input", "Ours"), never the conclusion.
7. Tables follow the same rules, with the caption above the table (A2.4).

The checker counts the words; a citation, a reference, or an inline formula counts as one word. It warns when a caption opens with a conclusion, has no conclusion, has more than 3 sentences after the first, or explains formatting.

```latex
% Too long (62 words): the analysis and the reasons belong in the text.
\caption{Qualitative comparison on the D-NeRF dataset. We compare our method with 4D-GS, Deformable 3DGS, and D-NeRF on four scenes. As can be seen, our method produces sharper details and fewer artifacts than the baselines, especially around thin structures such as fingers and hair. This is because our deformation field models motion at a finer scale, which demonstrates the effectiveness of our design.}

% Opens with the conclusion, and explains formatting.
\caption{\textbf{Ours keeps thin structures that the baselines blur.} Novel views on the D-NeRF dataset. Our results are highlighted in red boxes.}

% Better (35 words): what it shows, the parts, a reading aid, then a short conclusion.
\caption{Qualitative comparison on the D-NeRF dataset~\cite{dnerf}. (a) Lego. (b) Jumping Jacks. Methods follow the order of Table~\ref{tab:main}, and insets zoom into the boxed regions. Ours keeps the thin structures that the baselines blur.}
```

## Check Every Figure

Check every figure after drawing it, and again after every change (Writing Rule A2.9):

1. Export plots and diagrams to PDF at the printed width (Technical Requirements, below).
2. Run the QA script on the script that draws them, or on finished files:

   ```bash
   python3 <this skill's directory>/scripts/figure_qa.py figures/make_figures.py   # every figure the script saves
   python3 <this skill's directory>/scripts/figure_qa.py figures/teaser.png          # photos, renders, other tools
   ```

   It reports:
   - a legend that covers data;
   - text that overlaps other text, the legend, or another panel;
   - content cut off at the figure edge, or data outside the axis range;
   - text smaller than the caption font, and text, lines, or markers that are too small or too large;
   - axis ranges much wider than the data, and empty margins;
   - panel titles that state a conclusion.

   Add `--print-width 3.25` when a figure is printed at a width other than the one it is drawn at.
3. Fix every ERROR and every WARN, then run it again; justify any remaining WARN in your reply.
4. Open each preview it writes to `.figure-qa/` next to the figure, and look at it. Check what no script sees: the message shows within five seconds, and nothing looks crowded or empty.

`check_tex.py` reads `.figure-qa/record.json`: it reports an ERROR for any included image that was not checked after its last change, and repeats what the QA found.

## Technical Requirements

1. Draw each figure at its printed width and include it at that width (`width=\columnwidth` or `\linewidth`), so its text stays at the caption size (A2.2). Typical widths: CVPR and ICCV 3.25 in per column and 6.875 in across; ICML 3.25 in and 6.75 in; ACL 3.03 in and 6.3 in; NeurIPS and ICLR 5.5 in; ECCV 4.8 in. Confirm with `\the\columnwidth` and `\the\textwidth` in the template.
2. Save plots and drawn diagrams as vector PDF with embedded fonts (in Matplotlib, set `pdf.fonttype` to 42; A1.4). Use PNG or JPEG only for generated figures such as the architecture figure (`references/method.md`), photos, and renderings, at 300 dpi or more at print size.
3. Show each method under the same name, and in the same order, in every figure and table (A2.3).
