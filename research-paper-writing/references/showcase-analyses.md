# Showcase Analyses: Figures and Tables That Reveal the Core Idea

Read this file once the main comparison table and the ablation are complete (Writing Rule A2.11 in `SKILL.md`). The main table shows that our method wins and the ablation shows that each component matters, whereas showcase analyses show why the method works and make the paper memorable. Every showcase analysis connects directly to our core idea, and it either explains an interesting phenomenon or shows an advantage of our method. It also follows every rule in `references/figures.md`, so it is informative, looks good, and convinces.

## Think Deeply Before Drawing

Never draw the first analysis that comes to mind. Work through the following steps for the paper as a whole and then again for every candidate, and write the outcome into the analysis plan below.

1. State the mechanism. From the `% Story:` block, write in one sentence what our method does differently from prior methods and why that difference should matter, for example "neighboring points share one motion code, so that motion stays coherent where a single point observes too little."
2. Derive predictions. List at least five observable consequences of the mechanism. Ask what should happen with our method but not with the baselines or the ablated variant, where the gain should be largest, what the method should learn without supervision, and how its advantage should change as the factor that the idea targets grows, such as motion, sparsity, sequence length, noise, or scale.
3. Design a test for each prediction. Decide what is measured or visualized, on which data, against which methods and variants, and which single variable changes, and prefer the variable that the idea itself is about.
4. Check validity. The comparison must be fair, with the same data, budget, and protocol for every method. No trivial explanation may produce the same picture, a control must isolate our component (usually the ablated variant), and the effect must hold on more than one case.
5. Check interest. The analysis must reveal something that the main table cannot, ideally something a reader would not have guessed, and its point must be visible within five seconds.
6. Check the connection. Write one sentence of the form "Because ours <mechanism>, <phenomenon or advantage>." If that sentence does not hold, drop the candidate.
7. Select the two to four strongest candidates, run the experiments behind them (`references/experiments.md`, Run Missing Experiments), and record every candidate with its verdict in the analysis plan.

## Forms That Often Work

These forms serve as inspiration and never as a checklist, because the prediction decides the form.

| What the idea predicts | A showcase that can reveal it |
|---|---|
| Our component learns a meaningful internal quantity. | A visualization of that quantity (attention, weights, codes, fields, or routing) on real inputs, next to what a baseline learns. |
| Our lead grows with the factor that the idea targets. | Lines over that factor for our method, the strongest baselines, and the ablated variant. |
| The gain comes from the cases that the mechanism addresses. | The gain per case (category, difficulty bin, or region type), sorted, with the cases of the mechanism highlighted. |
| Our component removes a specific failure. | The same inputs for the full model and the ablated variant, with zoom-ins and error maps on a shared color scale. |
| The method learns a property without supervision. | The emergent structure, such as clusters, segments, or correspondences, on several inputs. |
| An internal quantity explains the result. | A scatter of that quantity against the error or the gain, together with their correlation. |
| The mechanism works in isolation. | A controlled toy or synthetic experiment in which only the mechanism differs. |
| The module is general. | A plug-in table that adds it to other methods (`references/table-types.md`). |
| Our method reaches higher quality at a lower cost. | Quality against cost, with our method at the best corner. |

## Make It Fancy and Honest

A showcase analysis should be striking at first glance and exact on closer inspection. Compose multi-panel figures with care, overlay error maps or internal quantities on the inputs with one shared color scale, zoom into the region where the mechanism acts, let color encode the variable of the idea, and annotate the phenomenon directly on the figure. Real data, honest axes, and identical scales across compared panels keep the figure convincing (`references/figures.md`).

## Record the Analysis Plan

Write the plan at the top of the main `.tex` file, next to the figure plan. The `Mechanism` line states the core idea, each selected analysis gets a line under its figure or table label, and every rejected candidate remains in the plan together with the reason it was dropped.

```latex
% Analysis plan:
% Mechanism: neighboring points share one motion code, so motion stays coherent where a single point observes too little
% fig:motion_gap: because shared codes pool evidence from neighbors, our lead grows with motion magnitude -> PSNR over per-scene motion magnitude; control: w/o sharing
% fig:codes: because neighbors on one rigid part move together, the codes cluster by part without supervision -> t-SNE of the motion codes colored by part; control: per-point codes of 4D-GS
% fig:error_maps: because shared codes keep thin parts coherent, ours removes the floaters around thin structures -> error maps with zoom-ins; control: w/o sharing
% dropped: gain per texture bin -> unrelated to motion sharing
% dropped: training-time curve -> efficiency is not what the idea is about
```

Every selected analysis also has its line in the figure plan. Its caption ends with the phenomenon or the advantage, and the text explains the mechanism behind it (Writing Rule A2.1).

## What the Checker Verifies

The checker stays silent until the main comparison table and the ablation table appear in the main text without placeholders. From then on, it reports the following problems.

- An ERROR when the analysis plan is missing, has no `Mechanism` line, lists fewer than five candidates, or selects fewer than two analyses.
- An ERROR when a selected line lacks the `because` link to the mechanism, the form after `->`, or the `control:`, or when its label is not a figure or table of the paper.
- A WARN when a dropped candidate gives no reason, or when no selected analysis appears in the main text.

The checker cannot judge whether an analysis is deep, valid, or interesting. Reread every selected analysis against steps 4 to 6 above before you finish.
