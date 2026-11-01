from dataclasses import replace
from datetime import timedelta
from decimal import Decimal

from models.day_A import DayA
from models.report import Report
from services.transformations.base_transformation_strategy import (
    BaseTransformationStrategy,
)
from services.transformations.time_utils import shift_time


class TypeATransformationStrategy(BaseTransformationStrategy):
    """Transformation rules for report type A."""

    def transform(
        self,
        report: Report,
        offset_minutes: int
    ) -> Report:
        new_days = []

        for day in report.days:
            if not isinstance(day, DayA):
                raise ValueError(
                    "Expected DayA in report type A."
                )

            # Shift entry and exit times
            new_entry = shift_time(
                day.entry_time,
                offset_minutes
            )

            new_exit = shift_time(
                day.exit_time,
                offset_minutes
            )

            # Calculate working hours after subtracting the break
            worked_minutes = (
                new_exit.hour * 60 + new_exit.minute
                - new_entry.hour * 60 - new_entry.minute
            )

            break_minutes = int(
                day.break_time.total_seconds() // 60
            )

            net_minutes = worked_minutes - break_minutes

            if net_minutes < 0:
                raise ValueError(
                    "Break time exceeds working time."
                )

            new_total_hours = (
                Decimal(net_minutes) / Decimal(60)
            )

            # Create a new day without changing the original
            new_day = replace(
                day,
                entry_time=new_entry,
                exit_time=new_exit,
                total_hours=new_total_hours,
            )

            new_days.append(new_day)

        # Create a new report without changing the original report
        return replace(
            report,
            days=new_days
        )