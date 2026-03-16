"""achub regime — Market regime and trading day information."""
from __future__ import annotations

from datetime import date, datetime, time

import click

from achub.utils.formatting import print_regime

# NYSE holidays for 2026
_NYSE_HOLIDAYS_2026 = {
    date(2026, 1, 1),   # New Year's Day
    date(2026, 1, 19),  # Martin Luther King Jr. Day
    date(2026, 2, 16),  # Presidents' Day
    date(2026, 4, 3),   # Good Friday
    date(2026, 5, 25),  # Memorial Day
    date(2026, 7, 3),   # Independence Day (observed, July 4 is Saturday)
    date(2026, 9, 7),   # Labor Day
    date(2026, 11, 26), # Thanksgiving Day
    date(2026, 12, 25), # Christmas Day
}

# Known half days (early close at 1:00 PM ET)
_NYSE_HALF_DAYS_2026 = {
    date(2026, 7, 2),   # Day before Independence Day (observed)
    date(2026, 11, 27), # Day after Thanksgiving
    date(2026, 12, 24), # Christmas Eve (Thursday)
}


def _get_market_phase(now: datetime, is_half_day: bool) -> str:
    """Determine market phase based on ET time.

    Phases:
        pre-market:  04:00 - 09:30
        open:        09:30 - 16:00 (or 13:00 on half days)
        post-market: 16:00 - 20:00 (or 13:00 - 17:00 on half days)
        closed:      otherwise
    """
    t = now.time()
    close_time = time(13, 0) if is_half_day else time(16, 0)
    post_end = time(17, 0) if is_half_day else time(20, 0)

    if time(4, 0) <= t < time(9, 30):
        return "pre-market"
    elif time(9, 30) <= t < close_time:
        return "open"
    elif close_time <= t < post_end:
        return "post-market"
    else:
        return "closed"


def _is_trading_day(d: date) -> bool:
    """Check if a date is a trading day (weekday and not a holiday)."""
    if d.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    if d in _NYSE_HOLIDAYS_2026:
        return False
    return True


@click.command()
@click.argument("domain")
@click.option(
    "--date",
    "date_str",
    default=None,
    help="Date to check in YYYY-MM-DD format. Defaults to today.",
)
@click.pass_context
def regime(ctx, domain: str, date_str: str | None):
    """Show market regime and trading day context.

    Returns whether a date is a trading day, market phase, and half-day status.

    Example: achub regime trading --date 2026-07-02
    """
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            click.echo(f"Invalid date format: {date_str}. Use YYYY-MM-DD.", err=True)
            raise SystemExit(1)
        # For a specific date without time, report phase as of market hours summary
        now = datetime.combine(target_date, time(12, 0))
    else:
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo("America/New_York"))
            target_date = now.date()
        except ImportError:
            now = datetime.utcnow()
            target_date = now.date()

    trading_day = _is_trading_day(target_date)
    is_half_day = target_date in _NYSE_HALF_DAYS_2026
    is_holiday = target_date in _NYSE_HOLIDAYS_2026

    if trading_day:
        phase = _get_market_phase(now, is_half_day)
    else:
        phase = "closed"

    regime_info = {
        "regime": f"{domain} market regime",
        "date": str(target_date),
        "day_of_week": target_date.strftime("%A"),
        "is_trading_day": str(trading_day),
        "is_half_day": str(is_half_day),
        "is_holiday": str(is_holiday),
        "market_phase": phase,
    }

    print_regime(regime_info)
