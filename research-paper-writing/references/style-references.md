# Style References: How the Field Writes

Read this file first, with `references/story.md` (Core Workflow step 2 in `SKILL.md`). The papers closest to ours show how the field writes: the order and length of the sections, the terms, the tone, and the results reviewers expect to see. Use them as the reference for the writing. Decide what each figure and table shows yourself, never by copying theirs (`references/figures.md`). The Writing Rules still apply on top.

## Pick the Papers

1. Choose 3-5 papers of three kinds: the closest prior works (`references/experiments.md`, Experiment Planning), recent well-written papers on the same task, ideally from the target venue and the last two years, and papers whose contribution is of a similar size and kind to ours. A new module on an existing pipeline is written differently from a new task or a new paradigm, so match the level of ours. Ask the user if they have favorites.
2. Find them with the alphaXiv tools, a web search, or the user's list.
3. Download each PDF into the project, e.g., `refs/paperA.pdf`. If you cannot download one, ask the user for it.

## Look at Them

1. Run `python3 <this skill's directory>/scripts/page_qa.py --reference refs/paperA.pdf`. It writes overview sheets of the paper's main pages, four per sheet, with a code on each.
2. Open every sheet and see how the paper is built: the order of its sections and what it shows where.
3. Read the text of each section, with the alphaXiv tools or from the PDF.
4. Confirm with the codes, e.g., `page_qa.py refs/paperA.pdf --confirm K7QF`.

## What to Take from Them

- The vibe, such as how each section opens, how quickly the Introduction reaches the problem, how the insight is presented, how confident the claims sound, and the length and pace of the paragraphs.
- The order and length of the sections, and how the Introduction lists the contributions.
- The terms and notation of the field, the tone, and how results are stated.
- The benchmarks, metrics, and baselines that reviewers will expect, so our comparison is complete.

Take their vibe, and never copy their sentences or their specific content. Never make a figure or table only because they have one.

## Record It

Write the block at the top of the main `.tex` file. The checker reads it:

```latex
% Style references:
% PaperA (Author et al., CVPR 2024), refs/paperA.pdf -> closest work; section structure, the vibe of the Introduction
% PaperB (Author et al., ICCV 2025), refs/paperB.pdf -> recent; terms and notation, how results are stated
% PaperC (Author et al., CVPR 2025), refs/paperC.pdf -> similar contribution; tone and pace, the benchmarks reviewers expect
```

The checker reports an ERROR when the block is missing, when it lists fewer than 3 papers, and when a PDF is missing or its sheets were not all viewed. It warns when a line names nothing to take from the paper.

## Use Them

- Before writing a section, reread that section in each reference, and match its vibe, that is, its structure, length, tone, and pace, in your own sentences.
- When the references disagree, follow the one from the target venue, then the most recent one.
