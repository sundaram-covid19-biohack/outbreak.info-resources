
import csv
import os
import sys
import click
import pathlib
import logging
import calendar
import time
import pathlib
from encodeproject import download as encode_download  # type: ignore
from colorama import Fore, Style
from datetime import datetime
from datetime import date

# If set to True, will only process the number of terms
# specified by the DEFAULT_TEST_COUNT
DEFAULT_TEST_MODE = False

# This sets the default number of terms to be processed
DEFAULT_TEST_COUNT = 2

DEFAULT_VERBOSE = False

DEFAULT_COVID_TERMS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covid_terms.txt')

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

g_verbose = False
g_test_mode = False
g_test_count = 0

def retrieve_datasets(terms_list, outdir):
    """Retrieve the datasets (JSON format) from protocols.io
    for the specified terms.
    :param terms_list: {list} the list of terms
    :param outdir: {str} the output directory
    :returns None:
    """

    for i, term in enumerate(terms_list):
        logging.info("Processing term '{}'".format(term))

        url = 'https://www.protocols.io/api/v3/protocols?filter="public"&key="' + term.lower() + '"'
        logging.info("URL is '{}'".format(url))
        outfile_basename = term.replace(' ', '') + '.json'
        outfile = os.path.join(outdir , outfile_basename)
        logging.info("outfile is '{}'".format(outfile))

        if g_verbose:
            print(Fore.BLUE + "Processing term '{}'".format(term))
            print(Style.RESET_ALL + '', end='')
            print("URL is '{}'".format(url))
            print("outfile is '{}'".format(outfile))

        encode_download(url=url, path=outfile)

        if not os.path.exists(outfile):
            logging.error("output file '{}' does not exist".format(outfile))
        if g_test_mode:
            if i > g_test_count:
                break


def load_terms_list(terms_file):
    """Load the search terms from a control file into a list
    :param terms_file: {str}
    :returns terms_list: {list}
    """
    terms_list = []

    with open(terms_file, 'r') as fh:
        for line in fh:
            if line.startswith('#'):
                continue
            line = line.strip()
            terms_list.append(line)

    logging.info("Loaded '{}' terms from file '{}' into the terms list".format(len(terms_list), terms_file))
    if g_verbose:
        print("Loaded '{}' terms from file '{}' into the terms list\n".format(len(terms_list), terms_file))
    return terms_list


@click.command()
@click.option('--outdir', help='The default is the current working directory - default is {}'.format(DEFAULT_OUTDIR))
@click.option('--terms_file', help="The new-line separated list of covid terms - default is {}".format(DEFAULT_COVID_TERMS_FILE))
@click.option('--logfile', help="The log file - if not is specified a default will be assigned")
@click.option('--verbose', is_flag=True, help="Whether to execute in verbose mode - default is {}".format(DEFAULT_VERBOSE))
@click.option('--test_mode', is_flag=True, help="Whether to execute in test mode (will limit number of terms processed - default is {})".format(DEFAULT_TEST_MODE))
@click.option('--test_count', help="The number of terms to process when executing in test mode - default is {}".format(DEFAULT_TEST_COUNT))
def main(outdir, terms_file, logfile, verbose, test_mode, test_count):
    """Retrieve datasets (JSON format) from protocols.io for covid-related terms.
    The terms are specified via the --terms_file option.  This should be a newline
    separated list of terms.
    """

    if verbose is None:
        verbose = DEFAULT_VERBOSE
        print(Fore.YELLOW + "--verbose was not specified and therefore was set to default '{}'".format(verbose))
        print(Style.RESET_ALL + '', end='')

    global g_verbose
    g_verbose = verbose

    if test_mode is None:
        test_mode = DEFAULT_TEST_MODE
        print(Fore.YELLOW + "--test_mode was not specified and therefore was set to default '{}'".format(test_mode))
        print(Style.RESET_ALL + '', end='')

    global g_test_mode
    g_test_mode = test_mode

    if test_mode:
        if test_count is None:
            test_count = DEFAULT_TEST_COUNT
            print(Fore.YELLOW + "--test_count was not specified and therefore was set to default '{}'".format(test_count))
            print(Style.RESET_ALL + '', end='')

        global g_test_count
        g_test_count = test_count

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

    if terms_file is None:
        terms_file = DEFAULT_COVID_TERMS_FILE
        print(Fore.YELLOW + "--terms_file was not specified and therefore was set to '{}'".format(terms_file))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(terms_file, str)

    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)

    terms_list = load_terms_list(terms_file)

    retrieve_datasets(terms_list, outdir)


if __name__ == "__main__":
    main()