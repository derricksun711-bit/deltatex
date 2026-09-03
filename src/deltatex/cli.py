from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Callable

from .core import compare_documents
from .report import terminal_summary, write_html, write_json


class CliError(Exception):
    """An expected user-facing file or encoding error."""


def _short_name(path: Path) -> str:
    return path.name or "<path>"


def _read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise CliError(f"cannot read {_short_name(path)}: file does not exist") from error
    except IsADirectoryError as error:
        raise CliError(f"cannot read {_short_name(path)}: path is a directory") from error
    except PermissionError as error:
        raise CliError(f"cannot read {_short_name(path)}: permission denied") from error
    except UnicodeDecodeError as error:
        raise CliError(f"cannot read {_short_name(path)}: file is not valid UTF-8") from error
    except OSError as error:
        detail = error.strerror or "I/O error"
        raise CliError(f"cannot read {_short_name(path)}: {detail}") from error


def _write_output(writer: Callable[[dict, Path], None], result: dict, path: Path) -> None:
    try:
        writer(result, path)
    except FileNotFoundError as error:
        raise CliError(
            f"cannot write {_short_name(path)}: output directory does not exist"
        ) from error
    except PermissionError as error:
        raise CliError(f"cannot write {_short_name(path)}: permission denied") from error
    except IsADirectoryError as error:
        raise CliError(f"cannot write {_short_name(path)}: path is a directory") from error
    except OSError as error:
        detail = error.strerror or "I/O error"
        raise CliError(f"cannot write {_short_name(path)}: {detail}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deltatex",
        description="Explain risky mathematical changes between two LaTeX files.",
    )
    parser.add_argument("old", type=Path, help="old UTF-8 LaTeX file")
    parser.add_argument("new", type=Path, help="new UTF-8 LaTeX file")
    parser.add_argument(
        "--html",
        type=Path,
        default=Path("deltatex-report.html"),
        help="HTML report path (default: deltatex-report.html)",
    )
    parser.add_argument("--json", type=Path, dest="json_path", help="optional JSON report path")
    parser.add_argument(
        "--fail-on",
        choices=["never", "high", "change"],
        default="never",
        help="return a non-zero status for high-risk findings or any change",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = compare_documents(_read_utf8(args.old), _read_utf8(args.new))
        _write_output(write_html, result, args.html)
        if args.json_path:
            _write_output(write_json, result, args.json_path)
    except CliError as error:
        print(f"DeltaTeX error: {error}", file=sys.stderr)
        return 2

    print(terminal_summary(result))
    print(f"HTML report: {args.html}")
    if args.json_path:
        print(f"JSON report: {args.json_path}")
    if args.fail_on == "high" and result["summary"]["risks"]["high"]:
        return 2
    if args.fail_on == "change" and any(result["summary"][k] for k in ("changed", "added", "removed")):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
