# -*- coding: utf-8 -*-

import re
import logging
import json
import numpy as np



# PYTHONIOENCODIG="utf-8" # python -c 'import sys'

# to check is pandas available?
# import pandas as pd

# PYTHONIOENCODING="UTF-8"

logger = logging.getLogger(__name__)

logging.getLogger("pdfminer").setLevel(logging.WARNING)

DEFAULT_OPTIONS = {"field_separator": r"\s+", "line_separator": r"\n"}

#  place in parsers folder

'''
# def parse(template, field, _settings, content):
    """Try to extract tables from the invoice"""
# parser seems more logical? but also no path
'''

# invoice2data camelot-example.pdf --input-reader=pdftotext --template-folder=./Templates --debug

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
    # logger.debug("Camelot :)")

    # allows to pass multiple camelot arguments
    for setting in self["camelot"]:

        # whole block may need adjusting

        # Validate settings
        assert "start" in setting, "Start setting for Camelot missing"
        assert "end" in setting, "End setting for Camelot missing"
        assert "body" in setting, "Body setting missing"
        #assert (
        #    value.count(self.options["decimal_separator"]) < 2
        #), "Decimal separator cannot be present several times"

        # Which inputs are needed??
        # Settings json for camelot
        # Which table number to extract?? (Should we do this what if recognition issues?)
        # if passed, do only that table, else do all

        # can/should be handled in invoice_template.py or here as pandas is quicker
        # see parse_number

        ######################
        # Options
        ######################
        # Change the column headers to a key from the config file
        # set datatype?
        # Option: Use regex, for example start_date parsing

        # Automatically remove the currency sign when an amount field is set.

        # SECTION HEADERS, TITLE's
        # ho to mark a record with off standard settings? for example, section headers?
        # regularly it will be converted to json with the column header as key.
        # we want to replace that key if:
        # Regex matches
        # The columns besid it are empty.
        # eg no price info or qty means it is a section header

        # Ignore Columns
        # If we want to exclude a column from the JSON output
        # How can that be done?

        # First apply default options.
        plugin_settings = DEFAULT_OPTIONS.copy()
        plugin_settings.update(setting)
        setting = plugin_settings

        # how to pase additional options
        logger.debug("Camelot rule_options 1!!*%s*", setting["camelot_rules_json"])
        rule_options = ""
        rule_options = json.loads(setting["camelot_rules_json"]) #rule.
        logger.debug("Camelot rule_options *%s*", rule_options)
        # ok so now is passing json

        start = re.search(setting["start"], content)
        end = re.search(setting["end"], content)

        if not start or not end:
            logger.warning(
                "no table body found - start %s, end %s", start, end
            )
            continue

    tables = camelot.read_pdf(invoicefile) # , strip_text=currency_symbol


    logger.debug(self) # write to output for testing

    logger.debug("Camelot tables %s", tables)
    df = tables[0].df
    # camelot_json = tables[0].to_json
    # logger.debug("Camelot json result %s", camelot_json)

    #######################
    # Replace header rows #
    #######################
    # we got to replace the header
    #new_header = df.iloc[0] #grab the first row for the header
    # df = df[1:] #take the data less the header row gives copy error


    # set first row as column name
    df.rename(columns=df.iloc[0], inplace = True) # .drop(df.index[0], inplace = True)
    # drop the first row from the dataset
    df.drop(df.index[0], inplace = True)

    # next step, rename the columns
    df.rename(columns={'Discount' : 'Bill'}, inplace = True)

    # When 2 similar named columns are passed, an error occurs b/c/ of not unique key constraint.
    # But in this use case, we are not in control which clumn names are on the pdf.
    # better solution is to assign a custom column name. Leave the index with an integer in tact
    # when converting to json, use the custom column as key instead of the index.
    # in that way, the user has the ability to replace the "double" key, before writing to json 

    logger.debug("Camelot df\n%s", df)
    # testd = df.Amount.values.dtype
    # logger.debug("testd is !!!! %s", testd) # return object

    # export df
    # df.to_csv("result.csv")


    #######################
    # Cleanup currency rows header rows #
    #######################
# def clean_currency_field():
    # remove all non numbers from the Amount field
    element = "Amount" # target element in output
    amounttype = df.loc[:, 'Amount'].dtype
    print(f"amounttype (clean alt)  is !!!! {amounttype}") # return object


    if "," in self.options["decimal_separator"]:
        # replace , with .
        df.loc[:, (element)] = np.char.replace(df.loc[:, (element)].values.astype(str), ',','.')
    df.loc[:, (element)] = [numbers(x) for x in df.loc[:, (element)]]
    df.loc[:, (element)] = df.loc[:, (element)].replace('', np.nan).astype(float)

    # Check the returned dtype
    testd = df.loc[:, (element)].dtype
    logger.debug(f"{element} dtype is {testd} !!!!") # return object


    logger.debug(f"Camelot df after processing \n{df}")

    #######################
    # Cleanup currency rows header rows #
    #######################
    date_element = "Amount" # target element in output


    #######################
    # DATAFRAME TO JSON   #
    #######################

    result = df.to_json(orient="records", force_ascii=False) # make orient configurable
    logger.debug("Pandas dataframe to json result\n%s", result)

    # for debugging write json to logger
    parsed = json.loads(result)
    # json.dumps(parsed, indent=4)
    parsed = json.dumps(parsed,indent=4, sort_keys=True, ensure_ascii=False, separators=(',', ': ')).replace('\\n','\n')
    logging.info('dataframe head\n{}'.format(parsed, force_ascii=False))

    # logger.debug("json dumps result %s", parsed)


    # append the result to the output
    output["camelot"] = result

def numbers(element2):

    return "".join(filter(is_number, element2)).replace(',','.') # .join(filter(str.isnumeric, element2))


def is_number(element2):
    # logger.debug(f"Element2 of is number is !!!! *{element2}* ")
    list_of_vowels = ['.', '-', ',']
    if element2 in list_of_vowels or element2.isnumeric():
        return True
