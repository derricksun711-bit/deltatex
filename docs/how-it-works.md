# How DeltaTeX works

DeltaTeX v0.1 is intentionally a conservative rule engine. It reports
inspectable syntactic risks and never claims to prove equivalence.

## Pipeline

1. **Extract** common display-math environments and bracket display math.
2. **Align** labeled equations by label; align remaining equations by order.
3. **Normalize** comments, whitespace and a small allowlist of harmless syntax.
4. **Compare** normalized tokens.
5. **Explain** recognized changes with a risk level and exact evidence.
6. **Render** the same result model to terminal, JSON and HTML.

## Why an allowlist?

Aggressive normalization can hide a real mathematical change. DeltaTeX
therefore removes only syntax with a clear, tested interpretation. For
example, it treats `\le` and `\leq` as aliases, but it does not reorder
addition or simplify algebraic expressions.

Alias replacement matches complete LaTeX control words rather than command
prefixes. When whitespace separates a control word from a following letter,
DeltaTeX preserves an internal token boundary; this keeps `\sin x` distinct
from the different control word `\sinx`.

Every equivalence normalization needs two tests:

- a positive case showing two spellings that should be treated as equal;
- a near-miss case showing a similar but meaningful change that must remain.

## Alignment trade-off

`\label` is the strongest stable identifier available in ordinary LaTeX.
When labels are missing, v0.1 falls back to document order. Inserting one
unlabeled equation can therefore shift later matches. A future matcher can use
token similarity as a secondary signal, but must expose its confidence.

## Multiple changes in one formula

The comparison removes recognized summation-bound spans and inverse/transpose
exponents from temporary comparison strings before comparing ordinary scripts.
This avoids duplicate script findings without suppressing unrelated scripts in
the same formula. The original formulas remain intact in every report.

After recognized bounds, operations, inequalities and flat scripts are removed,
a different remainder adds `additional formula tokens changed`. This notice
inherits the highest matched risk and does not claim precise token attribution.
Rules compare lists, not syntax trees or base/exponent associations: nested
bounds, composite exponents and moved operations can still lack a specific
explanation. An unchanged operation count does not establish unchanged meaning.
The operation label is a syntactic heuristic and does not prove a base is a matrix.

## Existing ecosystem

- [latexdiff on CTAN](https://ctan.org/pkg/latexdiff) creates visually marked-up
  LaTeX revisions. DeltaTeX is complementary: it summarizes recognized
  mathematical risks.
- [pylatexenc LatexWalker](https://pylatexenc.readthedocs.io/en/latest/latexwalker/)
  exposes a LaTeX node tree and is the leading candidate for replacing the
  lightweight extractor when DeltaTeX adds custom macros and nested syntax.

## Adding a rule

A rule should answer all four questions:

1. What exact token pattern changed?
2. Why can that change matter mathematically?
3. Which harmless near-misses must be excluded?
4. What evidence will the report display?

If a rule cannot answer these questions, it belongs in an experimental plugin
rather than the default risk set.
