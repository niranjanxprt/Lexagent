"""Pytest fixtures for LexAgent backend tests. No API keys required."""

import pytest


@pytest.fixture
def temp_data_dir(tmp_path):
    """Return a temporary directory path for session data (caller patches storage.DATA_DIR)."""
    return tmp_path / "data"


@pytest.fixture
def temp_reports_dir(tmp_path):
    """Return a temporary directory path for reports (caller patches tools.REPORTS_DIR)."""
    return tmp_path / "reports"
