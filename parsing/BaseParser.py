import re
from abc import ABC, abstractmethod
import random

from models.report import Report
from datetime import date, datetime, time


class ReportParser(ABC):
    DATE_RE = re.compile(r"(?<!\d)(\d{1,2}/\d{1,2}/(?:\d{4}|\d{2}))(?!\d)")

    @staticmethod
    def get_day_name(day_date: date) -> str:
        """Calculate the weekday name from a date."""

        days = [
            "יום שני",
            "יום שלישי",
            "יום רביעי",
            "יום חמישי",
            "יום שישי",
            "יום שבת",
            "יום ראשון",
        ]

        return days[day_date.weekday()]

    @abstractmethod
    def parse(self, raw_text: str) -> Report:
        """Convert OCR text into a Report model."""
        pass

    @staticmethod
    def extract_date(line: str) -> date | None:
        """Extract a date in DD/MM/YYYY or DD/MM/YY format."""
        match = ReportParser.DATE_RE.search(line)
        if not match:
            return None

        date_text = match.group(1)
        fmt = "%d/%m/%Y" if len(date_text.rsplit("/", 1)[1]) == 4 else "%d/%m/%y"

        try:
            return datetime.strptime(date_text, fmt).date()
        except ValueError:
            return None


    @staticmethod
    def generate_employee_name() -> str:
        first_names = [
            "דוד",
            "משה",
            "יוסף",
            "אברהם",
            "יעקב",
        ]

        last_names = [
            "כהן",
            "לוי",
            "מזרחי",
            "פרידמן",
            "אברהם",
        ]

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        return f"{first_name} {last_name}"
