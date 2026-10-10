# Skills: Research Paper Writing

[中文介绍](./README_zh.md).

> Important Attribution
> Most writing knowledge and methodology in this repository comes from Prof. Peng Sida (彭思达)'s open study notes:
> https://pengsida.notion.site/c1a22465a0fa4b15a12985223916048e
> Prof. Peng's original repository:
> https://github.com/pengsida/learning_research
> I sincerely thank Prof. Peng for openly sharing these valuable experiences.
> My contribution is organization, structured adaptation, and packaging as reusable Skills.

## Repository Overview

This repository currently provides one skill package:

- `research-paper-writing/`
  - `SKILL.md`: core workflow, usage rules, and the writing and typesetting rules applied to every edit
  - `references/`: section-specific writing guides and templates
  - `scripts/check_tex.py`: rule checker the agent runs after every edit (Python 3, standard library only). It ends with a pass/fail list of the parts every paper must have, which the agent copies into its reply. The list starts with the story of the paper, where every claim has a figure or table as evidence. The agent works in a loop: it edits, runs every check, reviews the paper (with parallel reviewer sub-agents when available), fixes what they find, and logs the round in the paper, until a round finds nothing. Next come the style references, 3-5 papers that are recent, closest to ours, or similar to ours in the level of contribution. The agent views them page by page and imitates their vibe (structure, tone, and pace) without copying their sentences or specific content, decides what each figure shows itself, and uses the built-in example bank only to fill gaps. It also covers the venue's template, its Appendix rules, and three page limits looked up for the venue: the main text of a long paper, the references, and the whole paper (8 pages of main text, references excluded, when the rules cannot be found); the closest work's figures and tables, reproduced where they say something about ours or reviewers expect them; the latest state of the art; at least 3 figures, each checked by `figure_qa.py`, including an architecture figure in the Method that the agent generates with the `generate_image` tool (when the tool is missing or fails, it asks you how to proceed); the paper compiled with pdflatex, as on Overleaf and arXiv (when pdflatex is missing, the agent installs TeX Live or works with you until it is installed, and never falls back to another tool), and every page viewed with `page_qa.py`; the experiments the paper needs, which the agent runs itself or logs as running or blocked; and the metrics. It also flags every sentence about where our method loses, because the paper sells its story with every result that supports it, and it flags informal wording (contractions, colloquialisms, exclamations, rhetorical questions), ultra-short and overlong sentences, and paragraphs without transition words, so that the prose stays formal, academic, and well connected
  - `scripts/figure_qa.py`: checks every figure after drawing (legend over data, overlapping or cut-off content, text and markers too small or too large, empty axis ranges and margins, titles that state a conclusion) and writes a preview to look at
  - `scripts/page_qa.py`: makes the agent look at every page after each compile. It renders the PDF and boxes white space (blank bands, columns that end early, narrow figures, stretched spacing), text in the margins, and short last lines. It writes color images at the highest resolution an image viewer keeps: main-text pages in quarters (about 200 dpi), other pages in halves (about 150 dpi), and figures or tables cut by a tile edge whole, at up to 300 dpi. Each image carries a code, which the agent can only get by viewing it, and after a recompile only changed pages need viewing again. `check_tex.py` fails until the codes of the current PDF are confirmed. With `--reference`, it writes overview sheets of a style-reference paper, to see how it is written and laid out
  - `agents/openai.yaml`: agent metadata

Typical use cases:

- Drafting or rewriting Abstract / Introduction / Method / Experiments / Conclusion
- Improving paragraph flow and section logic
- Checking claim-evidence alignment
- Running pre-submission self-review from a reviewer mindset

## Figures and Tables

Every figure must be informative, look good, and convince. It need not prove a claim of the story, since a paper has many figures and only a few claims. It earns its place by showing something informative, such as a result, a comparison, how the method works, or what the model learns. The agent writes what each figure shows in one sentence, picks the form that shows it most clearly, and redraws it until it looks good and convinces. That means one look across the paper, readable text at print size, clean layouts, direct comparisons with zoom-ins, and honest axes. It never copies the figures of another paper. Each figure and table gets a line in a figure plan (`label: message -> form`). Those that are the evidence for a claim carry its tag, e.g., `[C1]`, so every claim has evidence. One form is used for at most two main-text figures. Once the main table and the ablation are complete, the agent designs two to four showcase analyses, which are striking figures or tables that tie directly to the core idea and either explain an interesting phenomenon or show an advantage of the method. It first states the mechanism, derives at least five testable predictions, checks every candidate for validity, interest, and its link to the idea, and records all candidates with their verdicts in an analysis plan that the checker verifies. The Method section always has an architecture figure that shows the inputs, every module, the data flow, and the outputs; the agent generates it with `generate_image`, checks every label at full size, and asks you for the figure or another route when the tool is unavailable or keeps failing. Captions first say what the figure shows, then what each part shows, then the conclusion in at most two sentences, within 50 words (80 for a teaser or pipeline figure). Details: `research-paper-writing/references/figures.md` and `research-paper-writing/references/table-types.md`. After drawing, `scripts/figure_qa.py` checks every figure, and the checker rejects any image not checked since its last change.

## Installation

Assume you are in the repository root.

These commands copy the skill, so an installed copy does not change when you update this repository. After updating, delete the installed folder and copy it again, or install it once with `ln -s "$PWD/research-paper-writing" <skills-dir>/` instead of `cp -R`.

### 1) Codex

Copy the skill into `$CODEX_HOME/skills/`:

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R research-paper-writing "$CODEX_HOME/skills/"
```

Usage example:

```text
Use $research-paper-writing to improve my paper's Introduction.
```

### 2) CC (Claude Code)

Use either a global or project-level installation.

Global:

```bash
mkdir -p "$HOME/.claude/skills"
cp -R research-paper-writing "$HOME/.claude/skills/"
```

Project-level:

```bash
mkdir -p .claude/skills
cp -R research-paper-writing .claude/skills/
```

In prompts, explicitly request this skill, for example: `Please use the research-paper-writing skill`.

### 3) Gemini

Copy this skill into your Gemini skills directory:

```bash
mkdir -p "$HOME/.gemini/skills"
cp -R research-paper-writing "$HOME/.gemini/skills/"
```

Then ask concrete tasks in Gemini (for example, rewriting an Abstract with claim-evidence checks).

## Credits

Again, this repository is primarily based on Prof. Peng Sida (彭思达)'s open notes, while my work focuses on curation and Skills adaptation.
Prof. Peng's original repository: https://github.com/pengsida/learning_research

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
