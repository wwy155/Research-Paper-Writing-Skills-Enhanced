---
name: research-paper-writing
description: Write or improve academic paper writing quality for ML/CV/NLP-style papers with clear section structure, paragraph flow, and reviewer-facing presentation. Use when drafting or revising Abstract, Introduction, Related Work, Preliminaries, Method, Experiments, or Conclusion; polishing figures/tables, wording, or LaTeX typesetting; checking claim-support alignment; or performing self-review before submission.
---
# Research Paper Writing

## Required in Every Paper

These hold after every task that edits the paper, even a narrow one, unless the user explicitly says to skip one. The checker reports each gap as an ERROR and ends with a pass/fail list of these items; copy that list into your reply. Missing data never excuses a gap: create the figure or table, and run the experiment behind it (item 10).

1. The venue is settled, its rules are looked up and recorded, and its template is in use. The main text ends exactly at its page limit, and the references and the whole paper stay within theirs (Execution Rule 1).
2. The Appendix or Supplementary file exists from the start, follows the venue's Appendix rules (placement, page limit, format), holds the detailed content, and the main text references it (Execution Rule 2).
3. The story is written down, and every claim has evidence (Core Workflow step 3).
4. At least 3 style references were viewed with `scripts/page_qa.py --reference`, and the writing follows their vibe (Core Workflow step 2).
5. The closest-work plan gives every figure and table of each closest paper a line, each reproduced where it informs our comparison or reviewers expect it, or skipped with a reason (Core Workflow step 2).
6. The main comparison includes the latest state of the art, and the text discusses it (`references/experiments.md`).
7. The main text has at least 3 figures, and every figure and table has its message and form in the figure plan (A2.1, A2.7).
8. The Method section has an architecture figure (A2.10).
9. Every included image passed `scripts/figure_qa.py` after its last change (A2.9).
10. Every needed result is run and filled in from its result file, or logged as running, or as blocked with the user asked (`% Experiment log:` in `references/experiments.md`).
11. Experiments explains and cites every metric before the first result (A4.9).
12. The paper was compiled with pdflatex after the last edit, every page was viewed with `scripts/page_qa.py`, and no page shows white space (Execution Rule 3, Checking the Writing Rules step 4).
13. The loop ran to the end: the last round in `% Review log:` found no errors and nothing new in review (Core Workflow step 7).

## Core Workflow

Steps 1-3 set the paper up. Steps 4-7 are a loop: repeat them until a round finds nothing to fix.

1. Settle the target venue first, asking the user if needed (Execution Rule 1), then create the Appendix or Supplementary file (Execution Rule 2).
2. Pick 3-5 style references for the writing, recent, closest, and similar in contribution to ours, and view them (`references/style-references.md`). Whenever the paper has an Experiments section, also write the closest-work plan and find the latest state of the art before any other Experiments or figure work (`references/experiments.md`).
3. Before editing any section, find the story and record it as a `% Story:` block (`references/story.md`). Tell the whole paper around it: every section and paragraph advances it, and the rest goes to the Appendix or is cut.
4. Edit. Write paragraph by paragraph, and follow the Writing Rules in every sentence you write or edit.
5. Check everything that applies (Checking the Writing Rules): `check_tex.py`, `figure_qa.py` for changed figures, a pdflatex compile with `page_qa.py`, and a reverse outline of each changed section (`references/paragraph-clarity.md`).
6. Review the paper as a skeptical reviewer, with sub-agent reviewers in parallel when available (`references/paper-review.md`).
7. Fix every ERROR, WARN, and review finding, log the round in `% Review log:`, and go back to step 5. Stop only when a round's checks find no errors and its review finds nothing new. If a missing tool, a blocked experiment, or a question for the user stops the loop, ask the user.

## Principles

1. One message per paragraph, stated in its first sentence; define terms before reusing them, and link each sentence to the last.
2. Outline before drafting; in each subsection, state the motivation, the design, and the technical advantage.
3. Sell the story: lead with what ours brings. Back it with every result that supports it, even a few cases or one subset, and scope each claim to where it holds (`references/story.md`). Never discuss where ours loses; never invent numbers or drop table rows.

## Writing Rules (Apply to Every Edit)

The style references come first (Core Workflow step 2): imitate their vibe, never their sentences or content. The examples in `references/examples/` only fill gaps. These rules win over both.

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

