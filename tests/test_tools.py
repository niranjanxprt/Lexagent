"""Tests for app.tools.save_report: file content and metadata."""

import pytest

from app import tools
from app.tools import save_report


def test_save_report_creates_file_with_metadata_and_content(tmp_path):
    tools.REPORTS_DIR = tmp_path / "reports"
    content = "## Executive Summary\n\nContent here."
    path = save_report("sid-1", "My goal", content)
    assert path
    full_path = tools.REPORTS_DIR / "sid-1.md"
    assert full_path.exists()
    text = full_path.read_text(encoding="utf-8")
    assert "Legal Research Report" in text
    assert "My goal" in text
    assert "## Executive Summary" in text
    assert "Content here." in text
    assert "---" in text
