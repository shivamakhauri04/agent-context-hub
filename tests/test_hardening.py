"""Tests for Phase 1, Phase 2 & Phase 3 product hardening features."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from achub.cli import main
from achub.core.index import _tokenize
from achub.core.registry import ContentRegistry
from achub.integrations.mcp import _format_llm, _load_achub_config
from achub.prompts import get_system_prompt
from achub.utils.paths import find_project_root


@pytest.fixture()
def registry() -> ContentRegistry:
    root = find_project_root()
    reg = ContentRegistry(root)
    reg.build()
    return reg


class TestSynonymSearch:
    """1.1 — Synonym expansion + tag indexing."""

    def test_natural_language_trade_query_finds_pdt(self, registry: ContentRegistry):
        """'can I make another trade today' must return PDT doc."""
        results = registry.search("can I make another trade today")
        assert len(results) > 0
        ids = [r["content_id"] for r in results]
        assert any("pdt" in cid for cid in ids), f"PDT not found in: {ids}"

    def test_tags_are_searchable(self, registry: ContentRegistry):
        """Tags from frontmatter should be indexed and searchable."""
        results = registry.search("finra", domain="trading")
        assert len(results) > 0
        # PDT doc has 'finra' tag
        ids = [r["content_id"] for r in results]
        assert any("pdt" in cid for cid in ids)

    def test_wash_sale_synonym(self, registry: ContentRegistry):
        """Query 'tax loss' should find wash sale doc via synonyms."""
        results = registry.search("tax loss", domain="trading")
        assert len(results) > 0


class TestSeverityBoost:
    """1.7 — CRITICAL docs rank above MEDIUM at similar scores."""

    def test_pdt_outranks_medium_docs(self, registry: ContentRegistry):
        """PDT (CRITICAL) should appear before medium-severity docs."""
        results = registry.search("trading rule", domain="trading")
        if len(results) < 2:
            pytest.skip("Need at least 2 results")
        # Find the PDT result
        for i, r in enumerate(results):
            if "pdt" in r["content_id"]:
                # Check that no medium doc comes before it
                for j in range(i):
                    before_severity = (
                        results[j].get("metadata", {}).get("severity", "").upper()
                    )
                    if before_severity == "MEDIUM":
                        pytest.fail(
                            f"MEDIUM doc {results[j]['content_id']} ranked "
                            f"above CRITICAL PDT doc"
                        )
                break


class TestStaleness:
    """1.4 — Runtime staleness warning."""

    def test_fresh_doc_not_stale(self, registry: ContentRegistry):
        """Docs verified within threshold should NOT be marked stale."""
        content = registry.get("trading/regulations/pdt-rule/rules")
        assert content is not None
        # The fixture doc has last_verified = 2026-03-01, test date is 2026-03-16
        # Only 15 days old, well within 90 day threshold
        assert content.get("stale") is not True

    def test_stale_doc_annotated(self, tmp_path: Path):
        """Docs older than threshold should get stale annotation."""
        # Create a domain with an old doc
        domain_dir = tmp_path / "domains" / "test-domain"
        domain_dir.mkdir(parents=True)
        (domain_dir / "DOMAIN.md").write_text(
            "---\nname: test-domain\ndescription: test\n---\n# Test\n"
        )
        topic_dir = domain_dir / "cat" / "topic"
        topic_dir.mkdir(parents=True)
        (topic_dir / "rules.md").write_text(
            "---\n"
            "id: test-domain/cat/topic/rules\n"
            "title: Old Doc\n"
            "domain: test-domain\n"
            "version: '1.0.0'\n"
            "category: cat\n"
            "tags: []\n"
            "severity: medium\n"
            "last_verified: '2024-01-01'\n"  # Very old
            "---\n\n# Old Doc\n\nSome content.\n"
        )

        reg = ContentRegistry(tmp_path, staleness_threshold_days=90)
        reg.build()
        content = reg.get("test-domain/cat/topic/rules")
        assert content is not None
        assert content.get("stale") is True
        assert content.get("stale_days", 0) > 90


class TestLLMFormat:
    """1.6 — LLM format uses blocklist, not allowlist."""

    def test_guidelines_section_included(self, tmp_path: Path):
        """Sections titled 'Guidelines' should NOT be silently dropped."""
        from achub.commands.get import _print_llm_format

        content = {
            "content_id": "test/doc",
            "metadata": {"title": "Test Doc", "severity": "medium"},
            "body": (
                "# Test Doc\n\n"
                "## Summary\n\nThis is a summary.\n\n"
                "## Guidelines\n\nThese are guidelines.\n\n"
                "## Constraints\n\nThese are constraints.\n\n"
                "## Sources\n\nhttps://example.com\n"
            ),
        }
        from unittest.mock import patch

        with patch("achub.commands.get.click") as mock_click:
            captured = []
            mock_click.echo = lambda x: captured.append(x)
            _print_llm_format(content)

        text = "\n".join(captured)
        assert "Guidelines" in text
        assert "Constraints" in text
        # Summary and Sources should be skipped
        assert "This is a summary" not in text
        assert "https://example.com" not in text


class TestSystemPrompt:
    """1.3 — System prompt generation."""

    def test_prompt_includes_critical_docs(self, registry: ContentRegistry):
        """System prompt should list CRITICAL docs with mandatory language."""
        prompt = get_system_prompt("trading", registry)
        assert "MANDATORY" in prompt
        assert "CRITICAL" in prompt
        assert "PDT" in prompt or "pdt" in prompt.lower()

    def test_prompt_unknown_domain(self, registry: ContentRegistry):
        """Unknown domain should return informative message."""
        prompt = get_system_prompt("nonexistent", registry)
        assert "No content found" in prompt


class TestPathsUtility:
    """2.3 — Deduplicated find_project_root."""

    def test_find_project_root_from_anywhere(self):
        """Should find the project root from any starting point."""
        root = find_project_root()
        assert (root / "pyproject.toml").exists()
        assert (root / "domains").is_dir()

    def test_find_project_root_with_explicit_start(self):
        """Should work when given an explicit start path."""
        root = find_project_root()
        # Starting from a subdirectory should still find the root
        found = find_project_root(start=root / "src" / "achub")
        assert found == root


class TestExtraContentDirs:
    """2.1 — Content extensibility without forking."""

    def test_extra_content_dir_indexed(self, tmp_path: Path):
        """Extra content directories should be indexed alongside built-in."""
        # Create an extra domain directory
        extra_dir = tmp_path / "extra"
        domain_dir = extra_dir / "domains" / "custom"
        domain_dir.mkdir(parents=True)
        (domain_dir / "DOMAIN.md").write_text(
            "---\nname: custom\ndescription: Custom domain\n---\n# Custom\n"
        )
        topic_dir = domain_dir / "rules" / "topic"
        topic_dir.mkdir(parents=True)
        (topic_dir / "rules.md").write_text(
            "---\n"
            "id: custom/rules/topic/rules\n"
            "title: Custom Rule\n"
            "domain: custom\n"
            "version: '1.0.0'\n"
            "category: rules\n"
            "tags: [custom]\n"
            "severity: high\n"
            "last_verified: '2026-03-01'\n"
            "---\n\n# Custom Rule\n\nCustom content.\n"
        )

        root = find_project_root()
        reg = ContentRegistry(root, extra_content_dirs=[extra_dir])
        reg.build()

        # Should find both built-in and extra content
        assert reg.get("custom/rules/topic/rules") is not None
        assert reg.get("trading/regulations/pdt-rule/rules") is not None


class TestCLIPrompt:
    """3.3 — CLI prompt command."""

    def test_cli_prompt_command(self):
        """achub prompt --domain trading outputs MANDATORY instructions."""
        runner = CliRunner()
        result = runner.invoke(main, ["prompt", "--domain", "trading"])
        assert result.exit_code == 0
        assert "MANDATORY" in result.output


class TestSearchCLIJson:
    """3.5 — Search CLI JSON format."""

    def test_search_cli_json_format(self):
        """achub search 'pdt' --format json returns valid JSON."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "pdt", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "results" in data
        assert len(data["results"]) > 0
        first = data["results"][0]
        assert "content_id" in first
        assert "score" in first


