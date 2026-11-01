
from decimal import Decimal

from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from models.report import Report
from generation.base_renderer import BaseRenderer


class PdfRenderer(BaseRenderer):
    """Generate an attendance report as a PDF file."""

    def render(self, report: Report, output_path: str) -> None:

        # Register a Hebrew-compatible font
        if "Arial" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(
                TTFont("Arial", r"C:\Windows\Fonts\arial.ttf")
            )

        document = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=10 * mm,
            leftMargin=10 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "HebrewTitle",
            parent=styles["Title"],
            fontName="Arial",
            fontSize=16,
            alignment=TA_CENTER,
        )

        text_style = ParagraphStyle(
            "HebrewText",
            parent=styles["Normal"],
            fontName="Arial",
            fontSize=8,
            alignment=TA_RIGHT,
        )

        elements = []

        def hebrew(text: str) -> str:
            return get_display(str(text))

        # Report title
        elements.append(
            Paragraph(
                hebrew("דוח נוכחות"),
                title_style,
            )
        )

        elements.append(Spacer(1, 5 * mm))

        # Company name - only if exists
        if report.company_name:
            elements.append(
                Paragraph(
                    hebrew(f"שם החברה: {report.company_name}"),
                    text_style,
                )
            )

        # Employee name
        elements.append(
            Paragraph(
                hebrew(f"שם העובד: {report.employee_name}"),
                text_style,
            )
        )

        elements.append(Spacer(1, 5 * mm))

        # Table headers
        headers = [
            "שבת",
            "150%",
            "125%",
            "100%",
            'סה"כ שעות',
            "הפסקה",
            "יציאה",
            "כניסה",
            "מקום עבודה",
            "יום",
            "תאריך",
            "הערות",
        ]

        table_data = [[hebrew(header) for header in headers]]

        total_hours = Decimal("0")

        # Add one row for each day
        for day in report.days:

            break_time = getattr(day, "break_time", None)

            break_text = (
                str(break_time)
                if break_time is not None
                else "-"
            )

            exit_text = (
                day.exit_time.strftime("%H:%M")
                if day.exit_time is not None
                else "-"
            )

            entry_text = (
                day.entry_time.strftime("%H:%M")
                if day.entry_time is not None
                else "-"
            )

            row = [
                str(getattr(day, "saturday_hours", "-")),
                str(getattr(day, "hours_150", "-")),
                str(getattr(day, "hours_125", "-")),
                str(getattr(day, "hours_100", "-")),
                str(day.total_hours),
                break_text,
                exit_text,
                entry_text,
                hebrew(getattr(day, "workplace", "-")),
                hebrew(day.day),
                day.date.strftime("%d/%m/%Y") if day.date else "-",
                hebrew(getattr(day, "notes", "-")),
            ]

            table_data.append(row)
            total_hours += day.total_hours

        # Create the table
        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                18 * mm,
                18 * mm,
                18 * mm,
                18 * mm,
                20 * mm,
                17 * mm,
                17 * mm,
                17 * mm,
                25 * mm,
                20 * mm,
                25 * mm,
                35 * mm,
            ],
        )

        table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        elements.append(table)
        elements.append(Spacer(1, 5 * mm))

        # Total working hours
        elements.append(
            Paragraph(
                hebrew(f'סך שעות העבודה: {total_hours}'),
                text_style,
            )
        )

        document.build(elements)
