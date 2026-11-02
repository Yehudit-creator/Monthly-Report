
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from pytesseract import Output


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text(pdf_path: str) -> str:
    """Extract text from all pages of a PDF using OCR."""
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("The provided file is not a PDF.")

    pages = convert_from_path(str(path), dpi=300)

    all_text = []

    for page in pages:
        raw_text = pytesseract.image_to_string(
            page,
            lang="heb+eng",
            config="--psm 6"
        )
        all_text.append(raw_text)

    return "\n".join(all_text)