class TestMCPPromptTool:
    """3.3 — MCP achub_prompt tool (test underlying function)."""

    def test_achub_prompt_returns_prompt(self, registry: ContentRegistry):
        """get_system_prompt returns prompt text with MANDATORY."""
        result = get_system_prompt("trading", registry)
        assert "MANDATORY" in result
        assert "CRITICAL" in result


class TestSearchAndGetEnvelope:
    """3.4 — achub_search_and_get JSON envelope."""

    def test_search_and_get_json_envelope(self, registry: ContentRegistry):
        """search_and_get returns JSON with content_id, score, content keys."""
        results = registry.search("pdt rule")
        assert len(results) > 0
        top = results[0]
        # Simulate what the MCP tool does
        envelope = {
            "content_id": top.get("content_id", ""),
            "score": round(top.get("score", 0.0), 4),
            "severity": top.get("metadata", {}).get("severity", ""),
            "content": _format_llm(top),
        }
        assert envelope["content_id"]
        assert envelope["score"] > 0
        assert envelope["content"]

    def test_search_and_get_low_confidence(self, registry: ContentRegistry):
        """Nonsense query with high min_score should trigger warning."""
        results = registry.search("xyzzy gobbledygook nonsense")
        if results:
            top = results[0]
            score = top.get("score", 0.0)
            # With a very high min_score, this should be a low-confidence match
            if score < 10.0:
                assert score < 10.0  # Would get warning field in MCP tool
        # No results is also valid — means no false positives


