# Paragraph Clarity Check

Use this quick test whenever the user asks whether a paragraph "flows" or is clear, and for the reverse outlining after each section (Core Workflow step 5 in `SKILL.md`).

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
3. If flow is still weak, add temporary section headers during revision and make each sentence's relation to the previous one explicit (cause, contrast, consequence). Name that relation with a transition word from the table below (B2.5), and avoid empty emphasis openers such as "Notably" (B3.5). Remove unnecessary headers before finalizing.

Source reference for this check:

- `references/does-my-writing-flow-source.md`

## Formal, Complete Sentences

Academic prose connects its statements into reasoning, so each sentence should carry a complete thought together with its cause, condition, or consequence (Writing Rules B2.1, B2.4, and B2.5 in `SKILL.md`).

- Aim for 15-25 words per sentence. Join related short statements with a subordinate clause or a transition word, and split any sentence longer than 30 words into two complete sentences.
- Keep the register formal: full forms instead of contractions, precise verbs instead of colloquial ones, and statements instead of questions or exclamations.

Choppy: "Prior methods are slow. They optimize each scene. This takes hours."
Formal: "Prior methods optimize every scene from scratch, which takes several hours per scene and therefore rules out interactive use."

## Transition Words

Choose each transition word by the relation between the two sentences or clauses that it joins, and never use one whose relation does not hold. For example, "However" must introduce a real contrast.

| Relation | Transition words |
|---|---|
| Contrast or difference | however, whereas, in contrast, by contrast, on the other hand, unlike, instead |
| Concession or unexpectedness | although, even though, yet, despite, in spite of, regardless of, nevertheless, nonetheless |
| Addition | moreover, furthermore, in addition, additionally, also (inside a sentence) |
| Cause and effect | because, since, therefore, thus, hence, consequently, as a result |
| Example or specification | for example, for instance, such as, in particular, specifically, namely |
| Sequence | first, then, subsequently, finally |
| Similarity | similarly, likewise, in the same way |
| Purpose | to this end, so that, in order to |

- Vary the transition words. Do not open three sentences of one paragraph with additive ones such as "Moreover", "Furthermore", and "In addition", and merge such points into fewer sentences instead.
- Use "also" inside a sentence ("We also evaluate ..."), and "Moreover" or "In addition" when a sentence must open with an addition.
- Avoid empty emphasis openers such as "Notably", "Importantly", and "Interestingly", because they name no relation (B3.5).

Without transitions: "Our codes are shared across neighbors. Baselines learn one code per point. Our method converges in ten minutes."
With transitions: "Whereas baselines learn one code per point, our codes are shared across neighbors, and as a result our method converges within ten minutes."

The checker warns when a paragraph of four or more sentences contains no transition word, and when three of its sentences open with an additive transition.
