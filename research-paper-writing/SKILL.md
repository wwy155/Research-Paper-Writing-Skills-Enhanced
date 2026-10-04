---
name: research-paper-writing
description: Write or improve academic paper writing quality for ML/CV/NLP-style papers with clear section structure, paragraph flow, and reviewer-facing presentation. Use when drafting or revising Abstract, Introduction, Related Work, Preliminaries, Method, Experiments, or Conclusion; polishing figures/tables, wording, or LaTeX typesetting; checking claim-support alignment; or performing self-review before submission.
---
# Research Paper Writing

## Required in Every Paper

These hold after every task that edits the paper, even a narrow one, unless the user explicitly says to skip one. The checker reports each gap as an ERROR and ends with a pass/fail list of these items; copy that list into your reply. Missing data never excuses a gap: create the figure or table, and run the experiment behind it (item 9).

1. The venue is settled, its rules are looked up and recorded, its template is in use, and the main text ends exactly at its page limit (Execution Rule 1).
2. The Appendix or Supplementary file exists from the start, follows the venue's Appendix rules (placement, page limit, format), holds the detailed content, and the main text references it (Execution Rule 2).
3. The story is written down, every figure and table supports one of its claims, and every claim has evidence (Core Workflow step 3).
4. At least 3 style references, the papers closest to ours, were viewed with `scripts/page_qa.py --reference`, and the paper follows their writing, figure, and table style (Core Workflow step 2).
5. The closest-work plan gives every figure and table of each closest paper a line, and each one is reproduced in our paper or skipped with a reason (Core Workflow step 2).
6. The main comparison includes the latest state of the art, and the text discusses it (`references/experiments.md`).
7. The main text has at least 3 figures, and every figure and table has its message and form in the figure plan (A2.1, A2.7).
8. Every included image passed `scripts/figure_qa.py` after its last change (A2.9).
9. Every needed result is run and filled in from its result file, or logged as running, or as blocked with the user asked (`% Experiment log:` in `references/experiments.md`).
10. Experiments explains and cites every metric before the first result (A4.9).
11. After the last compile, every page was viewed with `scripts/page_qa.py`, and no page shows white space (Checking the Writing Rules, step 4).

## Core Workflow

1. First, settle the target venue: if it is not settled, your first action is to ask the user with the ask-user tool (Execution Rule 1). Then create the Appendix or Supplementary file if it does not exist yet (Execution Rule 2).
2. Pick 3-5 papers closest to ours as style references and view them (`references/style-references.md`). Their writing, figures, and tables are the main style reference; this skill's examples only fill gaps. Whenever the paper has an Experiments section, also write the closest-work plan and find the latest state of the art before any other Experiments or figure work (`references/experiments.md`, "Experiment Planning").
3. Before editing any section, find the story and record it as a `% Story:` block: problem, insight, method, claims, takeaway, key term (`references/story.md`). Tell the whole paper around it. Every section and paragraph advances it, and every figure and table supports one of its claims; the rest goes to the Appendix or is cut.
4. Rewrite paragraph-by-paragraph with one message per paragraph. Follow the Writing Rules below in every sentence you write or edit, in every section, not only in a final pass.
5. Run reverse outlining after writing each section (`references/paragraph-clarity.md`).
6. Run final-paper adversarial review with `references/paper-review.md`.
7. After every edit, run the checks in "Checking the Writing Rules" below; fix and re-check until they pass. Before you finish, if sub-agents are available, run reviewers in parallel, each given the absolute paths of this file and `scripts/check_tex.py`. One checks that every reference exists and matches the real paper, one checks every Writing Rule, and one checks the venue's template, page limit, anonymity, and Appendix rules.

## Principles

1. One message per paragraph, stated in its first sentence; define terms before reusing them, and link each sentence to the last.
2. Outline before drafting; in each subsection, state the motivation, the design, and the technical advantage.
3. Sell the story: lead with what ours brings. Back it with every result that supports it, even a few cases or one subset, and scope each claim to where it holds (`references/story.md`). Never discuss where ours loses; never invent numbers or drop table rows.

