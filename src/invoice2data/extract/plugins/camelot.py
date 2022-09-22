# -*- coding: utf-8 -*-

import re
import logging
import json
import numpy as np

from collections import OrderedDict

from pathlib import Path
import os

import camelot
from camelot.parsers import Stream, Lattice
from camelot.utils import get_rotation, get_page_layout, get_text_objects

# added for get pages
from PyPDF2 import PdfFileReader, PdfFileWriter


# PYTHONIOENCODIG="utf-8" # python -c 'import sys'

# to check is pandas available?
# import pandas as pd

# PYTHONIOENCODING="UTF-8"

logger = logging.getLogger(__name__)

logging.getLogger("pdfminer").setLevel(logging.WARNING)

DEFAULT_OPTIONS = {"field_separator": r"\s+", "line_separator": r"\n", "coltofloat": ['Unit price', 'Amount']}
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
    # logger.debug(self)
    logger.debug("%s is the invoicefile",invoicefile)  # is there a path var?
    # logger.debug("Camelot :)")

    # allows to pass multiple camelot arguments
    for setting in self["camelot"]:

        # whole block may need adjusting

        # Validate settings
        # assert "start" in setting, "Start setting for Camelot missing"
        assert "table" in setting, "table setting for Camelot missing"
        # assert "end" in setting, "End setting for Camelot missing"
        # assert "body" in setting, "Body setting missing"
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
        logger.debug(f"Camelot setting 000000000000\n{setting}")
        # how to pase additional options
        logger.debug("Camelot rule_options 1!!*%s*", setting["camelot_rules_json"])
        rule_options = ""
        rule_options = json.loads(setting["camelot_rules_json"]) #rule.
        logger.debug("Camelot rule_options \n*%s*", rule_options)
        # ok so now is passing json


    '''
        flavor = rule_options.pop("flavor")
        pages = rule_options.pop("pages")

        tables = []
        filepaths = json.loads(file.filepaths) # need change
        # pages is not needed here, can be a kwarg pages 1-end
        for p in pages:
            kwargs = pages[p]
            kwargs.update(rule_options)
            parser = (
                Lattice(**kwargs) if flavor.lower() == "lattice" else Stream(**kwargs)
            )
            t = parser.extract_tables(filepaths[p])
            for _t in t:
                _t.page = int(p)
            tables.extend(t)
        tables = TableList(tables)
    '''

    kwargs = {}
    # kwargs.update(rule_options)
    logger.debug("Camelot arguments \n*%s*", kwargs)
    # old method from cli
    # tables = camelot.read_pdf(invoicefile, **kwargs) # , strip_text=currency_symbol


    # new method
    flavor = rule_options.pop("flavor")
    pages = rule_options.pop("pages")
    # pages = 1  # ovverride pages
    tables = []
    # session = Session()

# from excalibur
    PDFS_FOLDER = Path.home()
    filepath = os.path.join(PDFS_FOLDER, invoicefile)

    file = File(
        # self,
        __tablename__="table",
        file_id=100, # (ID_LEN), primary_key=True
        # uploaded_at = DateTime
        pages="all",
        total_pages=1,
        extract_pages=1,
        filename=invoicefile,
        filepath=filepath,
        has_image=0,
        filenames="",
        filepaths="",
        imagenames="",
        imagepaths="",
        filedims="",
        imagedims="",
        detected_areas=""
    )   
    logger.debug("Camelot file object is \n*%s*", file)
    extract_pages, total_pages = get_pages(file.filepath, file.pages)

    (
        filenames,
        filepaths,
        imagenames,
        imagepaths,
        filedims,
        imagedims,
        detected_areas,
    ) = ({} for i in range(7))

    for page in extract_pages:
        # extract into single-page PDF
        save_page(file.filepath, page)
        # todo assign file_id

        # place files in home dir for debugging
        PDFS_FOLDER = Path.home()
        filename = f"page-{page}.pdf"
        # filepath = os.path.join(PDFS_FOLDER, file.file_id, filename)
        filepath = os.path.join(PDFS_FOLDER, filename)
        # todo change PDFS_FOLDER to tempdir
        imagename = "".join([filename.replace(".pdf", ""), ".png"])
        imagepath = os.path.join(PDFS_FOLDER, imagename)


    filename = f"page-{page}.pdf"
    filenames[page] = filename
    filepaths[page] = filepath
    imagenames[page] = imagename
    imagepaths[page] = imagepath
    filedims[page] = {} # get_file_dim(filepath)
    imagedims[page] = {} # get_image_dim(imagepath)


    file.extract_pages = json.dumps(extract_pages)
    file.total_pages = total_pages
    file.has_image = True
    file.filenames = json.dumps(filenames)
    file.filepaths = json.dumps(filepaths)
    file.imagenames = json.dumps(imagenames)
    file.imagepaths = json.dumps(imagepaths)
    file.filedims = json.dumps(filedims)
    file.imagedims = json.dumps(imagedims)
    file.detected_areas = json.dumps(detected_areas)

