# The Story: One Argument for the Whole Paper

Read this file before you write or rewrite any section (Core Workflow step 3 in `SKILL.md`). A paper makes one argument. Every section and paragraph advances it or goes to the Appendix. Figures and tables need not each prove a claim, since a paper has many figures and only a few claims. Each must show something informative (`references/figures.md`).

## Find the Story

Answer these before writing, in this order; they are the backward-reasoning questions of `references/introduction.md`:

1. Problem: what task, what makes it hard, and why the best prior methods still fail. Name the concrete cause, not "it is challenging".
2. Insight: the one observation or idea that makes the problem tractable. A reviewer should be able to repeat it in one sentence.
3. Method: how the method turns the insight into a design, and the name the paper uses for it (the key term).
4. Claims: 2-4 checkable claims the experiments will prove, e.g., "ours keeps 2 dB more PSNR than the best baseline when the input views drop to 3". Each claim needs at least one figure or table as evidence.
5. Takeaway: the one sentence a reader should remember a week later.

Then write the story in one sentence: "[Task] is hard because [cause], and prior methods [fail how]. We observe that [insight], which lets [method] [achieve the main result]."

When the paper already exists, derive the story from its strongest results, not from its current wording. Pick the most interesting story that the evidence supports.

## Find the Evidence

Sell the story actively (Principle 3 in `SKILL.md`). Search every result you have, not only the main table, for evidence that supports it:

- per-scene, per-class, and per-difficulty breakdowns;
- hard subsets: fast motion, sparse views, long sequences, small objects, rare classes;
- settings: little data, few steps, low memory, low resolution, noisy input;
- cost: speed, memory, parameters, training time;
- qualitative cases, user studies, and the internals of ours (learned features, attention, error maps).

A few data points are enough when they show something interesting, e.g., ours wins on the three scenes with the fastest motion. A result that holds only on part of the data still supports a claim about that part. Name that part in the claim, e.g., "on scenes with fast motion, ours gains 2.1 dB". Show those cases in a figure: sorted gain bars, or zoom-ins on the hard cases. If a quick experiment would give the evidence, such as a breakdown of existing results or an extra metric, run it (`references/experiments.md`, Run Missing Experiments).

Never discuss where ours loses, anywhere in the paper: no failure cases, and no sentences on scenes or metrics where a baseline wins. Those numbers stay in the tables without comment. Never invent or change a number, and never drop a method, dataset, or row because ours loses there.

## Record It

Write the story at the top of the main `.tex` file, before editing any section, and update it when the story changes. The checker reads it:

```latex
% Story:
% Problem: [task] fails when [condition], because [cause]; [prior methods] [fail how].
% Insight: [the observation or idea that makes it tractable].
% Method: [how the method turns the insight into a design].
% Claim C1: [checkable claim, e.g., ours beats the latest state of the art on (benchmark)].
% Claim C2: [checkable claim, e.g., ours degrades least as (difficulty) grows].
% Claim C3: [checkable claim, e.g., each component of ours helps].
% Takeaway: [the one sentence to remember].
% Key term: [the name the paper uses for the key idea]
```

Tag the figure-plan lines of the figures and tables that are evidence for a claim, so every claim has evidence. Other figures need no tag:

```latex
% fig:teaser: ours keeps details that baselines blur -> results teaser with zoom-ins
% fig:pipeline: how the method works -> pipeline diagram
% tab:main: [C1] ours has the best PSNR on both datasets -> SOTA comparison table
% fig:views: [C2] our lead grows as the views get sparser -> lines over the number of views
% tab:ablation: [C3] each module helps -> ablation table
```

## Tell It in Every Section

| Part | Its job in the story |
|---|---|
| Title | Names the key idea or the main result. |
| Abstract | One or two sentences per story part: problem, insight, method, the strongest evidence. |
| Introduction | Background, then the problem or motivation, the insight, the method, and contributions that restate the claims (`references/introduction.md`). |
| Related Work | Groups prior work by what it lacks relative to the insight; each topic ends with how ours differs. |
| Method | Motivates every module by the problem, and shows how it realizes the insight; nothing in it is unrelated to the story. |
| Experiments | Tests each claim in turn, with a figure or table as evidence, and says what each result means for the story. |
| Conclusion | Restates the problem, the insight, the strongest evidence, and the takeaway, then what it opens up. |

Use the key term for the key idea everywhere, with no synonyms (B1).

## Check It

1. Reverse outline (`references/paragraph-clarity.md`): every paragraph's first sentence maps to one story part. Move or cut a paragraph that maps to none.
2. Every claim has a figure or table as evidence, tagged with the claim in the figure plan. The checker reports a claim without evidence as an ERROR.
3. No sentence says where ours loses or fails. The checker reports such a sentence as an ERROR (Writing Rule B4.3), and a "Limitations" or "Failure cases" part as a WARN.
4. The key term appears in the abstract, the Introduction, the Experiments, and the Conclusion; the checker warns where it is missing.
5. Read the abstract, the last paragraph of the Introduction, the captions, and the Conclusion alone: together they must tell the whole story.
