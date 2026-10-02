---
name: research-paper-writing
description: Write or improve academic paper writing quality for ML/CV/NLP-style papers with clear section structure, paragraph flow, and reviewer-facing presentation. Use when drafting or revising Abstract, Introduction, Related Work, Preliminaries, Method, Experiments, or Conclusion; polishing figures/tables, wording, or LaTeX typesetting; checking claim-support alignment; or performing self-review before submission.
---
# Research Paper Writing

## Overview

Use this skill to rewrite a research paper into a reviewer-friendly, high-clarity draft.
Prioritize first-impression quality (figures/tables/layout), logical flow, and evidence-backed claims.

## Required in Every Paper

These hold after every task that edits the paper, even a narrow one, unless the user explicitly says to skip one. The checker reports each gap as an ERROR and ends with a pass/fail list of these items; copy that list into your reply. Missing data never excuses a gap: add the figure or table with `[TODO]` placeholders and list the experiment for the author.

1. The venue is settled, recorded, and its template is in use (Execution Rule 8).
2. The Appendix or Supplementary file exists from the start, holds the detailed content, and the main text references it (Execution Rule 9).
3. The closest-work plan gives every figure and table of each closest paper a line, and each one is reproduced in our paper or skipped with a reason (Core Workflow step 2).
4. The main text has at least 3 figures, each with its message and form in the figure plan (A2.1, A2.7).
5. Experiments states every metric before the first result (A4.9).

## Core Workflow

1. First, before any other work, settle the target venue (Execution Rule 8). If it is not settled yet, your first action is to ask the user which venue to submit to, with the ask-user tool (`AskUserQuestion` in Claude Code). Then create the Appendix or Supplementary file if it does not exist yet (Execution Rule 9).
2. Whenever the paper has an Experiments section, write the closest-work plan before any other Experiments or figure work (`references/experiments.md`, "Experiment Planning"). Every figure and table of each closest paper gets a line, and each one is reproduced in our paper or skipped for a stated reason.
3. Clarify the paper story before sentence-level edits.
4. Use section-specific guidance in `references/`.
5. Rewrite paragraph-by-paragraph with one message per paragraph. Follow the Writing Rules below in every sentence you write or edit, in every section, not only in a final pass.
6. Run reverse outlining after writing each section (`references/paragraph-clarity.md`).
7. Check every major claim in Abstract/Introduction against experimental evidence.
8. Run final-paper adversarial review with `references/paper-review.md`.
9. After every edit, run the checks in "Checking the Writing Rules" below; fix and re-check until they pass. Before you finish, if sub-agents are available, also run one reviewer per aspect in parallel, and give each reviewer the absolute paths of this file and of `scripts/check_tex.py`:
   - references: every entry exists, and its title, authors, and venue match the real paper (no hallucinated citations);
   - wording and format: every Writing Rule, reported rule by rule;
   - template compliance when the venue is known: page limit, anonymity, Appendix/Supplementary rules.

## Global Principles

1. Keep one paragraph for one message only.
2. State the paragraph message in the first sentence.
3. Make nouns self-contained; define new terms before reusing them.
4. Maintain sentence-to-sentence flow (cause, contrast, consequence, or refinement).
5. Iterate with adversarial self-review: read as a skeptical reviewer.
6. Treat visual quality as core content: a clean teaser and pipeline figure, readable minimal-ink tables, and consistent formatting.
7. Sell the paper, do not just introduce it: state explicitly what our method brings over prior work, and back every selling point with evidence.

## Writing Rules (Apply to Every Edit)

Apply these rules whenever you write or edit text, in any section. Table layout rules are in `references/experiments.md`. The examples in `references/examples/` are quoted from published papers: reuse their logic, never their wording; where they conflict with these rules, these rules win.

### Do Not Violate

1. Preserve meaning: never change numbers, equations, citation keys, labels, or the scope of a claim.
2. Never invent claims or numbers; leave `[TODO: number]` instead.
3. Do not rewrite clear sentences for variety, and never introduce the patterns in B3.

### A. Typesetting

#### A1. Page Layout and Compliance

1. Never change the template's margins, fonts, or spacing; the main text must end exactly at the page limit.
2. The last line of every paragraph must fill more than 60% of the line width; fix it by rewording, not by spacing tricks.
3. Review version: no author names, acknowledgments, identifying links, or author PDF metadata; cite your own work in the third person.
4. Embed all fonts and avoid Type 3 fonts (check with `pdffonts`; in Matplotlib set `pdf.fonttype` to 42).
5. Leave no `??` or `[?]` in the paper or the supplement.
6. Leave no white space in the main text: no gaps around floats, no half-empty columns, and no page holding only a small float. Fix it by moving, resizing, or combining floats, by moving content to or from the Appendix, or by rewording; never by shrinking spacing (A1.1).

