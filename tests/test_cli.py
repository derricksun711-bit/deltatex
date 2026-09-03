from contextlib import redirect_stderr, redirect_stdout
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from deltatex.cli import main


class DeltaTeXCliTests(unittest.TestCase):
    def test_fail_on_high_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "old.tex"
            new = root / "new.tex"
            report = root / "report.html"
            old.write_text(
                r"\begin{equation}\label{eq:a}x\le y\end{equation}",
                encoding="utf-8",
            )
            new.write_text(
                r"\begin{equation}\label{eq:a}x\ge y\end{equation}",
                encoding="utf-8",
            )
            code = main([str(old), str(new), "--html", str(report), "--fail-on", "high"])
            self.assertEqual(code, 2)
            html = report.read_text(encoding="utf-8")
            self.assertIn("eq:a", html)
            self.assertIn("Old formula · line 1", html)
            self.assertIn("<head>", html)
            self.assertIn("<body>", html)

    def test_layout_only_change_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "old.tex"
            new = root / "new.tex"
            report = root / "report.html"
            old.write_text(r"\begin{equation}\left(x+y\right)\end{equation}", encoding="utf-8")
            new.write_text(r"\begin{equation}( x + y )\end{equation}", encoding="utf-8")
            code = main([str(old), str(new), "--html", str(report), "--fail-on", "change"])
            self.assertEqual(code, 0)

    def test_missing_input_has_friendly_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            error_output = io.StringIO()
            with redirect_stderr(error_output):
                code = main([str(root / "missing-old.tex"), str(root / "missing-new.tex")])
            message = error_output.getvalue()
            self.assertNotEqual(code, 0)
            self.assertIn("DeltaTeX error: cannot read missing-old.tex", message)
            self.assertNotIn("Traceback", message)
            self.assertNotIn(str(root), message)

    def test_invalid_utf8_has_friendly_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "old.tex"
            new = root / "new.tex"
            old.write_bytes(b"\xff\xfe")
            new.write_text(r"\begin{equation}x=y\end{equation}", encoding="utf-8")
            error_output = io.StringIO()
            with redirect_stderr(error_output):
                code = main([str(old), str(new)])
            self.assertNotEqual(code, 0)
            self.assertIn("file is not valid UTF-8", error_output.getvalue())
            self.assertNotIn("Traceback", error_output.getvalue())

    def test_missing_output_directory_has_friendly_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "old.tex"
            new = root / "new.tex"
            old.write_text(r"\begin{equation}x=y\end{equation}", encoding="utf-8")
            new.write_text(r"\begin{equation}x=z\end{equation}", encoding="utf-8")
            report = root / "missing" / "report.html"
            error_output = io.StringIO()
            with redirect_stderr(error_output):
                code = main([str(old), str(new), "--html", str(report)])
            self.assertNotEqual(code, 0)
            self.assertIn("output directory does not exist", error_output.getvalue())
            self.assertNotIn(str(root), error_output.getvalue())

    def test_permission_error_has_friendly_error(self):
        error_output = io.StringIO()
        with patch("deltatex.cli.Path.read_text", side_effect=PermissionError):
            with redirect_stderr(error_output):
                code = main(["old.tex", "new.tex"])
        self.assertNotEqual(code, 0)
        self.assertIn("permission denied", error_output.getvalue())
        self.assertNotIn("Traceback", error_output.getvalue())

    def test_json_output_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "old.tex"
            new = root / "new.tex"
            html_report = root / "report.html"
            json_report = root / "report.json"
            old.write_text(r"\begin{equation}x\le y\end{equation}", encoding="utf-8")
            new.write_text(r"\begin{equation}x\ge y\end{equation}", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                code = main([
                    str(old),
                    str(new),
                    "--html",
                    str(html_report),
                    "--json",
                    str(json_report),
                ])
            payload = json.loads(json_report.read_text(encoding="utf-8"))
            self.assertEqual(code, 0)
            self.assertEqual(payload["summary"]["risks"]["high"], 1)


if __name__ == "__main__":
    unittest.main()
