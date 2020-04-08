import os
import sys
import click
import pathlib
import logging
import calendar
import time
import pathlib
import json
from jsonpath_ng import jsonpath, parse
from colorama import Fore, Style
from datetime import datetime
from datetime import date

SCHEMAS_TERM_IDX = 0
PROTOCOLS_TERM_IDX = 1

DEFAULT_VERBOSE = False

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

g_verbose = False

def extract_values(protocols_json_file: str = None, protocols_schema_mapping_file: str = None, outfile: str = None) -> None:
    """Extract the values from the protocols.io JSON file.
    The protocols schema mapping file will drive the process.
    :param protocols_json_file: {str}
    :param protocols_schema_mapping_file: {str}
    :param outfile: {str}
    :returns None:
    """
    lookup = load_mapping_lookup(protocols_schema_mapping_file)
    
    results = []

    with open(protocols_json_file, 'r') as json_fh:
        
        json_data = json.load(json_fh)

        if 'items' not in json_data:
            logging.error("'items' does not exist in the JSON file '{}'".format(protocols_json_file))
            sys.exit(1)

        data_lookup = {}
        
        item_ctr = 0
        
        for item_lookup in json_data['items']:
            item_ctr += 1

            for term in lookup:
                source = lookup[term]
                if source is None or source == '' or source == 'N/A':
                    logging.info("There is no mapping for term '{}'".format(term))
                    continue
                else:
                    value = get_param_value(item_lookup, term)
                    if value is None or value == '':
                        logging.info("Did not find any value for term '{}'".format(term))
                        continue
                    else:
                        logging.info("Found value '{}' for term '{}'".format(value, term))
                        data_lookup[term] = value
            
            results.append(data_lookup)
        
        logging.info("Processed '{}' items in JSON file '{}'".format(item_ctr, protocols_json_file))
                
    write_output_file(results, outfile)

     
def write_output_file(results: dict = {}, outfile: str = None) -> None:
    """Write the extracted results to an output JSON file
    :param results: {dict}
    :param outfile: {str}
    :returns None:
    """
    with open(outfile, 'w') as fout:
        json.dump(results, fout, indent=2)

    logging.info("Wrote '{}'".format(outfile))
    if g_verbose:
        print("Wrote '{}'".format(outfile))



def get_param_value(json_data: dict = None, text: str = None) -> str:
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


def load_mapping_lookup(infile: str = None) -> dict:
    """Parse the protocols schema mapping tab-delimited file and load the tuples into
    a dictionary.
    :param infile: {str}
    :returns lookup: {dict}
    """
    mapping_lookup = {}

    logging.info("Will parse '{}'".format(infile))
    
    with open(infile, 'r') as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('#'):
                continue
            parts = line.split("\t")
            if len(parts) > 1:
                protocol_term = parts[PROTOCOLS_TERM_IDX] 
                schema_term = parts[SCHEMAS_TERM_IDX]
                if protocol_term is not None and schema_term is not None:                
                    mapping_lookup[protocol_term] =  schema_term
    logging.info("Loaded the mapping lookup")
    return mapping_lookup



@click.command()
@click.option('--outdir', help='The output directory - default is {}'.format(DEFAULT_OUTDIR))
@click.option('--outfile', help='The output file - if not specified a default will be assigned')
@click.option('--protocols_json_file', help="The protocols.io JSON file from which param values will be extracted")
@click.option('--protocols_schema_mapping_file', help="The protocols schema mapping file")
@click.option('--logfile', help="The log file - if not is specified a default will be assigned")
@click.option('--verbose', is_flag=True, help="Whether to execute in verbose mode - default is {}".format(DEFAULT_VERBOSE))
def main(outdir, outfile, protocols_json_file, protocols_schema_mapping_file, logfile, verbose):
    """Parse the protocols JSON file to extract the param values as specified in the protocols schema mapping file.
    """

    error_ctr = 0
    
    if protocols_json_file is None:
        print(Fore.RED + "--protocols_json_file was not specified")
        print(Style.RESET_ALL + '', end='')
        error_ctr += 1

    if protocols_schema_mapping_file is None:
        print(Fore.RED + "--protocols_schema_mapping_file was not specified")
        print(Style.RESET_ALL + '', end='')
        error_ctr += 1

    if error_ctr > 0:
        print(Fore.RED + "Required command-line arguments were not specified")
        print(Style.RESET_ALL + '', end='')
        sys.exit(1)
        
    assert isinstance(protocols_json_file, str)
    assert isinstance(protocols_schema_mapping_file, str)

    if not os.path.exists(protocols_json_file):
        print(Fore.RED + "'{}' does not exist".format(protocols_json_file))
        print(Style.RESET_ALL + '', end='')
        sys.exit(1)
        
    if not os.path.exists(protocols_schema_mapping_file):
        print(Fore.RED + "'{}' does not exist".format(protocols_schema_mapping_file))
        print(Style.RESET_ALL + '', end='')
        sys.exit(1)

    if verbose is None:
        verbose = DEFAULT_VERBOSE
        print(Fore.YELLOW + "--verbose was not specified and therefore was set to default '{}'".format(verbose))
        print(Style.RESET_ALL + '', end='')

    global g_verbose
    g_verbose = verbose

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        print(Fore.YELLOW + "--outdir was not specified and therefore was set to default '{}'".format(outdir))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(outdir, str)

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        print(Fore.YELLOW + "Created output directory '{}'".format(outdir))
        print(Style.RESET_ALL + '', end='')

    if logfile is None:
        logfile = outdir + '/' + os.path.basename(__file__) + '.log'
        print(Fore.YELLOW + "--logfile was not specified and therefore was set to '{}'".format(logfile))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(logfile, str)

    if outfile is None:
        outfile = outdir + '/' + os.path.basename(__file__) + '.txt'
        print(Fore.YELLOW + "--outfile was not specified and therefore was set to '{}'".format(outfile))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(outfile, str)


    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)

    extract_values(protocols_json_file, protocols_schema_mapping_file, outfile)


if __name__ == "__main__":
    main()