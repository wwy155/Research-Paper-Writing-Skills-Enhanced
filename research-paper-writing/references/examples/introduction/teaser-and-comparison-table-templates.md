# Introduction Figure and Table Templates

The code blocks below are templates, not quotations: fill the brackets with your own methods, properties, and numbers. Part D of `references/introduction.md` says when to use each. Style every figure and table with the chosen scheme (`references/figure-table-styles.md`).

## Comparison Table

```latex
% Preamble: \usepackage{pifont}, \newcommand{\cmark}{\ding{51}}, \newcommand{\xmark}{\ding{55}},
% and \input{table-style} from the chosen style scheme (defines \oursrow).

% Text: point to the table where the gap is stated.
As summarized in Table~\ref{tab:intro_comparison}, existing methods support either [property A] or [property B], but not both.

\begin{table}[t]
  \caption{\textbf{Only [method] supports [property A], [property B], and [property C] together.} [Define each property in a short phrase.]}
  \label{tab:intro_comparison}
  \centering
  \begin{tabular}{lccc}
    \toprule
    Method & [Property A] & [Property B] & [Property C] \\
    \midrule
    [Method 1]~\cite{key1} & \cmark & \xmark & \xmark \\
    [Method 2]~\cite{key2} & \xmark & \cmark & \xmark \\
    [Method 3]~\cite{key3} & \cmark & \xmark & \cmark \\
    \oursrow [Our method] & \cmark & \cmark & \cmark \\
    \bottomrule
  \end{tabular}
\end{table}
```

## Trade-Off Plot

```python
import matplotlib.pyplot as plt
import paperstyle  # copy of scripts/paperstyle.py

paperstyle.use("clean")
ST = paperstyle.method_styles(ALL_METHODS, ours="Ours")  # every method in the paper, in table order
NUDGE = {"[Method 2]": (4, -11)}  # render it, look, and move any labels that overlap
fig, ax = plt.subplots()  # 3.25 x 2.2 in: one CVPR column
for m in SHOWN:
    ax.plot(fps[m], psnr[m], **{**ST[m], "linestyle": "none", "markersize": 9 if m == "Ours" else 7})
    ax.annotate(m, (fps[m], psnr[m]), textcoords="offset points", xytext=NUDGE.get(m, (4, 3)))
ax.set_xscale("log")
ax.set_xlabel(r"Rendering speed (FPS) $\uparrow$")
ax.set_ylabel(r"PSNR (dB) $\uparrow$")
fig.savefig("figures/teaser_tradeoff.pdf")
```

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/teaser_tradeoff}
  \caption{\textbf{[Method] matches the quality of [baseline] at [N]$\times$ its speed.} PSNR and rendering speed on [dataset], measured on [GPU].}
  \label{fig:teaser}
\end{figure}

As shown in Figure~\ref{fig:teaser}, [method] reaches [quality] comparable to [baseline] while running [N]$\times$ faster.
```

## Results Teaser

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/teaser_results}
  \caption{\textbf{[Baseline] [fails how] on [hard case]; [method] recovers [what].} [Input] from [dataset]; zoom-ins show [region].}
  \label{fig:teaser}
\end{figure*}

As shown in Figure~\ref{fig:teaser}, [baseline] produces [failure] on [hard case], while [method] recovers [what].
```