# end from excalibur



    # file = session.query(File).filter(File.file_id == job.file_id).first()
    # file = invoicefile # temp override
    # filepaths = json.loads(file.filepaths)
    # filepaths = invoicefile
    relative = Path(invoicefile)
    absolute = relative.absolute()  # absolute is a Path object
    absolute = str(absolute) # .as_posix()
    filepaths = {"1":absolute,"2":2} # invoicefile
    filepaths = json.loads(file.filepaths) # original


    logger.debug("Camelot filepaths is \n*%s*", filepaths)
    for p in pages:
        logger.debug("Camelot p is *%s*", p)
        kwargs = pages[p]
        kwargs.update(rule_options)
        parser = (
            Lattice(**kwargs) if flavor.lower() == "lattice" else Stream(**kwargs)
        )
        t = parser.extract_tables(filepaths[p])
        # for _t in t:
        #    _t.page = int(p)
        tables.extend(t)


    logger.debug(self) # write to output for testing

    logger.debug("Camelot tables %s", tables)

    # TODO
    # Make flexible to extract more tables
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
    # df.rename(columns={'Discount' : 'Bill'}, inplace = True)
    df.rename(columns=setting["rename_columns"], inplace = True)

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

    # element = "Amount" # target element in output
    # element contain the list of columns to parse to float.
    # could be a to_float

    # element = ['Unit price', 'Amount']
    # Load the element var from default settings
    element = setting["coltofloat"]
    # How to handle Key error

    '''
    amounttype = df.loc[:, 'Amount'].dtype
    print(f"amounttype (clean alt)  is !!!! {amounttype}") # return object
    '''

## new test ##

    # for column in columns:

    # place this in for loop
    # need to adjust this. Do not change it in result, but before utilizing df

    # option:
    # A detect amount in column name, more user friendly.
    # B use assignment, more flexible

    # Load A in standard setting and append B.
    # qty = float
    # 
    # price_unit | float
    # discount | float
    # price_subtotal | float | 

    # elif k.startswith("amount"):
    # so if part of column name matches amount, then perform currency cleanup
    # So loop trough column names in df, match setting 

    # needs different approach because currency cleanup and type conversion is onethrow 
    logger.debug(f"Camelot setting \n{setting}")
    resulting = []
    keys = setting.keys()
    logger.debug(f"Camelot col is *{keys}*")
    # if type in setting:
    if setting.get("type") is "float": # .get(col)
        logger.debug(f"\nlucky me \n*{type}*\n")

    # parse yaml settings and add to element list
    #for field, typ in setting.items():
    for field, val in setting.items():
            # print('{}: {}'.format(key, field))
        logger.debug("komt het\n")
        logger.debug("{}: {}".format(val, field))
        logger.debug("was het")
        if type(val) == OrderedDict:
          for typ, v in val.items():
                logger.debug(f"type is in val, typ is *{v}*")
                if v == "float":
                    logger.debug("type is float, so append to list")
                    element.append(field)
                    logger.debug(f"element is now *{element}* ")

    # Add function which deletes the columns which are not in the df, to prevent KeyError
    # can fail on the standard settings
    # can fail on the settings from the yaml.

    # alternative
    # For each table create a 
    # task (task kan niet, want column moet bekend zijn)
    # 1 looptrough df columns, 
    # 2 if column matches yaml or standard setting, append to list
    # 

    '''
    for col in setting:
        keys = setting.keys()
        logger.debug(f"Camelot col is *{col}*")
        val = setting.get(col)
        logger.debug(f"Camelot val is *{val}*")
        # if val.get("type") is float:
            # logger.debug(f"\nCol type found!!!\n")
        if "type" in col:
            temp = setting["type"]
            logger.debug(f"Camelot type is in setting!!!")
            logger.debug(f"Camelot type is in setting!!! type is FLOAT *{temp}*")
            # for each passed column with type float.
            # append column name to the list element 
            # for setting[key], setting["type"] in setting:
            if type in col is "float":
                element.append(setting[key])
                # logger.debug(f"Camelot type is in setting!!! type is FLOAT *{setting["type"]}*")
            for k, v in enumerate(resulting):
                resulting[k] = template.coerce_type(v, setting["type"])
                logger.debug(f"Camelot dresult k \n{resulting[k]}")
    '''

    if "," in self.options["decimal_separator"]:
        # replace , with .
        df.loc[:, (element)] = np.char.replace(df.loc[:, (element)].values.astype(str), ',','.')
    for elm in element:
        df.loc[:, (elm)] = [numbers(x) for x in df.loc[:, (elm)]]
        logger.debug(f"Camelot dfS step processing \n{df}")
    df.loc[:, (element)] = df.loc[:, (element)].replace('', np.nan).astype(float)

    # Check the returned dtype
    # testd = df.loc[:, (element)].dtype
    # logger.debug(f"{element} dtype is {testd} !!!!") # return object


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

