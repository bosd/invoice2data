import unittest
from typing import Any
from typing import Dict
from typing import List

from invoice2data.extract.invoice_template import InvoiceTemplate


def test_template_with_exclude_keyword_is_not_matched() -> None:
    optimized_str = "Basic Test Which should not pass because of the word Exclude_this"
    invoicetempl = InvoiceTemplate(  # type: ignore[no-untyped-call]
        [
            ("keywords", ["Basic Test"]),
            ("exclude_keywords", ["Exclude_this"]),
            ("template_name", "excludekeywordnotlist.yml"),
            ("priority", 5),
            ("issuer", "Basic Test"),
        ]
    )
    template_matched = InvoiceTemplate.matches_input(invoicetempl, optimized_str)
    assert template_matched is False, "A template with exclude keywords is not matched"


def test_skip_template_with_too_long_lang_code() -> None:  # Added return type hint
    options_test: Dict[str, List[str]] = {  # Added type hint
        "currency": ["EUR"],  # Changed to list
        "date_formats": [],
        "languages": ["aaa"],
        "decimal_separator": ["."],  # Changed to list
        "replace": [],
    }

    tpl: Dict[str, Any] = {}  # Added type hint
    tpl["keywords"] = ["Basic Test"]
    tpl["exclude_keywords"] = []
    tpl["options"] = options_test
    tpl["template_name"] = ["3_char_langcode.yml"]  # Changed to list
    try:
        InvoiceTemplate(tpl)  # type: ignore[no-untyped-call]
    except Exception:
        assert (
            True
        ), "Template with language code length != 2 characters is not initiated"
    else:
        assert (
            False
        ), "Template with language code length != 2 characters is not initiated"


class TestInvoiceTemplateMethods(unittest.TestCase):
    def test_replace_a_with_b(self) -> None:  # Added return type hint
        options_test: Dict[str, Any] = {  # Added type hint
            "currency": ["EUR"],  # Changed to list
            "date_formats": [],
            "languages": ["aa"],
            "decimal_separator": ["."],  # Changed to list
            "replace": [["a", "b"]],
        }

        tpl: Dict[str, Any] = {}  # Added type hint
        tpl["keywords"] = ["Basic Test"]
        tpl["exclude_keywords"] = []
        tpl["options"] = options_test
        tpl["template_name"] = "replace_a_with_b"  # Changed to list
        invoicetempl = InvoiceTemplate(tpl)  # type: ignore[no-untyped-call]
        extracted_str = "a"
        print("InvoiceTempl: \n%s" % invoicetempl)

        optimized_str = invoicetempl.prepare_input(extracted_str)
        print("extracted_str: \n%s" % extracted_str)
        print("optimized_str: \n%s" % optimized_str)
        self.assertEqual(optimized_str, "b")

    def test_remove_accents(self) -> None:  # Added return type hint
        options_test: Dict[str, Any] = {  # Added type hint
            "currency": ["EUR"],  # Changed to list
            "date_formats": [],
            "languages": ["aa"],
            "decimal_separator": ["."],  # Changed to list
            "remove_accents": True,
        }

        tpl: Dict[str, Any] = {}  # Added type hint
        tpl["keywords"] = ["Basic Test"]
        tpl["exclude_keywords"] = []
        tpl["options"] = options_test
        tpl["template_name"] = "test_remove_accents"  # Changed to list
        invoicetempl = InvoiceTemplate(tpl)  # type: ignore[no-untyped-call]
        extracted_str = "é€$%^&*@!.a Málaga François Phút Hơn 中文"
        print("InvoiceTempl: \n%s" % invoicetempl)

        optimized_str = invoicetempl.prepare_input(extracted_str)
        print("extracted_str: \n%s" % extracted_str)
        print("optimized_str: \n%s\n" % optimized_str)
        self.assertEqual(
            optimized_str,
            "e€$%^&*@!.a Malaga Francois Phut Hon 中文",
            "Remove accents function failed, output not equal",
        )

    def test_remove_whitespace(self) -> None:  # Added return type hint
        options_test: Dict[str, Any] = {  # Added type hint
            "currency": ["EUR"],  # Changed to list
            "date_formats": [],
            "languages": ["aa"],
            "decimal_separator": ["."],  # Changed to list
            "remove_whitespace": True,
        }

        tpl: Dict[str, Any] = {}  # Added type hint
        tpl["keywords"] = ["Basic Test"]
        tpl["exclude_keywords"] = []
        tpl["options"] = options_test
        tpl["template_name"] = "test_remove_whitespace"  # Changed to list
        invoicetempl = InvoiceTemplate(tpl)  # type: ignore[no-untyped-call]
        extracted_str = "a    b"
        print("InvoiceTempl: \n%s" % invoicetempl)

        optimized_str = invoicetempl.prepare_input(extracted_str)
        print("extracted_str: \n%s" % extracted_str)
        print("optimized_str: \n%s\n" % optimized_str)
        self.assertEqual(optimized_str, "ab", "remove whitespace test failed")

    def test_lowercase(self) -> None:  # Added return type hint
        options_test: Dict[str, Any] = {  # Added type hint
            "currency": ["EUR"],  # Changed to list
            "date_formats": [],
            "languages": ["aa"],
            "decimal_separator": ["."],  # Changed to list
            "lowercase": True,
        }

        tpl: Dict[str, Any] = {}  # Added type hint
        tpl["keywords"] = ["Basic Test"]
        tpl["exclude_keywords"] = []
        tpl["options"] = options_test
        tpl["template_name"] = "test_lowercase"  # Changed to list
        invoicetempl = InvoiceTemplate(tpl)  # type: ignore[no-untyped-call]
        extracted_str = "ABCD"
        print("InvoiceTempl: \n%s" % invoicetempl)

        optimized_str = invoicetempl.prepare_input(extracted_str)
        print("extracted_str: \n%s" % extracted_str)
        print("optimized_str: \n%s\n" % optimized_str)
        self.assertEqual(optimized_str, "abcd", "Lowercase test failed")


if __name__ == "__main__":
    unittest.main()
