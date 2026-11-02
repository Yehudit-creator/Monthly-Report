
from dataclasses import replace

from models.day_B import DayB
from models.report import Report
from services.transformations.base_transformation_strategy import (
    BaseTransformationStrategy,
)
from services.transformations.time_utils import shift_time


class TypeBTransformationStrategy(BaseTransformationStrategy):
    """Transformation rules for report type B."""

    def transform(
        self,
        report: Report,
        offset_minutes: int
    ) -> Report:

        new_days = []

        for day in report.days:
            if not isinstance(day, DayB):
                raise ValueError(
                    "Expected DayB in report type B."
                )

            # Shift entry time only if it exists
            new_entry = (
                shift_time(day.entry_time, offset_minutes)
                if day.entry_time is not None
                else None
            )

            # Shift exit time only if it exists
            new_exit = (
                shift_time(day.exit_time, offset_minutes)
                if day.exit_time is not None
                else None
            )

            # Create a new day without changing the original
            new_day = replace(
                day,
                entry_time=new_entry,
                exit_time=new_exit,
            )

            new_days.append(new_day)

        # Create a new report without changing the original
        return replace(
            report,
            days=new_days
        )