---
name: research-paper-writing
description: Improve academic paper writing quality for ML/CV/NLP-style papers with clear section structure, paragraph flow, and reviewer-facing presentation. Use when drafting or revising Abstract, Introduction, Related Work, Preliminaries, Method, Experiments, or Conclusion; polishing figures/tables, wording, or LaTeX typesetting; checking claim-support alignment; or performing self-review before submission.
---
# Research Paper Writing

## Overview

Use this skill to rewrite a research paper into a reviewer-friendly, high-clarity draft.
Prioritize first-impression quality (figures/tables/layout), logical flow, and evidence-backed claims.

## Core Workflow

1. Clarify the paper story before sentence-level edits.
2. Use section-specific guidance in `references/`.
3. Rewrite paragraph-by-paragraph with one message per paragraph. Follow the Writing Rules below in every sentence you write or edit, in every section, not only in a final pass.
4. Run reverse outlining after writing each section.
5. Check every major claim in Abstract/Introduction against experimental evidence.
6. Run final-paper adversarial review with `references/paper-review.md`.
7. After every edit, run the checks in "Checking the Writing Rules" below; fix and re-check until they pass. For a whole paper, if sub-agents are available, also run one reviewer per aspect in parallel, and give each reviewer the absolute paths of this file and of `scripts/check_tex.py`:
   - references: every entry exists, and its title, authors, and venue match the real paper (no hallucinated citations);
   - wording and format: every Writing Rule, reported rule by rule;
   - template compliance when the venue is known: page limit, anonymity, Appendix/Supplementary rules.

## Global Principles

1. Keep one paragraph for one message only.
2. State the paragraph message in the first sentence.
3. Make nouns self-contained; define new terms before reusing them.
4. Maintain sentence-to-sentence flow (cause, contrast, consequence, or refinement).
5. Iterate with adversarial self-review: read as a skeptical reviewer.
6. Treat visual quality as core content, not decoration.
7. Use a clean teaser and pipeline figure.
8. Use readable, minimal-ink tables.
9. Keep formatting consistent and tidy.
10. Sell the paper, do not just introduce it: state explicitly what our method brings over prior work, and back every selling point with evidence.

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

#### A2. Figures and Floats

1. Each figure and table must support a different conclusion and show different content; merge or cut any that repeats another's message.
2. Use vector PDF for plots and diagrams; text inside a figure should be no smaller than the caption font.
3. Give each method the same name, color, and order in every figure and table, and always highlight ours.
4. Start each caption with a bold one-line takeaway, then add what is needed to read the figure without the main text. Figure captions go below, table captions above.
5. Except for the teaser, a figure, table, or algorithm must appear after the text that mainly introduces it and inside the same (sub)section. Put its source right after that paragraph; `flafter` keeps it from appearing earlier, and `\FloatBarrier` (`placeins`) before the next (sub)section keeps it from drifting out. Check the compiled PDF.

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
6. Cite every named model, method, dataset, benchmark, metric, or application at its first mention, right after the name: `ScanNet~\cite{a} and Replica~\cite{b}`, not `ScanNet and Replica~\cite{a,b}`. Every claim that is not our own result must cite a source, especially in the Introduction. Never invent a reference; mark an unknown source as `\cite{TODO}`.
7. Do not end a long sentence with a long citation list; split it and cite each point where it is made.
8. Aim for at least 35 references. Add only real papers whose title, authors, and venue you have checked; if there are fewer, list the gaps as `[TODO: cite ...]` for the author instead of padding the bibliography.

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

1. Opening: no clichés such as "With the rapid development of deep learning, ..."; start from the task and its concrete difficulty.
2. Contributions: parallel, concrete, and each checkable against an experiment.
3. Results: every result sentence names metric, dataset, baseline, and magnitude.
4. Related Work: specific and fair ("does not model X"), never dismissive.

### Checking the Writing Rules

1. After every edit, run `python3 <this skill's directory>/scripts/check_tex.py main.tex` (use `python` if `python3` is missing). It follows `\input` / `\include` and finds the `.bib`. Fix every `ERROR`; fix every `WARN`, or justify it in your reply (e.g., "DynaSplat: our method, no citation"). Re-run until it reports 0 errors.
2. The script cannot check A1.1, A1.2, A2.1-A2.3, A2.5, A3.1, B1, B2.2, B4.2, or B4.4: check them by rereading the text you changed.
3. After compiling (Execution Rule 10), re-run it with `--log main.log --pdf main.pdf`, adding `--review` for the anonymous version, to check undefined references, overfull boxes, fonts, and anonymity. Then render the pages (`pdftoppm -r 60 -png main.pdf page`) and look at them for the page limit (A1.1), paragraph last lines (A1.2), and float positions (A2.5).
4. If a check cannot run (no Python, TeX, or PDF tools), report its rules as "not checked" with the reason; never report them as passed.

## Paragraph Clarity Check (Important)

Use this quick test whenever the user asks whether a paragraph "flows" or is clear.

