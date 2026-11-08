from dataclasses import dataclass

from models.report_type import ReportType


@dataclass(frozen=True)
class Column:
    title: str        # header text, exactly as in the original
    field: str        # which AttendanceRow attribute goes in this column


@dataclass(frozen=True)
class ReportLayout:
    columns: tuple[Column, ...]
    summary_on_top: bool


LAYOUTS: dict[ReportType, ReportLayout] = {
    ReportType.B: ReportLayout(
        columns=(Column("תאריך", "date"), Column("יום בשבוע", "day"),
                 Column("שעת כניסה", "entry_time"), Column("שעת יציאה", "exit_time"),
                 Column('סה"כ שעות', "total_hours"), Column("הערות", "notes")),
        summary_on_top=True,
    ),
    ReportType.A: ReportLayout(
        columns=(Column("תאריך", "date"), Column("יום", "day"), Column("מקום", "workplace"),
                 Column("כניסה", "entry_time"), Column("יציאה", "exit_time"), Column("הפסקה", "break_time"),
                 Column('סה"כ', "total_hours"), Column("100%", "hours_100"),
                 Column("125%", "hours_125"), Column("150%", "hours_150")),
        summary_on_top=False,
    ),
}