## Writing Rules (Apply to Every Edit)

The style references come first (Core Workflow step 2). The examples in `references/examples/` only fill gaps: reuse their logic, never their wording. These rules win over both.

### Do Not Violate

1. Preserve meaning: never change numbers, equations, citation keys, labels, or the scope of a claim.
2. Never invent claims or numbers; run the experiment, and leave `[TODO: number]` only until it finishes.
3. Do not rewrite clear sentences for variety, and never introduce the patterns in B3.

### A. Typesetting

#### A1. Page Layout and Compliance

1. Never change the template's margins, fonts, or spacing; the main text must end exactly at the page limit.
2. The last line of every paragraph must fill more than 60% of the line width; fix it by rewording, not by spacing tricks.
3. Review version: no author names, acknowledgments, identifying links, or author PDF metadata; cite your own work in the third person.
4. Embed all fonts and avoid Type 3 fonts (check with `pdffonts`; in Matplotlib set `pdf.fonttype` to 42).
5. Leave no `??` or `[?]` in the paper or the supplement.
6. Leave no white space in the main text: no gaps around floats, no half-empty columns, and no page holding only a small float. Fix it as `references/page-check.md` says, never by shrinking spacing (A1.1).

#### A2. Figures and Floats

1. Make a figure or table only to show an advantage of our method or a non-obvious finding, never for decoration. Before drawing, write its conclusion and its form in the figure plan (A2.6); end the caption with the conclusion, and analyze it in the text: what it shows, why, and what follows. Merge or cut any that repeats another's message. Never plot numbers a table already shows, unless the figure reveals what the table cannot (a trend, a trade-off).
2. Use vector PDF for plots and diagrams; text inside a figure should be no smaller than the caption font.
3. Give each method the same name, color, and order in every figure and table, and always highlight ours.
4. Captions: first what it shows ("Qualitative comparison on D-NeRF."), then what each part shows ("(a) ... (b) ..."), then the conclusion in at most 2 short sentences; within 50 words, or 80 for a teaser or pipeline figure. No formatting notes ("best in bold"), no significance details. Titles inside a figure and subfigure captions name what is shown, never the conclusion. Figure captions go below, table captions above.
5. Except for the teaser, place a figure, table, or algorithm right after the paragraph that introduces it, in the same (sub)section: `flafter`, and `\FloatBarrier` (`placeins`) before the next (sub)section. If the barrier leaves white space (A1.6), move the source earlier or resize the float.
6. Before making a figure or table, look at how the style references show the same kind of result, and match their form and style (`references/figure-table-styles.md`, `references/table-types.md`). Add it to the figure plan, and use one style scheme for all, the one closest to the references; if the user has not chosen one, ask with the ask-user tool.
7. The main text has at least 3 figures, 4 when space allows (e.g., teaser, pipeline, qualitative comparison, analysis), each with a key message (A2.1). If there are fewer, plan and create the missing ones now: draw diagrams yourself, and run the experiments behind result figures. Use one form (e.g., line plots) for at most 2 main-text figures; merge related ones into one multi-panel figure, or move one to the Appendix.
8. Tables: pick the type that fits the comparison (SOTA comparison, plug-in, ablation, efficiency, ...). Run every method you can under one protocol, cite every method in its row, and include the latest state of the art. Numbers you could not run go in the same table, marked † with a one-line note; never in a separate table.
9. Draw each figure at its printed width, export it to PDF, and run `scripts/figure_qa.py` on the script that draws it, or on the file. Fix every overlap, cut-off, size, and white-space problem it reports, then look at the preview it writes. Repeat after every change; `check_tex.py` reports any image not checked since its last change.

#### A3. Math

1. Define every symbol at first use and keep notation fixed across the paper.
2. Set word subscripts upright: `x_{\text{gt}}`, not `x_{gt}`.
3. Punctuate display equations as part of the sentence.

#### A4. References and LaTeX Details

