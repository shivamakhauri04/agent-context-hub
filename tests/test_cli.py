from __future__ import annotations

from click.testing import CliRunner

from achub import __version__
from achub.cli import main


def test_version() -> None:
    """--version outputs the package version string."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_list_command() -> None:
    """'list --domain trading' outputs content IDs."""
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--domain", "trading"])
    assert result.exit_code == 0
    # Should contain at least one content ID from the trading domain
    assert "trading/" in result.output


def test_search_command() -> None:
    """'search \"stock split\"' returns some output."""
    runner = CliRunner()
    result = runner.invoke(main, ["search", "stock split"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


def test_get_command() -> None:
    """'get trading/regulations/pdt-rule/rules' outputs PDT content."""
    runner = CliRunner()
    result = runner.invoke(main, ["get", "trading/regulations/pdt-rule/rules"])
    assert result.exit_code == 0
    assert "PDT" in result.output or "pdt" in result.output.lower()


def test_validate_all() -> None:
    """'validate --all' exits with code 0 when all content is valid."""
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--all"])
    assert result.exit_code == 0


def test_regime_command() -> None:
    """'regime trading' outputs market regime information."""
    runner = CliRunner()
    result = runner.invoke(main, ["regime", "trading"])
    assert result.exit_code == 0
    assert "market" in result.output.lower() or "trading" in result.output.lower()
