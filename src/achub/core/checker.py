"""Structured check evaluator for agent-context-hub.

Evaluates machine-parseable check conditions from content documents using a
safe expression parser (no eval()).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CheckResult:
    id: str
    passed: bool
    severity: str
    message: str


class StructuredCheckEvaluator:
    """Evaluate structured check conditions against a context dict."""

    def evaluate_checks(
        self, checks: list[dict], context: dict
    ) -> list[CheckResult]:
        results = []
        for check in checks:
            check_id = check.get("id", "unknown")
            condition = check.get("condition", "")
            severity = check.get("severity", "medium")
            message = check.get("message", "Check failed")
            try:
                passed = self._evaluate_condition(condition, context)
            except Exception:
                passed = False
                message = f"{message} (condition evaluation error)"
            results.append(CheckResult(
                id=check_id, passed=passed, severity=severity, message=message
            ))
        return results

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        tokens = self._tokenize(condition)
        pos, result = self._parse_or(tokens, 0, context)
        return result

    def _tokenize(self, condition: str) -> list[str]:
        pattern = (
            r"""(\band\b|\bor\b|\bnot\b|>=|<=|!=|==|>|<"""
            r"""|\(|\)|'[^']*'|"[^"]*"|\d+\.?\d*|\w+)"""
        )
        return re.findall(pattern, condition, re.IGNORECASE)

    def _parse_or(
        self, tokens: list[str], pos: int, ctx: dict
    ) -> tuple[int, bool]:
        pos, left = self._parse_and(tokens, pos, ctx)
        while pos < len(tokens) and tokens[pos].upper() == "OR":
            pos += 1
            pos, right = self._parse_and(tokens, pos, ctx)
            left = left or right
        return pos, left

    def _parse_and(
        self, tokens: list[str], pos: int, ctx: dict
    ) -> tuple[int, bool]:
        pos, left = self._parse_not(tokens, pos, ctx)
        while pos < len(tokens) and tokens[pos].upper() == "AND":
            pos += 1
            pos, right = self._parse_not(tokens, pos, ctx)
            left = left and right
        return pos, left

    def _parse_not(
        self, tokens: list[str], pos: int, ctx: dict
    ) -> tuple[int, bool]:
        if pos < len(tokens) and tokens[pos].upper() == "NOT":
            pos += 1
            pos, val = self._parse_not(tokens, pos, ctx)
            return pos, not val
        return self._parse_comparison(tokens, pos, ctx)

    def _parse_comparison(
        self, tokens: list[str], pos: int, ctx: dict
    ) -> tuple[int, bool]:
        if pos < len(tokens) and tokens[pos] == "(":
            pos += 1  # skip (
            pos, result = self._parse_or(tokens, pos, ctx)
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1  # skip )
            return pos, result

        pos, left = self._parse_value(tokens, pos, ctx)
        if pos < len(tokens) and tokens[pos] in ("==", "!=", "<", ">", ">=", "<="):
            op = tokens[pos]
            pos += 1
            pos, right = self._parse_value(tokens, pos, ctx)
            return pos, self._compare(left, op, right)
        # Bare value: truthy check
        return pos, bool(left)

    def _parse_value(self, tokens: list[str], pos: int, ctx: dict):
        if pos >= len(tokens):
            return pos, None
        token = tokens[pos]
        # String literal
        if (token.startswith("'") and token.endswith("'")) or \
           (token.startswith('"') and token.endswith('"')):
            return pos + 1, token[1:-1]
        # Number
        try:
            if "." in token:
                return pos + 1, float(token)
            return pos + 1, int(token)
        except ValueError:
            pass
        # Boolean keywords
        if token.upper() in ("TRUE",):
            return pos + 1, True
        if token.upper() in ("FALSE",):
            return pos + 1, False
        # Variable lookup from context
        return pos + 1, ctx.get(token, None)

    def _compare(self, left, op: str, right) -> bool:
        if left is None or right is None:
            return op == "!=" if (left is None) != (right is None) else op == "=="
        try:
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            # Numeric comparisons
            left_n = float(left) if not isinstance(left, (int, float)) else left
            right_n = float(right) if not isinstance(right, (int, float)) else right
            if op == "<":
                return left_n < right_n
            if op == ">":
                return left_n > right_n
            if op == ">=":
                return left_n >= right_n
            if op == "<=":
                return left_n <= right_n
        except (TypeError, ValueError):
            return False
        return False
