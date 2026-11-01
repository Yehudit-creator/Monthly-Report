
from dataclasses import dataclass, field
from typing import Optional

from models.day import Day


@dataclass
class Report:
    employee_name: str
    days: list[Day] = field(default_factory=list)
    company_name: Optional[str] = None