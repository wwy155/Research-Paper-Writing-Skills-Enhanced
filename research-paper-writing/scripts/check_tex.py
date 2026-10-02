#!/usr/bin/env python3
r"""Check a LaTeX paper against the mechanical Writing Rules in SKILL.md.

Usage:
  python3 check_tex.py main.tex [more.tex ...] [--bib refs.bib] [--log main.log]
                       [--pdf main.pdf] [--review] [--max-words 25] [--min-refs 35] [--min-figures 3]

Follows \input, \include, and \subfile, finds the .bib from \bibliography or
\addbibresource, and prints one line per issue:

  path:line: ERROR [A4.1] message | snippet

ERROR: must be fixed. WARN: fix it, or justify it in your reply.
Exit status is 1 when there is at least one ERROR, 2 on a usage error.
Only the Python standard library is used. --pdf also uses pdffonts, pdftotext,
and pdfinfo (poppler-utils) when they are installed.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ERROR, WARN = "ERROR", "WARN"

NOT_CHECKED = ("A1.1, A1.2, A1.6, A2.1-A2.3, A2.5, A2.6, A3.1, B1, B2.2, B4.2, B4.4 "
               "(and A1.3-A1.5 without --pdf/--log/--review)")

MATH_ENVS = (r"equation|align|gather|multline|eqnarray|flalign|alignat|"
             r"displaymath|math|dmath")
VERBATIM_ENVS = r"verbatim|Verbatim|lstlisting|minted|comment"
TABULAR_ENVS = r"tabular\*?|tabularx|tabulary|longtable|array"
# Commands whose (optional and first mandatory) arguments are not prose.
ARG_CMDS = (r"label|ref|eqref|cref|Cref|autoref|pageref|nameref|url|href|"
            r"includegraphics|input|include|subfile|bibliography|"
            r"bibliographystyle|addbibresource|usepackage|documentclass|"
            r"begin|end|cite[a-zA-Z]*|autocite|parencite|textcite|footcite|"
            r"color|textcolor|colorbox|definecolor|vspace|hspace|setlength|"
            r"addtolength|resizebox|scalebox|hypersetup|title|author|"
            r"affiliation|institute|email")
CITE_CMD = r"\\(?:cite|citep)(?![a-zA-Z])\*?(?:\s*\[[^\]]*\])*\s*\{"
PREPOSITIONS = {"in", "by", "of", "from", "following", "see", "to", "and",
                "or", "with", "than", "as", "like", "unlike", "per", "via",
                "on", "into", "for", "cf"}
ABBREVIATIONS = re.compile(
    r"\b(?:e\.g|i\.e|et al|etc|vs|Fig|Figs|Eq|Eqs|Sec|Secs|Tab|Tabs|Alg|"
    r"Ref|Refs|cf|resp|approx|No|Nos|Dr|Prof|Supp)\.")
MARKETING_ADJECTIVES = {
    "efficient", "effective", "scalable", "robust", "accurate", "fast",
    "flexible", "general", "generalizable", "simple", "lightweight",
    "versatile", "practical", "reliable", "interpretable", "powerful",
    "seamless", "stable", "compact", "elegant", "principled", "easy"}
NAME_EXCLUDE = {
    "LaTeX", "TeX", "BibTeX", "arXiv", "GitHub", "iPhone", "iPad", "YouTube",
    "kNN", "k-NN", "mAP", "mIoU", "IoU", "GHz", "MHz", "kHz", "GiB", "MiB",
    "FLOPs", "GFLOPs", "TFLOPs", "OpenReview"}
GENERIC_NOUNS = (r"dataset|datasets|benchmark|benchmarks|model|models|method|methods|network|"
                 r"networks|framework|representation|loss|metric|algorithm|architecture|"
                 r"pipeline|encoder|decoder|backbone|library|toolkit|engine|renderer|split|splits")
NAME_SUFFIXES = re.compile(
    r"-(?:based|like|style|only|free|aware|guided|driven|conditioned|"
    r"specific|level|wise|type)$")
# Start of a sentence: after . ! ? or a closing brace, or at a line start.
SENT_START = r"(?:^|(?<=[.!?}]))[ \t]*"

PROSE_PATTERNS = [
    (ERROR, "B3.1",
     "Trailing participle: state the consequence as its own sentence, or delete it",
     r",\s+(?:highlighting|underscoring|showcasing|emphasi[sz]ing|"
     r"paving the way|enabling|fostering|allowing|making|leading to|"
     r"resulting in|ensuring|facilitating|providing|offering|yielding|"
     r"thereby\s+\w+ing)\b"),
    (ERROR, "B3.2",
     "Negate-then-correct: state the positive claim directly ('A and B')",
     r"\bnot\s+(?:merely|only|just|simply)\b[^.;:]{0,150}?\bbut\b"),
    (ERROR, "B3.2", "'It is A, not B': state what it is, and drop the contrast",
     r"\b(?:[Ii]t|[Tt]his|[Tt]hat|[Tt]hese|[Tt]hey|[Tt]he (?:key|goal|aim|point|idea|result|difference|problem|"
     r"challenge|bottleneck|issue|question)|[Oo]ur (?:method|model|approach|framework|goal|aim|key idea|contribution|"
     r"insight|design|module))\s+(?:is|are|was|were|lies|remains)\s+[^.;:!?]{1,80}?,\s+not\s+(?!only\b)"),
    (ERROR, "B3.2", "Negate-then-correct ('is not A but B'): state B directly",
     r"\b(?:is|are|was|were)\s+not\s+(?!only\b)[^.;:!?,]{1,80}?,?\s+but\s+(?!also\b)"),
    (ERROR, "B3.3", "Summary closer: delete it, or turn it into a transition",
     SENT_START + r"(?:Overall|In summary|To summarize|To sum up|In conclusion|"
     r"Taken together|Collectively|All in all)\s*,(?![^.:]{0,40}\bcontributions?\b)"),
    (ERROR, "B3.3", "Generic summary claim: state the concrete result instead",
     r"\b(?:[Tt]hese|[Tt]he|[Oo]ur|[Ss]uch)\s+(?:results|experiments|findings|evaluations|"
     r"comparisons)\s+(?:clearly\s+)?(?:demonstrates?|shows?|validates?|"
     r"confirms?|verif(?:y|ies)|highlights?|proves?)\s+the\s+(?:effectiveness|"
     r"superiority|efficacy|advantages?|benefits?|robustness|strength)"),
    (ERROR, "B3.4", "Progress-then-gap: name what fails and why instead",
     r"\b(?:achieved|made|witnessed|seen|shown|undergone|experienced|enjoyed)"
     r"\s+(?:remarkable|significant|great|tremendous|impressive|substantial|"
     r"considerable|rapid|unprecedented|notable)\s+(?:progress|success(?:es)?|"
     r"advances|advancements?|strides|improvements?|breakthroughs?)"),
    (ERROR, "B4.1", "Cliche opener: start from the task and its concrete difficulty",
     r"\b(?:[Ww]ith the (?:rapid|fast|swift|recent) (?:development|"
     r"advancements?|advances|progress|growth|rise)|[Ii]n recent years|"
     r"[Rr]ecent years have (?:witnessed|seen)|(?:attracted|gained|drawn|"
     r"received|garnered) (?:increasing|growing|much|considerable|significant|"
     r"widespread|tremendous|great) (?:attention|interest)|"
     r"[Tt]he (?:\w+ )?community (?:has|have|is|are|was|were)\b|"
     r"(?:attention|interest) (?:from|of|in) the (?:\w+ )?community)"),
    (WARN, "B2.3", "Ambiguous This/It: name the noun ('This design ...')",
     SENT_START + r"(?:This|These|It)\s+(?:is|are|was|were|makes?|allows?|"
     r"enables?|leads?|shows?|means|motivates|results|helps|ensures|provides|"
     r"indicates|demonstrates|suggests|can|will|would|may|might)\b"),
    (ERROR, "A4.3", "Write e.g., / i.e., with a comma",
     r"\b(?:e\.g|i\.e)\.(?!,)"),
    (ERROR, "A4.3", "Use `` and '' instead of straight double quotes",
     r"(?<!\\)\""),
    (ERROR, "A4.3", "Use `` and '' instead of Unicode quotes",
     r"[\u201c\u201d\u2018\u2019]"),
    (ERROR, "A4.3", "Use -- for numeric ranges",
     r"(?<![\w.\-])\d+(?:\.\d+)?-\d+(?:\.\d+)?(?![\w.\-])"),
]
EM_DASH = r"-{3,}|[\u2014\u2015\u2e3a\u2e3b]|\\textemdash\b"
ADVERBS = (SENT_START + r"(?:Notably|Importantly|Furthermore|Moreover|"
           r"Additionally|Crucially|Interestingly|Remarkably|Significantly|"
           r"Besides|In addition)\s*,")
RESULT_WORDS = re.compile(r"\b(?:outperform\w*|state-of-the-art|SOTA|superior|"
                          r"surpass\w*|better than|significant(?:ly)? improve\w*)")


def blank(s):
    """Replace every character except newlines with a space, keeping offsets."""
    return re.sub(r"[^\n]", " ", s)


def strip_comments(text):
    lines = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        lines.append(line if not m else line[:m.start()] + " " * (len(line) - m.start()))
    return "\n".join(lines)


def document_body(text):
    begin, end = text.find("\\begin{document}"), text.find("\\end{document}")
    start = begin + len("\\begin{document}") if begin >= 0 else 0
    stop = end if end >= 0 else len(text)
    return blank(text[:start]) + text[start:stop] + blank(text[stop:])


def mask(text, pattern, flags=re.S, placeholder=""):
    """Blank every match of pattern; optionally keep a short placeholder."""
    def repl(m):
        s = blank(m.group(0))
        return placeholder + s[len(placeholder):] if placeholder and "\n" not in s[:len(placeholder)] else s
    return re.sub(pattern, repl, text, flags=flags)


def math_spans(text):
    pats = [r"\\begin\{(" + MATH_ENVS + r")(\*?)\}.*?\\end\{\1\2\}",
            r"\\\[.*?\\\]", r"(?<!\\)\$\$.*?(?<!\\)\$\$",
            r"\\\(.*?\\\)", r"(?<![\\$])\$(?!\$)(?:\\.|[^$\\])+?\$"]
    spans, masked = [], text
    for p in pats:
        for m in re.finditer(p, masked, re.S):
            spans.append((m.start(), m.end()))
        masked = mask(masked, p)
    return spans


def mask_args(text):
    pattern = (r"(\\(?:" + ARG_CMDS + r")\*?)((?:\s*\[[^\]]*\])*)(\s*\{)([^{}]*)(\})")
    return re.sub(pattern, lambda m: m.group(1) + blank(m.group(2)) + m.group(3)
                  + blank(m.group(4)) + m.group(5), text)


def brace_end(text, i):
    """Index just past the {...} group that opens at text[i]; None if it never closes."""
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return None


def latex_words(tex):
    """Words as printed: a citation, a reference, or an inline formula counts as one word."""
    t = re.sub(r"\\(?:cite[a-zA-Z]*|ref|eqref|autoref|[cC]ref)\*?(?:\s*\[[^\]]*\])*\s*\{[^}]*\}", " X ", tex)
    t = re.sub(r"\\(?:label|TODO|todo)\{[^{}]*\}", " ", t)  # author notes are not printed text
    t = re.sub(r"(?<!\\)\$(?:\\.|[^$\\])+?\$", " X ", t)
    t = re.sub(r"\\[A-Za-z]+\*?", " ", t)
    return re.findall(r"[A-Za-z0-9]+(?:[.'\-][A-Za-z0-9]+)*", t)


class File:
    def __init__(self, path):
        self.path = path
        with open(path, encoding="utf-8", errors="replace") as f:
            self.raw = f.read()
        self.lines = self.raw.split("\n")
        self.clean = document_body(strip_comments(self.raw))
        no_verb = mask(self.clean, r"\\begin\{(" + VERBATIM_ENVS + r")\}.*?\\end\{\1\}")
        no_verb = mask(no_verb, r"\\verb\*?([^a-zA-Z\s]).*?\1")
        # Whole file (preamble too, e.g. \title), minus comments and verbatim.
        whole = mask(strip_comments(self.raw), r"\\begin\{(" + VERBATIM_ENVS + r")\}.*?\\end\{\1\}")
        self.whole = mask(whole, r"\\verb\*?([^a-zA-Z\s]).*?\1")
        self.nonverbatim = no_verb
        self.keys_masked = mask_args(no_verb)  # math kept, command arguments blanked
        spans = math_spans(no_verb)
        prose = no_verb
        for a, b in spans:
            prose = prose[:a] + ("X" + blank(prose[a + 1:b]) if b - a > 1 else " ") + prose[b:]
        prose = mask(prose, r"\\begin\{(" + TABULAR_ENVS + r")\}.*?\\end\{\1\}")
        self.prose = mask_args(prose)
        math_only = blank(no_verb)
        for a, b in spans:
            math_only = math_only[:a] + no_verb[a:b] + math_only[b:]
        self.math = math_only

    def line_of(self, pos):
        return self.clean.count("\n", 0, pos) + 1

    def snippet(self, pos, width=70):
        line = self.line_of(pos)
        text = self.lines[line - 1] if line - 1 < len(self.lines) else ""
        col = pos - (self.clean.rfind("\n", 0, pos) + 1)
        start = max(0, col - width // 2)
        s = text[start:start + width].strip()
        return ("..." if start > 0 else "") + s


class Report:
    def __init__(self):
        self.items = []

    def add(self, f, pos, level, rule, msg):
        path, line, snip = (f.path, f.line_of(pos), f.snippet(pos)) if f else ("(build)", 0, "")
        self.items.append((path, line, level, rule, msg, snip))

    def add_plain(self, path, level, rule, msg):
        self.items.append((path, 0, level, rule, msg, ""))

    def count(self, level):
        return sum(1 for i in self.items if i[2] == level)


def resolve(base_dir, name, ext):
    cands = [name, name + ext] if not name.endswith(ext) else [name]
    for c in cands:
        p = c if os.path.isabs(c) else os.path.join(base_dir, c)
        if os.path.isfile(p):
            return p
    return None


def collect_files(paths):
    ordered, seen, missing = [], set(), []
    root = os.path.dirname(os.path.abspath(paths[0]))

    def visit(p):
        ap = os.path.abspath(p)
        if ap in seen:
            return
        seen.add(ap)
        f = File(p)
        ordered.append(f)
        for m in re.finditer(r"\\(?:input|include|subfile)\{([^}]+)\}", f.clean):
            child = resolve(root, m.group(1).strip(), ".tex") or resolve(
                os.path.dirname(ap), m.group(1).strip(), ".tex")
            if child:
                visit(child)
            else:
                missing.append((f, m.start(), m.group(1)))

    for p in paths:
        visit(p)
    return ordered, missing, root


def check_citations(f, rep):
    for m in re.finditer(CITE_CMD, f.prose):
        before = f.prose[:m.start()]
        if re.search(r"(?:^|\n[ \t]*\n)[ \t]*$", before) or re.search(r"[.!?][)}\]]*\s*$", before) \
                or re.search(r"\\item\s*$", before):
            rep.add(f, m.start(), ERROR, "A4.2",
                    "A citation is not a noun: name the work first (NeRF~\\cite{...} shows ...)")
            continue
        prev = re.search(r"([A-Za-z]+)[.,]?(\s*~?\s*)$", before)
        if prev and prev.group(1).lower() in PREPOSITIONS:
            rep.add(f, m.start(), ERROR, "A4.2",
                    "Citation used as a noun ('in [1]'): name the work, then cite it")
        elif not before.endswith("~") and not re.search(r"[(\[{]\s*$", before):
            rep.add(f, m.start(), ERROR, "A4.1", "Use ~ before \\cite (Name~\\cite{...})")
    for m in re.finditer(r"\\(?:ref|eqref)\{", f.prose):
        before = f.prose[:m.start()]
        if re.search(r"[A-Za-z.]\s+$", before):
            rep.add(f, m.start(), ERROR, "A4.1", "Use ~ before \\ref (Figure~\\ref{...})")
    # "A and B~\cite{a,b}": cite each item right after its name.
    pat = (r"(?<![\w-])[A-Z][\w-]*(?:\s*,\s*[A-Z][\w-]*)*\s*,?\s+(?:and|or)\s+"
           r"[A-Z][\w-]*\s*~?(" + CITE_CMD + r")([^}]*)\}")
    for m in re.finditer(pat, f.prose):
        keys = f.nonverbatim[m.start(2):m.end(2)]
        if len([k for k in keys.split(",") if k.strip()]) >= 2:
            rep.add(f, m.start(), ERROR, "A4.6",
                    "Cite each item right after its name: A~\\cite{a} and B~\\cite{b}")
    for m in re.finditer(CITE_CMD + r"([^}]*)\}\s*\.", f.nonverbatim):
        if len([k for k in m.group(1).split(",") if k.strip()]) >= 4:
            rep.add(f, m.start(), WARN, "A4.7",
                    "Long citation list ends the sentence: split it and cite each point where it is made")


def check_prose(f, rep, max_words):
    for level, rule, msg, pat in PROSE_PATTERNS:
        for m in re.finditer(pat, f.prose, re.M):
            rep.add(f, m.start(), level, rule, msg)
    for m in re.finditer(r"\b([A-Za-z]+),\s+([A-Za-z]+),?\s+and\s+([A-Za-z]+)\b", f.prose):
        words = [w.lower() for w in m.groups()]
        if sum(w in MARKETING_ADJECTIVES for w in words) >= 2:
            rep.add(f, m.start(), WARN, "B3.6",
                    "Adjective triplet: keep only the properties the experiments show")
    for para in re.finditer(r"(?:(?!\n[ \t]*\n).)+", f.prose, re.S):
        hits = list(re.finditer(ADVERBS, para.group(0), re.M))
        if len(hits) >= 2:
            rep.add(f, para.start() + hits[1].start(), ERROR, "B3.5",
                    f"{len(hits)} stacked adverbs (Notably/Furthermore/Moreover...) in one "
                    "paragraph: keep only real relations")
    # Sentences: long sentences (B2.1) and result sentences without numbers (B4.3).
    protected = ABBREVIATIONS.sub(lambda m: m.group(0).replace(".", "\0"), f.prose)
    bounds = [0]
    for m in re.finditer(r"(?<=[.!?])[)}\]'\"]*\s+|\n[ \t]*\n|\\item\b|"
                         r"\\(?:sub)*section\*?|\\paragraph\*?|\\caption", protected):
        bounds.append(m.end())
    bounds.append(len(protected))
    for a, b in zip(bounds, bounds[1:]):
        sent = protected[a:b]
        text = re.sub(r"\\[A-Za-z]+\*?", " ", sent)
        words = re.findall(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*", text)
        if not words:
            continue
        first = re.search(r"(?<![\\A-Za-z])[A-Za-z0-9]", sent)
        start = a + (first.start() if first else 0)
        if len(words) > max_words:
            rep.add(f, start, WARN, "B2.1",
                    f"Sentence has {len(words)} words (> {max_words}): split it")
        if RESULT_WORDS.search(sent) and not re.search(r"\d", f.keys_masked[a:b]):
            rep.add(f, start, WARN, "B4.3",
                    "Result sentence without numbers: name metric, dataset, baseline, and magnitude")


def check_math(f, rep):
    for m in re.finditer(r"_\{(?:[A-Za-z]{3,}|gt|fg|bg)\}|_(?![{\\\s])[A-Za-z]{2,}", f.math):
        rep.add(f, m.start(), ERROR, "A3.2",
                "Set word subscripts upright: x_{\\text{gt}}, not x_{gt}")
    pats = [r"\\begin\{(?:" + MATH_ENVS + r")\*?\}(.*?)\\end\{(?:" + MATH_ENVS + r")\*?\}",
            r"\\\[(.*?)\\\]", r"(?<!\\)\$\$(.*?)(?<!\\)\$\$"]
    for p in pats:
        for m in re.finditer(p, f.nonverbatim, re.S):
            body = m.group(1)
            while True:
                new = re.sub(r"(?:\s+|\\label\{[^}]*\}|\\nonumber|\\notag|\\\\|"
                             r"\\end\{(?:split|aligned|gathered|cases|array|[pbvBV]?matrix)\})$",
                             "", body)
                if new == body:
                    break
                body = new
            if body and not re.search(r"(?:[.,;]|\\(?:text|mbox|mathrm)\{\s*[.,;]\s*\})$", body):
                rep.add(f, m.start(), ERROR, "A3.3",
                        "Punctuate the display equation as part of the sentence (end with , or .)")


CAPTION_WORDS, DIAGRAM_CAPTION_WORDS = 50, 80
DIAGRAM_LABEL = re.compile(r"teaser|pipeline|overview|framework|architecture|arch\b|method", re.I)
SUBFLOATS = r"\\begin\{(subfigure|subtable)\}.*?\\end\{\1\}"
# A caption first says what is shown: usually a noun phrase ("Qualitative comparison on ...").
DESCRIPTION_START = re.compile(
    r"^(?:\(?[a-z]\)\s*)?(?:Qualitative|Quantitative|Visual|Comparisons?|Results?|Overview|Ablations?|Effects?|Impact|"
    r"Influence|Analys[ie]s|Visuali[sz]ations?|Illustrations?|Examples?|Samples?|Training|Per-\w+|Breakdown|"
    r"Distributions?|Evaluations?|Sensitivity|Robustness|Generali[sz]ation|Efficiency|Statistics|Architecture|"
    r"Pipeline|Framework|Teaser|Failure|Novel|Renderings?|Reconstructions?|Predictions?|Attention|Errors?|Accuracy|"
    r"Runtime|Speed|Memory|Performance|Numbers?|Scaling|User|Human|"
    r"We\s+(?:compare|show|visuali[sz]e|plot|report|evaluate|ablate|illustrate|study|present|test|measure|list))\b")
# Words that make a sentence a claim. CLAIM decides whether the first sentence concludes;
# CLAIM_ANY (broader) decides whether the caption has a conclusion at all.
CLAIM = re.compile(r"\b(?:outperform\w*|beats?|surpass\w*|superior|better|worse|best|worst|highest|lowest|fastest|"
                   r"slowest|sharpest|most|least|only|exceeds?|dominates?|wins?|keeps?|preserves?|recovers?|matches|"
                   r"achieves?|improves?|reduces?|degrades?|fails?|blurs?|grows?|helps?|costs?|comes? from|scales?)\b",
                   re.I)
CLAIM_ANY = re.compile(CLAIM.pattern + r"|\b(?:faster|slower|sharper|higher|lower|larger|smaller|fewer|more|less|"
                       r"gains?|drops?|stays?|remains?|than|while|whereas|consistent\w*|los(?:e|es|s|t)|prefer\w*|ahead|behind|"
                       r"trails?|leads?|robust|stable|insensitive|within)\b", re.I)
SUBFIGURE_SENTENCE = re.compile(r"^(?:\(?[a-z]\)|(?:Left|Right|Top|Bottom|Middle|Center|Rows?|Columns?|From (?:left|top)"
                                r"\w*(?: to \w+)?)\b)", re.I)
FILLER = re.compile(
    r"\b(?:best|second|third|top)(?:[- ]best)?\b[^.;]{0,60}?\b(?:bold\w*|underlin\w*|highlight\w*|colou?r\w*|shad\w+|"
    r"in (?:red|blue|green|orange|yellow|gr[ae]y))"
    r"|\b(?:bold\w*|underlin\w*|shad\w+|highlight\w*)\b[^.;]{0,40}?\b(?:best|second|ours|our (?:method|row|results?))\b"
    r"|\b(?:ours|our (?:method|row|results?))\b[^.;]{0,30}?\b(?:shad\w+|highlight\w*|bold\w*|colou?r\w*|in gr[ae]y)"
    r"|\b(?:plotted|drawn|generated|created|made|produced)\s+(?:with|using|by|in)\s+(?:matplotlib|seaborn|plotly|tikz|"
    r"pgfplots|python|excel|inkscape|illustrator|draw\.io)\b"
    r"|(?:\\uparrow|\\downarrow|\u2191|\u2193)[^.;]{0,40}?\b(?:means|denotes|indicates|higher|lower)\b"
    r"|\b(?:higher|lower) (?:is|means) better\b", re.I)
SIGNIFICANCE = re.compile(r"\bp\s*(?:<|>|=|\\leq?|\\geq?|\\le\b|\\ge\b)|\bp-values?\b|\bt-tests?\b|\bWilcoxon\b|"
                          r"\bMann-Whitney\b|\bconfidence intervals?\b|\b9[059]\s*\\?%\s*CI\b|\bbootstrap\w*|"
                          r"\bstatistical(?:ly)?\s+significan\w*|\bsignificance\b|\bBonferroni\b|\bHolm\b", re.I)


def caption_sentences(arg):
    """Sentences of a caption, as printed text."""
    text = re.sub(r"\\(?:cite[a-zA-Z]*|ref|eqref|autoref|[cC]ref)\*?(?:\s*\[[^\]]*\])*\s*\{[^}]*\}", "X", arg)
    text = re.sub(r"\\(?:label|TODO|todo)\{[^{}]*\}", " ", text)
    text = re.sub(r"\\(?:textbf|emph|textit|underline|text)\{", "", text)
    text = re.sub(r"\\(?:small|footnotesize|scriptsize|normalsize)\b|[{}]", " ", text)
    text = ABBREVIATIONS.sub(lambda m: m.group(0).replace(".", ""), text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(\[\\])", text) if latex_words(s)]


def states_conclusion(sentence):
    return not DESCRIPTION_START.match(sentence) and bool(CLAIM.search(sentence))


def check_caption(f, rep, pos, arg, limit, results=True):
    """A2.4: what it shows first, then (a)/(b), then at most 2 short sentences of conclusion; no filler."""
    sentences = caption_sentences(arg)
    if not sentences:
        rep.add(f, pos, ERROR, "A2.4", "Empty caption: say what it shows, then the conclusion in 1-2 sentences")
        return
    if states_conclusion(sentences[0]):
        rep.add(f, pos, WARN, "A2.4", "The caption opens with a conclusion: first say what it shows ('Qualitative "
                "comparison on ...'), then (a)/(b), then the conclusion in at most 2 sentences")
    rest = [s for s in sentences[1:] if not SUBFIGURE_SENTENCE.match(s)]
    if len(rest) > 3:
        rep.add(f, pos, WARN, "A2.4", f"Caption has {len(rest)} sentences after the first: keep what it shows, "
                "(a)/(b), and at most 2 short sentences of conclusion")
    elif results and not states_conclusion(sentences[0]) and not any(CLAIM_ANY.search(s) for s in rest):
        rep.add(f, pos, WARN, "A2.4", "The caption has no conclusion: after saying what it shows, add it in 1-2 "
                "short sentences")
    m = FILLER.search(arg)
    if m:
        rep.add(f, pos, WARN, "A2.4", f"Formatting filler in the caption ('{m.group(0)[:40]}'): readers know the "
                "conventions; say what it shows and what to conclude")
    if SIGNIFICANCE.search(arg):
        rep.add(f, pos, WARN, "B4.5", "Significance details in a caption: move them to the Appendix and keep one "
                "sentence in the text")
    n = len(latex_words(arg))
    if n > limit:
        rep.add(f, pos, WARN, "A2.4", f"Caption has {n} words (> {limit}): keep what it shows, (a)/(b), and a short "
                "conclusion; move the analysis to the text")


def check_floats(f, rep, plan=None):
    for m in re.finditer(r"\\begin\{(table|figure)(\*?)\}(.*?)\\end\{\1\2\}", f.nonverbatim, re.S):
        env, full, off = m.group(1), m.group(3), m.start(3)
        body = mask(full, SUBFLOATS)  # captions of subfigures are not the float's caption
        labels = re.findall(r"\\label\{([^}]*)\}", full)
        kinds = set().union(*[plan[l.strip()][2] for l in labels if plan and l.strip() in plan])
        diagram = env == "figure" and (kinds & {"teaser", "diagram"} or any(DIAGRAM_LABEL.search(l) for l in labels))
        caps = list(re.finditer(r"\\caption(?:\[[^\]]*\])?\{", body))
        for c in caps:
            end = brace_end(body, c.end() - 1) or len(body)
            check_caption(f, rep, off + c.start(), body[c.end():end - 1],
                          DIAGRAM_CAPTION_WORDS if diagram else CAPTION_WORDS, results=not diagram)
        for sub in re.finditer(SUBFLOATS, full, re.S):
            for c in re.finditer(r"\\caption(?:\[[^\]]*\])?\{", sub.group(0)):
                end = brace_end(sub.group(0), c.end() - 1) or len(sub.group(0))
                text = " ".join(caption_sentences(sub.group(0)[c.end():end - 1]))
                if states_conclusion(text):
                    rep.add(f, off + sub.start() + c.start(), WARN, "A2.4", "A subfigure caption states a conclusion: "
                            "name what it shows ('Input', 'Ours'), and put the conclusion in the main caption")
        if env == "table":
            tab = re.search(r"\\begin\{(?:" + TABULAR_ENVS + r")\}", full)
            if caps and tab and caps[0].start() > tab.start():
                rep.add(f, off + caps[0].start(), ERROR, "A2.4", "Put the table caption above the table")
            for t in re.finditer(r"\\begin\{(?:" + TABULAR_ENVS + r")\}((?:\s*\{[^{}]*\}){1,2})", full):
                if "|" in t.group(1):
                    rep.add(f, off + t.start(), ERROR, "Tables",
                            "No vertical rules in the column spec (see references/experiments.md)")
            hl = list(re.finditer(r"\\(?:hline|cline)\b", full))
            if hl:
                rep.add(f, off + hl[0].start(), ERROR, "Tables",
                        f"{len(hl)} x \\hline/\\cline: use \\toprule, \\midrule, \\cmidrule, \\bottomrule")
        else:
            inc = list(re.finditer(r"\\includegraphics|\\begin\{tikzpicture\}", full))
            if caps and inc and caps[-1].start() < inc[-1].start():
                rep.add(f, off + caps[-1].start(), ERROR, "A2.4", "Put the figure caption below the figure")


# All-caps names that always need a citation; is_named misses them otherwise.
CITED_ACRONYMS = {
    "CLIP", "DINO", "BERT", "VGG", "BLIP", "YOLO", "DETR", "SIREN", "COLMAP",  # methods and tools
    "SSIM", "MS-SSIM", "LPIPS", "FID", "KID", "FVD", "BLEU", "ROUGE", "METEOR", "SPICE",  # metrics
    "KITTI", "COCO", "MS-COCO", "DTU", "LLFF", "MNIST", "LVIS", "GLUE", "MMLU"}  # datasets
# A mention counts as cited when \cite follows the name, a version ("360", "v3"), or a generic noun.
CITED_AFTER = re.compile(r"(?:\s+(?:\d[\w.]*|v\d[\w.]*))?(?:\s+(?:" + GENERIC_NOUNS + r"))?"
                         r"\s*\)?\s*~?\s*\\cite[a-zA-Z]*")
EXP_TITLE = re.compile(r"Experiment|Evaluation|Results")


def is_named(tok):
    if tok in CITED_ACRONYMS:
        return True
    if len(tok) <= 2 or tok in NAME_EXCLUDE:
        return False
    if re.fullmatch(r"\d+D(?:-\d+D)*", tok) or re.fullmatch(r"[A-Z]{2,}s", tok):
        return False
    if "-" in tok and all(re.fullmatch(r"[A-Z]?[a-z]+", part) for part in tok.split("-")):
        return False  # title-case compound such as "Per-Scene" or "Real-Time"
    letters = tok.replace("-", "")
    inner_upper = any(c.isupper() for c in letters[1:])
    lower_or_digit = any(c.islower() or c.isdigit() for c in letters)
    return (inner_upper and lower_or_digit) or (letters[0].isdigit() and any(c.isupper() for c in letters))


def experiment_spans(files, root):
    """{path: [(start, end)]}: the parts of each file inside a main-text Experiments section.
    An \\input file starts in the section that surrounds its \\input command."""
    appendix_paths = split_main(files, root)[0]
    inherited, spans = {}, {}
    for f in files:
        key = os.path.abspath(f.path)
        title, in_app = inherited.get(key, ("", False))
        marks = [(0, title, in_app or key in appendix_paths)]
        for m in re.finditer(r"\\section\*?\{([^}]*)\}|\\appendix\b", f.clean):
            in_app = marks[-1][2] or m.group(0).startswith("\\appendix")
            marks.append((m.start(), m.group(1) or "", in_app))
        for m in re.finditer(r"\\(?:input|include|subfile)\{([^}]+)\}", f.clean):
            child = resolve(root, m.group(1).strip(), ".tex") or resolve(os.path.dirname(key), m.group(1).strip(), ".tex")
            if child:
                state = [s for s in marks if s[0] <= m.start()][-1]
                inherited.setdefault(os.path.abspath(child), state[1:])
        ends = [s[0] for s in marks[1:]] + [len(f.clean)]
        spans[key] = [(a, b) for (a, title, app), b in zip(marks, ends) if not app and EXP_TITLE.search(title)]
    return spans


def named_mentions(f):
    """(position, name, cited, adjective) for every named item in the prose of f, outside the abstract.
    adjective: the name was used with a suffix, as in "NeRF-based"."""
    text = f.prose
    for m in re.finditer(r"\\begin\{abstract\}.*?\\end\{abstract\}", f.nonverbatim, re.S):
        text = text[:m.start()] + blank(text[m.start():m.end()]) + text[m.end():]
    for m in re.finditer(r"(?<![\\\w-])([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)(?![\w-])", text):
        tok = NAME_SUFFIXES.sub("", m.group(1))
        adjective = tok != m.group(1)
        if tok.endswith("s") and is_named(tok[:-1]) and not tok.isupper():
            tok = tok[:-1]
        if not is_named(tok) and tok.split("-")[0] in CITED_ACRONYMS:
            tok = tok.split("-")[0]  # ROUGE-L
        if is_named(tok):
            yield m.start(), tok, bool(CITED_AFTER.match(text, m.end())), adjective


def check_named_items(files, rep, exp_spans):
    """A4.6: cite a name at its first mention, and again at its first mention in Experiments.
    Returns the names cited somewhere, i.e. prior work."""
    mentions = [(f, *m) for f in files for m in named_mentions(f)]
    known = {tok for _, _, tok, cited, _ in mentions if cited}
    seen, seen_exp = set(), set()
    for f, pos, tok, cited, adjective in mentions:
        in_exp = any(a <= pos < b for a, b in exp_spans.get(os.path.abspath(f.path), ()))
        if tok not in seen:
            seen.add(tok)
            if in_exp:
                seen_exp.add(tok)
            if not cited:
                rep.add(f, pos, WARN, "A4.6",
                        f"'{tok}' has no citation at its first mention: cite it, or justify (ours / generic)")
        elif in_exp and tok not in seen_exp and not adjective:
            seen_exp.add(tok)
            if tok in known and not cited:
                rep.add(f, pos, WARN, "A4.6", f"'{tok}' is not cited at its first mention in Experiments: "
                        "cite it again here, even though it was cited earlier")
    return known


ROW_NOISE = re.compile(r"\\(?:toprule|midrule|bottomrule|hline|oursrow|addlinespace)\b(?:\[[^\]]*\])?|"
                       r"\\(?:cmidrule|cline)(?:\([^)]*\))?\{[^}]*\}|"
                       r"\\(?:rowcolor|cellcolor)(?:\[[^\]]*\])?\{[^}]*\}|\\multi(?:row|column)\{[^}]*\}\{[^}]*\}")


def check_table_citations(files, root, rep, known):
    """A4.6: a main-text table row that names prior work cites it in the row."""
    appendix_paths = split_main(files, root)[0]
    for f in files:
        if os.path.abspath(f.path) in appendix_paths:
            continue
        cut = re.search(r"\\appendix\b", f.nonverbatim)
        text = f.nonverbatim[:cut.start()] if cut else f.nonverbatim
        for tab in re.finditer(r"\\begin\{(" + TABULAR_ENVS + r")\}(.*?)\\end\{\1\}", text, re.S):
            body = tab.group(2)
            n_args = 2 if tab.group(1) in ("tabular*", "tabularx", "tabulary") else 1  # width, then column spec
            spec = re.match(r"\s*(?:\[[^\]]*\])?" + r"\s*\{(?:[^{}]|\{[^{}]*\})*\}" * n_args, body)
            start = spec.end() if spec else 0
            for sep in list(re.finditer(r"\\\\(?:\s*\[[^\]]*\])?", body)) + [None]:
                end = sep.start() if sep else len(body)
                cell = re.split(r"(?<!\\)&", body[start:end])[0]
                clean = re.sub(r"\\cite[a-zA-Z]*\*?(?:\s*\[[^\]]*\])*\s*\{[^}]*\}", " CITE ", ROW_NOISE.sub(" ", cell))
                clean = re.sub(r"\\[A-Za-z]+\*?|[{}~]", " ", clean)
                name = re.match(r"\s*([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)", clean)
                if name and name.group(1) in known and "CITE" not in clean:
                    pos = tab.start(2) + start + max(0, body[start:end].find(name.group(1)))
                    rep.add(f, pos, WARN, "A4.6", f"Table row names '{name.group(1)}' without a citation: "
                            f"cite it in the row ({name.group(1)}~\\cite{{...}})")
                start = sep.end() if sep else len(body)


METRICS = ["PSNR", "MS-SSIM", "SSIM", "LPIPS", "FID", "KID", "FVD", "CLIPScore", "CD", "EMD", "F-[Ss]core",
           "mIoU", "IoU", "mAP", "AP", "AUC", "NDS", "BLEU", "ROUGE(?:-[12L])?", "METEOR", "CIDEr", "SPICE",
           "BERTScore", "PPL", "EPE", "AbsRel", "RMSE", "MAE", "MSE", "ATE", "RPE", "NLL", "ECE"]
METRIC_RE = re.compile(r"(?<![\w-])(" + "|".join(METRICS) + r")(?![\w-])")
# Metrics with a source paper to cite (A4.9).
SOURCED_METRICS = {"SSIM", "MS-SSIM", "LPIPS", "FID", "KID", "FVD", "BLEU", "ROUGE", "ROUGE-1", "ROUGE-2", "ROUGE-L",
                   "METEOR", "CIDEr", "SPICE", "BERTScore", "CLIPScore", "NDS"}
DIRECTION = re.compile(r"\b(?:higher|lower|larger|smaller|better|worse|increas\w*|decreas\w*|maximi[sz]\w*|"
                       r"minimi[sz]\w*)\b|\\uparrow|\\downarrow|\u2191|\u2193", re.I)


def check_metrics(files, rep, exp_spans):
    """A4.9: every metric an Experiments table or figure reports is stated in the Experiments text before it."""
    in_float, in_text = {}, {}
    for i, f in enumerate(files):
        spans = exp_spans.get(os.path.abspath(f.path), [])
        floats = [(m.start(), m.end()) for m in
                  re.finditer(r"\\begin\{(table|figure)(\*?)\}.*?\\end\{\1\2\}", f.nonverbatim, re.S)]
        text = f.prose
        for a, b in floats:
            text = text[:a] + blank(text[a:b]) + text[b:]
        for a, b in spans:
            for fa, fb in floats:
                if a <= fa < b:
                    for m in METRIC_RE.finditer(f.keys_masked, fa, fb):
                        in_float.setdefault(m.group(1), (i, fa, f))
            for m in METRIC_RE.finditer(text, a, b):
                if m.group(1) not in in_text:
                    para_a = max(text.rfind("\n\n", a, m.start()), a)
                    para_b = text.find("\n\n", m.end(), b)
                    para = f.nonverbatim[para_a:para_b if para_b >= 0 else b]
                    in_text[m.group(1)] = (i, m.start(), f, bool(CITED_AFTER.match(text, m.end())),
                                           bool(DIRECTION.search(para)))
    for metric, (i, pos, f) in sorted(in_float.items(), key=lambda kv: kv[1][:2]):
        stated = in_text.get(metric)
        if stated is not None and stated[:2] < (i, pos):
            _, spos, sf, cited, direction = stated
            if metric in SOURCED_METRICS and not cited:
                rep.add(sf, spos, ERROR, "A4.9", f"Cite the source of '{metric}' where Experiments first explains it "
                        f"('{metric}~\\cite{{...}}')")
            if not direction:
                rep.add(sf, spos, WARN, "A4.9", f"Say which direction is better for '{metric}' where you explain it "
                        "(higher or lower)")
            continue
        if stated is None:
            rep.add(f, pos, ERROR, "A4.9", f"'{metric}' is reported here but the Experiments text never states it: "
                    "before the results, say what it measures, which direction is better, and cite its source")
        else:
            rep.add(f, pos, ERROR, "A4.9", f"'{metric}' is reported here before the Experiments text states it: "
                    "define it before the first result")


def check_references(files, missing_inputs, bibs, rep, min_refs):
    for f, pos, name in missing_inputs:
        rep.add(f, pos, WARN, "Input", f"Could not find \\input file '{name}'; it was not checked")
    labels, cited = set(), {}
    for f in files:
        labels.update(k.strip() for k in re.findall(r"\\label\{([^}]*)\}", f.nonverbatim))
    for f in files:
        for m in re.finditer(r"\\(?:ref|eqref|pageref|autoref|nameref|[cC]ref)\{([^}]*)\}", f.nonverbatim):
            for key in m.group(1).split(","):
                if key.strip() and key.strip() not in labels:
                    rep.add(f, m.start(), ERROR, "A1.5", f"\\ref to undefined label '{key.strip()}' prints ??")
        for m in re.finditer(r"\\(?:cite[a-zA-Z]*|autocite|parencite|textcite|footcite)\*?"
                             r"(?:\s*\[[^\]]*\])*\s*\{([^}]*)\}", f.nonverbatim):
            for key in m.group(1).split(","):
                if key.strip():
                    cited.setdefault(key.strip(), (f, m.start()))
    if bibs:
        bib_keys = set()
        for b in bibs:
            with open(b, encoding="utf-8", errors="replace") as fh:
                for typ, key in re.findall(r"@\s*(\w+)\s*\{\s*([^,\s]+)\s*,", fh.read()):
                    if typ.lower() not in ("string", "comment", "preamble"):
                        bib_keys.add(key)
        for key, (f, pos) in cited.items():
            if key not in bib_keys and key != "TODO":
                rep.add(f, pos, ERROR, "A1.5", f"Citation key '{key}' is not in the .bib (prints [?])")
    else:
        rep.add_plain("(bib)", WARN, "A1.5", "No .bib file found; citation keys were not checked")
    real = [k for k in cited if k != "TODO"]
    if len(real) < min_refs:
        rep.add_plain("(bib)", WARN, "A4.8",
                      f"{len(real)} distinct references cited (aim for >= {min_refs}); add only "
                      "verified real papers, never invented ones")
    if "TODO" in cited:
        f, pos = cited["TODO"]
        rep.add(f, pos, WARN, "A4.6", "\\cite{TODO} left for the author")


def check_figure_names(files, rep):
    fig = sum(len(re.findall(r"\bFigs?\.~?\\ref", f.prose)) for f in files)
    full = sum(len(re.findall(r"\bFigures?~?\\ref", f.prose)) for f in files)
    if fig and full:
        rep.add_plain("(paper)", WARN, "A4.1",
                      f"Mixed 'Fig.' ({fig}x) and 'Figure' ({full}x) before \\ref: choose one")


def check_review(files, rep):
    for f in files:
        for m in re.finditer(r"\\section\*?\{\s*Acknowledg", f.nonverbatim):
            rep.add(f, m.start(), ERROR, "A1.3", "Review version: remove the acknowledgments")
        for m in re.finditer(r"\\thanks\{", f.nonverbatim):
            rep.add(f, m.start(), ERROR, "A1.3", "Review version: remove \\thanks (identifying)")
        for m in re.finditer(r"(?:github\.com|gitlab\.com|huggingface\.co)/[\w.-]+", f.nonverbatim):
            rep.add(f, m.start(), WARN, "A1.3", "Review version: is this link identifying? Use an anonymous link")


APPENDIX_NAME = re.compile(r"supp|appendix", re.I)
REF_CMDS = r"\\(?:ref|eqref|pageref|autoref|nameref|[cC]ref)\{([^}]*)\}"


def split_main(files, root):
    """Main-text parts and Appendix labels. Text after \\appendix, files included after it,
    and files named like a supplement or appendix belong to the Appendix."""
    main = files[0]
    # Only included files are judged by name; the main file never is.
    appendix_paths = {os.path.abspath(f.path) for f in files[1:] if APPENDIX_NAME.search(os.path.basename(f.path))}
    cut = re.search(r"\\appendix\b", main.clean)
    if cut:
        for m in re.finditer(r"\\(?:input|include|subfile)\{([^}]+)\}", main.clean[cut.end():]):
            p = resolve(root, m.group(1).strip(), ".tex")
            if p:
                appendix_paths.add(os.path.abspath(p))
    main_texts, appendix_labels = [], set()
    for f in files:
        text = f.clean
        if os.path.abspath(f.path) in appendix_paths:
            appendix_labels.update(re.findall(r"\\label\{([^}]*)\}", text))
            continue
        k = re.search(r"\\appendix\b", text)
        if k:
            appendix_labels.update(re.findall(r"\\label\{([^}]*)\}", text[k.end():]))
            text = text[:k.start()]
        main_texts.append(text)
    return appendix_paths, main_texts, appendix_labels


def appendix_content(files, root, appendix_paths, sibling):
    """Words of prose and number of floats in the Appendix, wherever it lives."""
    parts, included = [], {os.path.abspath(f.path) for f in files}
    for f in files:
        if os.path.abspath(f.path) in appendix_paths:
            parts.append((f.prose, f.nonverbatim))
        else:
            k = re.search(r"\\appendix\b", f.clean)
            if k:
                parts.append((f.prose[k.end():], f.nonverbatim[k.end():]))
    for name in sibling:
        path = os.path.join(root, name)
        if os.path.abspath(path) not in included:
            try:
                g = File(path)
            except OSError:
                continue
            parts.append((g.prose, g.nonverbatim))
    words = sum(len(re.findall(r"[A-Za-z]{2,}", re.sub(r"\\[A-Za-z]+\*?", " ", prose))) for prose, _ in parts)
    floats = sum(len(re.findall(r"\\begin\{(?:figure|table)\*?\}", body)) for _, body in parts)
    return words, floats


def check_structure(files, root, rep, min_figures=3):
    """Appendix (Execution Rule 2), figure count (A2.7), closest-work plan, and white-space hints (A1.6, A1.1)."""
    appendix_paths, main_texts, appendix_labels = split_main(files, root)
    sibling = [n for n in os.listdir(root) if n.endswith(".tex") and APPENDIX_NAME.search(n)
               and n != os.path.basename(files[0].path)]
    if not (appendix_paths or sibling or any(re.search(r"\\appendix\b", f.clean) for f in files)):
        rep.add_plain("(paper)", ERROR, "Appendix", "No Appendix or Supplementary Material found: create it now, "
                      "following the template (Execution Rule 2)")
    else:
        keys = {k.strip() for t in main_texts for g in re.findall(REF_CMDS, t) for k in g.split(",")}
        named = any(re.search(r"\b(?:[Aa]ppendix|[Ss]upplement\w*|[Ss]upp\.)", mask_args(t)) for t in main_texts)
        if not (keys & appendix_labels or named):
            rep.add_plain("(paper)", ERROR, "Appendix", "The main text never points to the Appendix or Supplementary "
                          "Material: reference its important parts (Execution Rule 2)")
        words, floats = appendix_content(files, root, appendix_paths, sibling)
        if words < 150 and not floats:
            rep.add_plain("(paper)", WARN, "Appendix", f"The Appendix has only {words} word(s): move the detailed content "
                          "there (implementation details, per-scene results, more qualitative results, proofs, "
                          "reproduced closest-work analyses) and reference it from the main text")
    n_fig = sum(len(re.findall(r"\\begin\{figure\*?\}", t)) for t in main_texts)
    if n_fig < min_figures:
        rep.add_plain("(paper)", ERROR, "A2.7", f"The main text has {n_fig} figure(s): add at least {min_figures - n_fig} "
                      f"(e.g., teaser, pipeline, qualitative comparison, analysis), each with a key message in the "
                      "figure plan. Draw diagrams now; use a [TODO] placeholder where results are missing")
    extra = []
    for name in sibling:  # a separate Supplementary document, e.g. supp.tex next to main.tex
        try:
            extra.append(File(os.path.join(root, name)))
        except OSError:
            pass
    check_closest_plan(files, rep, extra)
    for f in files:
        for m in re.finditer(r"\\begin\{(?:figure|table)\*?\}\s*\[([^\]]*)\]", f.nonverbatim):
            spec = m.group(1)
            if "H" in spec or ("h" in spec and not re.search(r"[tbp]", spec)):
                rep.add(f, m.start(), WARN, "A1.6", f"[{spec}] placement often leaves white space: use [t]")
        for m in re.finditer(r"\\vspace\*?\{\s*-", f.nonverbatim):
            rep.add(f, m.start(), WARN, "A1.1", "Negative \\vspace squeezes the template's spacing: fix white space "
                    "by moving or resizing floats, or by rewording")


PLAN_HEAD = re.compile(r"^[ \t]*%[ \t]*Closest-work plan\b", re.I | re.M)
PLAN_PAPER = re.compile(r"^\s*%\s*\[?(?P<paper>[^\]:%()\n]+?)\]?\s*(?:\([^)]*\))?\s*:\s*(?P<nf>\d+)\s+fig\w*\b[^%\n]*?"
                        r"(?P<nt>\d+)\s+tab\w*\b", re.I)
PLAN_ITEM = re.compile(r"^\s*%\s*\[?(?P<paper>[^\]\n]+?)\]?\s+(?P<refs>(?:Supp\w*\.?\s*)?(?:Fig|Tab)\w*\.?\s*\d.*?)"
                       r"->\s*(?P<target>.*?)\s*$", re.I)
PLAN_REF = re.compile(r"(?P<supp>Supp\w*\.?\s*)?(?P<kind>Fig|Tab)\w*\.?\s*(?P<nums>\d+(?:\s*(?:-|--|\u2013|,|and|&)\s*\d+)*)",
                      re.I)
PLAN_LABEL = re.compile(r"(?<![\w\\])[A-Za-z][\w-]*:[\w.:-]*\w")
NO_DATA = re.compile(r"\b(?:no|missing|lack\w*|without|unavailable|not\s+(?:yet\s+)?(?:available|run|provided|given|done))\b"
                     r".*\b(?:data|results?|numbers?|experiments?|images?|renderings?|code|checkpoints?)\b", re.I)
FLOAT_ENVS = r"figure|table|algorithm|wrapfigure|wraptable|SCfigure"
EMPTY_REASON = r"n/?a|none|not (?:applicable|relevant|needed|necessary|important)|irrelevant|out of scope"


def plan_numbers(nums):
    """'2-4' -> 2, 3, 4; '5, 6' and '5 and 6' -> 5, 6."""
    out = set()
    for part in re.split(r"\s*(?:,|and|&)\s*", nums):
        span = re.split(r"\s*(?:--|-|\u2013)\s*", part)
        if all(s.isdigit() for s in span) and span:
            lo, hi = int(span[0]), int(span[-1])
            out.update(range(lo, hi + 1) if hi >= lo and hi - lo < 50 else [lo])
    return out


def paper_key(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def has_experiments(files):
    return any(re.search(r"\\section\*?\{[^}]*(?:Experiment|Evaluation|Results)", f.clean) for f in files)


def check_closest_plan(files, rep, extra=()):
    """Experiments Planning: the closest-work plan covers every figure and table of each closest paper,
    every reproduction exists in our paper (with [TODO] placeholders if its data is missing), and
    every skip has a reason."""
    if not has_experiments(files):
        return
    src = next((f for f in files if PLAN_HEAD.search(f.raw)), None)
    if src is None:
        rep.add_plain("(paper)", ERROR, "Experiments", "No '% Closest-work plan:' block: name the 1-3 closest papers "
                      "with their figure and table counts, and reproduce or skip each figure and table "
                      "(references/experiments.md, Experiment Planning)")
        return
    head_pos = PLAN_HEAD.search(src.raw).start()
    pos = src.raw.find("\n", head_pos) + 1 or len(src.raw)
    lines = []
    for line in src.raw[pos:].split("\n"):
        if not line.lstrip().startswith("%"):
            break
        lines.append((pos, line))
        pos += len(line) + 1
    docs = list(files) + [g for g in extra if os.path.abspath(g.path) not in {os.path.abspath(f.path) for f in files}]
    float_labels = {l.strip() for f in docs
                    for m in re.finditer(r"\\begin\{(" + FLOAT_ENVS + r")\*?\}(.*?)\\end\{\1\*?\}", f.nonverbatim, re.S)
                    for l in re.findall(r"\\label\{([^}]*)\}", m.group(2))}
    papers, covered, names = {}, {}, {}
    for at, line in lines:
        head, item = PLAN_PAPER.match(line), PLAN_ITEM.match(line)
        if item and "->" in line:
            paper = item.group("paper").strip()
            key = paper_key(paper)
            names.setdefault(key, (paper, at))
            refs = [(r.group("kind")[0].upper(), n) for r in PLAN_REF.finditer(item.group("refs")) if not r.group("supp")
                    for n in plan_numbers(r.group("nums"))]
            covered.setdefault(key, set()).update(refs)
            what = f"{paper} {item.group('refs').split('(')[0].strip()}"
            target = item.group("target")
            skip = re.match(r"(?:\w+\s+)?skipped\b[^:]*:?\s*(.*)$", target, re.I)
            if skip:
                reason = skip.group(1).strip().rstrip(".")
                if len(reason.split()) < 2 or re.fullmatch(EMPTY_REASON, reason, re.I):
                    rep.add(src, at, ERROR, "Experiments", f"{what} is skipped without a reason: state why the "
                            "analysis does not apply to our setting, or reproduce it")
                elif NO_DATA.search(reason):
                    rep.add(src, at, ERROR, "Experiments", f"{what}: missing data is not a reason to skip. Create "
                            "the figure or table now with [TODO] placeholders and list the experiment to run")
                continue
            labels = [l for l in PLAN_LABEL.findall(target) if not re.match(r"(?:done|todo|partly|shows)\b", l, re.I)]
            if not labels:
                rep.add(src, at, ERROR, "Experiments", f"{what}: name the label of our figure or table "
                        "('-> tab:main: done') or write '-> skipped: <reason>'")
            for label in labels:
                if label not in float_labels:
                    rep.add(src, at, ERROR, "Experiments", f"{what} -> {label}: no figure or table has this label. "
                            "Create it now, with [TODO] cells or a placeholder where data is missing")
        elif head:
            paper = head.group("paper").strip()
            papers[paper_key(paper)] = (paper, int(head.group("nf")), int(head.group("nt")), at)
    if not papers:
        rep.add(src, head_pos, ERROR, "Experiments", "The plan gives no figure and table counts: add "
                "'% <paper> (<authors, venue>): N figures, M tables' for each closest paper, then cover each "
                "of its figures and tables")
    for key, (name, nf, nt, at) in papers.items():
        listed = covered.get(key, set())
        missing = [f"Fig. {k}" for k in range(1, nf + 1) if ("F", k) not in listed]
        missing += [f"Tab. {k}" for k in range(1, nt + 1) if ("T", k) not in listed]
        if missing:
            rep.add(src, at, ERROR, "Experiments", f"{name}: {', '.join(missing)} not in the plan. Reproduce each "
                    "one, or skip it with a reason")
    for key, (name, at) in names.items():
        if key not in papers:
            rep.add(src, at, ERROR, "Experiments", f"'{name}' has no count line: add "
                    f"'% {name} (<authors, venue>): N figures, M tables'")


def check_figure_use(files, rep):
    """A2.1: every figure and table is discussed in the text."""
    refs = {k.strip() for f in files for g in re.findall(REF_CMDS, f.nonverbatim) for k in g.split(",")}
    for f in files:
        for m in re.finditer(r"\\begin\{(figure|table)(\*?)\}(.*?)\\end\{\1\2\}", f.nonverbatim, re.S):
            kind, body = m.group(1), m.group(3)
            labels = {l.strip() for l in re.findall(r"\\label\{([^}]*)\}", body)}
            if not labels:
                rep.add(f, m.start(), WARN, "A2.1", f"This {kind} has no \\label, so the text cannot discuss it")
            elif not labels & refs:
                rep.add(f, m.start(), WARN, "A2.1", f"The {kind} '{sorted(labels)[0]}' is never referenced: "
                        "analyze its conclusion in the text, or cut it")


PLAN_START = re.compile(r"^[ \t]*%[ \t]*Figure plan\b", re.I | re.M)
PLAN_LINE = re.compile(r"^\s*%\s*(\S+?):\s+(.*?)\s*(?:->|\u2192)\s*(.+?)\s*$")
# Form names the figure plan may use. Earlier kinds win; teaser, diagram, and
# qualitative grid describe the whole figure, the others can share a figure (panels).
FORM_KINDS = [
    ("teaser", r"\bteasers?\b", True),
    ("diagram", r"\b(?:diagrams?|pipelines?|overviews?|architectures?|frameworks?|flowcharts?|schematics?)\b", True),
    ("qualitative grid", r"\b(?:qualitative|visual comparisons?|renderings?|image grids?|zoom-ins?|insets?|crops?)\b", True),
    ("distribution plot", r"\b(?:cumulative(?:\s+[\w-]+){0,2}\s+curves?|cumulative|cdfs?|histograms?|"
                          r"box\s*plots?|violin\s*plots?)\b", False),
    ("map", r"\b(?:heat\s*maps?|maps?)\b", False),
    ("scatter plot", r"\bscatter(?:\s*plots?)?\b", False),
    ("bar chart", r"(?<!error\s)\b(?:bar\s+charts?|bars?)\b", False),
    ("line plot", r"\b(?:line\s+plots?|lines?|curves?)\b", False),
    ("table", r"\btables?\b", False),
]


def form_kinds(form):
    text, kinds = form.lower(), set()
    for kind, pat, whole in FORM_KINDS:
        if re.search(pat, text):
            kinds.add(kind)
            if whole:
                break
            text = re.sub(pat, " ", text)
    return kinds


def read_plan(files):
    """The '% Figure plan' block as {label: (message, form, kinds)}; None if there is none."""
    for f in files:
        m = PLAN_START.search(f.raw)
        if not m:
            continue
        plan = {}
        for line in f.raw[m.end():].split("\n")[1:]:
            if not line.lstrip().startswith("%"):
                break
            p = PLAN_LINE.match(line)
            if p:
                plan[p.group(1)] = (p.group(2), p.group(3), form_kinds(p.group(3)))
        return plan
    return None


TABLE_TYPE = re.compile(r"\b(?:SOTA|state[- ]of[- ]the[- ]art|main comparison|plug-?in|add-?on|ablation|efficiency|"
                        r"cost|runtime|breakdown|per-(?:class|category|scene|dataset)|generali[sz]ation|cross-dataset|"
                        r"robustness|property|capabilit\w*|sensitivity|hyperparameter|user study|preference|"
                        r"statistics)\b", re.I)


def check_figure_plan(files, root, rep, plan):
    """A2.1: every main-text figure and table is in the figure plan. A2.7: at most 2 figures per form.
    A2.8: each table names its type."""
    figs, tables = [], []
    for t in split_main(files, root)[1]:
        for m in re.finditer(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", t, re.S):
            labels = [l.strip() for l in re.findall(r"\\label\{([^}]*)\}", m.group(2))]
            if labels:
                (figs if m.group(1) == "figure" else tables).append(labels)
    if not figs and not tables:
        return
    if plan is None:
        rep.add_plain("(paper)", ERROR, "A2.1", "No '% Figure plan' block: before drawing, write one line per figure "
                      "and table, '% label: message -> form' (references/figure-table-styles.md)")
        return
    missing = [labels[-1] for labels in figs + tables if not any(l in plan for l in labels)]
    if missing:
        rep.add_plain("(paper)", ERROR, "A2.1", f"The figure plan has no line for {', '.join(missing)}: "
                      "add '% label: message -> form'")
    for labels in tables:
        entry = next((plan[l] for l in labels if l in plan), None)
        if entry and not TABLE_TYPE.search(entry[1]):
            rep.add_plain("(paper)", WARN, "A2.8", f"The plan line of {labels[-1]} names no table type: pick one from "
                          "references/table-types.md (SOTA comparison, plug-in, ablation, efficiency, ...)")
    by_kind = {}
    for labels in figs:
        entry = next((plan[l] for l in labels if l in plan), None)
        for kind in (entry[2] if entry else set()) - {"table"}:
            by_kind.setdefault(kind, []).append(labels[-1])
    for kind, labs in sorted(by_kind.items()):
        if len(labs) > 2:
            rep.add_plain("(paper)", WARN, "A2.7", f"{len(labs)} main-text figures are {kind}s ({', '.join(labs)}): "
                          "use one form for at most 2; merge related ones into one multi-panel figure, "
                          "or move one to the Appendix")


def main_parts(files, root):
    """(file, start, end) spans of the main text (before the Appendix) in each file."""
    appendix_paths = split_main(files, root)[0]
    out = []
    for f in files:
        if os.path.abspath(f.path) in appendix_paths:
            continue
        cut = re.search(r"\\appendix\b", f.clean)
        out.append((f, 0, cut.start() if cut else len(f.clean)))
    return out


def check_significance(files, root, rep):
    """B4.5: significance gets one sentence in the main text; the details go to the Appendix."""
    total, first = 0, None
    for f, a, b in main_parts(files, root):
        floats = [(m.start(), m.end()) for m in re.finditer(r"\\begin\{(table|figure)(\*?)\}.*?\\end\{\1\2\}",
                                                            f.nonverbatim[:b], re.S)]
        for fa, fb in floats:
            for m in re.finditer(r"\\begin\{(" + TABULAR_ENVS + r")\}.*?\\end\{\1\}", f.nonverbatim[fa:fb], re.S):
                hit = SIGNIFICANCE.search(m.group(0))
                if hit:
                    rep.add(f, fa + m.start() + hit.start(), WARN, "B4.5", "Significance columns or marks in a "
                            "main-text table: report the mean (and at most +- std), and put the tests in the Appendix")
        prose = f.prose
        for fa, fb in floats:  # captions and tables are checked on their own
            prose = prose[:fa] + blank(prose[fa:fb]) + prose[fb:]
        for para in re.finditer(r"(?:(?!\n[ \t]*\n).)+", prose[a:b], re.S):
            hits = list(SIGNIFICANCE.finditer(para.group(0)))
            total += len(hits)
            if hits and first is None:
                first = (f, a + para.start())
            if len(hits) >= 2:
                rep.add(f, a + para.start() + hits[0].start(), WARN, "B4.5", "This paragraph discusses significance "
                        "at length: one sentence is enough (std over runs, or 'tests in Appendix X'), the rest goes "
                        "to the Appendix")
    if total >= 4 and first:
        rep.add(*first, WARN, "B4.5", f"The main text mentions significance {total} times: keep one sentence and move "
                "the details to the Appendix")


RUN_IN_HEAD = re.compile(r"^\s*(?:\\noindent\s*)?\\(?:paragraph\*?|subparagraph\*?|textbf)\s*\{")
RUN_IN_EXEMPT = re.compile(r"Related|Background|Prior|Preliminar", re.I)


def check_run_in_heads(files, root, rep):
    """B4.6: bold run-in headings sparingly; not on every paragraph (Related Work topics are exempt)."""
    for f, a, b in main_parts(files, root):
        text = re.sub(r"(\\paragraph\*?\{[^}]*\})[ \t]*\n[ \t]*\n", lambda m: m.group(1) + " " * (len(m.group(0)) -
                      len(m.group(1))), f.nonverbatim[:b])
        sections = [(m.start(), m.group(1)) for m in re.finditer(r"\\section\*?\{([^}]*)\}", text)]
        for k, (s, title) in enumerate(sections):
            if s < a or RUN_IN_EXEMPT.search(title):
                continue
            e = sections[k + 1][0] if k + 1 < len(sections) else len(text)
            body = mask(text[s:e], r"\\begin\{(" + FLOAT_ENVS + r"|" + MATH_ENVS + r")(\*?)\}.*?\\end\{\1\2\}")
            paras = [re.sub(r"^(?:\s*\\(?:(?:sub)*section\*?\{[^}]*\}|label\{[^}]*\}))+", "", p)
                     for p in re.split(r"\n[ \t]*\n", body)]
            paras = [p for p in paras if len(re.findall(r"[A-Za-z]{2,}", re.sub(r"\\[A-Za-z]+\*?(?:\{[^}]*\})?",
                                                                                 " ", p))) >= 8]
            heads = [p for p in paras if RUN_IN_HEAD.match(p)]
            if len(heads) >= 3 and len(heads) >= 0.6 * len(paras):
                rep.add(f, s, WARN, "B4.6", f"{len(heads)} of {len(paras)} paragraphs in '{title}' open with a bold "
                        "heading: keep them only where the reader needs to find a part again")


SOTA_LINE = re.compile(r"^[ \t]*%[ \t]*Latest SOTA\b[^:\n]*:\s*(?P<entry>[^\n]*?)\s*(?:->|\u2192)\s*(?P<target>[^\n]*?)"
                       r"\s*$", re.I | re.M)


def float_bodies(docs):
    """{label: float body} for every figure, table, and algorithm."""
    out = {}
    for f in docs:
        for m in re.finditer(r"\\begin\{(" + FLOAT_ENVS + r")\*?\}(.*?)\\end\{\1\*?\}", f.nonverbatim, re.S):
            for l in re.findall(r"\\label\{([^}]*)\}", m.group(2)):
                out[l.strip()] = m.group(2)
    return out


def check_latest_sota(files, rep, exp_spans, extra=()):
    """Experiments: the main comparison includes the latest state of the art, and the text discusses it."""
    if not has_experiments(files):
        return
    lines = [(f, m) for f in files for m in SOTA_LINE.finditer(f.raw)]
    if not lines:
        rep.add_plain("(paper)", ERROR, "SOTA", "No '% Latest SOTA:' line: search for the strongest method on your "
                      "main benchmark from the past 12 months (top venues, arXiv), compare with it in the main table, "
                      "and discuss it (references/experiments.md)")
        return
    bodies = float_bodies(list(files) + list(extra))
    exp_text = " ".join(f.prose[a:b] for f in files for a, b in exp_spans.get(os.path.abspath(f.path), ()))
    for f, m in lines:
        name = re.split(r"\s*\(", m.group("entry"))[0].strip().strip("[]")
        target = m.group("target")
        skip = re.match(r"not comparable\b[^:]*:?\s*(.*)$", target, re.I)
        if not name:
            rep.add(f, m.start(), ERROR, "SOTA", "Name the method: '% Latest SOTA: <method> (<venue year>) -> "
                    "tab:main: done'")
            continue
        if skip:
            reason = skip.group(1).strip()
            if len(reason.split()) < 3 or NO_DATA.search(reason) or re.search(r"\bcode\b", reason, re.I):
                rep.add(f, m.start(), ERROR, "SOTA", f"'{name}' is not compared, and the reason does not hold: if "
                        "it has results on your benchmark, use its reported numbers and mark them")
            continue
        labels = [l for l in PLAN_LABEL.findall(target) if not re.match(r"(?:done|todo|partly|shows)\b", l, re.I)]
        if not labels:
            rep.add(f, m.start(), ERROR, "SOTA", f"Name the table that compares with '{name}' ('-> tab:main: done')")
        token = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")
        for label in labels:
            if label not in bodies:
                rep.add(f, m.start(), ERROR, "SOTA", f"'{label}' does not exist: add the comparison with '{name}'")
            elif not token.search(bodies[label]):
                rep.add(f, m.start(), ERROR, "SOTA", f"'{label}' has no row for '{name}': add it, with [TODO] cells "
                        "if its numbers are missing")
        if not token.search(exp_text):
            rep.add(f, m.start(), ERROR, "SOTA", f"The Experiments text never discusses '{name}': say how ours "
                    "compares with it and why")


IMAGE_EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")


def figure_files(docs, root):
    """Every image file the paper includes: [(file, position, name, path or None)]."""
    dirs = [root]
    for f in docs:
        for m in re.finditer(r"\\graphicspath\s*\{((?:\s*\{[^}]*\})+)\s*\}", strip_comments(f.raw)):
            dirs += [os.path.join(root, d) for d in re.findall(r"\{([^}]*)\}", m.group(1))]
    out = []
    for f in docs:
        for m in re.finditer(r"\\includegraphics\*?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", f.nonverbatim):
            name = m.group(1).strip()
            if name.startswith("example-image"):
                continue
            path = None
            for d in dirs:
                for cand in [name] + [name + e for e in IMAGE_EXTS]:
                    p = os.path.join(d, cand)
                    if os.path.isfile(p):
                        path = p
                        break
                if path:
                    break
            out.append((f, m.start(), name, path))
    return out


def check_figure_qa(files, root, rep, extra=()):
    """A2.9: every included image was checked with figure_qa.py after its last change, with no errors left."""
    import hashlib
    import json
    seen = set()
    for f, pos, name, path in figure_files(list(files) + list(extra), root):
        if path is None:
            rep.add(f, pos, ERROR, "A1.5", f"Image '{name}' not found: LaTeX stops here. Create it, or a placeholder")
            continue
        key = os.path.abspath(path)
        if key in seen:
            continue
        seen.add(key)
        rel = os.path.relpath(path, root)
        try:
            with open(path, "rb") as fh:
                digest = hashlib.sha1(fh.read()).hexdigest()
            with open(os.path.join(os.path.dirname(path), ".figure-qa", "record.json"), encoding="utf-8") as fh:
                entry = json.load(fh).get(os.path.basename(path))
        except (OSError, ValueError):
            entry = None
        if not entry or entry.get("sha1") != digest:
            rep.add(f, pos, ERROR, "A2.9", f"'{rel}' was not checked after its last change: run python3 <this skill's "
                    "directory>/scripts/figure_qa.py on the script that draws it (or on the file), fix what it "
                    "reports, and look at its preview")
            continue
        issues = entry.get("issues", [])
        errors = [msg for level, msg in issues if level == ERROR]
        warns = [msg for level, msg in issues if level == WARN]
        if errors:
            rep.add(f, pos, ERROR, "A2.9", f"'{rel}': {errors[0]}" + (f" (+{len(errors) - 1} more)" if len(errors) > 1
                                                                       else ""))
        if warns:
            rep.add(f, pos, WARN, "A2.9", f"'{rel}': {warns[0]}" + (f" (+{len(warns) - 1} more)" if len(warns) > 1
                                                                    else ""))


def check_log(path, rep):
    with open(path, encoding="utf-8", errors="replace") as fh:
        log = fh.read()
    for m in re.finditer(r"LaTeX Warning: `h' float specifier changed to `ht'[^\n]*", log):
        rep.add_plain(path, WARN, "A1.6", "A float with [h] was moved: use [t] so it does not leave white space")
    for m in re.finditer(r"(?:LaTeX|Package \w+) Warning: (Reference|Citation) [`']([^']*)' "
                         r"on page (\d+) undefined", log):
        rep.add_plain(path, ERROR, "A1.5", f"{m.group(1)} '{m.group(2)}' undefined on page {m.group(3)}")
    small = 0
    for m in re.finditer(r"Overfull \\[hv]box \(([\d.]+)pt too (?:wide|high)\)(?:[^\n]*?lines? ([\d-]+))?", log):
        if float(m.group(1)) > 1.0:
            where = f" at source lines {m.group(2)}" if m.group(2) else ""
            rep.add_plain(path, ERROR, "Build", f"Overfull box {m.group(1)}pt{where}: reword or resize")
        else:
            small += 1
    if small:
        rep.add_plain(path, WARN, "Build", f"{small} overfull boxes under 1pt (usually invisible)")
    for m in re.finditer(r"LaTeX Warning: Float too large[^\n]*", log):
        rep.add_plain(path, WARN, "Build", m.group(0).strip())


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return None


def check_pdf(path, review, rep):
    if shutil.which("pdffonts"):
        out = run(["pdffonts", path]) or ""
        for line in out.splitlines()[2:]:
            cols = line.split()
            if "Type 3" in line:
                rep.add_plain(path, ERROR, "A1.4", f"Type 3 font: {cols[0]} (set pdf.fonttype 42 in Matplotlib)")
            m = re.search(r"\s(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
            if m and m.group(1) == "no":
                rep.add_plain(path, ERROR, "A1.4", f"Font not embedded: {cols[0]}")
    else:
        rep.add_plain(path, WARN, "A1.4", "pdffonts not installed: fonts not checked")
    if shutil.which("pdftotext"):
        text = run(["pdftotext", "-layout", path, "-"]) or ""
        for token in ("??", "[?]"):
            n = text.count(token)
            if n:
                rep.add_plain(path, ERROR, "A1.5", f"'{token}' appears {n}x in the PDF")
    else:
        rep.add_plain(path, WARN, "A1.5", "pdftotext not installed: PDF not searched for ?? / [?]")
    if review and shutil.which("pdfinfo"):
        info = run(["pdfinfo", path]) or ""
        m = re.search(r"^Author:\s*(\S.*)$", info, re.M)
        if m:
            rep.add_plain(path, ERROR, "A1.3", f"Review version: PDF metadata names an author ({m.group(1).strip()})")


VENUE_COMMENT = re.compile(r"^[ \t]*%[ \t]*Venue[ \t]*:[ \t]*(\S[^\n]*?)\s*$", re.I | re.M)
# Template packages and classes that name the venue (fullmatch, case-insensitive).
VENUE_TEMPLATES = [
    (r"cvpr", "CVPR"), (r"iccv", "ICCV"), (r"eccv\w*", "ECCV"), (r"wacv", "WACV"),
    (r"neurips_\d{4}|nips_?\d{4}", "NeurIPS"), (r"iclr\d{4}_conference", "ICLR"), (r"icml\d{4}", "ICML"),
    (r"acl|acl_natbib|acl\d{4}|naaclhlt\d{4}|emnlp\d{4}", "ACL, EMNLP, or NAACL"), (r"aaai\d{2}", "AAAI"),
    (r"ijcai\d{2}", "IJCAI"), (r"colm\d{4}_conference", "COLM"), (r"tmlr", "TMLR"), (r"jmlr2e", "JMLR"),
    (r"corl_\d{4}", "CoRL"), (r"acmart", "an ACM venue"), (r"IEEEtran", "an IEEE venue"),
    (r"llncs", "a Springer LNCS venue"), (r"elsarticle", "an Elsevier journal")]


def check_venue(files, rep):
    """Execution Rule 1: the venue is recorded, or its template is loaded. Returns its name or None."""
    for f in files:
        m = VENUE_COMMENT.search(f.raw)
        if m:
            return m.group(1)
    code = strip_comments(files[0].raw)
    for cmd in re.finditer(r"\\(?:documentclass|usepackage)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", code):
        for name in (n.strip() for n in cmd.group(1).split(",")):
            for pat, venue in VENUE_TEMPLATES:
                if re.fullmatch(pat, name, re.I):
                    return f"{venue}, from {name}"
    rep.add_plain("(paper)", ERROR, "Venue", "Venue not recorded: if the user has not named it, ask (ask-user tool); "
                  "then record it as '% Venue: <name> <year>' at the top of the main .tex file and use its template")
    return None


def required_block(rep, venue, has_exp, min_figures):
    """The pass/fail list of 'Required in Every Paper' in SKILL.md, for the agent to copy into its reply."""
    groups = [
        ("Venue and template", lambda rule, msg: rule == "Venue"),
        ("Appendix or Supplementary Material", lambda rule, msg: rule == "Appendix"),
        ("Closest-work plan", lambda rule, msg: rule == "Experiments"),
        ("Latest SOTA compared and discussed", lambda rule, msg: rule == "SOTA"),
        (f"At least {min_figures} main-text figures; every figure and table in the plan",
         lambda rule, msg: (rule == "A2.7" and "figure(s)" in msg) or (rule == "A2.1" and "plan" in msg.lower())),
        ("Every image checked with figure_qa.py", lambda rule, msg: rule == "A2.9"),
        ("Metrics explained and cited before the results", lambda rule, msg: rule == "A4.9")]
    items = sorted(set(rep.items), key=lambda i: (i[0], i[1]))
    lines = ["Required in Every Paper (SKILL.md); copy this list into your reply:"]
    for k, (name, match) in enumerate(groups, 1):
        hits = [i for i in items if match(i[3], i[4])]
        errors = [i for i in hits if i[2] == ERROR]
        if k in (3, 4, 7) and not has_exp:
            status = "n/a (no Experiments section yet)"
        elif errors:
            head = errors[0][4].split(": ")[0]
            if k == 3 and not head.startswith("No '%"):
                head = f"{len(errors)} gap(s) in the plan"
            elif len(errors) > 1:
                head += f" (+{len(errors) - 1} more)"
            status = f"FAIL: {head}"
        elif hits:
            status = f"WARN: {hits[0][4].split(': ')[0]}"
        else:
            status = "PASS" + (f" ({venue})" if k == 1 and venue else "")
        lines.append(f"  {k}. {name}: {status}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", nargs="+", help="main .tex file (and any extra .tex files)")
    ap.add_argument("--bib", action="append", default=[], help=".bib file (default: from \\bibliography)")
    ap.add_argument("--log", help="LaTeX .log file from the latest compile")
    ap.add_argument("--pdf", help="compiled PDF")
    ap.add_argument("--review", action="store_true", help="anonymous review version: check A1.3")
    ap.add_argument("--max-words", type=int, default=25, help="B2.1 sentence length limit (default 25)")
    ap.add_argument("--min-refs", type=int, default=35, help="A4.8 reference target (default 35)")
    ap.add_argument("--min-figures", type=int, default=3, help="A2.7 figures in the main text (default 3)")
    args = ap.parse_args(argv)
    for p in args.tex + args.bib + [x for x in (args.log, args.pdf) if x]:
        if not os.path.isfile(p):
            print(f"check_tex.py: no such file: {p}", file=sys.stderr)
            return 2

    files, missing, root = collect_files(args.tex)
    bibs = list(args.bib)
    if not bibs:
        for f in files:
            for m in re.finditer(r"\\(?:bibliography|addbibresource(?:\s*\[[^\]]*\])?)\{([^}]+)\}", f.clean):
                for name in m.group(1).split(","):
                    b = resolve(root, name.strip(), ".bib")
                    if b and b not in bibs:
                        bibs.append(b)

    rep = Report()
    plan = read_plan(files)
    for f in files:
        check_citations(f, rep)
        check_prose(f, rep, args.max_words)
        check_math(f, rep)
        check_floats(f, rep, plan)
        for m in re.finditer(r"[\uff0c\u3002\uff1a\uff1b\uff01\uff1f\uff08\uff09\u3010\u3011\u300a\u300b\u3001]",
                             f.nonverbatim):
            rep.add(f, m.start(), ERROR, "A4.4", "Full-width punctuation: use ASCII , . : ; ( )")
        for m in re.finditer(EM_DASH, f.whole):
            rep.add(f, m.start(), ERROR, "B3.7",
                    "Em dash: use a comma, a colon, parentheses, or a new sentence (in a table cell, use - or N/A)")
    exp_spans = experiment_spans(files, root)
    known = check_named_items(files, rep, exp_spans)
    check_table_citations(files, root, rep, known)
    check_metrics(files, rep, exp_spans)
    check_references(files, missing, bibs, rep, args.min_refs)
    check_figure_names(files, rep)
    check_structure(files, root, rep, args.min_figures)
    check_figure_use(files, rep)
    check_figure_plan(files, root, rep, plan)
    check_significance(files, root, rep)
    check_run_in_heads(files, root, rep)
    supp = [File(os.path.join(root, n)) for n in os.listdir(root) if n.endswith(".tex") and APPENDIX_NAME.search(n)
            and os.path.abspath(os.path.join(root, n)) not in {os.path.abspath(f.path) for f in files}]
    check_latest_sota(files, rep, exp_spans, supp)
    check_figure_qa(files, root, rep, supp)
    venue = check_venue(files, rep)
    if args.review:
        check_review(files, rep)
    if args.log:
        check_log(args.log, rep)
    if args.pdf:
        check_pdf(args.pdf, args.review, rep)

    order = {ERROR: 0, WARN: 1}
    for path, line, level, rule, msg, snip in sorted(set(rep.items), key=lambda i: (i[0], i[1], order[i[2]], i[3])):
        loc = f"{path}:{line}" if line else path
        print(f"{loc}: {level} [{rule}] {msg}" + (f" | {snip}" if snip else ""))
    checked = ", ".join(os.path.relpath(f.path) for f in files)
    print(f"\nChecked: {checked}" + (f" (+ {', '.join(os.path.relpath(b) for b in bibs)})" if bibs else ""))
    print(required_block(rep, venue, has_experiments(files), args.min_figures))
    print(f"== {rep.count(ERROR)} errors, {rep.count(WARN)} warnings ==")
    print("Fix every ERROR. Fix every WARN, or justify it in your reply.")
    print(f"Not checked by this script, so reread the changed text for: {NOT_CHECKED}.")
    return 1 if rep.count(ERROR) else 0


if __name__ == "__main__":
    sys.exit(main())
