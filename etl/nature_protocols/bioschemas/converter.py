import os
import sys
import pathlib
import logging
import calendar
import time
import json
from singleton_decorator import singleton
from jsonpath_ng import jsonpath, parse
from colorama import Fore, Style
from datetime import datetime
from datetime import date

import etl.bioschemas.converter


DEFAULT_VERBOSE = False

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))


@singleton
class Converter(etl.bioschemas.converter.Converter):
    """
    """
    def __init__(self, **kwargs):
        """
        """
        if 'verbose' in kwargs:
            self._verbose = kwargs['verbose']
        else:
            self._verbose = DEFAULT_VERBOSE

        if 'outdir' in kwargs:
            self._outdir = kwargs['outdir']
        else:
            self._outdir = DEFAULT_OUTDIR

        if 'outfile' in kwargs:
            self._outfile = kwargs['outfile']
        else:
            self._outfile = os.path.join(self._outdir, os.path.basename(self._infile) + '.json')

        
    def run(self, protocols_json_file: str = None, protocols_schema_mapping_file: str = None, outfile: str = None) -> None:
        """Extract the values from the protocols.io JSON file.
        The protocols schema mapping file will drive the process.
        :param protocols_json_file: {str}
        :param protocols_schema_mapping_file: {str}
        :param outfile: {str}
        :returns None:
        """
        logging.error("NOT YET IMPLEMENTED")
        sys.exit(1)

