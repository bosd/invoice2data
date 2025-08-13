"""PyMuPDF-based PDF text extraction module."""

from typing import Any
from typing import Dict
from typing import Optional

import fitz


def extract_full_text(doc: fitz.Document) -> str:
    """Extracts text from the entire PDF document.

    Args:
        doc (fitz.Document): The PyMuPDF document object.

    Returns:
        str: A string containing the extracted text.
    """
    text = ""
    # flags = pymupdf.TEXT_PRESERVE_LIGATURES | pymupdf.TEXT_PRESERVE_WHITESPACE

    for page in doc:
        text += page.get_text("text")
    return text


def extract_area_text(doc: fitz.Document, area_details: Dict[str, Any]) -> str:
    """Extracts text from a specified region in the PDF using PyMuPDF.

    Args:
        doc (fitz.Document): The PyMuPDF document object.
        area_details (Dict[str, Any]): A dictionary containing the area specifications
                                      (page number, coordinates, and resolution).

    Returns:
        str: A string containing the extracted text from the specified region.
    """
    page_num = area_details.get("f", 1) - 1  # Page number (1-indexed)
    x = area_details.get("x", 0)
    y = area_details.get("y", 0)
    w = area_details.get("W", 1000)  # Default width
    h = area_details.get("H", 1000)  # Default height
    resolution = area_details.get("r", 100)  # Default resolution

    page = doc[page_num]

    # Calculate coordinates in points
    x_pt = x / resolution * 72
    y_pt = y / resolution * 72
    w_pt = w / resolution * 72
    h_pt = h / resolution * 72

    # Create the rectangle with the calculated coordinates
    rect = fitz.Rect(x_pt, y_pt, x_pt + w_pt, y_pt + h_pt)

    return str(page.get_text("text", clip=rect))


def to_text(invoice_file: str, area_details: Optional[Dict[str, Any]] = None) -> str:
    """Extracts text from a PDF invoice.

    Args:
        invoice_file (str): Path to the PDF invoice file.
        area_details (Optional[Dict[str, Any]]): A dictionary containing area
                                                 specifications for extracting text
                                                 from a specific region. Defaults
                                                 to None.

    Returns:
        str: The extracted text from the PDF.
    """
    doc = fitz.open(invoice_file)

    if area_details is None:
        return extract_full_text(doc)
    else:
        return extract_area_text(doc, area_details)
