"""Pypdf input module for invoice2data."""

from typing import Any
from typing import Dict
from typing import Optional

import pypdf
from pypdf.generic import RectangleObject


class PyPDFLoader:
    def __init__(self, path: str):
        self.path = path
        self.file_handle = open(path, "rb")  # Keep the file handle open
        self.reader = pypdf.PdfReader(self.file_handle)
        self._extracted_text = None

    def __del__(self):
        # Close the file when the object is garbage collected
        if self.file_handle:
            self.file_handle.close()


    @property
    def extracted_text(self) -> str:
        if self._extracted_text is None:
            # Extract text from all pages and store it
            num_pages = len(self.reader.pages)
            self._extracted_text = ""
            for page_num in range(num_pages):
                page = self.reader.pages[page_num]
                self._extracted_text += page.extract_text(extraction_mode="layout")
        return self._extracted_text

    def get_text(self, area: Optional[Dict[str, Any]] = None) -> str:
            """Extracts text from the given PDF file.

            Args:
                area (Optional[Dict[str, Any]]): A dictionary containing the area
                                                    specifications (page numbers,
                                                    coordinates, and resolution).

            Returns:
                str: Extracted text from the specified area of the PDF.
            """

            if area is None:
                return self.extracted_text  # Use cached text

            # Extract text from specified area
            page_num = area.get("f", 1) - 1  # Page number (1-indexed)
            x = area.get("x", 0)
            y = area.get("y", 0)
            w = area.get("W", 1000)  # Default width
            h = area.get("H", 1000)  # Default height
            resolution = area.get("r", 300)  # Default resolution

            page = self.reader.pages[page_num]
            page_text = page.extract_text(extraction_mode="layout")  # Extract text only once
            page_width = page.mediabox.width
            page_height = page.mediabox.height

            # Calculate coordinates in points
            x_pt = x / resolution * 72
            y_pt = (page_height - y - h) / resolution * 72  # Adjust y-coordinate
            w_pt = w / resolution * 72
            h_pt = h / resolution * 72

            # Create a rectangle for the area
            rect = RectangleObject((x_pt, y_pt, x_pt + w_pt, y_pt + h_pt))

            # --- Improved Area Extraction ---
            lines = page_text.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines
            extracted_lines = []
            current_y = 0  # Track the current y position

            for line_num, line in enumerate(non_empty_lines):
                line_height = 12 / resolution  # Estimate line height (adjust as needed)
                current_y += line_height  # Update the y position

                if y <= current_y <= y + h / page_height:  # Check if line is within the area
                    char_start = int(x / page_width * len(line))
                    char_end = int((x + w) / page_width * len(line))
                    extracted_lines.append(line[char_start:char_end])

            return "\n".join(extracted_lines)


def to_text(path: str, area: Optional[Dict[str, Any]] = None) -> str:
    """Extracts text from the given PDF file.

    Args:
        path (str): Path to the PDF file.
        area (Optional[Dict[str, Any]]): A dictionary containing the area
                                            specifications (page numbers,
                                            coordinates, and resolution).

    Returns:
        str: Extracted text from the specified area of the PDF.
    """
    loader = PyPDFLoader(path)
    return loader.get_text(area)
