# Changelog

All notable changes to DeltaTeX will be documented here.

## 0.1.1 - 2026-09-06

### Fixed

- show explicit old/new equation counts with correct singular/plural wording in
  terminal and HTML summaries, including complete equation deletion;
- report unrelated script changes alongside summation-bound or matrix-operation
  changes without duplicating recognized bound/operation findings;
- add a conservative notice when additional formula tokens change;
- keep longer control words and exponents out of recognized inequality/operation spans.

### Changed

- test Python 3.10, 3.11 and 3.12 with one GitHub Actions matrix;
- update the Social Preview to the verified summation-bound, inequality and
  inverse-added example, with a reviewable (not correctness-guaranteeing) tagline;
- document the limits of lightweight multi-change detection and refresh the demo summary.

The JSON field structure is unchanged. No composite inverse/transpose rule was added.

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
