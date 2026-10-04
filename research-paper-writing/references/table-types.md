# Tables: Pick the Type for the Comparison

Read this file before you create or restyle any table (Writing Rule A2.8 in `SKILL.md`). A table supports one comparison. First write that comparison as one sentence. Then pick the type below that shows it, and add the table to the figure plan with its type:

```latex
% tab:main: [C1] ours has the best PSNR on both datasets -> SOTA comparison table
% tab:plugin: [C2] our module helps every detector it is added to -> plug-in table
```

Lay out each table as the style references do (`references/style-references.md`): their columns, grouping, metric arrows, decimals, and marks for the best results. Use the templates below for what they leave open, and style every table with the chosen scheme (`references/figure-table-styles.md`).

## Pick the Type

| What the table must show | Type | Rows | Columns |
|---|---|---|---|
| Ours beats prior work on the standard benchmarks. | SOTA comparison | Methods grouped by family, ours last | Datasets, then metrics with ↑ or ↓; cost columns only if speed or size is a claim |
| Our module helps whatever method it is added to. | Plug-in | Each base method, then the same method "+ ours" | Metrics with the gain, and the added cost |
| Each component matters. | Ablation | One variant per row, the full model last | A ✓ or ✗ per component, then metrics |
| Ours is cheaper or faster. | Efficiency | Methods | Training time, memory, parameters, speed, and one quality metric |
| Where the gain comes from. | Breakdown | Methods | Categories, difficulty bins, or scenes |
| Ours transfers to unseen data. | Generalization | Methods | Train-to-test pairs, or unseen datasets |
| Ours holds up on harder inputs. | Robustness | Methods | Levels of noise, sparsity, or occlusion |
| Ours supports what others cannot. | Property | Methods | Properties, each ✓ or ✗ |
| Ours is insensitive to a setting. | Sensitivity | Values of the setting | Metrics |
| People prefer ours. | User study | Ours against each baseline | Share of votes for ours |

Prefer a plot over a table when the message is a trend, a trade-off, or a distribution (robustness and sensitivity usually are; see `references/figure-table-styles.md`). Prefer a table when readers will cite or compare the exact numbers. Never show the same numbers twice. Draw a figure of a table's numbers only if it reveals what the table cannot, such as a trend across settings or a trade-off. Otherwise, cut one of them.

Main text: the SOTA comparison, the ablation, and the tables that carry a claim. Appendix: per-scene and per-class tables, full sensitivity sweeps, and extra baselines.

## Rules for Every Comparison Table

1. Run every method you can under one protocol: the same split, resolution, metrics, training budget, and, for timings, the same GPU. Say it in the setup text, not in the caption.
2. Cite every method in its row: `4D-GS~\cite{wu2024}` (Writing Rule A4.6).
3. Numbers you could not run go in the same table. Copy them from the original paper, mark them with `\textsuperscript{\dag}`, and explain the mark in a one-line table note, e.g., "\dag Reported by the original paper." Mention it once in the text, in a short clause. Never move reported numbers to a separate table, and never explain where they come from at length in the caption or the text.
4. Include the strongest and the latest methods (the `% Latest SOTA:` line in `references/experiments.md`). Write `--` with a table note for a missing number; never drop the row.
5. Put the metric direction (`PSNR$\uparrow$`, `LPIPS$\downarrow$`) and the unit in the header, and use the same number of decimals in a column.
6. Mark the best and second-best number of each column with `\best` and `\second`, shade the row of ours with `\oursrow`, and put ours last in its group.
7. Group rows by method family or setting with `\midrule`, and columns by dataset with `\multicolumn` and `\cmidrule`. No vertical rules.
8. Fit the column or page width by dropping columns that do not serve the comparison, or by moving them to the Appendix. Never shrink a table with `\resizebox` below the caption size.
9. Caption above the table: what it compares and on which data, then the conclusion in at most 2 sentences (Writing Rule A2.4). No formatting notes such as "best in bold".
10. Analyze it in the text: the numbers, the reason, and what follows (Writing Rule A2.1).

## Templates

The preamble needs `booktabs`, the scheme's `\input{table-style}`, and, for check marks, `\usepackage{pifont}` with `\newcommand{\cmark}{\ding{51}}` and `\newcommand{\xmark}{\ding{55}}`. Fill the brackets with your own methods and numbers.

### SOTA Comparison

```latex
\begin{table*}[t]
  \caption{Comparison with state-of-the-art methods on the [Dataset 1]~\cite{d1} and [Dataset 2]~\cite{d2} datasets. [Conclusion, e.g., Ours has the best PSNR on both datasets and renders 1.4$\times$ faster than the fastest baseline.]}
  \label{tab:main}
  \centering
  \small
  \begin{tabular}{lccccccc}
    \toprule
    & \multicolumn{3}{c}{[Dataset 1]} & \multicolumn{3}{c}{[Dataset 2]} & \\
    \cmidrule(lr){2-4} \cmidrule(lr){5-7}
    Method & PSNR$\uparrow$ & SSIM$\uparrow$ & LPIPS$\downarrow$ & PSNR$\uparrow$ & SSIM$\uparrow$ & LPIPS$\downarrow$ & FPS$\uparrow$ \\
    \midrule
    \multicolumn{8}{l}{\textit{[Family 1, e.g., NeRF-based]}} \\
    [Method 1]~\cite{m1} & [..] & [..] & [..] & [..] & [..] & [..] & [..] \\
    [Method 2]~\cite{m2} & [..] & [..] & [..] & [..] & [..] & [..] & [..] \\
    \midrule
    \multicolumn{8}{l}{\textit{[Family 2, e.g., Gaussian-based]}} \\
    [Method 3]~\cite{m3}\textsuperscript{\dag} & [..] & [..] & [..] & -- & -- & -- & [..] \\
    [Latest SOTA]~\cite{m4} & \second{[..]} & [..] & [..] & \second{[..]} & [..] & [..] & \second{[..]} \\
    \oursrow Ours & \best{[..]} & \best{[..]} & \best{[..]} & \best{[..]} & \best{[..]} & \best{[..]} & \best{[..]} \\
    \bottomrule
    \multicolumn{8}{l}{\footnotesize \textsuperscript{\dag}Reported by the original paper. -- Not reported.} \\
  \end{tabular}
\end{table*}
```

