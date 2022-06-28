# -*- coding: utf-8 -*-

import re
import logging
import json

logger = logging.getLogger(__name__)

DEFAULT_OPTIONS = {"field_separator": r"\s+", "line_separator": r"\n"}

#  place in parsers folder

'''
# def parse(template, field, _settings, content):
    """Try to extract tables from the invoice"""
# parser seems more logical? but also no path
'''


def extract(self, content, output, invoicefile):
    # does not include path in plugin folder

    """
    Wrapper around `camelot`.
    Parameters
    ----------
    path : str
        path of electronic invoice in PDF
    Returns
    -------
    str : str
        returns extracted text from pdf
    """

    """
    pandas dataframe gebruiken?
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html
    of json en dat transformeren
    of markup

    """
    try:
        import camelot
    except ImportError:
        logger.debug("Cannot import camelot")

    # import tempfile

    # temp to show what is stored in self
    logger.debug(self)
    logger.debug("%s is the invoicefile",invoicefile)  # is there a path var?
    logger.debug("Camelot :)")
    # allows to pass multiple camelot arguments
    for setting in self["camelot"]:

        # whole block may need adjusting

        # Validate settings
        assert "start" in setting, "Start setting for Camelot missing"
        assert "end" in setting, "End setting for Camelot missing"
        assert "body" in setting, "Body setting missing"

        # Which inputs are needed??
        # Settings json for camelot
        # Which table number to extract?? (Should we do this what if recognition issues?)
        # if passed, do only that table, else do all
        currency_symbol = "€"

        ######################
        # Options
        ######################
        # Change the column headers to a key from the config file
        # Replace the currency sign
        # Replace custom characters, like % sign for vat
        # set datatype?
        # Option: Use regex, for example start_date parsing

        # First apply default options.
        plugin_settings = DEFAULT_OPTIONS.copy()
        plugin_settings.update(setting)
        setting = plugin_settings

        start = re.search(setting["start"], content)
        end = re.search(setting["end"], content)

        if not start or not end:
            logger.warning(
                "no table body found - start %s, end %s", start, end
            )
            continue

    tables = camelot.read_pdf(invoicefile, strip_text=currency_symbol)

    logger.debug("Camelot tables %s", tables)
    df = tables[0].df
    # camelot_json = tables[0].to_json
    # logger.debug("Camelot json result %s", camelot_json)

    # we got to replace the header
    # new_header = df.iloc[0] #grab the first row for the header
    # df = df[1:] #take the data less the header row
    # df.columns = new_header #set the header row as the df header

    # alternative
    # df.rename(columns=df.iloc[0]).drop(df.index[0])
    df, df.columns = df[1:] , df.iloc[0]

    logger.debug("Camelot df\n%s", df)
    result = df.to_json(orient="records", force_ascii=False) # make orient configurable
    logger.debug("Pandas dataframe to json result\n%s", result)

    parsed = json.loads(result)
    # json.dumps(parsed, indent=4)
    parsed = json.dumps(parsed,indent=4, sort_keys=True, ensure_ascii=False, separators=(',', ': ')).replace('\\n','\n')
    logging.info('dataframe head\n{}'.format(parsed, force_ascii=False))

    # logger.debug("json dumps result %s", parsed)

    output["camelot"] = result

    # tables.export('')
    """
    tables[0].to_csv('foo.csv')
    # to_json, to_excel, to_html, to_markdown, to_sqlite
    """
    # or tables[0].df
    """

    raw_text = ""
    raw_text = raw_text.encode(encoding='UTF-8')
    with pdfplumber.open(path, laparams={"detect_vertical": True}) as pdf:
        pages = []
        for pdf_page in pdf.pages:
            pages.append(
                pdf_page.extract_text(
                    layout=True, use_text_flow=True,
                    x_tolerance=6,
                    y_tolerance=4,
                    keep_blank_chars=True
                )
                # y_tolerance=6, dirty Fix for html table problem
            )
        res = {
            "all": "\n\n".join(pages),
            "first": pages and pages[0] or "",
        }
    logger.debug("Text extraction made with pdfplumber")

    raw_text = res_to_raw_text(res)
    return raw_text.encode("utf-8")
"""


def res_to_raw_text(res):
    # we need to convert result to raw text:
    raw_text_dict = res
    raw_text = (raw_text_dict["first"] or raw_text_dict["all"])
    return raw_text
