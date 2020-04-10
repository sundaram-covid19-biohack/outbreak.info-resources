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

from etl.bioschemas.converter import Converter as Con


DEFAULT_VERBOSE = False

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))


class Converter(Con):
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

        
    def run(self, protocols_json_file: str = None, protocols_schema_mapping_file: str = None, outfile: str = None) -> None:
        """Extract the values from the protocols.io JSON file.
        The protocols schema mapping file will drive the process.
        :param protocols_json_file: {str}
        :param protocols_schema_mapping_file: {str}
        :param outfile: {str}
        :returns None:
        """

        lookup = self._load_bioschema_term_to_json_search_param_lookup(protocols_schema_mapping_file)
        
        results = {}

        with open(protocols_json_file, 'r') as json_fh:
            
            json_data = json.load(json_fh)

            if 'items' not in json_data:
                logging.error("'items' does not exist in the JSON file '{}'".format(protocols_json_file))
                sys.exit(1)
            
            item_ctr = 0
            
            for item_lookup in json_data['items']:

                item_ctr += 1

                data_lookup = {}
                doi = None

                for term in lookup:
                    logging.info("Processing bioschema term '{}'".format(term))
                    json_search_param = lookup[term]
                    logging.info("json search param '{}'".format(json_search_param))
                    if json_search_param is None or json_search_param == '' or json_search_param == 'N/A':
                        logging.info("There is no valid json search param for bioschema term '{}'".format(term))
                        continue
                    else:

                        if '[' in json_search_param:
                            values = self._get_list_of_values(item_lookup, json_search_param)
                            if len(values) > 0:
                                logging.info("Found the following values for bioschema term '{}': '{}'".format(term, ', '.join(values)))
                                data_lookup[term] = values

                        else:
                            value = self._get_param_value(item_lookup, json_search_param)
                            if value is None or value == '':
                                logging.info("Did not find any value for bioschema term '{}'".format(term))
                                continue
                            else:
                                logging.info("Found value '{}' for bioschema term '{}'".format(value, term))
                                if term == 'identifier':
                                    doi = value
                                else:
                                    data_lookup[term] = value
                
                results[doi] = self._transform_authors(data_lookup)
            
            logging.info("Processed '{}' items in JSON file '{}'".format(item_ctr, protocols_json_file))
                    
        self._write_output_file(results, outfile)

    def _transform_authors(self, data_lookup):
        """Transform the data structure containing the author metadata
        :param data_lookup: {dict}
        :returns transformed_lookup: {dict}
        """
        logging.info("Going to transform the author data structure")
        transformed_lookup = {}
        
        author_name_list = None
        affiliation_list = None

        for param in data_lookup:
        
            logging.info("Processing param '{}'".format(param))
        
            if param == 'author.name':
                author_name_list = data_lookup[param]
            elif param == 'author.affiliation':
                affiliation_list = data_lookup[param]
            else:
                transformed_lookup[param] = data_lookup[param]
        
        author_list = []
        
        for i, author_name in enumerate(author_name_list):
            affiliation = affiliation_list[i]
            logging.info("Processing author name '{}' affiliation '{}'".format(author_name, affiliation))
            author_list.append({'name': author_name, 'affiliation': affiliation})
        
        transformed_lookup['author'] = author_list
        
        return transformed_lookup
