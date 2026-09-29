# Experiments Writing Guide

## Goal

Convince reviewers with complete evidence on effectiveness, causality, and practical value.

## Three Core Questions

1. Is the method better than strong baselines?
   - Run comparison experiments against strong and recent baselines.
   - Report standard metrics on the main benchmark(s).
   - Include SOTA or strongest public methods, not only weak baselines.
   - Keep protocol fair (same data split, preprocessing, and evaluation settings).
2. Which modules/design choices make the gain?
   - Run ablation studies for each key module/design choice.
   - Use remove/replace/disable variants and report delta to full model.
   - Include component interaction ablations when modules are coupled.
3. How far can the method generalize under harder settings?
   - Run demos/evaluations on harder or out-of-distribution settings.
   - Add stress-test scenarios (more complex scenes, rarer cases, noisier inputs, or stricter constraints).
   - Report both gains and failure modes to show realistic boundaries.

## Experiment Planning

Every figure and table must show an advantage of our method or a non-obvious finding (Writing Rule A2.1 in `SKILL.md`). Beyond the analyses of the closest work, look for where ours differs most: hard cases where baselines fail, trade-offs (quality against speed, memory, or data), scaling with data or model size, robustness to noise or sparse input, and per-category breakdowns that show where the gain comes from. Before making a figure or table, write its one-line conclusion; if you cannot, do not make it. Then pick the form that shows that conclusion from the table in `references/figure-table-styles.md`.

Before writing Experiments or making any figure or table, write the closest-work plan (Core Workflow step 2 in `SKILL.md`):

1. Name the 1-3 closest prior works: the methods ours is most directly compared with.
2. Open each paper, including its supplementary material, and list every figure and table. If you cannot open a paper, ask the user for its PDF or link.
3. Reproduce each one under the same setting (dataset, split, metrics, protocol) with our method included. Skip one only for a stated reason, e.g., the analysis does not apply to our setting.
4. Record the plan as a comment block at the start of the Experiments section; the checker warns when it is missing:

   ```latex
   % Closest-work plan:
   % [Paper A] Tab. 1 (main comparison on [dataset]) -> ours Tab. 1: done; shows [conclusion]
   % [Paper A] Fig. 6 (ablation of [module]) -> ours Fig. 5: TODO run [experiment]; shows [conclusion]
   % [Paper B] Tab. 3 (runtime) -> skipped: [reason]
   ```

5. Create every planned figure and table now, with `[TODO]` cells where data is missing, and list the experiments the author must run.

```mermaid
flowchart TB
    A["Key Paper Claims"] --> B["What Contributions Are Claimed?"]
    B --> C1["Contribution 1"]
    B --> C2["Contribution 2"]
    B --> C3["Contribution 3"]
    C1 --> D1["Validation Experiment 1"]
    C2 --> D2["Validation Experiment 2"]
    C3 --> D3["Validation Experiment 3"]

    E["Method Pipeline Figure"] --> F["What Modules and Parameters Matter?"]
    F --> G1["Technical Module 1"]
    F --> G2["Technical Module 2"]
    F --> G3["Key Parameter 1"]
    F --> G4["Key Parameter 2"]
    G1 --> H1["Ablation Study 1"]
    G2 --> H2["Ablation Study 2"]
    G3 --> H3["Ablation Study 3"]
    G4 --> H4["Ablation Study 4"]
```

## Experiment Section Decomposition

```mermaid
flowchart TB
    S1["Experimental Setup"] --> S2["Validation Experiment 1"]
    S2 --> S3["Validation Experiment 2"]
    S3 --> S4["Ablation Studies"]
```

## Figure/Table Writing Rules

`Good tables are part of experiment communication quality, not decoration.`

1. Figure captions and table captions are equally important in the writing quality of Experiments.

### Hard rules

1. Put caption above the table.
2. Avoid vertical lines (`|`) in tabular columns.
3. Do not use double rules or dense `\hline` stacks.
4. Use `booktabs` style (`\toprule`, `\midrule`, `\bottomrule`) for clean structure.
5. Use as few horizontal rules as possible; lines should separate groups, not every row.
6. Highlight best and second-best numbers and the row of ours with the macros of the chosen style scheme (`references/figure-table-styles.md`).

### Readability rules from review practice

1. Label metric direction in column headers (for example `PSNR ↑`, `LPIPS ↓`).
2. Add units when needed so values are interpretable without guessing.
3. Align text columns left; keep numeric columns consistently aligned.
4. Keep numeric precision consistent (same decimal places within a metric column).
5. Group multi-dataset or multi-setting results using `\multicolumn` + `\cmidrule`, not vertical separators.
6. One table, one message: do not mix unrelated results in a single table.
7. If rows represent different attributes/ablations, encode that explicitly in row names or attribute columns.
8. Start each caption with a bold one-sentence takeaway of at most 15 words (Writing Rule A2.4 in `SKILL.md`). Then give only the setting, protocol, and notation needed to read it, within 50 words in total; no discussion (`references/figure-table-styles.md`, Write the Caption).
9. Analyze every figure and table in the text: the observation with numbers, the reason ours behaves this way, and what follows. A figure or table that the text never discusses should be cut.
10. For single-column figures/tables in two-column papers, prefer placing them in the right column when layout allows, so readers can enter the page from the left-top text without breaking reading flow.

### Minimal LaTeX checklist

1. Add packages in preamble: `\usepackage{booktabs}`, `\usepackage{colortbl,xcolor}` (and optionally `\usepackage{siunitx}` for decimal alignment).
2. Replace `\hline`-heavy style with `\toprule/\midrule/\bottomrule`.
3. Put `\caption{...}` before `\label{...}` and keep caption above.
4. Use restrained highlighting; never color too many cells.

## Recommended Ablation Package

1. One core ablation table for all major contributions.
2. Several focused mini-ablations for module-level design choices.
3. Matching qualitative visual results for each important ablation.

## Experimental Rigor Checklist

1. Are baselines recent and relevant?
2. Are metrics sufficient and standard for this task?
3. Is ablation tied to every key design claim?
4. Are claims in Abstract/Introduction supported by reported numbers?
5. Are limitations of evaluation scope explicitly stated?
