#!/usr/bin/env python3
r"""Check a LaTeX paper against the mechanical Writing Rules in SKILL.md.

Usage:
  python3 check_tex.py main.tex [more.tex ...] [--bib refs.bib] [--log main.log]
                       [--pdf main.pdf] [--review] [--max-words 25] [--min-refs 35]

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

NOT_CHECKED = ("A1.1, A1.2, A2.1-A2.3, A2.5, A3.1, B1, B2.2, B4.2, B4.4 "
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
     r"widespread|tremendous|great) (?:attention|interest))"),
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


def check_floats(f, rep):
    for m in re.finditer(r"\\begin\{(table|figure)(\*?)\}(.*?)\\end\{\1\2\}", f.nonverbatim, re.S):
        env, body, off = m.group(1), m.group(3), m.start(3)
        caps = list(re.finditer(r"\\caption(?:\[[^\]]*\])?\{", body))
        for c in caps:
            if not re.match(r"\s*(?:\\(?:small|footnotesize|scriptsize|normalsize)\s*)?\\textbf\{",
                            body[c.end():]):
                rep.add(f, off + c.start(), ERROR, "A2.4",
                        "Start the caption with a bold one-line takeaway (\\caption{\\textbf{...} ...})")
        if env == "table":
            tab = re.search(r"\\begin\{(?:" + TABULAR_ENVS + r")\}", body)
            if caps and tab and caps[0].start() > tab.start():
                rep.add(f, off + caps[0].start(), ERROR, "A2.4", "Put the table caption above the table")
            for t in re.finditer(r"\\begin\{(?:" + TABULAR_ENVS + r")\}((?:\s*\{[^{}]*\}){1,2})", body):
                if "|" in t.group(1):
                    rep.add(f, off + t.start(), ERROR, "Tables",
                            "No vertical rules in the column spec (see references/experiments.md)")
            hl = list(re.finditer(r"\\(?:hline|cline)\b", body))
            if hl:
                rep.add(f, off + hl[0].start(), ERROR, "Tables",
                        f"{len(hl)} x \\hline/\\cline: use \\toprule, \\midrule, \\cmidrule, \\bottomrule")
        else:
            inc = list(re.finditer(r"\\includegraphics|\\begin\{tikzpicture\}", body))
            if caps and inc and caps[-1].start() < inc[-1].start():
                rep.add(f, off + caps[-1].start(), ERROR, "A2.4", "Put the figure caption below the figure")


def is_named(tok):
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


def check_named_items(files, rep):
    seen = set()
    for f in files:
        text = f.prose
        for m in re.finditer(r"\\begin\{abstract\}.*?\\end\{abstract\}", f.nonverbatim, re.S):
            text = text[:m.start()] + blank(text[m.start():m.end()]) + text[m.end():]
        for m in re.finditer(r"(?<![\\\w-])([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)(?![\w-])", text):
            tok = NAME_SUFFIXES.sub("", m.group(1))
            if tok.endswith("s") and is_named(tok[:-1]) and not tok.isupper():
                tok = tok[:-1]
            if not is_named(tok) or tok in seen:
                continue
            seen.add(tok)
            after = text[m.end():m.end() + 60]
            if not re.match(r"(?:\s+(?:" + GENERIC_NOUNS + r"))?\s*\)?\s*~?\s*\\cite[a-zA-Z]*", after):
                rep.add(f, m.start(), WARN, "A4.6",
                        f"'{tok}' has no citation at its first mention: cite it, or justify (ours / generic)")


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


def check_log(path, rep):
    with open(path, encoding="utf-8", errors="replace") as fh:
        log = fh.read()
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", nargs="+", help="main .tex file (and any extra .tex files)")
    ap.add_argument("--bib", action="append", default=[], help=".bib file (default: from \\bibliography)")
    ap.add_argument("--log", help="LaTeX .log file from the latest compile")
    ap.add_argument("--pdf", help="compiled PDF")
    ap.add_argument("--review", action="store_true", help="anonymous review version: check A1.3")
    ap.add_argument("--max-words", type=int, default=25, help="B2.1 sentence length limit (default 25)")
    ap.add_argument("--min-refs", type=int, default=35, help="A4.8 reference target (default 35)")
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
    for f in files:
        check_citations(f, rep)
        check_prose(f, rep, args.max_words)
        check_math(f, rep)
        check_floats(f, rep)
        for m in re.finditer(r"[\uff0c\u3002\uff1a\uff1b\uff01\uff1f\uff08\uff09\u3010\u3011\u300a\u300b\u3001]",
                             f.nonverbatim):
            rep.add(f, m.start(), ERROR, "A4.4", "Full-width punctuation: use ASCII , . : ; ( )")
        for m in re.finditer(EM_DASH, f.whole):
            rep.add(f, m.start(), ERROR, "B3.7",
                    "Em dash: use a comma, a colon, parentheses, or a new sentence (in a table cell, use - or N/A)")
    check_named_items(files, rep)
    check_references(files, missing, bibs, rep, args.min_refs)
    check_figure_names(files, rep)
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
    print(f"== {rep.count(ERROR)} errors, {rep.count(WARN)} warnings ==")
    print("Fix every ERROR. Fix every WARN, or justify it in your reply.")
    print(f"Not checked by this script, so reread the changed text for: {NOT_CHECKED}.")
    return 1 if rep.count(ERROR) else 0


if __name__ == "__main__":
    sys.exit(main())