1. Make a figure or table only when it shows something informative, such as a result, an advantage of ours, how the method works, or a non-obvious finding. Never make one for decoration. End the caption with its conclusion, and analyze it in the text: what it shows, why, and what follows. Merge or cut any that repeats another's message, and never plot numbers a table already shows unless the figure reveals a trend or a trade-off.
2. Use vector PDF for plots and drawn diagrams, and PNG at 300 dpi or more at print size for generated figures and photos; text inside a figure should be no smaller than the caption font.
3. Give each method the same name and order in every figure and table, and make ours easy to find.
4. Captions: first what it shows ("Qualitative comparison on D-NeRF."), then what each part shows ("(a) ... (b) ..."), then the conclusion in at most 2 sentences; within 50 words, or 80 for a teaser or architecture figure. No formatting notes ("best in bold"), no significance details, and no conclusion in figure titles. Figure captions go below, table captions above.
5. Except for the teaser, place a figure, table, or algorithm right after the paragraph that introduces it, in the same (sub)section: `flafter`, and `\FloatBarrier` (`placeins`) before the next (sub)section. If the barrier leaves white space (A1.6), move the source earlier or resize the float.
6. Above all, every figure must look good and convince. Write what it shows and its form in the figure plan before making it, and redraw it until it does (`references/figures.md`, `references/table-types.md`). Never copy another paper's figures or tables.
7. The main text has at least 3 figures, 4 when space allows (e.g., teaser, architecture, qualitative comparison, analysis), each with a key message (A2.1); create any missing one now, running the experiments behind result figures. Use one form (e.g., line plots) for at most 2 main-text figures; merge related ones into one multi-panel figure, or move one to the Appendix.
8. Tables: pick the type that fits the comparison (`references/table-types.md`), run every method you can under one protocol, cite each method in its row, and include the latest state of the art. Numbers you could not run go in the same table, marked † with a one-line note.
9. Draw each figure at its printed width and run `scripts/figure_qa.py` on the script that draws it, or on the file. Fix every problem it reports, look at the preview it writes, and repeat after every change.
10. The Method section has an architecture figure that shows the inputs, each module under its name in the text, the data flow, and the outputs. Generate it with `generate_image` and check every label at full size; if the tool is missing or fails, ask the user (`references/method.md`).

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
6. Cite every named model, method, baseline, dataset, benchmark, metric, or application at its first mention, right after the name: `ScanNet~\cite{a} and Replica~\cite{b}`, not `ScanNet and Replica~\cite{a,b}`. In Experiments, cite each one again at its first mention there and in each table row that names it. Every claim that is not our own result must cite a source, especially in the Introduction. Never invent a reference; mark an unknown source as `\cite{TODO}`.
7. Do not end a long sentence with a long citation list; split it and cite each point where it is made.
8. Aim for at least 35 references. Add only real papers whose title, authors, and venue you have checked; if there are fewer, list the gaps as `[TODO: cite ...]` for the author instead of padding the bibliography.
9. At the start of Experiments, before the first result, explain every reported metric in one sentence (what it measures and which direction is better) and cite its source paper (`LPIPS~\cite{lpips}`), even if an earlier section explained it.

### B. Wording

#### B1. Terminology

One concept, one term: never alternate `module / block / component` for the same object. Define each abbreviation once, and spell dataset and method names exactly as their authors do.

#### B2. Sentence Clarity

1. Write complete, formal sentences of about 15-30 words, each built around one main idea. Avoid ultra-short sentences (under 8 words): join related statements with a subordinate clause or a precise connective (because, whereas, which). Split any sentence over 35 words.
2. Old-to-new: start with what the reader already knows, end with the new information.
3. No ambiguous `this` / `it`: write "This design ...", not "This ...".
4. Keep a formal academic register: no contractions, colloquialisms ("a lot of", "huge", "get"), exclamation marks, rhetorical questions, or casual openers ("So", "And", "But", "Also"); prefer precise verbs ("obtain", "preserve", "reduce").

#### B3. Sentence Patterns Overused by LLMs

LLMs overuse these patterns: never introduce them, and fix every instance.

1. Trailing participle: "..., highlighting / enabling / paving the way for ..." -> state the concrete consequence, or delete it.
2. Negate-then-correct: "not merely A, but B", "not only A but also B", or "It is A, not B" -> state B, or write "A and B".
3. Summary closer: "Overall, these results demonstrate ..." -> delete it, or turn it into a transition.
4. Progress-then-gap opener: "While X has achieved remarkable progress, ..." -> name what fails and why.
5. Stacked adverbs: "Notably, ... Importantly, ... Furthermore, ..." -> keep only real relations.
6. Unsupported triplets: "efficient, scalable, and robust" -> keep only what the experiments show.
7. Heavy punctuation: an em dash (`---`, `—`), a colon that announces a point ("The idea is simple: ..."), or clauses chained by semicolons -> rephrase it as one complete sentence, or as two. Never use an em dash, and use at most one colon or semicolon per paragraph. Hyphens and en dashes (`-`, `--`) are fine.

#### B4. Section-Specific Wording

