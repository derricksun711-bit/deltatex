# Contributing

Thank you for helping DeltaTeX catch risky mathematical edits.

The best contribution is a small, anonymized before/after formula pair that
demonstrates one real revision problem.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

When adding a detection rule:

1. add one test that should trigger it;
2. add at least one near-miss test that must not trigger it;
3. keep the finding explainable from source tokens;
4. document any syntax the rule cannot parse.

DeltaTeX does not accept rules that claim mathematical equivalence without a
sound, inspectable method.

