"""Tests for feedback.py — feedback command and persistence."""
from __future__ import annotations

from pathlib import Path

from achub.commands.feedback import _feedback_path, _load_feedback, _save_feedback


class TestFeedbackPath:
    def test_feedback_path_escaping(self):
        """Slashes in content_id are replaced with double underscores."""
        path = _feedback_path(Path("/project"), "a/b/c")
        assert path.name == "a__b__c.yaml"
        assert path.parent.name == "feedback"


class TestLoadFeedback:
    def test_load_feedback_missing_file(self, tmp_path: Path):
        """Non-existent path returns empty list."""
        result = _load_feedback(tmp_path / "nonexistent.yaml")
        assert result == []


class TestFeedbackCommand:
    def test_feedback_creates_file(self, tmp_path: Path):
        """CLI creates .achub/feedback/*.yaml."""
        fb_path = tmp_path / ".achub" / "feedback" / "test__doc.yaml"
        entries = _load_feedback(fb_path)
        assert entries == []

        _save_feedback(fb_path, [{"rating": "up", "timestamp": "2026-03-16T00:00:00+00:00"}])
        assert fb_path.exists()
        loaded = _load_feedback(fb_path)
        assert len(loaded) == 1
        assert loaded[0]["rating"] == "up"

    def test_feedback_appends_entries(self, tmp_path: Path):
        """Multiple saves append, don't overwrite."""
        fb_path = tmp_path / ".achub" / "feedback" / "test__doc.yaml"
        entries = [{"rating": "up", "timestamp": "2026-03-16T00:00:00+00:00"}]
        _save_feedback(fb_path, entries)

        entries = _load_feedback(fb_path)
        entries.append({"rating": "down", "timestamp": "2026-03-16T01:00:00+00:00"})
        _save_feedback(fb_path, entries)

        loaded = _load_feedback(fb_path)
        assert len(loaded) == 2
        assert loaded[0]["rating"] == "up"
        assert loaded[1]["rating"] == "down"

    def test_feedback_down_rating(self, tmp_path: Path):
        """Down rating stored correctly."""
        fb_path = tmp_path / ".achub" / "feedback" / "test__doc.yaml"
        _save_feedback(
            fb_path, [{"rating": "down", "timestamp": "2026-03-16T00:00:00+00:00"}]
        )
        loaded = _load_feedback(fb_path)
        assert loaded[0]["rating"] == "down"