1. Opening: no clichés such as "With the rapid development of deep learning, ..." or "The community has ..."; start from the task and its concrete difficulty.
2. Contributions: parallel, concrete, and each checkable against an experiment.
3. Results: every result sentence names metric, dataset, baseline, and magnitude. Write where ours wins, never where it loses or fails (Principle 3).
4. Related Work: specific and fair ("does not model X"), never dismissive.
5. Statistical significance: one sentence in the main text, such as the standard deviation over runs or a pointer to the tests in the Appendix. Never in captions; main tables show at most mean ± std.
6. Bold run-in headings (`\paragraph`, an opening `\textbf`): use them sparingly, only where the reader needs to find a part again; never on every paragraph, least of all in Method.

### Checking the Writing Rules

1. After every edit, run `python3 <this skill's directory>/scripts/check_tex.py main.tex`. Fix every `ERROR`; fix every `WARN`, or justify it in your reply with a reason the rule itself allows (e.g., "DynaSplat: our method, no citation"). "Not requested", "out of scope", and "no data yet" are not reasons. Never lower the checker's thresholds (`--min-figures`, `--min-refs`, `--max-words`) unless the user asks.
2. Run `scripts/figure_qa.py` after every figure change (A2.9).
3. The scripts cannot check A2.1-A2.3, A2.5, A2.6, A3.1, B1, B2.2, B4.2, or B4.4: check them by rereading the text you changed.
4. After every compile (Execution Rule 3), look at every page: run `scripts/page_qa.py main.pdf`, open every image it writes at full size, fix what you see, and confirm with their codes (`references/page-check.md`). Then re-run the checker, with `--review` for the anonymous version; it also checks `main.pdf` and `main.log`.
5. If a tool that a check needs is missing, install it or ask the user to; never skip compiling (Execution Rule 3) or report an unchecked rule as passed.

## Section Guides

Load from `references/` what the task needs: one guide per section (`introduction.md`, `abstract.md`, `related-work.md`, `method.md`, `experiments.md`, `conclusion.md`, `preliminary.md`), plus `story.md` and `style-references.md` (read first), `figures.md` and `table-types.md` (read before any figure or table), `venue-rules.md`, `page-check.md`, `paper-review.md`, `paragraph-clarity.md`, and `examples/index.md`.

## Execution Rules

1. First, before any other work, settle the target venue and its template:
   - Determine the venue from the user's request or the LaTeX preamble, and record it, e.g., `% Venue: CVPR 2027`. If it is unknown, never guess: ask with the ask-user tool (`AskUserQuestion` in Claude Code), offering 2-4 likely venues; without such a tool, ask in plain text and wait.
   - Look up this year's author guidelines, and record with their source the Appendix rules and the page limits of the main text (long paper), the references, and the whole paper (`references/venue-rules.md`). If not found, use 8 pages of main text, references excluded, and tell the user.
   - If the project lacks the venue's template, search for its latest official author kit and download it; if that fails, ask the user for its URL or files.
2. Create the Appendix or Supplementary Material at the start, following the venue's Appendix rules (placement, page limit, format; `references/venue-rules.md`). Move details there (implementation, per-scene and extra qualitative results, proofs), and reference them from the main text.
3. Compile only with pdflatex, as Overleaf and arXiv do (`pdflatex`, `bibtex`, `pdflatex` twice, or `latexmk -pdf`), never with XeLaTeX, LuaLaTeX, Tectonic, or another tool, and never skip it. If pdflatex is missing, install TeX Live, or ask the user with the ask-user tool until `pdflatex --version` works (`references/page-check.md`). Look at every page after each compile (Checking the Writing Rules, step 4).

## Output Contract

When asked to rewrite or draft sections, return:

1. A section outline (3-7 bullets).
2. The revised paragraphs, each labeled with its role (opening, challenge, method, advantage, evidence).
3. A claim-evidence map of the story's claims: `Claim: ... | Evidence: ... | Status: supported/needs evidence`.

After any edit, including a final polish, also return:

4. The checker's "Required in Every Paper" list, copied as printed, its final summary line, the rounds of the review log, and a one-line justification for each remaining `WARN`.
5. A Writing Rules report, one line per group (A1-A4, B1-B4), with each rule's status (pass, fixed, or not checked with the reason). Never mark a rule pass without checking it.
6. For a final polish: a short change log with one example per type of change. Always: the experiments still running or blocked, and what you need from the user.
7. A setup line: the story in one sentence, the venue and its page limits, the style references, and the Appendix path; after Experiments, figure, or table work, also the closest-work plan and the latest-SOTA line with each item's status.
8. For each figure or table you created or changed, its figure-plan line and its `figure_qa.py` result; after a compile, one line per page on what its images show.