1. Read as an external reader:
   - Does this paragraph have one explicit message?
   - Does the first sentence state what this paragraph will do?
   - Are all key nouns/terms readable without hidden context?
   - Does each sentence connect to the previous one with a clear relation (cause, contrast, consequence, refinement, example)?
2. Run reverse outlining for the current section:
   - Write down thesis/main claim.
   - Write down each paragraph topic sentence.
   - Write down the evidence/explanation points under each paragraph.
   - Check mapping: topic sentence -> thesis, and evidence -> topic sentence.
   - Revise or remove any paragraph that cannot be mapped cleanly.
3. If flow is still weak, add temporary section headers during revision and make each sentence's relation to the previous one explicit (cause, contrast, consequence). Use a transition word only when it names that relation, and never stack additive adverbs (B3.5). Remove unnecessary headers before finalizing.

Source reference for this check:

- `references/does-my-writing-flow-source.md`

## Section Guides

Load only the needed section file:

- Introduction: `references/introduction.md`
- Abstract: `references/abstract.md`
- Related Work: `references/related-work.md`
- Preliminary (optional; when the paper relies on a technique uncommon in its field, or the task needs a formal definition): `references/preliminary.md`
- Method: `references/method.md`
- Experiments: `references/experiments.md`
- Conclusion: `references/conclusion.md`
- Paper review (Paper Review): `references/paper-review.md`
- Paragraph clarity source: `references/does-my-writing-flow-source.md`
- Example bank index: `references/examples/index.md`

## Paper Review Core Points

Use `references/paper-review.md` for the full checklist and workflow.

1. Add an end-of-draft self-review question list in five dimensions:
   - contribution,
   - writing clarity,
   - experimental strength,
   - evaluation completeness,
   - method design soundness.
2. Treat claim-evidence alignment as a hard constraint, especially for Abstract and Introduction.
3. Perform adversarial writing: review as a skeptical reviewer and resolve every high-risk question.
4. Revise until major rejection risks are explicitly addressed.

## Execution Rules

1. Build a mini-outline before drafting prose.
2. For each subsection, explicitly include motivation, design, and technical advantage when applicable.
3. Avoid writing style that looks like incremental patching of a naive baseline.
4. Keep terminology stable across the full paper.
5. If a claim cannot be supported by results, weaken or remove the claim.
6. Before finalizing, append and answer a five-dimension self-review question list, then revise the paper based on unresolved items.
7. Do not load all section references (Introduction/Abstract/Related Work/Preliminary/Method/Experiments/Conclusion) at once; load only the specific section guide needed for the current edit target. The Writing Rules in this file apply to every edit regardless.
8. At the start, settle the target venue and its template:
   - Determine the venue from the user's request or the LaTeX preamble (e.g., `\usepackage[review]{cvpr}`, `\usepackage{neurips_2025}`). If it is still unknown, do not guess: call the ask-user tool (`AskUserQuestion` in Claude Code) to ask which venue to use, offering 2-4 likely venues in the paper's field as options (e.g., CVPR / ICCV / ECCV for vision, NeurIPS / ICML / ICLR for ML, ACL / EMNLP / NAACL for NLP); without such a tool, ask in plain text and wait for the answer.
   - If the project does not already contain the venue's template files, search the web for its latest official template (style files or author kit, from the venue's website or call for papers), download it into the project, and use it for the paper. If none is found or the download fails, ask the user to send the template URL or upload the template files directly.
   - Once the template is in place, the main text must end exactly at its page limit: neither short of it nor over it.
9. Create the Appendix or Supplementary Material at the start, following the template: check which name it uses and whether it goes in the same file or a separate one. Move overly detailed or redundant content there, and reference its important parts from the main text.
10. Compile with `pdflatex` (then `bibtex` and `pdflatex` twice), installing TeX Live or MiKTeX if it is missing. After each major revision, check the PDF and log as in "Checking the Writing Rules" (step 3): page limit, float positions, paragraph last lines, `??` / `[?]`, and overfull boxes.

## Output Contract

When asked to rewrite or draft sections, return:

1. A compact section outline (3-7 bullets).
2. Revised paragraphs with explicit paragraph roles (opening/challenge/method/advantage/evidence/limitation).
3. A short self-review checklist covering clarity, flow, terminology consistency, unsupported claims, and missing evidence.
4. A claim-evidence map for each major claim in the revised text using `Claim: ... | Evidence: ... | Status: supported/needs evidence`.

After any edit, including a final polish, also return:

5. The checker's final summary line, and a one-line justification for each remaining `WARN`.
6. A Writing Rules report with one line per group (A1-A4, B1-B4) giving the status of each rule in it, for example `A4: 1 fixed, 2 pass, 3 fixed, 4 pass, 5 pass, 6 fixed, 7 pass, 8 not checked (6 entries in the .bib)`. A status is pass, fixed, or not checked (with the reason); never mark a rule pass without checking it.
7. For a final polish: a short change log with one example per type of change, and the `[TODO]` items that need the author.
