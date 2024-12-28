"""Extracts text from a PDF file using the pypdfium2 library."""

from typing import Optional, Dict, Any
from pypdfium2 import PdfDocument  # Import PdfDocument
from PIL import Image
from io import BytesIO

PDFIUM_ZERO_WIDTH_NO_BREAK_SPACE = "\ufffe"

def pdfium_new_line_after_hyphens(text):
    return text.replace(PDFIUM_ZERO_WIDTH_NO_BREAK_SPACE, PDFIUM_ZERO_WIDTH_NO_BREAK_SPACE + '\n')
    # https://github.com/py-pdf/benchmarks/blob/main/pdf_benchmark/text_extraction_post_processing.py#L5

def to_text(filename: str, area: Optional[Dict[str, Any]] = None) -> str:
    """
    Extracts text from the given PDF file.

    Args:
        filename (str): Path to the PDF file.
        area (Optional[Dict[str, Any]]): A dictionary containing the area
                                        specifications (page numbers,
                                        coordinates, and resolution).

    Returns:
        str: Extracted text from the PDF.
    """
    pdf = PdfDocument(filename)
    page_indices = range(len(pdf)) if area is None else [area.get("f", 1) - 1]
    text = ""

    for page_index in page_indices:
        page = pdf.get_page(page_index)
        if area is None:
            # By default, preserve the layout
            # text += page.get_textpage().get_text_range()
            textpage = page.get_textpage()
            # text += pdfium_new_line_after_hyphens(textpage.get_text_range())
            text += pdfium_new_line_after_hyphens(textpage.get_text())

        else:
            # Extract text from the specified area
            image = self._render_page_area(page, area)
            text += self._extract_text_from_image(image)

    return text



def extract_text_from_area(pdf_path, area_details: Optional[Dict[str, Any]] = None):
    if area_details is not None:
        # An area was specified
        # Validate the required keys were provided
        assert "f" in area_details, "Area f details missing"
        assert "l" in area_details, "Area l details missing"
        assert "r" in area_details, "Area r details missing"
        assert "x" in area_details, "Area x details missing"
        assert "y" in area_details, "Area y details missing"
        assert "W" in area_details, "Area W details missing"
        assert "H" in area_details, "Area H details missing"

        pdf = PdfDocument(pdf_path)
        page = pdf.get_page(area_details.get("f", 1) - 1)

        # Convert all of the values to strings
        # for key in area_details.keys():
        #     area_details[key] = str(area_details[key])


        textpage = page.get_textpage()
        # text = textpage.get_text_bounded(left=area_details["x"], bottom=area_details["y"] + area_details["H"], right=area_details["x"] + area_details["W"], top=area_details["y"])
        # text = textpage.get_text_bounded(left=area_details["x"], bottom=area_details["y"], right=area_details["x"] + area_details["W"], top=area_details["y"])
        # text = textpage.get_text_bounded(left=0, bottom=600, right=825, top=655)
        text = textpage.get_text_bounded(left=0, bottom=620, right=825, top=748)
        # https://pdfium.patagames.com/help/html/WorkingSDK_TextPage.htm
        # https://pdfium.patagames.com/help/html/PdfViewer_CoordinateSystems.htm
        return text

# # Example usage:
# pdf_path = "NetpresseInvoice.pdf"
# page_num = 0  # First page
# x, y, w, h = 0, 155, 825, 170  # Area coordinates (adjust as needed)
# extracted_text = extract_text_from_area(pdf_path, page_num, x, y, w, h)
# print(extracted_text)

def _render_page_area(self, page, area):
    """Renders a specific area of a PDF page as an image."""
    x = area.get("x", 0)
    y = area.get("y", 0)
    width = area.get("W", 1000)
    height = area.get("H", 1000)
    resolution = area.get("r", 300)

    # Calculate the scaling factor based on the resolution
    scale = resolution / 72

    # Render the page to an image with the specified scale and crop
    image = page.render_to(
        width=int(width * scale),
        height=int(height * scale),
        scale=scale,
        crop=(x, y, x + width, y + height),
    )

    # Convert the rendered image to a PIL Image
    pil_image = Image.open(BytesIO(image.get_bytes()))
    return pil_image


def _extract_text_from_image(self, image: Image.Image) -> str:
    """Extracts text from an image using OCR."""
    # You can use any OCR library here (e.g., pytesseract)
    # For this example, we'll just return an empty string
    return ""  # Replace with actual OCR implementation
