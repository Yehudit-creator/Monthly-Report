from datetime import date, time, timedelta
from decimal import Decimal

import pytest

from models.report_type import ReportType
from parsing.TypeAParser import ReportParserA

HEADER = 'נ.ע. הנשר כח אדם בע"מ'


def make_line(
    date_str="07/02/2023",
    workplace="גונן",
    entry="08:00",
    exit_="16:00",
    break_="00:30",
    numbers="7.50 7.50 0.00 0.00 0.00",
) -> str:
    """בונה שורה בסדר שה-parser מצפה לו: תאריך | מקום כניסה יציאה הפסקה ומספרים."""
    return f"{date_str} | {workplace} {entry} {exit_} {break_} {numbers}"


def make_text(*lines: str) -> str:
    """מרכיב טקסט OCR: שורת חברה ואחריה שורות הימים."""
    return "\n".join([HEADER, *lines])


@pytest.fixture
def parser() -> ReportParserA:
    return ReportParserA()


# ---------- parse: הדוח כולו ----------

def test_report_type_is_a(parser):
    assert parser.parse(make_text(make_line())).report_type == ReportType.A


def test_company_name_is_first_non_digit_line(parser):
    report = parser.parse("12\n" + make_text(make_line()))
    assert report.company_name == HEADER


def test_empty_text_gives_no_days_and_no_company(parser):
    report = parser.parse("")
    assert report.days == ()
    assert report.company_name is None


def test_parse_is_deterministic(parser):
    text = make_text(make_line(), make_line(date_str="08/02/2023"))
    assert parser.parse(text).days == parser.parse(text).days


def test_summary_is_built_from_days(parser):
    text = make_text(make_line(), make_line(date_str="08/02/2023"))
    summary = parser.parse(text).summary

    assert summary.work_days_count == 2
    assert summary.hours_100 == Decimal("15.00")
    assert summary.hours_125 == Decimal("0")
    assert summary.hours_150 == Decimal("0")


# ---------- parse_day_line: שורה אחת ----------

def test_valid_line_fields(parser):
    day = parser.parse(make_text(make_line())).days[0]

    assert day.date == date(2023, 2, 7)              # הנחה: dd/mm/yyyy
    assert day.day == parser.get_day_name(day.date)  # היום נגזר מהתאריך
    assert day.workplace == "גונן"
    assert day.entry_time == time(8, 0)
    assert day.exit_time == time(16, 0)
    assert day.break_time == timedelta(minutes=30)
    assert day.total_hours == Decimal("7.5")
    assert day.hours_100 == Decimal("7.50")
    assert day.hours_125 == Decimal("0.00")
    assert day.hours_150 == Decimal("0.00")
    assert day.saturday_hours == Decimal("0.00")


def test_total_hours_is_calculated_not_taken_from_ocr(parser, capsys):
    # ה-OCR קרא 6.50 אבל הזמנים נותנים 7.5, וההפרש מודפס כאזהרה
    line = make_line(numbers="6.50 7.50 0.00 0.00 0.00")
    day = parser.parse(make_text(line)).days[0]

    assert day.total_hours == Decimal("7.5")
    assert "Warning" in capsys.readouterr().out


def test_line_without_date_is_skipped(parser):
    # החלטה: שורה בלי תאריך תקין מדולגת, בלי ניחוש מהשורות השכנות
    assert parser.parse(make_text(make_line(date_str="גונן"))).days == ()


def test_line_with_fewer_than_three_times_is_skipped(parser):
    line = "07/02/2023 | גונן 08:00 16:00 7.50 7.50 0.00 0.00 0.00"
    assert parser.parse(make_text(line)).days == ()


def test_line_with_fewer_than_five_numbers_is_skipped(parser):
    assert parser.parse(make_text(make_line(numbers="7.50 7.50 0.00"))).days == ()


def test_line_without_workplace_is_skipped(parser):
    line = "07/02/2023 08:00 16:00 00:30 7.50 7.50 0.00 0.00 0.00"
    assert parser.parse(make_text(line)).days == ()


def test_only_valid_lines_are_kept_in_order(parser):
    text = make_text(
        make_line(date_str="07/02/2023"),
        make_line(date_str="גונן"),          # בלי תאריך, מדולגת
        make_line(date_str="08/02/2023"),
    )
    days = parser.parse(text).days

    assert [d.date for d in days] == [date(2023, 2, 7), date(2023, 2, 8)]


@pytest.mark.xfail(reason="ה-parser לא מוודא שערכי השעות סבירים", strict=False)
def test_misread_number_is_not_accepted_as_hours(parser):
    # ה-OCR קרא 6.50 כ-650, והמספר נכנס כ-hours_100
    line = make_line(numbers="650 650 0.00 0.00 0.00")
    days = parser.parse(make_text(line)).days

    assert days == () or days[0].hours_100 <= 24  # 24: גבול פיזי של יממה


# ---------- calculate_total_hours ----------

@pytest.mark.parametrize(
    "entry, exit_, break_, expected",
    [
        (time(8, 0), time(16, 0), timedelta(minutes=30), Decimal("7.5")),
        (time(8, 0), time(16, 0), timedelta(0), Decimal("8")),
        (time(8, 30), time(17, 0), timedelta(minutes=30), Decimal("8")),
    ],
)
def test_calculate_total_hours(entry, exit_, break_, expected):
    assert ReportParserA.calculate_total_hours(entry, exit_, break_) == expected