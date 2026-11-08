from decimal import Decimal
from pathlib import Path

# ---------- נתיבים ----------
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "inputs"
OUTPUT_DIR = BASE_DIR / "outputs"
FONTS_DIR = BASE_DIR / "fonts"
# ---------- הזזת שעות ----------
# כמה דקות מזיזים. בכל הרצה נבחר אחד מהערכים (ובאקראי גם הכיוון: לפני או אחרי)
OFFSET_OPTIONS_MINUTES = [10, 20, 30]

# מה מזיזים בכל יום: שתיהן, רק כניסה, רק יציאה
# כדי להגדיל סיכוי למצב מסוים, כותבים אותו כמה פעמים ברשימה
SHIFT_MODES = ["both", "entry_only", "exit_only"]

# ימים שלא מזיזים בהם שעות (ב-Python: שני=0 ... שישי=4, שבת=5)
# SKIP_SHIFT_WEEKDAYS = {4, 5}

# ---------- שעות נוספות (סוג A בלבד) ----------
# הערכים נלקחו מהקוד המקורי. שניהם סף מצטבר של סה"כ שעות ביום
REGULAR_HOURS = Decimal("8.0")        # עד כאן: 100%
OVERTIME_125_UNTIL = Decimal("9.0")   # מעל 8.0 ועד כאן: 125%, ומעבר לכך: 150%
SUMMARY_SUM_FIELDS = ("hours_100", "hours_125", "hours_150")
