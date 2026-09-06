"""Extract and compare display equations without requiring a TeX engine.

The MVP deliberately reports risky syntactic changes rather than claiming to
prove mathematical equivalence. Each finding includes the exact before/after
formula so a human can audit it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable


MATH_ENVS = "equation|equation\\*|align|align\\*|gather|gather\\*|multline|multline\\*"
ENV_RE = re.compile(
    rf"\\begin\{{(?P<env>{MATH_ENVS})\}}(?P<body>.*?)\\end\{{(?P=env)\}}",
    re.DOTALL,
)
BRACKET_RE = re.compile(r"\\\[(?P<body>.*?)\\\]", re.DOTALL)
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
COMMENT_RE = re.compile(r"(?<!\\)%.*$")
SUM_RE = re.compile(r"\\sum_\{([^{}]*)\}\^\{([^{}]*)\}")
INEQUALITY_RE = re.compile(r"\\(?:leq?|geq?)(?![A-Za-z])|(?<![<>=])[<>](?![=])")
MATRIX_OP_PATTERNS = {
    "matrix inverse": re.compile(r"\^\{-1\}|\^-1(?![0-9])"),
    "matrix transpose": re.compile(r"\^(?:\{\\top\}|\\top(?![A-Za-z])|\{T\}|T(?![A-Za-z]))"),
}
SCRIPT_RE = re.compile(r"([_^])(?:\{([^{}]*)\}|([A-Za-z0-9]+))")
CONTROL_WORD_BOUNDARY = "\ue000"


@dataclass(frozen=True)
class Equation:
    key: str
    label: str | None
    index: int
    line: int
    latex: str
    normalized: str


@dataclass(frozen=True)
class Finding:
    key: str
    label: str | None
    old_index: int | None
    new_index: int | None
    old_line: int | None
    new_line: int | None
    status: str
    risk: str
    changes: tuple[str, ...]
    before: str | None
    after: str | None


def _strip_comments(text: str) -> str:
    return "\n".join(COMMENT_RE.sub("", line) for line in text.splitlines())


def _replace_control_word(value: str, source: str, target: str) -> str:
    """Replace one complete LaTeX control word, never a longer command prefix."""
    pattern = re.compile(rf"\\{re.escape(source)}(?![A-Za-z])")
    replacement = f"\\{target}" if target else ""
    return pattern.sub(lambda _: replacement, value)


def normalize_latex(value: str) -> str:
    """Remove layout-only noise while preserving mathematical tokens."""
    value = _strip_comments(value)
    value = LABEL_RE.sub("", value)
    value = _replace_control_word(value, "left", "")
    value = _replace_control_word(value, "right", "")
    value = re.sub(r"\\(?:qquad|quad)\b|\\[,;!]", "", value)
    for source, target in (("leq", "le"), ("geq", "ge"), ("ne", "neq")):
        value = _replace_control_word(value, source, target)
    # Whitespace terminates a control word. Preserve that boundary when the
    # following character is a letter, e.g. \\sin x versus \\sinx.
    value = re.sub(
        r"(\\[A-Za-z]+)\s+(?=[A-Za-z])",
        lambda match: match.group(1) + CONTROL_WORD_BOUNDARY,
        value,
    )
    value = re.sub(r"\s+", "", value)
    # x_i and x_{i} have the same mathematical structure.
    value = re.sub(r"(?<!\\)([_^])([A-Za-z0-9])", r"\1{\2}", value)
    # Treat the two most common transpose spellings as the same operation.
    value = value.replace(r"^{T}", r"^{\top}")
    return value.strip()


def extract_equations(text: str) -> list[Equation]:
    matches: list[tuple[int, str]] = []
    matches.extend((m.start(), m.group("body")) for m in ENV_RE.finditer(text))
    matches.extend((m.start(), m.group("body")) for m in BRACKET_RE.finditer(text))
    matches.sort(key=lambda item: item[0])

    equations: list[Equation] = []
    for index, (position, body) in enumerate(matches, start=1):
        label_match = LABEL_RE.search(body)
        label = label_match.group(1) if label_match else None
        key = label or f"equation-{index}"
        equations.append(
            Equation(
                key=key,
                label=label,
                index=index,
                line=text.count("\n", 0, position) + 1,
                latex=body.strip(),
                normalized=normalize_latex(body),
            )
        )
    return equations


def _inequalities(value: str) -> list[str]:
    return INEQUALITY_RE.findall(value)


def _matrix_ops(value: str) -> list[str]:
    found: list[str] = []
    for name, pattern in MATRIX_OP_PATTERNS.items():
        found.extend([name] * len(pattern.findall(value)))
    return found


def _scripts(value: str, marker: str) -> list[str]:
    return [braced or bare for kind, braced, bare in SCRIPT_RE.findall(value)
            if kind == marker]


def _without_special_scripts(value: str) -> str:
    """Exclude only recognized bounds and operation exponents, not whole formulas."""
    value = SUM_RE.sub(lambda _: r"\sum", value)
    for pattern in MATRIX_OP_PATTERNS.values():
        value = pattern.sub("", value)
    return value


def _remaining_tokens(value: str) -> str:
    """Conservative remainder; this does not associate scripts with their bases."""
    value = _without_special_scripts(value)
    value = SCRIPT_RE.sub("", value)
    # A removed control word may leave its normalization boundary behind.
    value = re.sub(
        rf"(?:{INEQUALITY_RE.pattern}){CONTROL_WORD_BOUNDARY}?", "", value
    )
    return value


def _summation_change(old_sums: list[tuple[str, str]], new_sums: list[tuple[str, str]]) -> list[str]:
    if len(old_sums) == len(new_sums) == 1:
        old_lower, old_upper = old_sums[0]
        new_lower, new_upper = new_sums[0]
        changes: list[str] = []
        if old_lower != new_lower:
            changes.append(f"summation lower bound changed: {old_lower} -> {new_lower}")
        if old_upper != new_upper:
            changes.append(f"summation upper bound changed: {old_upper} -> {new_upper}")
        return changes
    old_text = ", ".join(f"{lower}..{upper}" for lower, upper in old_sums) or "none"
    new_text = ", ".join(f"{lower}..{upper}" for lower, upper in new_sums) or "none"
    return [f"summation bounds changed: {old_text} -> {new_text}"]


def _format_values(values: list[str]) -> str:
    return ", ".join(values) or "none"


def _describe_change(before: str, after: str) -> tuple[str, tuple[str, ...]]:
    changes: list[str] = []
    risk = "low"

    old_sums, new_sums = SUM_RE.findall(before), SUM_RE.findall(after)
    sum_changed = old_sums != new_sums and bool(old_sums or new_sums)
    if sum_changed:
        changes.extend(_summation_change(old_sums, new_sums))
        risk = "high"

    old_ineq, new_ineq = _inequalities(before), _inequalities(after)
    if old_ineq != new_ineq:
        changes.append(
            f"inequality operator changed: {_format_values(old_ineq)} -> {_format_values(new_ineq)}"
        )
        risk = "high"

    old_ops, new_ops = _matrix_ops(before), _matrix_ops(after)
    if old_ops != new_ops:
        changes.append(
            f"matrix operation changed: {_format_values(old_ops)} -> {_format_values(new_ops)}"
        )
        risk = "high"

    old_rest, new_rest = _without_special_scripts(before), _without_special_scripts(after)
    old_sub, new_sub = _scripts(old_rest, "_"), _scripts(new_rest, "_")
    if old_sub != new_sub:
        changes.append(
            f"subscript changed: {_format_values(old_sub)} -> {_format_values(new_sub)}"
        )
        risk = "high" if risk == "high" else "medium"

    old_sup, new_sup = _scripts(old_rest, "^"), _scripts(new_rest, "^")
    if old_sup != new_sup:
        changes.append(
            f"superscript changed: {_format_values(old_sup)} -> {_format_values(new_sup)}"
        )
        risk = "high" if risk == "high" else "medium"

    if changes and _remaining_tokens(before) != _remaining_tokens(after):
        changes.append("additional formula tokens changed")
    if not changes:
        changes.append("formula tokens changed; no high-risk rule matched")
    return risk, tuple(changes)


def _align(old: Iterable[Equation], new: Iterable[Equation]) -> list[tuple[Equation | None, Equation | None]]:
    old_list, new_list = list(old), list(new)
    old_by_label = {e.label: e for e in old_list if e.label}
    new_by_label = {e.label: e for e in new_list if e.label}
    pairs: list[tuple[Equation | None, Equation | None]] = []
    used_old: set[int] = set()
    used_new: set[int] = set()

    for label in dict.fromkeys([e.label for e in old_list + new_list if e.label]):
        left, right = old_by_label.get(label), new_by_label.get(label)
        pairs.append((left, right))
        if left:
            used_old.add(left.index)
        if right:
            used_new.add(right.index)

    remaining_old = [e for e in old_list if e.index not in used_old]
    remaining_new = [e for e in new_list if e.index not in used_new]
    width = max(len(remaining_old), len(remaining_new))
    for i in range(width):
        pairs.append((remaining_old[i] if i < len(remaining_old) else None,
                      remaining_new[i] if i < len(remaining_new) else None))
    pairs.sort(key=lambda pair: min(
        pair[0].index if pair[0] else 10**9,
        pair[1].index if pair[1] else 10**9,
    ))
    return pairs


def compare_documents(old_text: str, new_text: str) -> dict:
    old_equations = extract_equations(old_text)
    new_equations = extract_equations(new_text)
    findings: list[Finding] = []

    for old, new in _align(old_equations, new_equations):
        key = (new or old).key  # type: ignore[union-attr]
        label = (new or old).label  # type: ignore[union-attr]
        if old is None:
            finding = Finding(key, label, None, new.index, None, new.line,
                              "added", "medium", ("equation added",), None, new.latex)
        elif new is None:
            finding = Finding(key, label, old.index, None, old.line, None,
                              "removed", "high", ("equation removed",), old.latex, None)
        elif old.normalized == new.normalized:
            finding = Finding(key, label, old.index, new.index, old.line, new.line,
                              "unchanged", "none", (), old.latex, new.latex)
        else:
            risk, changes = _describe_change(old.normalized, new.normalized)
            finding = Finding(key, label, old.index, new.index, old.line, new.line,
                              "changed", risk, changes, old.latex, new.latex)
        findings.append(finding)

    counts = {name: sum(f.status == name for f in findings)
              for name in ("unchanged", "changed", "added", "removed")}
    risks = {name: sum(f.risk == name for f in findings)
             for name in ("high", "medium", "low")}
    return {
        "summary": {
            "old_equations": len(old_equations),
            "new_equations": len(new_equations),
            **counts,
            "risks": risks,
        },
        "findings": [asdict(f) for f in findings],
    }
