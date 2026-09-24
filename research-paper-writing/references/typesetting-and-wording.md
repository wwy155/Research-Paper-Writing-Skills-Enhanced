# Typesetting and Wording Guide

Use for the final polish, after the story, structure, and experiments are stable. Table rules are in `references/experiments.md`.

## Rules (Do Not Violate)

1. Preserve meaning: never change numbers, equations, citation keys, labels, or the scope of a claim.
2. Never invent claims or numbers; leave `[TODO: number]` instead.
3. Do not rewrite clear sentences for variety, and never introduce the patterns in B3.

## Part A: Typesetting

### A1. Compliance (Desk-Reject Risks)

1. Never change the template's margins, fonts, or spacing; stay within the page limit.
2. Review version: no author names, acknowledgments, identifying links, or author PDF metadata; cite your own work in the third person.
3. Embed all fonts and avoid Type 3 fonts (check with `pdffonts`; in Matplotlib set `pdf.fonttype` to 42).
4. Leave no `??` or `[?]` in the paper or the supplement.

### A2. Figures and Floats

1. Use vector PDF for plots and diagrams; text inside a figure should be no smaller than the caption font.
2. Give each method the same name, color, and order in every figure and table, and always highlight ours.
3. Start each caption with a bold one-line takeaway, then add what is needed to read the figure without the main text. Figure captions go below, table captions above.
4. Except for the teaser, a figure, table, or algorithm must appear after the text that mainly introduces it and inside the same (sub)section. Put its source right after that paragraph; `flafter` keeps it from appearing earlier, and `\FloatBarrier` (`placeins`) before the next (sub)section keeps it from drifting out. Check the compiled PDF.

### A3. Math

1. Define every symbol at first use and keep notation fixed across the paper.
2. Set word subscripts upright: `x_{\text{gt}}`, not `x_{gt}`.
3. Punctuate display equations as part of the sentence.

### A4. References and LaTeX Details

1. Use a non-breaking space: `Figure~\ref{...}`, `NeRF~\cite{...}`. Choose `Fig.` or `Figure` once and keep it.
2. A citation is not a noun: write `NeRF~\cite{nerf} shows`, not `\cite{nerf} shows`.
3. Write ``` ``quotes'' ``` instead of `"quotes"`, `--` for ranges, and `e.g.,` / `i.e.,` with a comma.
4. Remove full-width punctuation (`，。：（）`) left by Chinese input methods.
5. Bibliography: consistent venue names, published versions instead of arXiv, protected capitals (`{NeRF}`).
6. Cite at first mention every named model, method, dataset, benchmark, metric, or application, and every important claim that is not ours. Never invent a reference; mark an unknown source as `\cite{TODO}`.

## Part B: Wording

### B1. Terminology

One concept, one term: never alternate `module / block / component` for the same object. Define each abbreviation once, and spell dataset and method names exactly as their authors do.

### B2. Sentence Clarity

1. One sentence, one idea; split sentences longer than about 30 words.
2. Old-to-new: start with what the reader already knows, end with the new information.
3. No ambiguous `this` / `it`: write "This design ...", not "This ...".

### B3. Sentence Patterns Overused by LLMs

Instruction-tuned LLMs use present participial clauses at 2-5 times the human rate and favor summative sentences (Reinhart et al., arXiv:2410.16107). Never introduce these patterns; in the author's text, fix them where they cluster.

1. Trailing participle: "..., highlighting / enabling / paving the way for ..." -> state the concrete consequence, or delete it.
2. Negate-then-correct: "not merely A, but B" -> state B.
3. Summary closer: "Overall, these results demonstrate ..." -> delete it, or turn it into a transition.
4. Progress-then-gap opener: "While X has achieved remarkable progress, ..." -> name what fails and why.
5. Stacked adverbs: "Notably, ... Importantly, ... Furthermore, ..." -> keep only real relations.
6. Unsupported triplets: "efficient, scalable, and robust" -> keep only what the experiments show.

### B4. Section-Specific Wording

1. Opening: no clichés such as "With the rapid development of deep learning, ..."; start from the task and its concrete difficulty.
2. Contributions: parallel, concrete, and each checkable against an experiment.
3. Results: every result sentence names metric, dataset, baseline, and magnitude.
4. Related Work: specific and fair ("does not model X"), never dismissive.

## Output Contract

Return the revised text with LaTeX commands, labels, and citation keys unchanged; a short change log with one example per type of change; and the `[TODO]` items that need the author.
