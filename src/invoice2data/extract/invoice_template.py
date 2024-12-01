"""This module abstracts templates for invoice providers.

Templates are initially read from .yml files and then kept as class.
"""

import re
import unicodedata
from collections import OrderedDict
from logging import getLogger
from pprint import pformat
from typing import Any
from typing import Dict

import dateparser  # type: ignore[import-untyped]

from ..input import ocrmypdf

# Area extraction is currently added for pdftotext, ocrmypdf and tesseract (which uses pdftotext)
from ..input import pdftotext
from ..input import tesseract
from . import parsers
from .plugins import lines
from .plugins import tables


logger = getLogger(__name__)

OPTIONS_DEFAULT = {
    "remove_whitespace": False,
    "remove_accents": False,
    "lowercase": False,
    "currency": "EUR",
    "date_formats": [],
    "languages": [],
    "decimal_separator": ".",
    "replace": [],  # example: see templates/fr/fr.free.mobile.yml
}

PARSERS_MAPPING = {
    "lines": parsers.lines,
    "regex": parsers.regex,
    "static": parsers.static,
}

PLUGIN_MAPPING = {"lines": lines, "tables": tables}


class InvoiceTemplate(OrderedDict[str, Any]):
    """Represents single template files that live as .yml files on the disk.

    Methods:
      prepare_input(extracted_str)
          Input raw string
          and perform transformations, as set in the template file.
      matches_input(extracted_str)
          Check if the string matches keywords set in the template file.
      parse_number(value)
          Parse number, remove decimal separator and add other options.
      parse_date(value)
          Parse date and return the date after parsing.
      coerce_type(value, target_type)
          Change the type of values.
      extract(optimized_str)
          Given a template file and a string, extract matching data fields.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Merge template-specific options with defaults
        self.options: Dict[str, Any] = OPTIONS_DEFAULT.copy()

        if "options" in self:
            self.options.update(self["options"])

        languages = self.options.get("languages", [])

        if not isinstance(languages, list):
            languages = [languages]

        for lang in self.options.get("languages", []):  # type: ignore [attr-defined]
            if len(lang) != 2:
                raise AssertionError(
                    "Error in Template %s lang code must have 2 letters"
                    % self["template_name"]
                )

        # Set issuer, if it doesn't exist.
        if "issuer" not in self.keys():
            self["issuer"] = self["keywords"][0]

    def prepare_input(self, extracted_str: str) -> str:
        """Input raw string and do transformations, as set in template file."""
        # Remove whitespace
        if self.options["remove_whitespace"]:
            optimized_str = re.sub(" +", "", extracted_str)
        else:
            optimized_str = extracted_str

        # Remove accents
        if self.options["remove_accents"]:
            optimized_str = re.sub(
                "[\u0300-\u0362]", "", unicodedata.normalize("NFKD", optimized_str)
            )

        # Convert to lower case
        if self.options["lowercase"]:
            optimized_str = optimized_str.lower()

        if not isinstance(self.options.get("replace", []), list):
            self.options["replace"] = [self.options["replace"]]

        # Specific replace
        for replace in self.options.get("replace", []):
            assert len(replace) == 2, (
                "Error in Template %s A replace should be a list of exactly 2 elements."
                % self["template_name"]
            )
            optimized_str = re.sub(replace[0], replace[1], optimized_str)

        return optimized_str

    def matches_input(self, extracted_str: str) -> bool:
        """Check if the extracted string matches the template keywords.

        Args:
            extracted_str (str): The extracted text from the invoice.

        Returns:
            bool: True if the extracted string matches the template keywords,
                  False otherwise.
        """
        if all([re.search(keyword, extracted_str) for keyword in self["keywords"]]):
            # All keyword patterns matched
            if self["exclude_keywords"]:
                if any(
                    [
                        re.search(exclude_keyword, extracted_str)
                        for exclude_keyword in self["exclude_keywords"]
                    ]
                ):
                    # At least one exclude_keyword matches
                    logger.debug(
                        "Template: %s | Keywords matched. Exclude keyword found!",
                        self["template_name"],
                    )
                    return False
            # No exclude_keywords or none match, template is good
            logger.debug(
                "Template: %s | Keywords matched. No exclude keywords found.",
                self["template_name"],
            )
            return True
        else:
            logger.debug(
                "Template: %s | Failed to match all keywords.", self["template_name"]
            )
            return False

    def parse_number(self, value: str) -> float:
        """Parses a number from a string.

        This function parses a numerical value from a string, handling
        different decimal separators and thousands separators based on locale.

        Args:
            value (str): The string containing the number to be parsed.

        Returns:
            float: The parsed numerical value.
        """
        assert isinstance(value, str)
        # Early exit if no thousands separator or custom decimal separator is present
        if not any(char in value for char in r",.'\s"):
            return float(value)

        # Ensure decimal_separator is a string before calling count()
        assert isinstance(self.options["decimal_separator"], str)
        assert value.count(self.options["decimal_separator"]) < 2, (
            f"Error in Template {self['template_name']}: "
            "Decimal separator cannot be present several times"
        )

        # Determine the thousands separator based on the decimal separator
        thousands_separator = "," if self.options["decimal_separator"] == "." else "."

        # Remove all possible thousands separators
        amount_no_thousand_sep = re.sub(
            r"[\s']", "", value.replace(thousands_separator, "")
        )

        # Replace the decimal separator with a dot
        return float(
            amount_no_thousand_sep.replace(str(self.options["decimal_separator"]), ".")
        )

    def parse_date(self, value: str) -> Any:
        """Parses date and returns date after parsing."""
        res = dateparser.parse(
            value,
            date_formats=self.options["date_formats"],
            languages=self.options["languages"],
        )
        logger.debug("result of date parsing=%s", res)
        return res

    def coerce_type(self, value: str, target_type: str) -> Any:
        """Coerces a value to the specified target type.

        Args:
            value (str): The value to be coerced.
            target_type (str): The target type to which the value should be coerced.
                                  Valid values: 'int', 'float', 'date'.

        Returns:
            Any: The coerced value.

        Raises:
            AssertionError: If the target_type is unknown.
        """
        if target_type == "int":
            if not value:
                return 0
            return int(self.parse_number(value))
        elif target_type == "float":
            if not value:
                return 0.0
            return float(self.parse_number(value))
        elif target_type == "date":
            return self.parse_date(value)
        elif target_type == "datetime":
            return self.parse_date(value)
        raise AssertionError("Unknown type")

    def extract(
        self, optimized_str: str, invoice_file: str, input_module: Any
    ) -> Dict[str, Any]:
        """Extracts data from the optimized string using the template.

        Args:
            optimized_str (str): The optimized string.
            invoice_file (str): The path to the invoice file.
            input_module (Any): The input module used.

        Returns:
            Dict[str, Any]: The extracted data.

        Raises:
            ValueError: If a required field could not be parsed
        """
        logger.debug("START optimized_str ========================\n" + optimized_str)
        logger.debug("END optimized_str ==========================")
        logger.debug(
            "Date parsing: languages=%s date_formats=%s",
            self.options["languages"],
            self.options["date_formats"],
        )
        logger.debug(
            "Float parsing: decimal separator=[%s]", self.options["decimal_separator"]
        )
        logger.debug("keywords=%s", self["keywords"])
        logger.debug(self.options)

        # Try to find data for each field.
        output = {}
        output["issuer"] = self["issuer"]

        for k, v in self["fields"].items():
            # k is the key of the field
            # v is the value
            if isinstance(v, dict):
                # Options were supplied to this field
                if "area" in v and input_module in (
                    pdftotext,
                    ocrmypdf,
                    tesseract,
                ):
                    # Area is currently only supported for pdftotext
                    # area is optional and re-extracts the text being searched
                    # This obviously has a performance impact, so use wisely
                    # Verify that the input_module is set to pdftotext ... this is the only one included right now
                    logger.debug(f"Area was specified with parameters {v['area']}")
                    # Extract the text for the specified area
                    # Do NOT overwrite optimized_str. We're inside a loop and it will affect all other fields!
                    optimized_str_area = input_module.to_text(invoice_file, v["area"])
                    # Log the text
                    logger.debug(
                        "START pdftotext area result ===========================\n%s",
                        optimized_str_area,
                    )
                    logger.debug(
                        "END pdftotext area result ============================="
                    )
                    optimized_str_for_parser = optimized_str_area
                else:
                    # No area specified
                    optimized_str_for_parser = optimized_str
                if "parser" in v:
                    # parser is required and may require additional options
                    # e.g. "parser: regex" requires "regex: [pattern]"
                    if v["parser"] in PARSERS_MAPPING:
                        parser = PARSERS_MAPPING[v["parser"]]
                        value = parser.parse(self, k, v, optimized_str_for_parser)
                        if value or value == 0.0:
                            output[k] = value
                        else:
                            logger.warning(
                                "Failed to parse field %s with parser %s",
                                k,
                                v["parser"],
                            )
                    else:
                        logger.error(
                            "Field %s has unknown parser %s set", k, v["parser"]
                        )
                else:
                    logger.error("Field %s doesn't have parser specified", k)
            elif k.startswith("static_"):
                logger.debug("field=%s | static value=%s", k, v)
                output[k.replace("static_", "")] = v
            else:
                # Legacy syntax support (backward compatibility)
                result = None
                if k.startswith("sum_amount") and type(v) is list:
                    k = k[4:]
                    result = parsers.regex.parse(
                        self,
                        k,
                        {"regex": v, "type": "float", "group": "sum"},
                        optimized_str,
                        True,
                    )
                elif k.startswith("date") or k.endswith("date"):
                    result = parsers.regex.parse(
                        self, k, {"regex": v, "type": "date"}, optimized_str, True
                    )
                elif k.startswith("amount"):
                    result = parsers.regex.parse(
                        self, k, {"regex": v, "type": "float"}, optimized_str, True
                    )
                else:
                    result = parsers.regex.parse(
                        self, k, {"regex": v}, optimized_str, True
                    )

                if result or result == 0.0:
                    output[k] = result
                else:
                    logger.warning("regexp for field %s didn't match", k)

        output["currency"] = self.options["currency"]

        # Run plugins:
        for plugin_keyword, plugin_func in PLUGIN_MAPPING.items():
            if plugin_keyword in self.keys():
                plugin_func.extract(self, optimized_str, output)

        # If required fields were found, return output, else log error.
        if "required_fields" not in self.keys():
            required_fields = ["date", "amount", "invoice_number", "issuer"]
        else:
            required_fields = []
            for v in self["required_fields"]:
                required_fields.append(v)

        if set(required_fields).issubset(output.keys()):
            output["desc"] = "Invoice from %s" % (self["issuer"])
            logger.debug("\n %s", pformat(output, indent=2))
            # when python 3.7 support stops add sort_dicts=False,
            return output
        else:
            fields = list(set(output.keys()))
            logger.error(
                "Unable to match all required fields. "
                f"The required fields are: {required_fields}. "
                f"Output contains the following fields: {fields}."
            )
            missing = set(required_fields) - set(fields)
            raise ValueError(f"Unable to parse required field(s): {missing}")
