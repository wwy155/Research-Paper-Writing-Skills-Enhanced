# Venue Rules: Page Limits and Appendix

Read this file when you settle the venue (Execution Rule 1 in `SKILL.md`) and before you create or move the Appendix (Execution Rule 2). Venues change their rules from year to year, so never rely on memory. Look up this year's rules every time.

## Find the Rules

1. Search the venue's website for this year's call for papers, author guidelines, and submission instructions. Also read the README and the example paper of its author kit.
2. Answer three questions about the page limits:
   - How many pages may the main text of a long paper have? Use the long-paper (full-paper) limit unless the user asks for a short paper, and the limit of the version you write, since the camera-ready often allows one more page. Note what counts toward it, such as references, acknowledgments, and any required checklist, limitations, or ethics section.
   - Do the references have a page limit, e.g., at most 2 pages after the main text?
   - Does the whole paper have a page limit, e.g., 9 pages in total?
3. Note the other rules:
   - where the Appendix goes, in the same PDF after the references or in a separate supplementary file, with its file format and size limit
   - any page limit of the Appendix or the supplementary material
   - format rules, such as the same template, anonymity, and what the Appendix may contain
   - the deadline of the supplementary material, if it differs from the paper's
4. If you cannot find the page limits, use the default and tell the user in your reply. The default is 8 pages of main text, with references excluded and unlimited, and no total limit. Many venues differ (9 or 10 pages, 4 for a short paper, references capped at 1 or 2 pages, or a total cap), so search before you fall back on it. If this year's rules are not out yet, use last year's and note the year.

## Record Them

Write the rules at the top of the main `.tex` file, with the page you read them on. The checker reads these lines. Fill the placeholders with the values you look up:

```latex
% Venue: [Venue] [Year], long paper
% Venue rules: https://[the guidelines page you read]
% Page limit: [N] pages of main text, references excluded
% Reference pages: no limit
% Total pages: no limit
% Appendix rules: separate PDF; no page limit; same template; anonymous
```

A venue that caps the references and the whole paper:

```latex
% Venue rules: https://[the guidelines page you read]
% Page limit: [N] pages of main text, references excluded
% Reference pages: at most [R]
% Total pages: at most [N+R]
% Appendix rules: separate PDF; at most [M] pages
```

Rules you could not find:

```latex
% Venue rules: not found; searched [where you looked]
% Page limit: 8 pages of main text, references excluded (default)
% Reference pages: no limit (default)
% Total pages: no limit (default)
% Appendix rules: same PDF after the references; no page limit (default)
```

- `Reference pages` counts the pages the references take after the last page of the main text.
- `Total pages` counts every page of the main PDF, with any Appendix in it. Add "Appendix excluded" when the venue does not count the Appendix.
- Write "references included" in the page limit when references count toward it, and "no separate limit" for the reference pages.
- Write "[M] pages" in the Appendix rules when the Appendix has a limit.
- When the venue requires a limitations section, add it to the page-limit line, e.g., `% Page limit: [N] pages of main text, references excluded; a Limitations section is required and not counted`. Without that note, the checker warns about any "Limitations" part (Principle 3 in `SKILL.md`).

## What the Checker Verifies

- ERROR when a rule line is missing, or a page limit is unclear.
- WARN when the rules were not found, so the default is in use. Tell the user, and search again before submission.
- ERROR when the Appendix sits in the wrong place. That is inside the main document when the venue wants a separate file, in a separate file when it wants the same PDF, or before the references when it must follow them.
- WARN when a separate supplementary file does not load the venue's template.
- It counts the pages of the compiled PDF (`main.pdf` next to `main.tex`, or `--pdf`, plus `--supp-pdf` for a separate supplementary file). ERROR when the main text, the references, the whole paper, or the Appendix runs past its limit. WARN when the main text ends short of its limit (Writing Rule A1.1).
- Its pass/fail list shows the limits you recorded, e.g., "main text 8 pages, references unlimited, total unlimited".
- The checker cannot verify that the rules you recorded match the venue's page. Reread that page before you finish.

## Fix Until It Complies

- Main text over the limit. Tighten the wording, move details, extra results, and proofs to the Appendix, and merge or resize floats. Never shrink fonts, margins, or spacing (A1.1).
- Main text short of the limit. Bring important content back from the Appendix, or add the analysis a reviewer would ask for (A1.1, A1.6).
- References over their limit. Shorten the entries with the venue's bibliography style (abbreviated venue names, no URLs or DOIs), merge duplicate entries, and cut citations the paper does not need.
- Whole paper over the total limit. Fix the main text and the references as above, and move an Appendix in the same PDF to a separate file when the venue allows it.
- Appendix in the wrong place. Move it where the rules say, and keep the main text's references to it working. For a separate file, use the `xr` package (`\externaldocument{supp}`) or refer to sections by name, e.g., "Appendix A".
- Appendix over its limit. Cut redundant results, and keep what the main text refers to.
- Recompile, and run the checker again until the page and Appendix checks pass.
