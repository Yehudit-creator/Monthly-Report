from datetime import datetime, time, timedelta


def shift_time(original_time: time, offset_minutes: int) -> time:
    """Shift a time by a given number of minutes."""
    reference_date = datetime.min.date()
    original_datetime = datetime.combine(reference_date, original_time)

    new_datetime = original_datetime + timedelta(minutes=offset_minutes)

    return new_datetime.time()