1. Use a non-breaking space: `Figure~\ref{...}`, `NeRF~\cite{...}`. Choose `Fig.` or `Figure` once and keep it.
2. A citation is not a noun: write `NeRF~\cite{nerf} shows`, not `\cite{nerf} shows`.
3. Write ``` ``quotes'' ``` instead of `"quotes"`, `--` for ranges, and `e.g.,` / `i.e.,` with a comma.
4. Remove full-width punctuation (`，。：（）`) left by Chinese input methods.
5. Bibliography: consistent venue names, published versions instead of arXiv, protected capitals (`{NeRF}`).
6. Cite every named model, method, baseline, dataset, benchmark, metric, or application at its first mention, right after the name: `ScanNet~\cite{a} and Replica~\cite{b}`, not `ScanNet and Replica~\cite{a,b}`. In Experiments, cite each one again at its first mention there, even if it was cited earlier, and in each table row that names it. Every claim that is not our own result must cite a source, especially in the Introduction. Never invent a reference; mark an unknown source as `\cite{TODO}`.
7. Do not end a long sentence with a long citation list; split it and cite each point where it is made.
8. Aim for at least 35 references. Add only real papers whose title, authors, and venue you have checked; if there are fewer, list the gaps as `[TODO: cite ...]` for the author instead of padding the bibliography.
9. Anywhere at the start of Experiments, before the first result, explain every metric you report in one short sentence: what it measures and which direction is better, citing its source paper (`LPIPS~\cite{lpips}`). Do this even if an earlier section explained it.

### B. Wording

#### B1. Terminology

One concept, one term: never alternate `module / block / component` for the same object. Define each abbreviation once, and spell dataset and method names exactly as their authors do.

#### B2. Sentence Clarity

1. One sentence, one idea. Keep sentences short: aim for about 20 words, and split any sentence over 25 words.
2. Old-to-new: start with what the reader already knows, end with the new information.
3. No ambiguous `this` / `it`: write "This design ...", not "This ...".

#### B3. Sentence Patterns Overused by LLMs

LLMs overuse these patterns: never introduce them, and fix every instance.

1. Trailing participle: "..., highlighting / enabling / paving the way for ..." -> state the concrete consequence, or delete it.
2. Negate-then-correct: "not merely A, but B", "not only A but also B", or "It is A, not B" -> state B, or write "A and B".
3. Summary closer: "Overall, these results demonstrate ..." -> delete it, or turn it into a transition.
4. Progress-then-gap opener: "While X has achieved remarkable progress, ..." -> name what fails and why.
5. Stacked adverbs: "Notably, ... Importantly, ... Furthermore, ..." -> keep only real relations.
6. Unsupported triplets: "efficient, scalable, and robust" -> keep only what the experiments show.
7. Heavy punctuation: an em dash (`---`, `—`), a colon that announces a point ("The idea is simple: ..."), or clauses chained by semicolons -> write a new sentence. Never use an em dash, and use at most one colon or semicolon per paragraph. Hyphens and en dashes (`-`, `--`) are fine.

#### B4. Section-Specific Wording

1. Opening: no clichés such as "With the rapid development of deep learning, ..." or "The community has ..."; start from the task and its concrete difficulty.
2. Contributions: parallel, concrete, and each checkable against an experiment.
3. Results: every result sentence names metric, dataset, baseline, and magnitude. Write where ours wins, never where it loses or fails (Principle 3).
4. Related Work: specific and fair ("does not model X"), never dismissive.
5. Statistical significance: one sentence in the main text, such as the standard deviation over runs or a pointer to the tests in the Appendix. Never in captions; main tables show at most mean ± std.
6. Bold run-in headings (`\paragraph`, an opening `\textbf`): use them sparingly, only where the reader needs to find a part again; never on every paragraph, least of all in Method.

### Checking the Writing Rules

