# Introduction Figure and Table Templates

The code blocks below are templates, not quotations: fill the brackets with your own methods, properties, and numbers. Part D of `references/introduction.md` says when to use each. Use one only when it shows the paper's main point at a glance.

## Comparison Table

```latex
% Preamble: \usepackage{pifont}, \newcommand{\cmark}{\ding{51}}, \newcommand{\xmark}{\ding{55}}.

% Text: point to the table where the gap is stated.
As summarized in Table~\ref{tab:intro_comparison}, existing methods support either [property A] or [property B], but not both.

\begin{table}[t]
  \caption{Properties of [task] methods, namely [property A] ([short definition]), [property B] ([short definition]), and [property C] ([short definition]). Only [method] supports all three.}
  \label{tab:intro_comparison}
  \centering
  \begin{tabular}{lccc}
    \toprule
    Method & [Property A] & [Property B] & [Property C] \\
    \midrule
    [Method 1]~\cite{key1} & \cmark & \xmark & \xmark \\
    [Method 2]~\cite{key2} & \xmark & \cmark & \xmark \\
    [Method 3]~\cite{key3} & \cmark & \xmark & \cmark \\
    [Our method] & \cmark & \cmark & \cmark \\
    \bottomrule
  \end{tabular}
\end{table}
```

## Trade-Off Plot

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/teaser_tradeoff}
  \caption{PSNR versus rendering speed on [dataset], measured on [GPU]. [Method] matches the quality of [baseline] at [N]$\times$ its speed.}
  \label{fig:teaser}
\end{figure}

As shown in Figure~\ref{fig:teaser}, [method] reaches [quality] comparable to [baseline] while running [N]$\times$ faster.
```

## Results Teaser

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/teaser_results}
  \caption{[Method] and [baseline] on [hard case] from [dataset], with zoom-ins on [region]. [Baseline] [fails how], while [method] recovers [what].}
  \label{fig:teaser}
\end{figure*}

As shown in Figure~\ref{fig:teaser}, [baseline] produces [failure] on [hard case], while [method] recovers [what].
```
