from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Summary:
    """מודל סיכום משותף לשני סוגי הדוחות.

    סוג A: כל ארבעת השדות מלאים.
    סוג B: אין חלוקה לשעות נוספות, ולכן hours_125 ו-hours_150 הם None,
    ו-hours_100 מחזיק את סה"כ השעות החודשיות.
    """

    work_days_count: int                       # סך ימי עבודה
    hours_100: Decimal                         # שעות 100%
    hours_125: Optional[Decimal] = None        # שעות 125% (סוג A בלבד)
    hours_150: Optional[Decimal] = None        # שעות 150% (סוג A בלבד)
