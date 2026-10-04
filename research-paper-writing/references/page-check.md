# Look at Every Page

Read this file before the first compile (Checking the Writing Rules, step 4 in `SKILL.md`). Reviewers see the PDF, not the source. Look at every page after every compile.

## Run the Page Check

1. Compile the paper (Execution Rule 3).
2. Run `python3 <this skill's directory>/scripts/page_qa.py main.pdf`, and add `supp.pdf` for a separate supplementary file. It needs PyMuPDF (`pip install pymupdf`) or poppler's `pdftoppm`.
3. It renders every page and reports the white space and overflow it can measure. It writes sheets of four pages each to `.page-qa/main/`, with each problem boxed in red (ERROR) or orange (WARN).
4. Open every sheet with your image viewer, such as the Read tool in Claude Code, and look at every page. If you cannot view images, ask the user to open the sheets, and to send you what they see and the codes.
5. Fix what you see, recompile, and run it again.
6. When every page looks right, confirm with the code printed on each sheet, e.g., `page_qa.py main.pdf --confirm K7QF H3XA`. `check_tex.py` reports an ERROR for a PDF whose sheets were not all viewed, or that changed after you viewed it.

## What to Look For

- White space. A blank band inside a column, a column that ends early, a page that holds a lone small float, a figure narrower than its column, an image with a white border, or stretched space between paragraphs (A1.6).
- Short last lines. A paragraph or caption that ends with one or two words (A1.2).
- Overflow. Text, a table, or a URL that runs into the margin or into the gap between the columns (A1.1).
- Float positions. Each figure and table sits right after the text that introduces it, in the same section (A2.5).
- Overlaps. Text over a figure, a caption that touches the text, or labels that overlap inside a figure.
- The page limit. The main text ends exactly at the limit, and the references and the Appendix follow the venue's rules (`references/venue-rules.md`).

The script misses overlaps, misplaced floats, and bad crops. Your eyes are the check.

## Fix What You See

| What you see | Fix |
|---|---|
| A blank band, or stretched space between paragraphs | LaTeX could not fit the next float or line. Move the float's source earlier or later, resize it, or reword nearby paragraphs. |
| A column or page that ends early | Move a float to a column with room, combine two floats, or move content to or from the Appendix. |
| A page that holds one small float | Enlarge the float to the column width, combine it with another, or place it with `[t]` next to its text. |
| A figure narrower than its column | Widen it to the column width, or put two panels side by side. |
| An image with a white border | Crop the image. |
| A short last line | Reword the paragraph by cutting or adding a few words. |
| Content in the margin | Shorten the cell or the line, break the URL, or resize the table or figure. Keep its text at least the caption size. |

Never fix white space with negative `\vspace`, smaller fonts, or changed margins (A1.1).
