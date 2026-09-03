"""Human-readable and machine-readable report rendering."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path


COLORS = {"high": "#dc2626", "medium": "#d97706", "low": "#2563eb", "none": "#64748b"}


def terminal_summary(result: dict) -> str:
    summary = result["summary"]
    lines = [
        "DeltaTeX semantic risk report",
        f"{summary['new_equations']} equations scanned | {summary['unchanged']} unchanged | "
        f"{summary['changed']} changed | {summary['added']} added | {summary['removed']} removed",
    ]
    for finding in result["findings"]:
        if finding["status"] == "unchanged":
            continue
        icon = {"high": "[HIGH]", "medium": "[MEDIUM]", "low": "[LOW]"}[finding["risk"]]
        lines.append(f"{icon} {finding['key']}: {'; '.join(finding['changes'])}")
    return "\n".join(lines)


def write_json(result: dict, path: Path) -> None:
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def write_html(result: dict, path: Path) -> None:
    summary = result["summary"]
    cards: list[str] = []
    for f in result["findings"]:
        changes = "".join(f"<li>{escape(item)}</li>" for item in f["changes"]) or "<li>No semantic token change</li>"
        before = escape(f["before"] or "—")
        after = escape(f["after"] or "—")
        old_location = f"line {f['old_line']}" if f["old_line"] is not None else "not present"
        new_location = f"line {f['new_line']}" if f["new_line"] is not None else "not present"
        cards.append(f"""
        <article class="finding">
          <div class="heading"><strong>{escape(f['key'])}</strong>
          <span style="background:{COLORS[f['risk']]}">{f['status']} · {f['risk']}</span></div>
          <ul>{changes}</ul>
          <div class="formula-grid">
            <div class="formula before"><small>Old formula · {old_location}</small><pre>{before}</pre></div>
            <div class="formula after"><small>New formula · {new_location}</small><pre>{after}</pre></div>
          </div>
        </article>""")
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DeltaTeX report</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font: 15px system-ui, sans-serif; background: #f8fafc; color: #172033; margin: 0; }}
    main {{ max-width: 1000px; margin: auto; padding: 40px 20px; }}
    h1 {{ margin-bottom: 4px; }}
    .summary {{ color: #475569; margin-bottom: 28px; }}
    .finding {{ background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; margin: 14px 0; box-shadow: 0 4px 16px #0f172a0a; }}
    .heading {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; }}
    .heading span {{ color: white; padding: 3px 9px; border-radius: 99px; font-size: 12px; white-space: nowrap; }}
    ul {{ color: #334155; padding-left: 22px; }}
    .formula-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .formula {{ background: #f1f5f9; border-radius: 9px; padding: 12px; min-width: 0; }}
    .formula.before {{ border-left: 4px solid #94a3b8; }}
    .formula.after {{ border-left: 4px solid #2563eb; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; margin: 6px 0 0; }}
    small {{ color: #64748b; font-weight: 600; }}
    @media (max-width: 640px) {{
      main {{ padding: 24px 12px; }}
      .formula-grid {{ grid-template-columns: 1fr; }}
      .heading {{ align-items: flex-start; }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>DeltaTeX</h1>
    <p class="summary">{summary['new_equations']} equations · {summary['changed']} changed · {summary['risks']['high']} high-risk</p>
    {''.join(cards)}
  </main>
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")
