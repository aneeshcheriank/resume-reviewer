"""Tests for src/pdf_editor.py — PDF text replacement."""

import tempfile
import os
import fitz
from src.pdf_editor import (
    _build_font_cache,
    _color_int_to_tuple,
    _get_text_spans,
    edit_pdf,
    rewrite_pdf_with_new_text,
)


class TestColorConversion:
    """Test the color integer-to-tuple conversion."""

    def test_black(self):
        r, g, b = _color_int_to_tuple(0x000000)
        assert r == 0.0 and g == 0.0 and b == 0.0

    def test_white(self):
        r, g, b = _color_int_to_tuple(0xFFFFFF)
        assert r == 1.0 and g == 1.0 and b == 1.0

    def test_red(self):
        r, g, b = _color_int_to_tuple(0xFF0000)
        assert r == 1.0 and g == 0.0 and b == 0.0


class TestFontCache:
    """Test font extraction from a PDF."""

    def test_builds_cache_from_pdf(self):
        """Font cache should be built from the sample resume PDF."""
        resume_path = "inputs/Resume.pdf"
        if not os.path.exists(resume_path):
            return  # Skip if file is missing

        doc = fitz.open(resume_path)
        page = doc.load_page(0)
        cache = _build_font_cache(doc, page)
        doc.close()

        assert isinstance(cache, dict)
        # Should have at least one font
        assert len(cache) > 0


class TestGetTextSpans:
    """Test span extraction from a PDF page."""

    def test_extracts_spans(self):
        resume_path = "inputs/Resume.pdf"
        if not os.path.exists(resume_path):
            return

        doc = fitz.open(resume_path)
        page = doc.load_page(0)
        spans = _get_text_spans(page)
        doc.close()

        assert isinstance(spans, list)
        assert len(spans) > 0
        # Each span should have the expected keys
        span = spans[0]
        assert "text" in span
        assert "bbox" in span
        assert "font" in span
        assert "size" in span
        assert "color" in span


class TestEditPdf:
    """Test PDF editing functions."""

    def test_edit_pdf_creates_output(self):
        """Editing a PDF with replacement text should produce a valid PDF file."""
        resume_path = "inputs/Resume.pdf"
        if not os.path.exists(resume_path):
            return

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        try:
            result = edit_pdf(resume_path, "Replacement text", output_path)
            assert result == output_path
            assert os.path.exists(output_path)
            # Verify it's a valid PDF
            doc = fitz.open(output_path)
            assert len(doc) >= 1
            doc.close()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_rewrite_pdf_preserves_page_count(self):
        """Page count should be preserved after rewriting."""
        resume_path = "inputs/Resume.pdf"
        if not os.path.exists(resume_path):
            return

        doc = fitz.open(resume_path)
        original_pages = len(doc)
        doc.close()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        try:
            rewrite_pdf_with_new_text(resume_path, "Some replacement text", output_path)
            doc = fitz.open(output_path)
            assert len(doc) == original_pages
            doc.close()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_edit_pdf_overwrites_original(self):
        """When output_path is None, the original should be overwritten."""
        resume_path = "inputs/Resume.pdf"
        if not os.path.exists(resume_path):
            return

        # Copy the original to a temp location first
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        import shutil
        try:
            shutil.copy2(resume_path, tmp_path)
            result = edit_pdf(tmp_path, "Overwritten text", None)
            assert result == tmp_path
            assert os.path.exists(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
