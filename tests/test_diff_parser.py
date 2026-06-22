"""Tests for src/diff_parser.py — parsing, diffing, and approving changes."""

from src.diff_parser import (
    parse_into_items,
    diff_items,
    apply_approvals,
    extract_change_summary,
)


class TestParseIntoItems:
    """Test the text-to-items parser."""

    def test_parse_bullets(self):
        text = """SKILLS
· Python programming
· Data analysis with SQL
· Team management"""
        items = parse_into_items(text, mode="bullets")
        assert len(items) >= 2
        assert any("Python" in item for item in items)

    def test_parse_paragraphs(self):
        text = """First paragraph about my background.

Second paragraph about my skills.

Third paragraph closing."""
        items = parse_into_items(text, mode="paragraphs")
        assert len(items) == 3
        assert "First paragraph" in items[0]
        assert "Second paragraph" in items[1]

    def test_parse_empty(self):
        assert parse_into_items("", mode="bullets") == []
        assert parse_into_items("", mode="paragraphs") == []

    def test_parse_fallback_no_bullets(self):
        """When no bullet markers found, falls back to line-by-line."""
        text = "Line one\nLine two\nLine three"
        items = parse_into_items(text, mode="bullets")
        assert len(items) > 0


class TestDiffItems:
    """Test the diff function."""

    def test_no_changes(self):
        orig = ["Bullet one", "Bullet two"]
        enhanced = ["Bullet one", "Bullet two"]
        diffs = diff_items(orig, enhanced)
        assert len(diffs) == 2
        assert not any(d["changed"] for d in diffs)

    def test_some_changes(self):
        orig = ["Old bullet", "Unchanged bullet"]
        enhanced = ["<modified>New bullet</modified>", "Unchanged bullet"]
        diffs = diff_items(orig, enhanced)
        assert diffs[0]["changed"] is True
        assert diffs[1]["changed"] is False
        # Tags should be stripped from new_text
        assert diffs[0]["new_text"] == "New bullet"

    def test_mismatched_lengths(self):
        orig = ["One"]
        enhanced = ["One", "Two"]
        diffs = diff_items(orig, enhanced)
        assert len(diffs) == 2
        assert diffs[0]["old_text"] == "One"
        assert diffs[1]["old_text"] == ""


class TestApplyApprovals:
    """Test applying user approve/reject choices."""

    def test_all_approved(self):
        orig = ["Old bullet", "Another old"]
        enhanced = ["<modified>New bullet</modified>", "<modified>Another new</modified>"]
        result = apply_approvals(orig, enhanced, [True, True])
        assert "New bullet" in result
        assert "Another new" in result
        assert "<modified>" not in result

    def test_some_rejected(self):
        orig = ["Old bullet", "Keep this original"]
        enhanced = ["<modified>New bullet</modified>", "<modified>Changed but rejected</modified>"]
        result = apply_approvals(orig, enhanced, [True, False])
        assert "New bullet" in result
        assert "Keep this original" in result
        assert "Changed but rejected" not in result

    def test_all_rejected(self):
        orig = ["Original one", "Original two"]
        enhanced = ["<modified>New one</modified>", "<modified>New two</modified>"]
        result = apply_approvals(orig, enhanced, [False, False])
        assert result == "Original one\nOriginal two"


class TestExtractChangeSummary:
    """Test the convenience function."""

    def test_resume_mode(self):
        orig = "· Python\n· Java"
        enhanced = "· <modified>Python expert</modified>\n· Java"
        orig_items, enhanced_items, diffs = extract_change_summary(orig, enhanced, mode="bullets")
        assert len(diffs) > 0
        assert any(d["changed"] for d in diffs)

    def test_cover_letter_mode(self):
        orig = "Para one.\n\nPara two."
        enhanced = "<modified>Enhanced para one.</modified>\n\nPara two."
        orig_items, enhanced_items, diffs = extract_change_summary(orig, enhanced, mode="paragraphs")
        assert len(diffs) == 2
        assert diffs[0]["changed"] is True
        assert diffs[1]["changed"] is False
