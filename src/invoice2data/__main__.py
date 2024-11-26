#!/usr/bin/python
"""Command-line interface."""

import datetime
import logging
import os
import shutil
from copy import deepcopy
from os.path import join
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import click

from invoice2data.extract.invoice_template import InvoiceTemplate
from invoice2data.extract.loader import read_templates

from .input import gvision
from .input import ocrmypdf
from .input import pdfminer_wrapper
from .input import pdfplumber
from .input import pdftotext
from .input import tesseract
from .input import text
from .output import to_csv
from .output import to_json
from .output import to_xml


logger = logging.getLogger()

input_mapping = {
    "pdftotext": pdftotext,
    "tesseract": tesseract,
    "pdfminer": pdfminer_wrapper,
    "pdfplumber": pdfplumber,
    "gvision": gvision,
    "text": text,
    "ocrmypdf": ocrmypdf,
}

output_mapping = {
    "csv": to_csv,
    "json": to_json,
    "xml": to_xml,
    "none": None,
}


class Color:
    """A class for terminal color codes."""

    BOLD = "\033[1m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW_BACK = "\033[1;43m"
    RED_BACK = "\033[1;41m"
    BOLD_RED = BOLD + RED
    END = "\033[0m"


class ColorLogFormatter(logging.Formatter):
    """A class for formatting colored logs."""

    FORMAT = (
        "%(prefix)s%(levelname)s:%(suffix)s%(name)s:%(prefix)s %(message)s%(suffix)s"
    )

    LOG_LEVEL_COLOR: ClassVar = {  # Annotate with ClassVar
        "DEBUG": {"prefix": "", "suffix": Color.END},
        "INFO": {"prefix": Color.BLUE, "suffix": Color.END},
        "WARNING": {"prefix": Color.YELLOW_BACK, "suffix": Color.END},
        "ERROR": {"prefix": Color.RED_BACK, "suffix": Color.END},
        "CRITICAL": {"prefix": Color.BOLD_RED, "suffix": Color.END},
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log and console records with colors.

        Format log records with a default prefix and suffix
        to terminal color codes that corresponds
        to the log level name.
        """
        if not hasattr(record, "prefix"):
            record.prefix = self.LOG_LEVEL_COLOR.get(record.levelname.upper()).get(
                "prefix"
            )

        if not hasattr(record, "suffix"):
            record.suffix = self.LOG_LEVEL_COLOR.get(record.levelname.upper()).get(
                "suffix"
            )

        formatter = logging.Formatter(self.FORMAT)
        return formatter.format(record)


stream_handler = logging.StreamHandler()
stream_handler.setFormatter(ColorLogFormatter())
logger.propagate = False

if not logger.handlers:
    logger.addHandler(stream_handler)


def extract_data(
    invoicefile: str, templates: Optional[List[Any]] = None, input_module: Any = None
) -> Dict[str, Any]:
    """Extracts structured data from PDF/image invoices.

    This function uses the text extracted from a PDF file or image and
    pre-defined regex templates to find structured data.

    Reads template if no template assigned.
    Required fields are matches from templates.

    Args:
        invoicefile (str): Path of electronic invoice file in PDF, JPEG, PNG
                                    (example: "/home/duskybomb/pdf/invoice.pdf").
        templates (Optional[List[Any]]): List of instances of class `InvoiceTemplate`.
                                                Templates are loaded using `read_template` function in `loader.py`.
        input_module (Any, optional): Library to be used to extract text
                                        from the given `invoicefile`.
                                        Choices: {'pdftotext', 'pdfminer', 'tesseract', 'text'}.

    Returns:
        Dict[str, Any]: Extracted and matched fields.
    """
    if input_module is None:
        if invoicefile.lower().endswith(".txt"):
            input_module = text
        else:
            input_module = pdftotext

    extracted_str = input_module.to_text(invoicefile)
    if not isinstance(extracted_str, str) or not extracted_str.strip():
        logger.error(
            "Failed to extract text from %s using %s",
            invoicefile,
            input_module.__name__,
        )
        return {}

    logger.debug(
        "START pdftotext result ===========================\n%s", extracted_str
    )
    logger.debug("END pdftotext result =============================")

    if not templates:
        templates = read_templates()

    # Convert templates to a list to allow indexing
    templates = list(templates)

    # Initialize result as an empty dictionary
    result: Dict[str, Any] = {}
    for template in templates:
        if template.matches_input(extracted_str):
            logger.info("Using %s template", template["template_name"])
            optimized_str = template.prepare_input(extracted_str)
            result = template.extract(optimized_str, invoicefile, input_module)
            break

    if not result:
        if ocrmypdf.ocrmypdf_available() and input_module is not ocrmypdf:
            logger.debug("Text extraction failed, falling back to ocrmypdf")
            extracted_str, invoicefile, templates_matched = (
                extract_data_fallback_ocrmypdf(invoicefile, templates, input_module)
            )
            if templates_matched:
                result = templates_matched[0].extract(
                    extracted_str, invoicefile, input_module
                )
            else:
                logger.error("No template for %s", invoicefile)
                return {}
        else:
            logger.error("No template for %s", invoicefile)
            return {}

    return deepcopy(result)


def extract_data_fallback_ocrmypdf(
    invoicefile: str,
    templates: List[InvoiceTemplate],
    input_module: Any,
) -> Tuple[str, str, List[InvoiceTemplate]]:
    logger.debug("Trying OCR extraction with ocrmypdf")
    extracted_str = ocrmypdf.to_text(invoicefile)

    # Convert the filter object to a list
    templates_matched: List[InvoiceTemplate] = list(
        filter(lambda t: t.matches_input(extracted_str), templates)
    )
    templates_matched.sort(key=lambda k: k["priority"], reverse=True)

    if templates_matched:
        result = templates_matched[0].extract(extracted_str, invoicefile, input_module)

        return extracted_str, invoicefile, templates_matched
    else:
        # Return empty list if no template is matched
        return extracted_str, invoicefile, []


@click.command()
@click.option(
    "--input-reader",
    "-i",
    type=click.Choice(list(input_mapping.keys())),
    help="Choose text extraction function. Default: auto-detect between text & pdftotext",
)
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(list(output_mapping.keys())),
    default="none",
    help="Choose output format. Default: none",
)
@click.option(
    "--output-date-format",
    "-d",
    default="%Y-%m-%d",
    help="Choose output date format. Default: %%Y-%%m-%%d (ISO 8601 Date)",
)
@click.option(
    "--output-name",
    "-o",
    default="invoices-output",
    help="Custom name for output file. Extension is added based on chosen format.",
)
@click.option("--debug", is_flag=True, help="Enable debug information.")
@click.option(
    "--copy", "-c", help="Copy and rename processed PDFs to specified folder."
)
@click.option(
    "--move", "-m", help="Move and rename processed PDFs to specified folder."
)
@click.option(
    "--filename-format",
    default="{date} {invoice_number} {desc}.pdf",
    help="Filename format to use when moving or copying processed PDFs."
    'Default: "{date} {invoice_number} {desc}.pdf"',
)
@click.option(
    "--template-folder",
    "-t",
    type=click.Path(exists=True),
    help="Folder containing invoice templates in yml file. Always adds built-in templates.",
)
@click.option(
    "--exclude-built-in-templates",
    is_flag=True,
    help="Ignore built-in templates.",
)
@click.argument(
    "input_files",
    type=click.File("wb"),
    nargs=-1,
)
@click.version_option()
def main(
    input_reader: Optional[str],
    output_format: str,
    output_date_format: str,
    output_name: str,
    debug: bool,
    copy: Optional[str],
    move: Optional[str],
    filename_format: str,
    template_folder: Optional[str],
    exclude_built_in_templates: bool,
    input_files: List[Any],
) -> None:
    """Extract structured data from PDF files and save to CSV or JSON."""
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)

    input_module = input_reader
    output_module = output_mapping[output_format]

    templates = []
    if template_folder:
        templates.extend(read_templates(os.path.abspath(template_folder)))
    if not exclude_built_in_templates:
        templates.extend(read_templates())

    output = []
    for f in input_files:
        try:  # Check if res is not None
            res = extract_data(f.name, templates=templates, input_module=input_module)
            if res:
                logger.info(res)
                output.append(res)

                if copy or move:  # Only perform copy/move operations if needed
                    kwargs = deepcopy(res)
                for key, value in kwargs.items():
                    if isinstance(value, list) and len(value) >= 1:
                        kwargs[key] = value[0]
                for key, value in kwargs.items():
                    if isinstance(value, datetime.datetime):
                        kwargs[key] = value.strftime("%Y-%m-%d")
                if copy:
                    filename = filename_format.format(**kwargs)
                    shutil.copyfile(f.name, join(copy, filename))
                if move:
                    filename = filename_format.format(**kwargs)
                    shutil.move(f.name, join(move, filename))
        except Exception as e:
            logger.critical(
                "Invoice2data failed to process %s. \nError message: %s", f.name, e
            )
        finally:
            f.close()

    if output_module is not None:
        output_module.write_to_file(output, output_name, output_date_format)


if __name__ == "__main__":
    main(prog_name="invoice2data")  # pragma: no cover
