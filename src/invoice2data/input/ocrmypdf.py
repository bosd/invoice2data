# -*- coding: utf-8 -*-

import logging

from subprocess import Popen, PIPE, STDOUT, CalledProcessError, TimeoutExpired
import shutil

logger = logging.getLogger(__name__)


def to_text(path: str, area_details: dict = None):
    
    """Parse PDF files with ocrmypdf for OCR.

    Before usage make sure you have the dependencies installed.

    Parameters
    ----------
    path : str
        path of electronic invoice in PDF format

    Returns
    -------
    extracted_str : str
        returns extracted text from pdf

    """

    try:
        import ocrmypdf
    except ImportError:
        logger.warning("Cannot import ocrmypdf")

    timeout = 180

    # ocrmypdf.configure_logging(verbosity: Verbosity, *, progress_bar_friendly: bool = True, manage_root_logger: bool = False, plugin_manager=None)
    # ocrmypdf.ocr('input.pdf', 'output.pdf', deskew=True)
    logger.debug("Text extraction made with ocrmypdf")

    myocr_cmd = [
        "ocrmypdf",
        path,
        "-",
        "--redo-ocr"
    ]

    try:
        p1 = Popen(myocr_cmd, stdout=PIPE)
    except TimeoutExpired:
        p1.kill()
        logger.warning("ocrmypdf took too long - skipping")
        return False

    if shutil.which('pdftotext'):
        cmd = ["pdftotext", "-layout", "-enc", "UTF-8"]
        if area_details is not None:
            # An area was specified
            # Validate the required keys were provided
            assert 'f' in area_details, 'Area r details missing'
            assert 'l' in area_details, 'Area r details missing'
            assert 'r' in area_details, 'Area r details missing'
            assert 'x' in area_details, 'Area x details missing'
            assert 'y' in area_details, 'Area y details missing'
            assert 'W' in area_details, 'Area W details missing'
            assert 'H' in area_details, 'Area H details missing'
            # Convert all of the values to strings
            for key in area_details.keys():
                area_details[key] = str(area_details[key])
            cmd += [
                '-f', area_details['f'],
                '-l', area_details['l'],
                '-r', area_details['r'],
                '-x', area_details['x'],
                '-y', area_details['y'],
                '-W', area_details['W'],
                '-H', area_details['H'],
            ]
        cmd += ["-", "-"]
        # Run the extraction
        p2 = Popen(cmd, stdin=p1.stdout, stdout=PIPE)
    try:
        out, err = p2.communicate(timeout=timeout)
        extracted_str = out
    except TimeoutExpired:
        p2.kill()
        logger.warning("pdftotext took too long - skipping")
    return extracted_str
