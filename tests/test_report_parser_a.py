
import unittest
from datetime import time, timedelta
from decimal import Decimal
from datetime import date

from models import day
from parsing.TypeAParser import ReportParserA


class TestReportParserA(unittest.TestCase):

    def test_parse_one_day(self):
        line = (
            "2 יום ראשון | גליליון | "
            "08:00 15:00 00:30 6.50 6.50 0.00 0.00 / 0.00"
        )

        day = ReportParserA.parse_day_line(line)

        self.assertIsNotNone(day)
        self.assertEqual(day.day, "יום ראשון")
        self.assertEqual(day.workplace, "גליליון")
        self.assertEqual(day.entry_time, time(8, 0))
        self.assertEqual(day.exit_time, time(15, 0))
        self.assertEqual(day.break_time, timedelta(minutes=30))
        self.assertEqual(day.total_hours, Decimal("6.50"))
        self.assertEqual(day.hours_100, Decimal("6.50"))
        self.assertEqual(day.hours_125, Decimal("0.00"))
        self.assertEqual(day.hours_150, Decimal("0.00"))
        self.assertEqual(day.saturday_hours, Decimal("0.00"))


    def test_parse_full_report(self):
        raw_text = """
        נ.ע. הנשר כח אדם בע"מ
        2 יום ראשון | גליליון | 08:00 15:00 00:30 6.50 6.50 0.00 0.00 / 0.00
        """

        parser = ReportParserA()
        report = parser.parse(raw_text)

        self.assertIsNotNone(report)
        self.assertEqual(report.days[0].day, "יום ראשון")
        self.assertEqual(report.days[0].workplace, "גליליון")
        self.assertEqual(report.company_name, 'נ.ע. הנשר כח אדם בע"מ')
        self.assertEqual(len(report.days), 1)
        self.assertEqual(report.days[0].total_hours, Decimal("6.50"))

    def test_extract_company_name_skips_number(self):
        raw_text = """
        4
        נ.ע. הנשר כח אדם בע"מ
        """

        company_name = ReportParserA.extract_company_name(raw_text)

        self.assertEqual(company_name, 'נ.ע. הנשר כח אדם בע"מ')

    def test_extract_date(self):
        extracted_date = ReportParserA.extract_date(
            "07/10/2022 גליליון | 08:00 15:00"
        )

        self.assertEqual(extracted_date, date(2022, 10, 7))

    def test_parse_day_with_date(self):
        line = (
            "07/10/2022 יום שישי | גליליון | "
            "08:00 15:00 00:30 6.50 6.50 0.00 0.00 / 0.00"
        )

        day = ReportParserA.parse_day_line(line)

        self.assertIsNotNone(day)
        self.assertEqual(day.date, date(2022, 10, 7))

    def test_parse_day_when_weekday_is_unrecognized(self):
        line = (
            "08/10/2022 100000 גליליון | "
            "08:00 15:00 00:30 6.50 6.50 0.00 0.00 / 0.00"
        )

        day = ReportParserA.parse_day_line(line)

        self.assertIsNotNone(day)
        self.assertEqual(day.day, "יום לא מזוהה")
        self.assertEqual(day.workplace, "100000 גליליון")

    def test_calculate_total_hours(self):
        total = ReportParserA.calculate_total_hours(
            time(8, 0),
            time(15, 0),
            timedelta(minutes=30)
        )

        self.assertEqual(total, Decimal("6.5"))


if __name__ == "__main__":
    unittest.main()
