from datetime import datetime, time, timedelta
from decimal import Decimal


def shift_time(original_time: time, offset_minutes: int) -> time:
    """Shift a time by a given number of minutes."""
    reference_date = datetime.min.date()
    original_datetime = datetime.combine(reference_date, original_time)

    new_datetime = original_datetime + timedelta(minutes=offset_minutes)

    return new_datetime.time()


def wraps_midnight(original: time, shifted: time, offset: int) -> bool:
    """True אם ההזזה עברה את חצות (השעה "קפצה" ליום אחר)."""
    return (offset > 0 and shifted < original) or (offset < 0 and shifted > original)


def minutes_between(entry: time, exit_: time) -> int:
    """משך העבודה בדקות בין כניסה ליציאה."""
    reference = datetime.min.date()
    start = datetime.combine(reference, entry)
    end = datetime.combine(reference, exit_)
    minutes = int((end - start).total_seconds() // 60)
    # יציאה אחרי חצות: מוסיפים 24 שעות
    return minutes if minutes >= 0 else minutes + 24 * 60


def calculate_total_hours(entry: time, exit_: time) -> Decimal:
    """משך בשעות עשרוניות (למשל 8.50) לפי כניסה ויציאה."""
    return (Decimal(minutes_between(entry, exit_)) / Decimal(60)).quantize(
        Decimal("0.01")
    )
