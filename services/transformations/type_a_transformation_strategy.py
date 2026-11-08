from dataclasses import replace
from decimal import Decimal

from services.randomness import make_rng

from config import SHIFT_MODES, SUMMARY_SUM_FIELDS
from models.day_A import DayA
from models.report import Report
from models.summary import Summary
from services.overtime import split_hours
from services.transformations.base_transformation_strategy import (
    BaseTransformationStrategy,
)
from services.transformations.time_utils import (
    calculate_total_hours,
    shift_time,
    wraps_midnight,
)


class TypeATransformationStrategy(BaseTransformationStrategy):
    """Transformation rules for report type A."""

    def transform(self, report: Report, offset_minutes: int) -> Report:
        new_days = []

        for day in report.days:
            if not isinstance(day, DayA):
                raise ValueError("Expected DayA in report type A.")

            # בוחרים באקראי מה להזיז ביום הזה
            mode = make_rng(report.employee_name, day.date).choice(SHIFT_MODES)

            new_entry = (
                shift_time(day.entry_time, offset_minutes)
                if mode in ("both", "entry_only")
                else day.entry_time
            )

            new_exit = (
                shift_time(day.exit_time, offset_minutes)
                if mode in ("both", "exit_only")
                else day.exit_time
            )

            # מקרי קצה: חצות או יציאה שהפכה למוקדמת מהכניסה
            if (
                wraps_midnight(day.entry_time, new_entry, offset_minutes)
                or wraps_midnight(day.exit_time, new_exit, offset_minutes)
                or (day.exit_time > day.entry_time and new_exit <= new_entry)
            ):
                new_days.append(day)
                continue

            # מחשבים את השינוי במשך העבודה
            delta = calculate_total_hours(new_entry, new_exit) - calculate_total_hours(
                day.entry_time, day.exit_time
            )

            new_total = day.total_hours + delta

            if new_total <= 0:
                new_days.append(day)
                continue

            # חלוקה מחדש ל-100%, 125%, 150%
            hours_100, hours_125, hours_150 = split_hours(new_total)

            new_days.append(
                replace(
                    day,
                    entry_time=new_entry,
                    exit_time=new_exit,
                    total_hours=new_total,
                    hours_100=hours_100,
                    hours_125=hours_125,
                    hours_150=hours_150,
                )
            )

        return replace(
            report,
            days=tuple(new_days),
            summary=self._update_summary(report, new_days),
        )

    @staticmethod
    def _update_summary(
        report: Report,
        new_days: list[DayA],
    ) -> Summary | None:

        summary = report.summary

        if summary is None:
            return None

        if summary.hours_125 is None or summary.hours_150 is None:
            raise ValueError(
                "Summary of type A must include 125% and 150% hours."
            )

        # מחשבים את השינוי בכל אחת מעמודות השעות
        changes = {}

        for field_name in SUMMARY_SUM_FIELDS:
            old_sum = sum(
                (getattr(day, field_name) for day in report.days),
                Decimal("0"),
            )

            new_sum = sum(
                (getattr(day, field_name) for day in new_days),
                Decimal("0"),
            )

            diff = new_sum - old_sum

            changes[field_name] = getattr(summary, field_name) + diff

        return replace(summary, **changes)