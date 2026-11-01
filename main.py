
import sys
import random


from parsing.ocr import extract_text
from parsing.classifier import identify_report_type

from parsing.TypeAParser import ReportParserA
from parsing.TypeBParser import ReportParserB

from services.report_variation_service import ReportVariationService

from services.transformations.type_a_transformation_strategy import (
    TypeATransformationStrategy,
)
from services.transformations.type_b_transformation_strategy import (
    TypeBTransformationStrategy,
)

from generation.pdf_renderer import PdfRenderer


def main():

    # Check that a PDF path was provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_path>")
        return

    pdf_path = sys.argv[1]

    # Step 1: Extract text from the PDF using OCR
    raw_text = extract_text(pdf_path)

    # Step 2: Identify the report type
    report_type = identify_report_type(raw_text)

    print(f"Report type: {report_type}")

    # Step 3: Select the appropriate parser and strategy
    if report_type == "A":
        parser = ReportParserA()
        strategy = TypeATransformationStrategy()

    elif report_type == "B":
        parser = ReportParserB()
        strategy = TypeBTransformationStrategy()

    else:
        print("Unknown report type. Cannot continue.")
        return

    # Step 4: Parse the OCR text into a Report object
    report = parser.parse(raw_text)

    # Step 5: Create the variation service
    variation_service = ReportVariationService(strategy)

    # Step 6: Pick a random time offset
    offset_minutes = random.choice([10, 20, 30])

    # Step 7: Transform the report
    transformed_report = variation_service.create_variation(
        report,
        offset_minutes
    )

    # Step 8: Print the transformed report
    print("\nTransformed report")
    print("------------------")

    print(f"Employee: {transformed_report.employee_name}")

    if transformed_report.company_name is not None:
        print(f"Company: {transformed_report.company_name}")

    print(f"Number of days: {len(transformed_report.days)}")

    for day in transformed_report.days:
        print(
            f"{day.date} | {day.day} | "
            f"Entry: {day.entry_time} | "
            f"Exit: {day.exit_time} | "
            f"Total hours: {day.total_hours}"
        )

        if hasattr(day, "notes") and day.notes:
            print(f"Notes: {day.notes}")

    # Step 9: Generate the output PDF
    renderer = PdfRenderer()
    output_path = "output.pdf"

    renderer.render(transformed_report, output_path)

    print(f"\nPDF generated successfully: {output_path}")


if __name__ == "__main__":
    main()
