
from decimal import Decimal

from models.day_A import DayA
from models.day_B import DayB
from models.summary import Summary


def build_summary(days: tuple[DayA | DayB, ...]) -> Summary:
    work_days_count = sum(
        1 for day in days if day.total_hours > 0
    )

    hours_100 = sum(
        (day.hours_100 for day in days if isinstance(day, DayA)),
        Decimal("0"),
    ) if any(isinstance(day, DayA) for day in days) else sum(
        (day.total_hours for day in days),
        Decimal("0"),
    )

    if days and isinstance(days[0], DayA):
        hours_125 = sum(
            (day.hours_125 for day in days),
            Decimal("0"),
        )
        hours_150 = sum(
            (day.hours_150 for day in days),
            Decimal("0"),
        )
    else:
        hours_125 = None
        hours_150 = None

    return Summary(
        work_days_count=work_days_count,
        hours_100=hours_100,
        hours_125=hours_125,
        hours_150=hours_150,
    )
