from dataclasses import replace
from decimal import Decimal

from services.randomness import make_rng

from config import SHIFT_MODES
from models.day_B import DayB
from models.report import Report
from models.summary import Summary
from services.transformations.base_transformation_strategy import (
    BaseTransformationStrategy,
)
from services.transformations.time_utils import (
    calculate_total_hours,
    shift_time,
    wraps_midnight,
)


class TypeBTransformationStrategy(BaseTransformationStrategy):
    """Transformation rules for report type B."""

    def transform(self, report: Report, offset_minutes: int) -> Report:
        new_days = []

        for day in report.days:
            if not isinstance(day, DayB):
                raise ValueError("Expected DayB in report type B.")

            # יום בלי כניסה או בלי יציאה: לא נוגעים
            if day.entry_time is None or day.exit_time is None:
                new_days.append(day)
                continue

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

            # מקרי קצה: חצות, או יציאה שהפכה למוקדמת מהכניסה
            if (
                wraps_midnight(day.entry_time, new_entry, offset_minutes)
                or wraps_midnight(day.exit_time, new_exit, offset_minutes)
                or (day.exit_time > day.entry_time and new_exit <= new_entry)
            ):
                new_days.append(day)
                continue

            # סה"כ חדש = הסה"כ המקורי + השינוי במשך
            delta = calculate_total_hours(new_entry, new_exit) - calculate_total_hours(
                day.entry_time, day.exit_time
            )
            new_total = day.total_hours + delta

            new_days.append(
                replace(
                    day,
                    entry_time=new_entry,
                    exit_time=new_exit,
                    total_hours=new_total,
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
        new_days: list[DayB],
    ) -> Summary | None:
        """מעדכן את הסיכום שבראש הדוח לפי השינוי בסך השעות."""

        summary = report.summary

        if summary is None:
            return None

        # סכום השעות לפני השינוי
        old_total = sum(
            (day.total_hours for day in report.days),
            Decimal("0"),
        )

        # סכום השעות אחרי השינוי
        new_total = sum(
            (day.total_hours for day in new_days),
            Decimal("0"),
        )

        # מחשבים רק את ההפרש ומוסיפים אותו לסיכום המקורי
        diff = new_total - old_total

        return replace(
            summary,
            hours_100=summary.hours_100 + diff,
        )