# https://numpy.org/doc/stable/reference/arrays.dtypes.html
# https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string


# https://www.quora.com/How-do-I-remove-the-commas-and-currency-symbols-while-webscraping-data-in-Python-so-that-the-data-can-be-used-as-an-integer-float
# how is cleanup   of decimals done in invoice2data

# how to know where to apply the replacing of chars
# apply a fulter on amount fields
# https://www.stackvidhya.com/pandas-get-column-names/  See section 'Pandas Get Column Names Starting With'

# https://discuss.dizzycoding.com/fast-replacement-of-values-in-a-numpy-array/

# currency cleanup
# https://pbpython.com/currency-cleanup.html


def coerce_type(self, value, target_type):
    if target_type == "int":
        if not value.strip():
            return 0
        return int(self.parse_number2(value))
    elif target_type == "float":
        if not value.strip():
            return 0.0
        return float(self.parse_number2(value))
    elif target_type == "date":
        return self.parse_date(value)
    assert False, "Unknown type"

def numbers(element2):

    return "".join(filter(is_number, element2)).replace(',','.') # .join(filter(str.isnumeric, element2))


def is_number(element2):
    # logger.debug(f"Element2 of is number is !!!! *{element2}* ")
    list_of_vowels = ['.', '-', ',']
    if element2 in list_of_vowels or element2.isnumeric():
        return True

## from excalibur
def split(file_id):
    try:
        # session = Session()
        file = session.query(File).filter(File.file_id == file_id).first()
        extract_pages, total_pages = self.get_pages(file.filepath, file.pages)

        (
            filenames,
            filepaths,
            imagenames,
            imagepaths,
            filedims,
            imagedims,
            detected_areas,
        ) = ({} for i in range(7))
        for page in extract_pages:
            # extract into single-page PDF
            self.save_page(file.filepath, page)

            filename = f"page-{page}.pdf"
            filepath = os.path.join(conf.PDFS_FOLDER, file_id, filename)
            imagename = "".join([filename.replace(".pdf", ""), ".png"])
            imagepath = os.path.join(conf.PDFS_FOLDER, file_id, imagename)

            # convert single-page PDF to PNG
            gs_call = f"-q -sDEVICE=png16m -o {imagepath} -r300 {filepath}"
            gs_call = gs_call.encode().split()
            null = open(os.devnull, "wb")
            with Ghostscript(*gs_call, stdout=null):
                pass
            null.close()

            filenames[page] = filename
            filepaths[page] = filepath
            imagenames[page] = imagename
            imagepaths[page] = imagepath
            filedims[page] = get_file_dim(filepath)
            imagedims[page] = get_image_dim(imagepath)

            lattice_areas, stream_areas = (None for i in range(2))
            # lattice
            parser = Lattice()
            tables = parser.extract_tables(filepath)
            if len(tables):
                lattice_areas = []
                for table in tables:
                    x1, y1, x2, y2 = table._bbox
                    lattice_areas.append((x1, y2, x2, y1))
            # stream
            parser = Stream()
            tables = parser.extract_tables(filepath)
            if len(tables):
                stream_areas = []
                for table in tables:
                    x1, y1, x2, y2 = table._bbox
                    stream_areas.append((x1, y2, x2, y1))

            detected_areas[page] = {"lattice": lattice_areas, "stream": stream_areas}

        file.extract_pages = json.dumps(extract_pages)
        file.total_pages = total_pages
        file.has_image = True
        file.filenames = json.dumps(filenames)
        file.filepaths = json.dumps(filepaths)
        file.imagenames = json.dumps(imagenames)
        file.imagepaths = json.dumps(imagepaths)
        file.filedims = json.dumps(filedims)
        file.imagedims = json.dumps(imagedims)
        file.detected_areas = json.dumps(detected_areas)

        # session.commit()
        # session.close()
    except Exception as e:
        logging.exception(e)

