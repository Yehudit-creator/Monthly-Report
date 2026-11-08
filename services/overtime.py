from decimal import Decimal

from config import OVERTIME_125_UNTIL, REGULAR_HOURS

ZERO = Decimal("0")


def split_hours(total_hours: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """מחלק סך שעות של יום חול ל-100%, 125% ו-150%."""
    # עד REGULAR_HOURS: 100%
    regular = min(total_hours, REGULAR_HOURS)

    # מעל REGULAR_HOURS ועד OVERTIME_125_UNTIL: 125%
    overtime_125 = min(
        max(total_hours - REGULAR_HOURS, ZERO),
        OVERTIME_125_UNTIL - REGULAR_HOURS,
    )

    # מעל OVERTIME_125_UNTIL: 150%
    overtime_150 = max(total_hours - OVERTIME_125_UNTIL, ZERO)

    return regular, overtime_125, overtime_150
