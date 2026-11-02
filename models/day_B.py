from dataclasses import dataclass
from datetime import time
from decimal import Decimal

from models.day import Day


@dataclass
class DayB(Day[time | None]):
    notes: str