### Plug-in

Use it when our contribution is a module, loss, or training scheme that other methods can adopt. Train each base method and its "+ ours" version with the same schedule, include the strongest base method, and report the added cost. Keep every base method you ran in the table; the text sells the gains and does not discuss a row where ours does not help.

```latex
\begin{table}[t]
  \caption{Adding [our module] to existing [task] methods on [Dataset]~\cite{d1}. [Conclusion, e.g., It improves every method by 0.6 to 1.4 AP at 3\% more parameters.]}
  \label{tab:plugin}
  \centering
  \small
  \begin{tabular}{lccc}
    \toprule
    Method & AP$\uparrow$ & Params (M) & Time (ms)$\downarrow$ \\
    \midrule
    [Method 1]~\cite{m1} & [..] & [..] & [..] \\
    \oursrow \quad + [our module] & [..] (+[..]) & [..] & [..] \\
    \midrule
    [Method 2]~\cite{m2} & [..] & [..] & [..] \\
    \oursrow \quad + [our module] & [..] (+[..]) & [..] & [..] \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Ablation

Change one thing per row, or build the model up one component at a time, as below. Use the same setting for every row. When a component fixes a visible artifact, add a qualitative row to a figure as well.

```latex
\begin{table}[t]
  \caption{Ablation of the components of [method] on [Dataset]~\cite{d1}. [Conclusion, e.g., Each component helps, and the deformation module adds the most (+2.1 dB).]}
  \label{tab:ablation}
  \centering
  \small
  \begin{tabular}{ccccc}
    \toprule
    [Component A] & [Component B] & [Component C] & PSNR$\uparrow$ & LPIPS$\downarrow$ \\
    \midrule
    & & & [..] & [..] \\
    \cmark & & & [..] & [..] \\
    \cmark & \cmark & & \second{[..]} & \second{[..]} \\
    \oursrow \cmark & \cmark & \cmark & \best{[..]} & \best{[..]} \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Efficiency

Measure every method on the same GPU, at the same resolution, and name both in the text. Keep one quality metric, so speed is not bought silently with quality.

```latex
\begin{table}[t]
  \caption{Training and rendering cost on [Dataset]~\cite{d1}. [Conclusion, e.g., Ours trains in 6 minutes and renders at 120 FPS, with the best PSNR.]}
  \label{tab:cost}
  \centering
  \small
  \begin{tabular}{lcccc}
    \toprule
    Method & Training (min)$\downarrow$ & Memory (GB)$\downarrow$ & FPS$\uparrow$ & PSNR$\uparrow$ \\
    \midrule
    [Method 1]~\cite{m1} & [..] & [..] & [..] & [..] \\
    [Method 2]~\cite{m2} & [..] & [..] & [..] & [..] \\
    \oursrow Ours & [..] & [..] & [..] & [..] \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Generalization

```latex
\begin{table}[t]
  \caption{Cross-dataset evaluation, trained on [A] and tested on [B] and [C] without fine-tuning. [Conclusion, e.g., On unseen data, ours drops 1.2 points and the baselines 4 to 6.]}
  \label{tab:transfer}
  \centering
  \small
  \begin{tabular}{lccc}
    \toprule
    Method & [A]$\rightarrow$[A] & [A]$\rightarrow$[B] & [A]$\rightarrow$[C] \\
    \midrule
    [Method 1]~\cite{m1} & [..] & [..] & [..] \\
    \oursrow Ours & [..] & [..] & [..] \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Breakdown, Robustness, and Sensitivity

Put these in the Appendix as tables, and show the point in the main text as a plot (`references/figure-table-styles.md`, panels (c), (d), and (f)). Use sorted gain bars for a breakdown, lines over the difficulty level for robustness, and a line over the setting for sensitivity.

### Property

See the comparison-table template in `references/examples/introduction/teaser-and-comparison-table-templates.md`. Use it in the Introduction or Related Work, never as evidence of accuracy.

### User Study

Report the share of votes for ours against each baseline, the number of participants and questions in the text, and the full protocol in the Appendix.

```latex
\begin{table}[t]
  \caption{User study on [task], with the share of votes for ours in pairwise comparisons. [Conclusion, e.g., Participants prefer ours over every baseline in at least 70\% of the votes.]}
  \label{tab:user}
  \centering
  \small
  \begin{tabular}{lc}
    \toprule
    Ours vs. & Votes for ours (\%)$\uparrow$ \\
    \midrule
    [Method 1]~\cite{m1} & [..] \\
    [Method 2]~\cite{m2} & [..] \\
    \bottomrule
  \end{tabular}
\end{table}
```

## Statistical Significance

Keep it short in the main text (Writing Rule B4.5). Main tables report the mean, at most with ± the standard deviation. The text spends one sentence on it, for example:

- "The standard deviation over 3 seeds is below 0.1 dB for every method."
- "Appendix C reports paired t-tests; all gains of ours are significant (p < 0.01)."

Put the per-seed numbers and the tests in the Appendix, never in captions.