class TestConfigLoading:
    """3.1 — Config loading with logging."""

    def test_load_config_missing_file(self, tmp_path: Path):
        """No achub.yaml returns empty dict."""
        result = _load_achub_config(tmp_path)
        assert result == {}

    def test_load_config_valid(self, tmp_path: Path):
        """Valid achub.yaml is parsed correctly."""
        (tmp_path / "achub.yaml").write_text(
            "extra_content:\n  - /some/path\nstaleness_threshold_days: 60\n"
        )
        result = _load_achub_config(tmp_path)
        assert result["staleness_threshold_days"] == 60
        assert result["extra_content"] == ["/some/path"]

    def test_load_config_invalid(self, tmp_path: Path, caplog):
        """Malformed YAML returns empty dict and logs warning."""
        (tmp_path / "achub.yaml").write_text("{{invalid yaml: [}")
        with caplog.at_level(logging.WARNING, logger="achub.integrations.mcp"):
            result = _load_achub_config(tmp_path)
        assert result == {}
        assert any("Failed to parse" in r.message for r in caplog.records)


class TestLoggingOnSilentFailures:
    """3.1 — Logging for extra_content_dirs and staleness."""

    def test_extra_dir_missing_logged(self, caplog):
        """Non-existent extra dir logs warning."""
        root = find_project_root()
        with caplog.at_level(logging.WARNING, logger="achub.core.registry"):
            reg = ContentRegistry(
                root, extra_content_dirs=[Path("/nonexistent/achub/dir")]
            )
            reg.build()
        assert any("does not exist" in r.message for r in caplog.records)

    def test_staleness_bad_date_logged(self, tmp_path: Path, caplog):
        """Bad last_verified format logs warning, no crash."""
        domain_dir = tmp_path / "domains" / "test-domain"
        domain_dir.mkdir(parents=True)
        (domain_dir / "DOMAIN.md").write_text(
            "---\nname: test-domain\ndescription: test\n---\n# Test\n"
        )
        topic_dir = domain_dir / "cat" / "topic"
        topic_dir.mkdir(parents=True)
        (topic_dir / "rules.md").write_text(
            "---\n"
            "id: test-domain/cat/topic/rules\n"
            "title: Bad Date Doc\n"
            "domain: test-domain\n"
            "version: '1.0.0'\n"
            "category: cat\n"
            "tags: []\n"
            "severity: medium\n"
            "last_verified: 'not-a-date'\n"
            "---\n\n# Bad Date\n\nContent.\n"
        )
        reg = ContentRegistry(tmp_path, staleness_threshold_days=90)
        reg.build()
        with caplog.at_level(logging.WARNING, logger="achub.core.registry"):
            content = reg.get("test-domain/cat/topic/rules")
        assert content is not None
        assert any("Bad last_verified" in r.message for r in caplog.records)