1. After every edit, run `python3 <this skill's directory>/scripts/check_tex.py main.tex` (or `python`). Fix every `ERROR`; fix every `WARN`, or justify it in your reply with a reason the rule itself allows (e.g., "DynaSplat: our method, no citation"). "Not requested", "out of scope", and "no data yet" are not reasons. Never lower the checker's thresholds (`--min-figures`, `--min-refs`, `--max-words`) unless the user asks. Re-run until it reports 0 errors.
2. After drawing or changing a figure, run `scripts/figure_qa.py` (A2.9) before rerunning the checker.
3. The scripts cannot check A2.1-A2.3, A2.5, A2.6, A3.1, B1, B2.2, B4.2, or B4.4: check them by rereading the text you changed.
4. After every compile (Execution Rule 3), look at every page: run `scripts/page_qa.py main.pdf`, open every sheet it writes, fix what you see, and confirm with the codes on the sheets (`references/page-check.md`). Then re-run the checker with `--log main.log --pdf main.pdf`, plus `--supp-pdf supp.pdf` for a separate supplementary file and `--review` for the anonymous version, to check references, overfull boxes, fonts, anonymity, and the page limits.
5. If a check cannot run (no Python, TeX, or PDF tools), report its rules as "not checked" with the reason; never report them as passed.

## Section Guides

In `references/`, load what the task needs; the Writing Rules apply to every edit regardless. Sections: `introduction.md`, `abstract.md`, `related-work.md`, `method.md`, `experiments.md`, `conclusion.md`, `preliminary.md`. Also `story.md` and `style-references.md` (read first), `figure-table-styles.md` and `table-types.md` (read before any figure or table), `venue-rules.md`, `page-check.md`, `paper-review.md`, `paragraph-clarity.md`, and `examples/index.md`.

## Execution Rules

1. First, before any other work, settle the target venue and its template:
   - Determine the venue from the user's request or the LaTeX preamble, and record it, e.g., `% Venue: CVPR 2027`. If it is unknown, do not guess: ask with the ask-user tool (`AskUserQuestion` in Claude Code), offering 2-4 likely venues in the field; without such a tool, ask in plain text and wait.
   - Look up this year's author guidelines, and record the page limit and the Appendix rules with their source (`references/venue-rules.md`).
   - If the project lacks the venue's template, search the web for its latest official author kit, download it into the project, and use it. If that fails, ask the user for the template URL or files.
2. Create the Appendix or Supplementary Material at the start, following the venue's Appendix rules (placement, page limit, format). Check the compiled PDF against them, and fix any violation (`references/venue-rules.md`). Move detailed or redundant content there (implementation details, per-scene and extra qualitative results, proofs), and reference its important parts from the main text.
3. Compile (`pdflatex`, `bibtex`, then `pdflatex` twice), installing TeX Live or MiKTeX if missing, and look at every page after each compile (Checking the Writing Rules, step 4).

## Output Contract

When asked to rewrite or draft sections, return:

1. A section outline (3-7 bullets).
2. The revised paragraphs, each labeled with its role (opening, challenge, method, advantage, evidence).
3. A short self-review (clarity, flow, terminology, unsupported claims), and a claim-evidence map of the story's claims: `Claim: ... | Evidence: ... | Status: supported/needs evidence`.

After any edit, including a final polish, also return:

4. The checker's "Required in Every Paper" list, copied as printed, its final summary line, and a one-line justification for each remaining `WARN`.
5. A Writing Rules report, one line per group (A1-A4, B1-B4), with each rule's status (pass, fixed, or not checked with the reason), e.g., `A4: 1 fixed, 2 pass, 8 not checked (6 .bib entries)`. Never mark a rule pass without checking it.
6. For a final polish: a short change log with one example per type of change. Always: the experiments still running or blocked, and what you need from the user.
7. A setup line: the story in one sentence, the venue and template, the style references, and the path of the Appendix or Supplementary file. When Experiments, figures, or tables were touched, add the closest-work plan and the latest-SOTA line with the status of each item.
8. For each figure or table you created or changed, its figure-plan line (e.g., `fig:noise: ours degrades least as noise grows -> lines over noise level`) and, for a figure, its `figure_qa.py` result. After a compile, one line per page on what its sheet shows.
