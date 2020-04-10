import os
import sys
import pathlib
import logging
import calendar
import time
import json
from jsonpath_ng import jsonpath, parse
from colorama import Fore, Style
from datetime import datetime
from datetime import date

BIOSCHEMAS_TERM_IDX = 0
JSON_SEARCH_PARAM_IDX = 1

DEFAULT_VERBOSE = False

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))


class Converter(object):
    """Class for convertering the protocols.io JSON results into bioschemas JSON
    """
    def __init__(self, **kwargs):
        """Class constructor
        :param verbose: {bool}
        :param outdir: {str}
        :param outfile: {str}
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


    def _get_list_of_values(self, json_data: dict = {}, text: str = None) -> list:
        """Retrieve a list of values
        :param json_data: {dict}
        :param text: {str}
        :returns list_of_values: {list}
        """
        search_text = '$.' + text
        logging.info("Using jsonpath search text '{}'".format(search_text))
        jsonpath_expression = parse(search_text)
        matches = jsonpath_expression.find(json_data)
        values = []
        if matches:
            for match in matches:
                val = match.value
                values.append(val)
        return values
        
    def _extract_values(self, protocols_json_file: str = None, protocols_schema_mapping_file: str = None, outfile: str = None) -> None:
        """Extract the values from the protocols.io JSON file.
        The protocols schema mapping file will drive the process.
        :param protocols_json_file: {str}
        :param protocols_schema_mapping_file: {str}
        :param outfile: {str}
        :returns None:
        """
        logging.error("This a method in an abstract base class - implement this method in a class that inherits this one")
        sys.exit(1)
        
    def _write_output_file(self, results: dict = {}, outfile: str = None) -> None:
        """Write the extracted results to an output JSON file
        :param results: {dict}
        :param outfile: {str}
        :returns None:
        """
        if outfile is None:
            if self._outfile is None:
                logging.error("outfile is not defined")
                sys.exit(1)
            outfile = self._outfile

        with open(outfile, 'w') as fout:
            json.dump(results, fout, indent=2)

        logging.info("Wrote '{}'".format(outfile))
        if self._verbose:
            print("Wrote '{}'".format(outfile))



    def _get_param_value(self, json_data: dict = None, text: str = None) -> str:
        """Use jsonpath to parse the JSON tree and retrieve the value for the specified search term
        :param json_data: {dict}
        :param text: {str}
        :returns value: {str}
        """
        search_text = '$.' + text
        logging.info("Using search term '{}'".format(search_text))
        jsonpath_expression = parse(search_text)
        match = jsonpath_expression.find(json_data)
        if match:
            return match[0].value
        else:
            return None


    def _load_bioschema_term_to_json_search_param_lookup(self, infile: str = None) -> dict:
        """Parse the protocols schema mapping tab-delimited file and load the tuples into
        a dictionary.
        :param infile: {str}
        :returns lookup: {dict}
        """
        bioschema_term_to_json_search_param_lookup = {}

        logging.info("Will parse '{}'".format(infile))
        
        with open(infile, 'r') as fh:
            for line in fh:
                line = line.strip()
                if line.startswith('#'):
                    continue
                parts = line.split("\t")
                if len(parts) > 1:
                    json_search_param = parts[JSON_SEARCH_PARAM_IDX] 
                    bioschema_term = parts[BIOSCHEMAS_TERM_IDX]
                    if bioschema_term is not None and json_search_param is not None:                
                        bioschema_term_to_json_search_param_lookup[bioschema_term] =  json_search_param
        
        logging.info("Loaded the bioschema term to json search param lookup")
        
        return bioschema_term_to_json_search_param_lookup

