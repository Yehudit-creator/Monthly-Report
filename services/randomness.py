import hashlib
import random


def stable_seed(*parts) -> int:
    """מחזיר מספר קבוע מתוך הערכים שהועברו (למשל שם עובד ותאריך).

    משתמש ב-sha256 ולא ב-hash(): ל-hash() של מחרוזת יש ערך שונה
    בכל הרצה של פייתון, ולכן הוא לא מתאים ל-seed יציב.
    """
    text = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def make_rng(*parts) -> random.Random:
    """מחולל מספרים אקראיים נפרד, עם seed שנגזר מהערכים שהועברו."""
    return random.Random(stable_seed(*parts))