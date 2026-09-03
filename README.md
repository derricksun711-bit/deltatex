# DeltaTeX

**A semantic risk diff for mathematical LaTeX.**

Git shows that `j` became `j-1`. DeltaTeX explains that a summation bound
changed and marks the edit for review.

## Demo

```text
DeltaTeX semantic risk report
2 equations scanned | 0 unchanged | 2 changed | 0 added | 0 removed
[HIGH] eq:accumulation: summation upper bound changed: j -> j-1
[HIGH] eq:stability: inequality operator changed: \\le -> \\ge
```

[Open the generated HTML report](./docs/demo-report.html) or inspect the
[machine-readable JSON](./docs/demo-report.json). GitHub displays the HTML
source; download the file and open it in a browser to view the formatted report.

## Why DeltaTeX?

A one-character edit can have a large mathematical effect:

```diff
- \sum_{k=i}^{j} A_k
+ \sum_{k=i}^{j-1} A_k
```

A text diff identifies the changed characters. DeltaTeX adds a narrow,
rule-based explanation:

```text
[HIGH] summation upper bound changed: j -> j-1
```

The intended users are researchers and collaborators reviewing revisions to
mathematical LaTeX documents.

## Features

- aligns labeled equations by `\label` and unlabeled equations by position;
- ignores a conservative set of layout-only differences;
- identifies recognized high-impact token changes;
- writes terminal, JSON and standalone HTML reports;
- supports CI failure on high-risk findings or any formula change;
- runs with the Python standard library at runtime.

## Quick Start

```bash
git clone https://github.com/derricksun711-bit/deltatex.git
cd deltatex
python -m pip install .
python -m deltatex examples/paper_v1.tex examples/paper_v2.tex \
  --html report.html --json report.json
```

If the installed `deltatex` command is on your PATH, it is equivalent to
`python -m deltatex`.

DeltaTeX requires Python 3.10 or later.

## Example

`old.tex`:

```latex
\begin{equation}
  \label{eq:sum}
  x_j = \sum_{k=i}^{j} A_k x_k
\end{equation}
```

`new.tex`:

```latex
\begin{equation}
  \label{eq:sum}
  x_j = \sum_{k=i}^{j-1} A_k x_k
\end{equation}
```

```bash
python -m deltatex old.tex new.tex --html report.html --json report.json
```

```text
[HIGH] eq:sum: summation upper bound changed: j -> j-1
```

Use `--fail-on high` to return a non-zero status when a high-risk finding is
present, or `--fail-on change` for any added, removed or changed formula.

## HTML Report

The standalone report separates old and new formulas, shows their source line
numbers, and lists the rule that produced each finding. JSON contains the same
evidence for scripts and CI workflows.

## Supported Checks

| Check | Default risk |
|---|---|
| Summation lower or upper bound changed | High |
| Inequality operator changed | High |
| Inverse or transpose operation added or removed | High |
| Display equation removed | High |
| Subscript or superscript changed | Medium |
| Display equation added | Medium |
| Other formula-token change | Low |

The lightweight extractor supports `equation`, `align`, `gather`,
`multline`, their starred forms, and `\[...\]` display math.

## Known Limitations

- DeltaTeX is heuristic and rule-based, not a theorem prover.
- It is not a full LaTeX parser and does not establish mathematical equivalence.
- Complex custom macros and deeply nested syntax may not be understood.
- Version 0.1 compares one input file per version; it does not expand `\input`.
- An `align` environment is treated as one display block.
- Unlabeled equations are aligned by position, so insertions can shift matches.

Every finding includes the original source text for human review.

## Why not `latexdiff`?

[`latexdiff`](https://ctan.org/pkg/latexdiff) produces a visually marked-up
LaTeX revision. DeltaTeX addresses a different step: it summarizes recognized
mathematical risk patterns. The tools are complementary.

## Project Structure

```text
src/deltatex/   package, CLI, comparison rules and report rendering
tests/          unittest regression and CLI tests
examples/       minimal old/new LaTeX inputs
docs/           generated demo report and design notes
.github/        CI workflow and issue forms
pyproject.toml  package metadata and command entry point
```

The project uses Python 3.10+, setuptools, unittest and GitHub Actions. Runtime
code has no third-party dependencies.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the rule-contribution checklist and
[how DeltaTeX works](./docs/how-it-works.md) for design trade-offs.

## Roadmap

- expand multi-file LaTeX projects;
- use richer parsing for custom macros and nested syntax;
- compare Git revisions directly;
- publish findings as pull-request comments.

## License

[MIT](./LICENSE)
