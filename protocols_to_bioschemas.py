import os
import sys
import click
import pathlib
import logging
import calendar
import time
from jsonpath_ng import jsonpath, parse
from colorama import Fore, Style
from datetime import datetime
from datetime import date

from etl.bioschemas.converter_factory import Factory


DEFAULT_VERBOSE = False

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO



@click.command()
@click.option('--outdir', help='The output directory - default is {}'.format(DEFAULT_OUTDIR))
@click.option('--outfile', help='The output file - if not specified a default will be assigned')
@click.option('--protocols_json_file', help="The protocols.io JSON file from which param values will be extracted")
@click.option('--protocols_schema_mapping_file', help="The protocols schema mapping file")
@click.option('--source_type', help="The type of protocols e.g.: protocols-io or nature-protocols")
@click.option('--logfile', help="The log file - if not is specified a default will be assigned")
@click.option('--verbose', is_flag=True, help="Whether to execute in verbose mode - default is {}".format(DEFAULT_VERBOSE))
def main(outdir, outfile, protocols_json_file, protocols_schema_mapping_file, source_type, logfile, verbose):
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

    if source_type is None:
        print(Fore.RED + "--source_type was not specified")
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

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        print(Fore.YELLOW + "--outdir was not specified and therefore was set to default '{}'".format(outdir))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(outdir, str)

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        print(Fore.YELLOW + "Created output directory '{}'".format(outdir))
        print(Style.RESET_ALL + '', end='')


    infile_basename = os.path.splitext(os.path.basename(protocols_json_file))[0]

    if logfile is None:
        logfile = os.path.join(outdir, infile_basename + '.log')
        print(Fore.YELLOW + "--logfile was not specified and therefore was set to '{}'".format(logfile))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(logfile, str)

    if outfile is None:
        outfile = os.path.join(outdir, infile_basename + '.json')
        print(Fore.YELLOW + "--outfile was not specified and therefore was set to '{}'".format(outfile))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(outfile, str)


    logging.basicConfig(filename=logfile, 
                    format=LOGGING_FORMAT, 
                    level=LOG_LEVEL)

    factory = Factory(verbose=verbose,
                    outdir=outdir)
    
    converter = factory.create(source_type)
    
    converter.run(protocols_json_file, 
                protocols_schema_mapping_file,
                outfile)



if __name__ == "__main__":
    main()