# The Story: One Argument for the Whole Paper

Read this file before you write or rewrite any section (Core Workflow step 3 in `SKILL.md`). A paper makes one argument. Every section, paragraph, figure, and table either advances it or goes to the Appendix.

## Find the Story

Answer these before writing, in this order; they are the backward-reasoning questions of `references/introduction.md`:

1. Problem: what task, what makes it hard, and why the best prior methods still fail. Name the concrete cause, not "it is challenging".
2. Insight: the one observation or idea that makes the problem tractable. A reviewer should be able to repeat it in one sentence.
3. Method: how the method turns the insight into a design, and the name the paper uses for it (the key term).
4. Claims: 2-4 checkable claims the experiments will prove, e.g., "ours keeps 2 dB more PSNR than the best baseline when the input views drop to 3". Each claim needs at least one figure or table as evidence.
5. Takeaway: the one sentence a reader should remember a week later.

Then write the story in one sentence: "[Task] is hard because [cause], and prior methods [fail how]. We observe that [insight], which lets [method] [achieve the main result]."

When the paper already exists, derive the story from its strongest results, not from its current wording. If the evidence does not support the intended story, change the story or weaken the claims (Principle 3 in `SKILL.md`); never stretch the evidence.

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

Tag each line of the figure plan with the claim it supports, or with `[Method]` or `[Insight]` for a pipeline diagram or a basic-idea teaser:

```latex
% fig:teaser: [Insight] ours keeps details that baselines blur -> results teaser with zoom-ins
% fig:pipeline: [Method] how the method works -> pipeline diagram
% tab:main: [C1] ours has the best PSNR on both datasets -> SOTA comparison table
% fig:views: [C2] our lead grows as the views get sparser -> lines over the number of views
% tab:ablation: [C3] each module helps -> ablation table
```

## Tell It in Every Section

| Part | Its job in the story |
|---|---|
| Title | Names the key idea or the main result. |
| Abstract | One or two sentences per story part: problem, insight, method, the strongest evidence. |
| Introduction | Problem, then why prior methods fail, then the insight, the method, the evidence, and contributions that restate the claims. |
| Related Work | Groups prior work by what it lacks relative to the insight; each topic ends with how ours differs. |
| Method | Motivates every module by the problem, and shows how it realizes the insight; nothing in it is unrelated to the story. |
| Experiments | Tests each claim in turn; every figure and table names its claim, and the text says what each result means for the story. |
| Conclusion | Restates the problem, the insight, and the takeaway, then the limits of the story's scope. |

Use the key term for the key idea everywhere, with no synonyms (B1).

## Check It

1. Reverse outline (`references/paragraph-clarity.md`): every paragraph's first sentence maps to one story part. Move or cut a paragraph that maps to none.
2. Every figure and table supports a claim; every claim has evidence. The checker reports a claim without evidence as an ERROR, and a figure or table without a claim tag as a WARN.
3. The key term appears in the abstract, the Introduction, the Experiments, and the Conclusion; the checker warns where it is missing.
4. Read the abstract, the last paragraph of the Introduction, the captions, and the Conclusion alone: together they must tell the whole story.
