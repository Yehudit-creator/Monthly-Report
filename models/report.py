
from dataclasses import dataclass, field
from typing import Optional

from models.day import Day
from models.report_type import ReportType
from models.summary import Summary


@dataclass(frozen=True)
class Report:
    employee_name: str
    report_type: ReportType
    days: tuple[Day, ...] = ()
    company_name: Optional[str] = None
    summary: Optional[Summary] = None
