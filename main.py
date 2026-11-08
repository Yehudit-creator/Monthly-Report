
import sys
import random

from models.report_type import ReportType
from parsing.ocr import extract_text
from parsing.classifier import identify_report_type
from config import INPUT_DIR, OFFSET_OPTIONS_MINUTES
from parsing.parser_factory import get_parser

from services.transformations.type_a_transformation_strategy import (
    TypeATransformationStrategy,
)
from services.transformations.type_b_transformation_strategy import (
    TypeBTransformationStrategy,
)

from generation.pdf_renderer import PdfRenderer


transformations = {
    ReportType.A: TypeATransformationStrategy(),
    ReportType.B: TypeBTransformationStrategy(),
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_name>")
        return

    pdf_path = INPUT_DIR / sys.argv[1]

    if not pdf_path.is_file():
        print(f"File not found: {pdf_path}")
        return

    # שלב 1: OCR
    raw_text = extract_text(str(pdf_path))

    # שלב 2: זיהוי סוג הדוח
    report_type = identify_report_type(raw_text)

    # שלב 3: בחירת Parser ואסטרטגיית שינוי
    parser = get_parser(report_type)
    strategy = transformations.get(report_type)

    if parser is None or strategy is None:
        raise ValueError(f"Unknown report type: {report_type}")

    # שלב 4: יצירת מודל
    report = parser.parse(raw_text)

    # שלב 5: שינוי השעות
    offset_minutes = (
        random.choice(OFFSET_OPTIONS_MINUTES)
        * random.choice([-1, 1])
    )

    transformed_report = strategy.transform(report, offset_minutes)

    # שלב 6: יצירת PDF
    renderer = PdfRenderer()
    renderer.render(transformed_report)


if __name__ == "__main__":
    main()
