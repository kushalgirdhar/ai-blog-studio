"""Unit tests for local_copyright_checker module."""
"""Unit tests for db_copyright_checker module."""

import unittest
from db_copyright_checker import (
    tokenize,
    get_shingles,
    find_overlapping_phrases,
    highlight_matches,
    difflib_ratio,
    tfidf_cosine_scores,
    check_generated_text,
    check_blog_draft_copyright,
    annotate_posts_with_copyright_info,
)


class DummyPost:
    def __init__(self, id, title, short_description, description):
        self.id = id
        self.title = title
        self.short_description = short_description
        self.description = description


class TestLocalCopyrightChecker(unittest.TestCase):

    def setUp(self):
        self.reference_doc = (
            "This landscape visual piece is centered around a rich palette of coffee brown and slate gray. "
            "The overall scene exhibits balanced illumination across the frame."
        )
        self.corpus = {
            "doc1.txt": self.reference_doc,
            "doc2.txt": "A completely unrelated document discussing cooking pasta and baking bread.",
        }

    def test_tokenization(self):
        tokens = tokenize("Hello, World! This is a test...")
        self.assertEqual(tokens, ["hello", "world", "this", "is", "a", "test"])

    def test_shingles(self):
        tokens = ["a", "b", "c", "d", "e"]
        shingles = get_shingles(tokens, n=3)
        self.assertEqual(shingles, {"a b c", "b c d", "c d e"})

    def test_overlapping_phrases(self):
        generated = "This landscape visual piece is centered around modern design."
        overlaps = find_overlapping_phrases(generated, self.reference_doc, n=4)
        self.assertTrue(len(overlaps) > 0)
        self.assertIn("this landscape visual piece", overlaps)

    def test_span_highlighting_html(self):
        text = "This landscape visual piece is centered around modern art."
        phrases = {"this landscape visual piece", "visual piece is centered"}
        highlighted = highlight_matches(text, phrases, mode="html")
        self.assertIn("<mark class=\"copyright-highlight\"", highlighted)
        self.assertIn("</mark>", highlighted)
        # Verify no broken/nested tags
        self.assertEqual(highlighted.count("<mark"), 1)
        self.assertEqual(highlighted.count("</mark>"), 1)

    def test_span_highlighting_markdown(self):
        text = "This landscape visual piece is centered around modern art."
        phrases = {"this landscape visual piece", "visual piece is centered"}
        highlighted = highlight_matches(text, phrases, mode="markdown")
        self.assertEqual(highlighted, "**This landscape visual piece is centered** around modern art.")

    def test_similarity_scoring(self):
        ratio = difflib_ratio("abc def", "abc def")
        self.assertEqual(ratio, 1.0)

        scores = tfidf_cosine_scores(self.reference_doc, self.corpus)
        self.assertIn("doc1.txt", scores)
        self.assertAlmostEqual(scores["doc1.txt"], 1.0, places=2)
        self.assertLess(scores["doc2.txt"], 0.2)

    def test_check_generated_text_flagged(self):
        gen_text = "This landscape visual piece is centered around a rich palette of coffee brown."
        report = check_generated_text(gen_text, extra_corpus=self.corpus)
        self.assertTrue(report["is_flagged"])
        self.assertGreater(len(report["matched_phrases"]), 0)
        self.assertIn("<mark", report["highlighted_text"])

    def test_check_generated_text_unique(self):
        gen_text = "Quantum algorithms leverage superposition and entanglement in cryogenic computing environments."
        report = check_generated_text(gen_text, extra_corpus=self.corpus)
        self.assertFalse(report["is_flagged"])
        self.assertEqual(len(report["matched_phrases"]), 0)
        self.assertEqual(report["highlighted_text"], gen_text)

    def test_check_blog_draft_copyright(self):
        title = "Landscape Study"
        short_desc = "This landscape visual piece is centered around nature."
        desc = "The overall scene exhibits balanced illumination across the frame."
        report = check_blog_draft_copyright(title, short_desc, desc, extra_corpus=self.corpus)
        self.assertTrue(report["is_flagged"])
        self.assertIn("highlighted_fields", report)
        self.assertIn("<mark", report["highlighted_fields"]["description"])

    def test_annotate_posts_with_copyright_info(self):
        p1 = DummyPost(
            1,
            "Hand Interacting with a Holographic Data Interface",
            "A hand interacts with a futuristic, holographic user interface featuring floating panels of data",
            "A human hand is positioned centrally against a dark background interacting with a series of floating digital panels",
        )
        p2 = DummyPost(
            2,
            "Hand Interacting with Holographic Data Interface",
            "A hand interacts with a futuristic, holographic user interface displaying various charts",
            "A human hand is shown interacting with a series of floating digital panels against a dark blue background",
        )
        p3 = DummyPost(
            3,
            "Culinary Arts and Italian Cooking",
            "A delicious pasta recipe made with fresh tomatoes and basil leaves.",
            "Traditional homemade pasta tossed with extra virgin olive oil, garlic, and freshly grated parmesan.",
        )
        posts = [p1, p2, p3]
        annotate_posts_with_copyright_info(posts)

        self.assertTrue(p1.is_flagged)
        self.assertTrue(p2.is_flagged)
        self.assertFalse(p3.is_flagged)
        self.assertIn("<mark class=\"copyright-highlight\"", p1.highlighted_title)
        self.assertIn("<mark class=\"copyright-highlight\"", p2.highlighted_title)
        self.assertIn("<mark class=\"copyright-highlight\"", p1.highlighted_short_description)
        self.assertIn("<mark class=\"copyright-highlight\"", p2.highlighted_description)


if __name__ == "__main__":
    unittest.main()