#### A2. Figures and Floats

1. Make a figure or table only to show an advantage of our method or a non-obvious finding, never for decoration. Before drawing, write its conclusion and the form that shows it at a glance in the figure plan (A2.6). State the conclusion in the caption's bold takeaway and analyze it in the text: what it shows, why, and what follows. Each supports a different conclusion; merge or cut any that repeats another's message or has no conclusion.
2. Use vector PDF for plots and diagrams; text inside a figure should be no smaller than the caption font.
3. Give each method the same name, color, and order in every figure and table, and always highlight ours.
4. Start each caption with a bold takeaway: one sentence of at most 15 words. Then add only what is needed to read the figure without the main text (setting, metric, notation), with no analysis. Keep the caption within 50 words, or 80 for a teaser or pipeline figure. Figure captions go below, table captions above.
5. Except for the teaser, a figure, table, or algorithm must appear after the text that mainly introduces it and inside the same (sub)section. Put its source right after that paragraph; `flafter` keeps it from appearing earlier, and `\FloatBarrier` (`placeins`) before the next (sub)section keeps it from drifting out. If the barrier leaves white space (A1.6), move the source earlier, still after its first mention, or resize the float. Check the compiled PDF.
6. Read `references/figure-table-styles.md` before creating or restyling a figure or table. Pick the form for its message there, add it to the figure plan, and use one style scheme for all of them. If the user has not chosen a scheme, ask with the ask-user tool.
7. The main text has at least 3 figures, 4 when space allows (e.g., teaser, pipeline, qualitative comparison, analysis). Each must carry a key message (A2.1): if there are fewer, plan the missing ones in the figure plan and create them now. Draw diagrams yourself, and use a `[TODO]` placeholder where results are missing. Vary their forms: use one form (e.g., line plots) for at most 2 main-text figures. Merge related ones into one multi-panel figure, or move one to the Appendix.

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
9. In Experiments, before the first result, state every metric you report: what it measures, which direction is better, and its source (`LPIPS~\cite{lpips}`). Do this even if an earlier section already explained it.

### B. Wording

#### B1. Terminology

One concept, one term: never alternate `module / block / component` for the same object. Define each abbreviation once, and spell dataset and method names exactly as their authors do.

#### B2. Sentence Clarity

1. One sentence, one idea. Keep sentences short: aim for about 20 words, and split any sentence over 25 words.
2. Old-to-new: start with what the reader already knows, end with the new information.
3. No ambiguous `this` / `it`: write "This design ...", not "This ...".

#### B3. Sentence Patterns Overused by LLMs

Instruction-tuned LLMs use present participial clauses at 2-5 times the human rate and favor summative sentences (Reinhart et al., arXiv:2410.16107). Never introduce these patterns, and fix every instance in the author's text.

1. Trailing participle: "..., highlighting / enabling / paving the way for ..." -> state the concrete consequence, or delete it.
2. Negate-then-correct: "not merely A, but B" or "not only A but also B" -> state B, or write "A and B".
3. Summary closer: "Overall, these results demonstrate ..." -> delete it, or turn it into a transition.
4. Progress-then-gap opener: "While X has achieved remarkable progress, ..." -> name what fails and why.
5. Stacked adverbs: "Notably, ... Importantly, ... Furthermore, ..." -> keep only real relations.
6. Unsupported triplets: "efficient, scalable, and robust" -> keep only what the experiments show.
7. Em dashes: never use an em dash (`---`, `—`) -> use a comma, a colon, parentheses, or a new sentence. Hyphens and en dashes (`-`, `--`) are fine.

#### B4. Section-Specific Wording

1. Opening: no clichés such as "With the rapid development of deep learning, ..." or "The community has ..."; start from the task and its concrete difficulty.
2. Contributions: parallel, concrete, and each checkable against an experiment.
3. Results: every result sentence names metric, dataset, baseline, and magnitude.
4. Related Work: specific and fair ("does not model X"), never dismissive.

### Checking the Writing Rules

1. After every edit, run `python3 <this skill's directory>/scripts/check_tex.py main.tex` (use `python` if `python3` is missing). It follows `\input` / `\include` and finds the `.bib`. Fix every `ERROR`; fix every `WARN`, or justify it in your reply with a reason the rule itself allows (e.g., "DynaSplat: our method, no citation"). "Not requested", "out of scope", and "no data yet" are not reasons. Never lower the checker's thresholds (`--min-figures`, `--min-refs`, `--max-words`) unless the user asks. Re-run until it reports 0 errors.
2. The script cannot check A1.1, A1.2, A1.6, A2.1-A2.3, A2.5, A2.6, A3.1, B1, B2.2, B4.2, or B4.4: check them by rereading the text you changed.
3. After compiling (Execution Rule 10), re-run it with `--log main.log --pdf main.pdf`, adding `--review` for the anonymous version, to check undefined references, overfull boxes, fonts, and anonymity. Then render the pages (`pdftoppm -r 60 -png main.pdf page`) and look at them for the page limit (A1.1), paragraph last lines (A1.2), white space (A1.6), and float positions (A2.5).
4. If a check cannot run (no Python, TeX, or PDF tools), report its rules as "not checked" with the reason; never report them as passed.

