import unittest

from deltatex.core import compare_documents, extract_equations, normalize_latex


class DeltaTeXCoreTests(unittest.TestCase):
    def test_layout_only_changes_are_ignored(self):
        self.assertEqual(
            normalize_latex(r"\left( x + y \right)"),
            normalize_latex(r"(x+y)"),
        )

    def test_detects_summation_bound_change(self):
        old = r"\begin{equation}\label{eq:sum}\sum_{k=i}^{j} A_k\end{equation}"
        new = r"\begin{equation}\label{eq:sum}\sum_{k=i}^{j-1} A_k\end{equation}"
        result = compare_documents(old, new)
        finding = result["findings"][0]
        self.assertEqual(finding["risk"], "high")
        self.assertEqual(finding["changes"][0], "summation upper bound changed: j -> j-1")

    def test_detects_inequality_direction_change(self):
        old = r"\begin{equation}\label{eq:risk}x \leq y\end{equation}"
        new = r"\begin{equation}\label{eq:risk}x \geq y\end{equation}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "high")
        self.assertTrue(any("inequality" in item for item in finding["changes"]))

    def test_aligns_equations_by_label_after_reordering(self):
        old = r"\begin{equation}a=1\label{eq:a}\end{equation}\begin{equation}b=2\label{eq:b}\end{equation}"
        new = r"\begin{equation}b=2\label{eq:b}\end{equation}\begin{equation}a=1\label{eq:a}\end{equation}"
        result = compare_documents(old, new)
        self.assertEqual(result["summary"]["unchanged"], 2)

    def test_extracts_bracket_display_math(self):
        equations = extract_equations("before\n\\[ x = y \\]\nafter")
        self.assertEqual(equations[0].line, 2)

    def test_removed_equation_is_high_risk(self):
        old = r"\begin{equation}\label{eq:gone}x=y\end{equation}"
        finding = compare_documents(old, "")["findings"][0]
        self.assertEqual(finding["status"], "removed")
        self.assertEqual(finding["risk"], "high")

    def test_added_equation_is_medium_risk(self):
        new = r"\begin{equation}\label{eq:new}x=y\end{equation}"
        finding = compare_documents("", new)["findings"][0]
        self.assertEqual(finding["status"], "added")
        self.assertEqual(finding["risk"], "medium")

    def test_detects_matrix_inverse_change(self):
        old = r"\begin{equation}\label{eq:m}Ax=b\end{equation}"
        new = r"\begin{equation}\label{eq:m}x=A^{-1}b\end{equation}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "high")
        self.assertTrue(any("matrix operation" in item for item in finding["changes"]))

    def test_equivalent_inequality_aliases_are_ignored(self):
        old = r"\begin{equation}x \leq y\end{equation}"
        new = r"\begin{equation}x\le y\end{equation}"
        self.assertEqual(compare_documents(old, new)["summary"]["unchanged"], 1)

    def test_equivalent_transpose_spellings_are_ignored(self):
        old = r"\begin{equation}A^T A\end{equation}"
        new = r"\begin{equation}A^{\top}A\end{equation}"
        self.assertEqual(compare_documents(old, new)["summary"]["unchanged"], 1)

    def test_single_character_script_braces_are_ignored(self):
        old = r"\begin{equation}x_i=y^2\end{equation}"
        new = r"\begin{equation}x_{i}=y^{2}\end{equation}"
        self.assertEqual(compare_documents(old, new)["summary"]["unchanged"], 1)

    def test_comments_are_ignored(self):
        old = "\\begin{equation}x=y % explain this\n\\end{equation}"
        new = "\\begin{equation}x=y\\end{equation}"
        self.assertEqual(compare_documents(old, new)["summary"]["unchanged"], 1)

    def test_unclassified_token_change_is_low_risk(self):
        old = r"\begin{equation}\label{eq:c}x+y=z\end{equation}"
        new = r"\begin{equation}\label{eq:c}x-y=z\end{equation}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "low")

    def test_arrow_control_words_keep_their_direction(self):
        old = r"\begin{equation}a\leftarrow b\end{equation}"
        new = r"\begin{equation}a\rightarrow b\end{equation}"
        result = compare_documents(old, new)
        self.assertEqual(result["summary"]["changed"], 1)
        self.assertEqual(result["summary"]["unchanged"], 0)

    def test_control_word_boundary_is_preserved(self):
        self.assertNotEqual(normalize_latex(r"\sin x"), normalize_latex(r"\sinx"))

    def test_ne_alias_matches_only_the_complete_control_word(self):
        self.assertEqual(normalize_latex(r"x\ne y"), normalize_latex(r"x\neq y"))
        self.assertNotIn(r"\neqq", normalize_latex(r"x\neq y"))

    def test_real_subscript_change_is_reported(self):
        old = r"\begin{equation}x_i=y\end{equation}"
        new = r"\begin{equation}x_{i+1}=y\end{equation}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "medium")
        self.assertIn("subscript changed: i -> i+1", finding["changes"])

    def test_real_superscript_change_is_reported(self):
        old = r"\begin{equation}x^2=y\end{equation}"
        new = r"\begin{equation}x^3=y\end{equation}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "medium")
        self.assertIn("superscript changed: 2 -> 3", finding["changes"])

    def test_transpose_removal_is_high_risk(self):
        old = r"\begin{equation}A^{\top}x=b\end{equation}"
        new = r"\begin{equation}Ax=b\end{equation}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "high")
        self.assertTrue(any("matrix operation" in item for item in finding["changes"]))

    def test_inverse_removal_is_high_risk(self):
        old = r"\begin{equation}x=A^{-1}b\end{equation}"
        new = r"\begin{equation}Ax=b\end{equation}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "high")

    def test_extracts_starred_equation_environment(self):
        equations = extract_equations(r"\begin{equation*}x=y\end{equation*}")
        self.assertEqual(len(equations), 1)

    def test_detects_change_inside_align_environment(self):
        old = r"\begin{align}x&\le y\\z&=1\end{align}"
        new = r"\begin{align}x&\ge y\\z&=1\end{align}"
        finding = compare_documents(old, new)["findings"][0]
        self.assertEqual(finding["risk"], "high")


if __name__ == "__main__":
    unittest.main()
