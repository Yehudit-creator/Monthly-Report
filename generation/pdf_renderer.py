from decimal import Decimal

from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from config import OUTPUT_DIR, FONTS_DIR
from models.report import Report
from models.report_type import ReportType
from generation.layouts import LAYOUTS, ReportLayout  # הנחה: שם הקובץ שבו נמצא LAYOUTS
from generation.base_renderer import BaseRenderer


def _heb(text) -> str:
    """הופך טקסט לסדר חזותי של ימין לשמאל, כדי שיוצג נכון ב-PDF."""
    return get_display(str(text), base_dir="R")


def _fmt(value) -> str:
    """ממיר ערך לטקסט להצגה: None הופך לריק, Decimal מוצג בלי אפסים מיותרים."""
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)


class PdfRenderer(BaseRenderer):
    file_extension = ".pdf"

    FONT = "HebFont"
    FONT_BOLD = "HebFont-Bold"

    def render(self, report: Report) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        pdf_path = OUTPUT_DIR / f"report{self.file_extension}"

        self._register_fonts()
        layout = LAYOUTS[report.report_type]

        doc = SimpleDocTemplate(
            str(pdf_path), pagesize=A4,
            rightMargin=1.2 * cm, leftMargin=1.2 * cm,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        )

        story = []

        # כותרת: שם החברה (אם קיים) ושם העובד
        title_style = ParagraphStyle(
            "title", fontName=self.FONT_BOLD, fontSize=16, alignment=TA_RIGHT, leading=22
        )
        if report.company_name:
            story.append(Paragraph(_heb(report.company_name), title_style))
        story.append(Paragraph(_heb(f"שם העובד: {report.employee_name}"), title_style))
        story.append(Spacer(1, 0.4 * cm))

        table = self._build_table(report, layout)
        summary = self._build_summary(report)  # None אם אין סיכום

        # summary_on_top קובע אם הסיכום לפני הטבלה (B) או אחריה (A)
        if summary is not None and layout.summary_on_top:
            story += [summary, Spacer(1, 0.4 * cm)]
        story.append(table)
        if summary is not None and not layout.summary_on_top:
            story += [Spacer(1, 0.4 * cm), summary]

        doc.build(story)

    def _register_fonts(self) -> None:
        pdfmetrics.registerFont(TTFont(self.FONT, str(FONTS_DIR / "NotoSansHebrew-Regular.ttf")))
        pdfmetrics.registerFont(TTFont(self.FONT_BOLD, str(FONTS_DIR / "NotoSansHebrew-Bold.ttf")))

    def _build_table(self, report: Report, layout: ReportLayout) -> Table:
        rows = [[_heb(col.title) for col in layout.columns]]

        for day in report.days:
            rows.append([_heb(_fmt(getattr(day, col.field))) for col in layout.columns])

        # העמודה הראשונה צריכה להופיע מימין, לכן הופכים את סדר העמודות בכל שורה
        rows = [list(reversed(r)) for r in rows]

        font_size = 8 if len(layout.columns) > 7 else 10

        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), self.FONT),
            ("FONTNAME", (0, 0), (-1, 0), self.FONT_BOLD),
            ("FONTSIZE", (0, 0), (-1, -1), font_size),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))
        return table

    def _build_summary(self, report: Report) -> Table | None:
        s = report.summary
        if s is None:
            return None

        if report.report_type == ReportType.B:
            # בסוג B אין חלוקה לשעות נוספות, ו-hours_100 הוא סה"כ השעות החודשיות
            data = [
                ("סה\"כ ימי עבודה", s.work_days_count),
                ("סה\"כ שעות חודשיות", s.hours_100),
            ]
        else:
            data = [
                ("ימי עבודה", s.work_days_count),
                ("שעות 100%", s.hours_100),
                ("שעות 125%", s.hours_125),
                ("שעות 150%", s.hours_150),
            ]

        # הערך משמאל והתווית מימין
        rows = [[_heb(_fmt(value)), _heb(label)] for label, value in data]

        table = Table(rows, hAlign="RIGHT")
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), self.FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        return table