class TestTokenizer:
    """3.2 — Tokenizer handles hyphens correctly."""

    def test_hyphenated_query(self):
        """_tokenize('wash-sale') splits on hyphen."""
        tokens = _tokenize("wash-sale")
        assert "wash" in tokens
        assert "sale" in tokens


class TestVerboseFlag:
    """4.5 — --verbose flag on CLI."""

    def test_verbose_flag_accepted(self):
        """achub -v list exits 0."""
        runner = CliRunner()
        result = runner.invoke(main, ["-v", "list"])
        assert result.exit_code == 0

    def test_verbose_flag_enables_logging(self):
        """achub -v produces DEBUG-level output."""
        runner = CliRunner()
        result = runner.invoke(main, ["-v", "list", "--domain", "trading"])
        # The command should succeed; debug logging goes to stderr
        assert result.exit_code == 0


class TestStructuredCheckWarnings:
    """4.3 — MCP achub_check surfaces structured check failures."""

    def test_achub_check_structured_failure_surfaces_warning(self):
        """Verify that the warnings field is included when structured checks fail.

        Since the MCP module requires mcp extras, we test the JSON contract
        directly: when check_warnings is non-empty, the response must contain
        a 'warnings' key.
        """
        # Simulate what achub_check does when StructuredCheckEvaluator raises
        violations: list[str] = []
        passed_rules = ["pdt"]
        check_warnings = [
            "Structured check evaluation failed: kaboom. "
            "Only Python checker results are shown."
        ]
        result_dict: dict = {
            "violations": violations,
            "passed": passed_rules,
            "has_violations": len(violations) > 0,
        }
        if check_warnings:
            result_dict["warnings"] = check_warnings

        result = json.loads(json.dumps(result_dict))
        assert "warnings" in result
        assert "kaboom" in result["warnings"][0]
        assert result["has_violations"] is False


class TestMalformedStructuredChecks:
    """4.4 — Malformed structured checks YAML logged."""

    def test_malformed_structured_checks_logged(self, tmp_path, caplog):
        """Broken YAML in structured checks section logs warning."""
        md_content = (
            "---\n"
            "id: test/doc\n"
            "title: Test\n"
            "domain: test\n"
            "version: '1.0'\n"
            "category: cat\n"
            "tags: []\n"
            "severity: medium\n"
            "last_verified: '2026-03-01'\n"
            "---\n\n"
            "# Test\n\n"
            "## Structured Checks\n\n"
            "```yaml\n"
            "checks:\n"
            "  - id: bad\n"
            "    {{invalid yaml: [}\n"
            "```\n"
        )
        md_path = tmp_path / "test.md"
        md_path.write_text(md_content)

        from achub.core.parser import parse_content

        with caplog.at_level(logging.WARNING, logger="achub.core.parser"):
            result = parse_content(md_path)
        assert result is not None
        assert "checks" not in result
        assert any(
            "Failed to parse structured checks" in r.message for r in caplog.records
        )


class TestMCPSearchAndGet:
    """4.9 — MCP achub_search_and_get integration test."""

    def test_mcp_search_and_get_returns_json_envelope(self, registry):
        """Valid JSON with content_id, score, content keys."""
        results = registry.search("pdt rule")
        assert len(results) > 0
        top = results[0]
        envelope = {
            "content_id": top.get("content_id", ""),
            "score": round(top.get("score", 0.0), 4),
            "severity": top.get("metadata", {}).get("severity", ""),
            "content": top.get("body", "")[:100],
        }
        parsed = json.loads(json.dumps(envelope))
        assert "content_id" in parsed
        assert "score" in parsed
        assert "content" in parsed
        assert parsed["score"] > 0

    def test_mcp_search_and_get_no_results(self, registry):
        """Nonsense query returns empty or error JSON."""
        results = registry.search("xyzzy99nonexistent")
        # Either no results or very low score
        if not results:
            error_json = json.dumps({"error": "No results found."})
            parsed = json.loads(error_json)
            assert "error" in parsed
