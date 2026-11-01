import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from models.day_A import DayA
from models.report import Report
from parsing.BaseParser import ReportParser


class ReportParserA(ReportParser):

    @staticmethod
    def extract_company_name(raw_text: str) -> str | None:
        """Extract the company name from OCR text."""

        for line in raw_text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.isdigit():
                continue

            return line

        return None



    def parse(self, raw_text: str) -> Report:
        """Parse OCR text into a Report containing DayA records."""

        company_name = self.extract_company_name(raw_text)
        employee_name = self.generate_employee_name()

        days = []

        for line in raw_text.splitlines():
            line = line.strip()

            if not line:
                continue

            day_record = self.parse_day_line(self, line)

            if day_record is not None:
                days.append(day_record)

        return Report(
            employee_name=employee_name,
            days=days,
            company_name=company_name,
        )

    @staticmethod
    def parse_day_line(self,line: str) -> DayA | None:
        """Parse one OCR line into a DayA object."""

        # Extract the date — it is required
        day_date = self.extract_date(line)

        if day_date is None:
            return None

        # Calculate the weekday from the date
        day = self.get_day_name(day_date)

        # Extract the working times
        times = re.findall(r"(?<!\d)(?:[01]?\d|2[0-3]):[0-5]\d(?!\d)", line)

        if len(times) < 3:
            return None


        first_time_index = line.find(times[0])
        date_match = ReportParser.DATE_RE.search(line)
        workplace_text = line[date_match.end():first_time_index]


        parts = [
            part.strip()
            for part in workplace_text.split("|")
            if part.strip()
        ]

        workplace = parts[-1] if parts else ""
        workplace = workplace.strip(" \t:₪\"'")

        if not workplace:
            return None

        try:
            entry_time = time.fromisoformat(times[0])
            exit_time = time.fromisoformat(times[1])

            break_hours, break_minutes = map(
                int, times[2].split(":")
            )

            break_time = timedelta(
                hours=break_hours,
                minutes=break_minutes
            )

            calculated_hours = ReportParserA.calculate_total_hours(
                entry_time,
                exit_time,
                break_time
            )

            # Extract numeric values after the break time
            break_index = line.find(times[2])
            values_text = line[break_index + len(times[2]):]

            numbers = re.findall(
                r"(?<![\d.])\d+(?:\.\d{2})?(?!\d)",
                values_text
            )

            if len(numbers) < 5:
                return None

            total_hours = Decimal(numbers[0])
            hours_100 = Decimal(numbers[1])
            hours_125 = Decimal(numbers[2])
            hours_150 = Decimal(numbers[3])
            saturday_hours = Decimal(numbers[4])

            if calculated_hours != total_hours:
                print(
                    f"Warning: OCR total hours ({total_hours}) "
                    f"do not match calculated hours "
                    f"({calculated_hours})"
                )

            return DayA(
                date=day_date,
                day=day,
                entry_time=entry_time,
                exit_time=exit_time,
                total_hours=calculated_hours,
                workplace=workplace,
                break_time=break_time,
                hours_100=hours_100,
                hours_125=hours_125,
                hours_150=hours_150,
                saturday_hours=saturday_hours,
            )

        except (ValueError, OverflowError):
            return None

    @staticmethod
    def calculate_total_hours(
        entry_time: time,
        exit_time: time,
        break_time: timedelta
    ) -> Decimal:
        """Calculate net working hours after subtracting the break."""

        entry_minutes = entry_time.hour * 60 + entry_time.minute
        exit_minutes = exit_time.hour * 60 + exit_time.minute

        worked_minutes = exit_minutes - entry_minutes
        break_minutes = int(break_time.total_seconds() // 60)

        net_minutes = worked_minutes - break_minutes

        return Decimal(net_minutes) / Decimal(60)
