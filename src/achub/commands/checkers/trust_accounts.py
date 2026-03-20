"""Trust accounts compliance checker."""
from __future__ import annotations


def check_trust_accounts(portfolio: dict) -> list[str]:
    """Check trust account compliance rules.

    Skips if ``trust_config`` is absent or ``is_trust_account`` is false.  Flags:
    - CRITICAL if trustee has self-dealing transaction
    - CRITICAL if trust assets exceed estate tax exclusion
    - WARNING if irrevocable trust where trustee is also beneficiary
    - WARNING if generation-skipping transfer without GST exemption tracking
    - WARNING if annual distribution rate exceeds 7%
    - INFO if revocable trust (assets remain in grantor's taxable estate)
    """
    violations: list[str] = []

    config = portfolio.get("trust_config")
    if not config:
        return violations

    if not config.get("is_trust_account", False):
        return violations

    trust_type = config.get("trust_type", "revocable")

    if config.get("has_self_dealing_transaction", False):
        violations.append(
            "TRUST CRITICAL: Self-dealing transaction detected -- "
            "trustee cannot transact for personal benefit under "
            "Uniform Trust Code fiduciary duties."
        )

    assets = config.get("trust_assets_usd", 0)
    exclusion = config.get("estate_tax_exclusion_usd", 13610000)
    if assets > exclusion:
        violations.append(
            f"TRUST CRITICAL: Trust assets ${assets:,.0f} exceed estate "
            f"tax exclusion ${exclusion:,.0f} -- estate tax exposure "
            f"of ${assets - exclusion:,.0f} requires planning."
        )

    if trust_type == "irrevocable" and config.get("trustee_is_beneficiary", False):
        violations.append(
            "TRUST WARNING: Irrevocable trust where trustee is also "
            "beneficiary -- potential conflict of interest that may "
            "invite IRS scrutiny."
        )

    if config.get("generation_skipping_transfer", False):
        gst_used = config.get("gst_exemption_used_usd", 0)
        if gst_used == 0:
            violations.append(
                "TRUST WARNING: Generation-skipping transfer enabled "
                "but GST exemption tracking shows $0 used -- ensure "
                "GSTT exemption is properly allocated."
            )

    dist_pct = config.get("annual_distribution_pct", 0)
    if dist_pct > 7:
        violations.append(
            f"TRUST WARNING: Annual distribution rate {dist_pct:.1f}% "
            f"exceeds 7% -- may not be sustainable and could erode "
            f"trust corpus over time."
        )

    if trust_type == "revocable":
        violations.append(
            "TRUST INFO: Revocable trust -- assets remain in the "
            "grantor's taxable estate. No estate tax benefit until "
            "trust becomes irrevocable."
        )

    return violations