## Section Guides

Load only the needed section file:

- Introduction: `references/introduction.md`
- Abstract: `references/abstract.md`
- Related Work: `references/related-work.md`
- Preliminary (optional; when the paper relies on a technique uncommon in its field, or the task needs a formal definition): `references/preliminary.md`
- Method: `references/method.md`
- Experiments: `references/experiments.md`
- Figures and tables (form and style; read before making any, A2.6): `references/figure-table-styles.md`
- Conclusion: `references/conclusion.md`
- Paper review (Paper Review): `references/paper-review.md`
- Paragraph clarity check and reverse outlining (when the user asks whether a paragraph flows or is clear, and after each section): `references/paragraph-clarity.md`
- Example bank index: `references/examples/index.md`

## Execution Rules

1. Build a mini-outline before drafting prose.
2. For each subsection, explicitly include motivation, design, and technical advantage when applicable.
3. Avoid writing style that looks like incremental patching of a naive baseline.
4. Keep terminology stable across the full paper.
5. If a claim cannot be supported by results, weaken or remove the claim.
6. Before finalizing, answer the self-review questions of `references/paper-review.md` in five dimensions (contribution, writing clarity, experimental strength, evaluation completeness, method design soundness), then revise the paper for every unresolved item.
7. Load only the section guide for the current edit target, not all of them at once. The Writing Rules in this file apply to every edit regardless.
8. First, before any other work, settle the target venue and its template:
   - Determine the venue from the user's request or the LaTeX preamble (e.g., `\usepackage[review]{cvpr}`, `\usepackage{neurips_2025}`). Unless the template package names it, record it at the top of the main `.tex` file, e.g., `% Venue: CVPR 2027`. If it is still unknown, do not guess: your first action is to call the ask-user tool (`AskUserQuestion` in Claude Code) to ask which venue to submit to, offering 2-4 likely venues in the paper's field as options (e.g., CVPR / ICCV / ECCV for vision, NeurIPS / ICML / ICLR for ML, ACL / EMNLP / NAACL for NLP); without such a tool, ask in plain text and wait for the answer.
   - If the project does not already contain the venue's template files, search the web for its latest official template (style files or author kit, from the venue's website or call for papers), download it into the project, and use it for the paper. If none is found or the download fails, ask the user to send the template URL or upload the template files directly.
   - Once the template is in place, the main text must end exactly at its page limit: neither short of it nor over it.
9. Create the Appendix or Supplementary Material at the start, following the template: check which name it uses and whether it goes in the same file or a separate one. Move overly detailed or redundant content there (implementation details, per-scene results, more qualitative results, proofs, reproduced closest-work analyses that do not fit), and reference its important parts from the main text.
10. Compile with `pdflatex` (then `bibtex` and `pdflatex` twice), installing TeX Live or MiKTeX if it is missing. After each major revision, check the PDF and log ("Checking the Writing Rules", step 3).

## Output Contract

When asked to rewrite or draft sections, return:

1. A section outline (3-7 bullets).
2. The revised paragraphs, each labeled with its role (opening, challenge, method, advantage, evidence, limitation).
3. A short self-review: clarity, flow, terminology, unsupported claims, missing evidence.
4. A claim-evidence map: `Claim: ... | Evidence: ... | Status: supported/needs evidence`.

After any edit, including a final polish, also return:

5. The checker's "Required in Every Paper" list, copied as printed, its final summary line, and a one-line justification for each remaining `WARN`.
6. A Writing Rules report with one line per group (A1-A4, B1-B4) giving the status of each rule in it, for example `A4: 1 fixed, 2 pass, 3 fixed, 4 pass, 5 pass, 6 fixed, 7 pass, 8 not checked (6 entries in the .bib)`. A status is pass, fixed, or not checked (with the reason); never mark a rule pass without checking it.
7. For a final polish: a short change log with one example per type of change, and the `[TODO]` items that need the author.
8. A setup line: the venue and template, the path of the Appendix or Supplementary file, and, when Experiments, figures, or tables were touched, the closest-work plan with the status of each item.
9. For each figure or table you created or changed, its line in the figure-plan format, e.g., `fig:noise: ours degrades least as noise grows -> lines over noise level`.