def get_pages(filename, pages, password=""):
    """Converts pages string to list of ints.
    Parameters
    ----------
    filename : str
        Path to PDF file.
    pages : str, optional (default: '1')
        Comma-separated page numbers.
        Example: 1,3,4 or 1,4-end.
    Returns
    -------
    N : int
        Total pages.
    P : list
        List of int page numbers.
    """
    page_numbers = []
    inputstream = open(filename, "rb")
    infile = PdfFileReader(inputstream, strict=False)
    N = infile.getNumPages()
    if pages == "1":
        page_numbers.append({"start": 1, "end": 1})
    else:
        if infile.isEncrypted:
            infile.decrypt(password)
        if pages == "all":
            page_numbers.append({"start": 1, "end": infile.getNumPages()})
        else:
            for r in pages.split(","):
                if "-" in r:
                    a, b = r.split("-")
                    if b == "end":
                        b = infile.getNumPages()
                    page_numbers.append({"start": int(a), "end": int(b)})
                else:
                    page_numbers.append({"start": int(r), "end": int(r)})
    inputstream.close()
    P = []
    for p in page_numbers:
        P.extend(range(p["start"], p["end"] + 1))
    return sorted(set(P)), N

def save_page(filepath, page_number):
    infile = PdfFileReader(open(filepath, "rb"), strict=False)
    page = infile.getPage(page_number - 1)
    outfile = PdfFileWriter()
    outfile.addPage(page)
    outpath = os.path.join(os.path.dirname(filepath), f"page-{page_number}.pdf")
    with open(outpath, "wb") as f:
        outfile.write(f)
    froot, fext = os.path.splitext(outpath)
    layout, __ = get_page_layout(outpath)
    # fix rotated PDF
    chars = get_text_objects(layout, ltype="char")
    horizontal_text = get_text_objects(layout, ltype="horizontal_text")
    vertical_text = get_text_objects(layout, ltype="vertical_text")
    rotation = get_rotation(chars, horizontal_text, vertical_text)
    if rotation != "":
        outpath_new = "".join([froot.replace("page", "p"), "_rotated", fext])
        os.rename(outpath, outpath_new)
        infile = PdfFileReader(open(outpath_new, "rb"), strict=False)
        if infile.isEncrypted:
            infile.decrypt("")
        outfile = PdfFileWriter()
        p = infile.getPage(0)
        if rotation == "anticlockwise":
            p.rotateClockwise(90)
        elif rotation == "clockwise":
            p.rotateCounterClockwise(90)
        outfile.addPage(p)
        with open(outpath, "wb") as f:
            outfile.write(f)


Base = any # declarative_base()  # type: Any

class File():
    def __init__(
        self,
        __tablename__,
        file_id, # (ID_LEN), primary_key=True
        # uploaded_at = DateTime
        pages,
        total_pages,
        extract_pages,
        filename,
        filepath,
        has_image,
        filenames,
        filepaths,
        imagenames,
        imagepaths,
        filedims,
        imagedims,
        detected_areas
    ):
        # self.has_image = False
        # self.age = age
        self.__tablename__ = __tablename__
        self.file_id = file_id
        self.pages = pages
        self.total_pages = total_pages
        self.extract_pages = extract_pages 
        self.filename = filename
        self.filepath = filepath
        self.has_image = has_image 
        self.filenames = filenames
        self.filepaths = filepaths 
        self.imagenames = imagenames 
        self.imagepaths = imagepaths
        self.filedims = filedims
        self.imagedims = imagedims
        self.detected_areas = detected_areas
        # file_id = str # (ID_LEN), primary_key=True
        # # uploaded_at = DateTime
        # pages = str
        # total_pages = int
        # extract_pages = str
        # filename = str
        # filepath = str
        # has_image = bool # , default=False
        # filenames = str
        # filepaths = str
        # imagenames = str
        # imagepaths =  str
        # filedims = str
        # imagedims = str
        # detected_areas = str

    def myfunc(abc):
        print("Hello my name is " + abc.name)