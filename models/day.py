from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Day(Generic[T]):
    date: date
    day: str
    entry_time: T
    exit_time: T
    total_hours: Decimal