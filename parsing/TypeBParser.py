
import re
from datetime import date, datetime, time
from decimal import Decimal

from models.day_B import DayB
from models.report import Report
from parsing.BaseParser import ReportParser


class ReportParserB(ReportParser):



    @staticmethod
    def extract_times(line: str) -> list[time]:
        """Extract and normalize working times from an OCR line."""

        times = []

        # Find times with a colon, such as 8:30 or 12:00
        matches = re.findall(
            r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)",
            line
        )

        for hour, minute in matches:
            try:
                times.append(
                    time(int(hour), int(minute))
                )
            except ValueError:
                continue

        # If fewer than two times were found,
        # look for times without a colon, such as 1200
        if len(times) < 2:
            matches = re.findall(
                r"(?<!\d)(\d{4})(?!\d)",
                line
            )

            for value in matches:
                hour = int(value[:2])
                minute = int(value[2:])

                try:
                    times.append(time(hour, minute))
                except ValueError:
                    continue

        return sorted(set(times))

    def parse(self, raw_text: str) -> Report:
        """Parse OCR text into a Report containing DayB records."""

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
            company_name=None,
        )

    @staticmethod
    def parse_day_line(self,line: str) -> DayB | None:
        """Parse one OCR line into a DayB object."""

        # Extract the date
        day_date = self.extract_date(line)

        if day_date is None:
            return None

        # Calculate the weekday
        day = self.get_day_name(day_date)

        # Check if the date is Saturday
        is_saturday = day_date.weekday() == 5

        # Identify holidays
        notes = ""

        if "ערב" in line and "השנה" in line:
            notes = "ערב ראש השנה"
        elif "השנה" in line:
            notes = "ראש השנה"

        is_holiday = bool(notes)

        # Saturday or holiday: no working hours
        if is_saturday or is_holiday:
            return DayB(
                date=day_date,
                day=day,
                entry_time=None,
                exit_time=None,
                total_hours=Decimal("0"),
                notes=notes,
            )

        # Extract working times
        parsed_times = ReportParserB.extract_times(line)

        if len(parsed_times) < 2:
            print(
                f"Warning: Could not identify working times "
                f"for {day_date}. Line: {line}"
            )
            return None

        entry_time = parsed_times[0]
        exit_time = parsed_times[-1]

        # Extract total hours from the text before the first time
        first_time_index = line.find(
            str(parsed_times[0].strftime("%H:%M"))
        )

        before_times = line[:first_time_index]

        number_match = re.search(
            r"(?<![\d.])(\d+\.\d{2}|\d{3})(?!\d)",
            before_times
        )

        if not number_match:
            print(
                f"Warning: Could not identify total hours "
                f"for {day_date}. Line: {line}"
            )
            return None

        total_text = number_match.group(1)

        # OCR sometimes reads 3.50 as 350
        if "." not in total_text:
            total_text = (
                total_text[:-2] + "." + total_text[-2:]
            )

        total_hours = Decimal(total_text)

        return DayB(
            date=day_date,
            day=day,
            entry_time=entry_time,
            exit_time=exit_time,
            total_hours=total_hours,
            notes=notes,
        )
