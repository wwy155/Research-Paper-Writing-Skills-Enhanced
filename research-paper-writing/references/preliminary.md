# Preliminary Writing Guide (Optional Section)

## When to Include

Include it only when the Method needs:

1. a technique uncommon in the target community,
2. a formal task definition (a new task or a non-standard setting), or
3. a base formulation that the Method modifies.

Skip it when the background is standard for the venue; a short recap in the Method Overview is enough. Use `\section{Preliminaries}` before the Method if it frames the whole paper; otherwise make it the first subsection of the Method.

## Rules

1. Background only: every contribution belongs in the Method. A novel part placed here gets credited to prior work.
2. Cite the source of every formulation.
3. Define only what the Method uses, and keep that notation fixed.
4. End with a bridge: the property our method exploits, or the limitation it removes.

## Sentence Skeletons

Technical background:

1. `Our method builds on [technique]~\cite{...}, which [what it does].`
2. `Given [input], [technique] computes [output] as` + equation + `where [symbol] denotes ...`
3. `However, [technique] assumes ..., which fails when ...` (bridge)

Problem formulation:

1. `Given [input] with [assumptions], our goal is to [recover/estimate/predict] [output].`
2. `Formally, we seek ... that minimizes/satisfies ...`
3. `Unlike [closest setting], our setting [key difference].`
