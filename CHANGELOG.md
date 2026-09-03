# Changelog

All notable changes to DeltaTeX will be documented here.

## 0.1.0 - 2026-09-03

### Added

- display-equation extraction for equation, align, gather, multline and bracket math;
- label-first equation alignment;
- risk rules for summation bounds, inequalities, matrix inverse/transpose and scripts;
- conservative normalization for comments, layout commands and common aliases;
- terminal, JSON and standalone HTML reports;
- CI-friendly `--fail-on` modes;
- examples, standard-library tests and GitHub issue templates.
- control-word-aware normalization that preserves LaTeX command boundaries;
- friendly CLI errors for file, encoding and output-path problems;
- source line numbers and side-by-side formulas in the HTML report.

### Known limitations

- one input file per version;
- lightweight parser does not fully expand custom macros;
- unlabeled equations are aligned by order;
- findings indicate review priority, not mathematical correctness.
