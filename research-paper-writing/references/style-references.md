# Style References: Write and Draw Like the Closest Papers

Read this file first, with `references/story.md` (Core Workflow step 2 in `SKILL.md`). The papers closest to ours are the most important reference for how the paper reads and looks. Reviewers in the area expect what those papers do. Follow them in writing, figures, and tables. The examples, templates, and style schemes of this skill only fill what they leave open. The Writing Rules still apply on top of both.

## Pick the Papers

1. Choose 3-5 papers. Start with the closest prior works (`references/experiments.md`, Experiment Planning), then add recent, well-written papers on the same task, ideally from the target venue and the last two years. Ask the user if they have favorites.
2. Find them with the alphaXiv tools, a web search, or the user's list.
3. Download each PDF into the project, e.g., `refs/paperA.pdf`. If you cannot download one, ask the user for it.

## Look at Them

1. Run `python3 <this skill's directory>/scripts/page_qa.py --reference refs/paperA.pdf`. It writes overview sheets of the paper's main pages, four per sheet, and each of its figures and tables at up to 300 dpi, with a code on each image.
2. Open every image with your image viewer, and study the layout on the sheets and the details of the figures and tables: fonts, line widths, colors, and markers.
3. Read the text of each section as well, with the alphaXiv tools or from the PDF.
4. Confirm with the codes, e.g., `page_qa.py refs/paperA.pdf --confirm K7QF`.

## What to Take from Them

- Writing. The order and length of the sections, how the Introduction opens and lists the contributions, the terms and notation of the field, the tone, and how results are stated.
- Figures. Which figures they have and where (teaser, pipeline, qualitative grids, plots), the layout of the teaser and the pipeline, the drawing style, colors, fonts, line widths, and markers, and how they mark zoom-ins.
- Tables. The columns and their grouping, the metric arrows, the decimals, how the best results are marked, and the caption style.

Follow their style with our own content. Never copy their text, figures, or captions.

## Record It

Write the block at the top of the main `.tex` file. The checker reads it:

```latex
% Style references:
% PaperA (Author et al., CVPR 2024), refs/paperA.pdf -> section structure, teaser layout, table layout
% PaperB (Author et al., ICCV 2025), refs/paperB.pdf -> plot style, colors and fonts, qualitative grid
% PaperC (Author et al., CVPR 2025), refs/paperC.pdf -> writing tone, pipeline style, captions
```

The checker reports an ERROR when the block is missing, when it lists fewer than 3 papers, and when a PDF is missing or its images were not all viewed. It warns when a line names nothing to follow, or when no line covers the writing, the figures, or the tables.

## Use Them

- Before writing a section, reread that section in each reference, and match its structure, length, and tone.
- Before drawing a figure, look at the reference figure with the same job, such as their teaser before ours, and match its layout and style. Use the style scheme closest to them, and adjust its colors and fonts to match (`references/figure-table-styles.md`).
- Before making a table, match their layout (`references/table-types.md`).
- When the references disagree, follow the one from the target venue, then the most recent one.
