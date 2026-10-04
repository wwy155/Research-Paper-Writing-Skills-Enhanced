# Venue Rules: Page Limit and Appendix

Read this file when you settle the venue (Execution Rule 1 in `SKILL.md`) and before you create or move the Appendix (Execution Rule 2). Venues change their rules from year to year, so never rely on memory: look up this year's rules every time.

## Find the Rules

1. Search the venue's website for this year's call for papers, author guidelines, and submission instructions. Also read the README and the example paper of its author kit. If you cannot open them, ask the user for the link or the text.
2. Note these rules:
   - the page limit of the main text, and what counts toward it: references, acknowledgments, and any required checklist, limitations, or ethics section;
   - where the Appendix goes: in the same PDF after the references, or in a separate supplementary file, with its file format and size limit;
   - any page limit of the Appendix or the supplementary material;
   - format rules: the same template, anonymity, and what the Appendix may contain;
   - the deadline of the supplementary material, if it differs from the paper's.
3. Record them at the top of the main `.tex` file, with the page you read them on. Two examples of the format, with placeholders for the values you look up:

   ```latex
   % Venue: [Venue] [Year]
   % Venue rules: https://[the guidelines page you read]
   % Page limit: [N] pages, references excluded
   % Appendix rules: separate PDF; no page limit; same template; anonymous
   ```

   ```latex
   % Venue rules: https://[the guidelines page you read]
   % Page limit: [N] pages, references excluded
   % Appendix rules: same PDF after the references; no page limit
   ```

   Write "references included" when references count toward the limit, and "[M] pages" in the Appendix rules when the Appendix has a limit.

## What the Checker Verifies

- ERROR when a rule line is missing.
- ERROR when the Appendix sits in the wrong place. That is inside the main document when the venue wants a separate file, in a separate file when it wants the same PDF, or before the references when it must follow them.
- WARN when a separate supplementary file does not load the venue's template.
- With `--pdf main.pdf`, plus `--supp-pdf supp.pdf` for a separate supplementary file, it counts pages. ERROR when the main text runs past the page limit, or the Appendix past its own limit. WARN when the main text ends short of the limit (Writing Rule A1.1).
- The checker cannot verify that the rules you recorded match the venue's page. Reread that page before you finish.

## Fix Until It Complies

- Main text over the limit: tighten the wording, move details, extra results, and proofs to the Appendix, and merge or resize floats. Never shrink fonts, margins, or spacing (A1.1).
- Main text short of the limit: bring important content back from the Appendix, or add the analysis a reviewer would ask for (A1.1, A1.6).
- Appendix in the wrong place: move it where the rules say, and keep the main text's references to it working. For a separate file, use the `xr` package (`\externaldocument{supp}`) or refer to sections by name, e.g., "Appendix A".
- Appendix over its limit: cut redundant results, and keep what the main text refers to.
- Recompile, and run the checker again until the page and Appendix checks pass.
