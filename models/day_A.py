from dataclasses import dataclass
from datetime import time, timedelta
from decimal import Decimal

from models.day import Day


@dataclass
class DayA(Day[time]):
    workplace: str
    break_time: timedelta
    hours_100: Decimal
    hours_125: Decimal
    hours_150: Decimal
    saturday_hours: Decimal