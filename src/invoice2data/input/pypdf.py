"""Pypdf input module for invoice2data."""

import pypdf
from pypdf.generic import RectangleObject
from typing import Optional, Dict, Any


def to_text(path: str, area: Optional[Dict[str, Any]] = None) -> str:
    """
    Extracts text from the given PDF file.

    Args:
        path (str): Path to the PDF file.
        area (Optional[Dict[str, Any]]): A dictionary containing the area
                                        specifications (page numbers,
                                        coordinates, and resolution).

    Returns:
        str: Extracted text from the specified area of the PDF.
    """
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)

        if area is None:
            # Extract text from all pages
            num_pages = len(reader.pages)
            text = ""
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text(extraction_mode="layout")
            return text
        else:
            # Extract text from specified area
            page_num = area.get("f", 1) - 1  # Page number (1-indexed)
            x = area.get("x", 0)
            y = area.get("y", 0)
            w = area.get("W", 1000)  # Default width
            h = area.get("H", 1000)  # Default height
            resolution = area.get("r", 300)  # Default resolution

            page = reader.pages[page_num]
            page_width = page.mediabox.width
            page_height = page.mediabox.height

            # Calculate coordinates in points
            x_pt = x / resolution * 72
            y_pt = (page_height - y - h) / resolution * 72  # Adjust y-coordinate
            w_pt = w / resolution * 72
            h_pt = h / resolution * 72

            # Create a rectangle for the area
            rect = RectangleObject(
                (x_pt, y_pt, x_pt + w_pt, y_pt + h_pt)
            )

            # Extract text within the rectangle
            text = page.extract_text(clip=rect)
            return text
