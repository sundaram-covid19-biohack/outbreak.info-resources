import os
import sys
import click
import pathlib
import logging
import calendar
import time
import pathlib
import yaml
from colorama import Fore, Style
from datetime import datetime
from datetime import date

DEFAULT_VERBOSE = False

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

g_verbose = False


def derive_terms_and_comments(infile: str = None, outfile: str = None) -> None:
    """Parse the input YAML file and derive the terms and corresponding comments.
    Write the tuples to the output file.
    :param infile: {str}
    :param outfile: {str}
    """

    id_ctr = 0
    comment_ctr = 0
    missing_id_ctr = 0
    missing_comment_ctr = 0
    null_comment_ctr = 0
    terms_and_comments_list = []

    logging.info("Abou to parse '{}'".format(infile))

    with open(infile) as file:

        documents = yaml.full_load(file)

        for item, doc in documents.items():
            if item == '@graph':
                logging.info("Found '@graph' section")

                graph_list = doc

                for graph_dict in graph_list:
                    term_name = None
                    comment = None
                    if '@id' in graph_dict:
                        term_name = graph_dict['@id']
                        id_ctr += 1
                        if 'rdfs:comment' in graph_dict:
                            comment = graph_dict['rdfs:comment']
                            if comment is None or comment == '':
                                comment = 'N/A'
                                logging.info("Found term '{}' with null comment so assigned '{}'".format(term_name, comment))
                                null_comment_ctr += 1
                            else:
                                logging.info("Found term '{}' with comment '{}'".format(term_name, comment))
                            comment_ctr += 1
                        else:
                            logging.info("Did not find comment for term '{}'".format(term_name))
                            missing_comment_ctr += 1
                    else:
                        logging.error("Did not find id!")
                        missing_id_ctr += 1

                    terms_and_comments_list.append([term_name, comment])

    logging.info("Found '{}' ids".format(id_ctr))
    logging.info("Found '{}' comments".format(comment_ctr))

    if missing_id_ctr > 0:
        print("Encountered '{}' missing ids".format(missing_id_ctr))

    if missing_comment_ctr > 0:
        print("Encountered '{}' missing comments".format(missing_comment_ctr))

    if null_comment_ctr > 0:
        print("Encountered '{}' comments with null values".format(null_comment_ctr))

    with open(outfile, 'w') as fh:
        for term_and_comment in terms_and_comments_list:
            fh.write(term_and_comment[0] + "\t" + term_and_comment[1] + "\n")

    logging.info("Wrote '{}'".format(outfile))
    print("Wrote '{}'".format(outfile))


@click.command()
@click.option('--outdir', help='The output directory - default is {}'.format(DEFAULT_OUTDIR))
@click.option('--outfile', help='The output file - if not specified a default will be assigned')
@click.option('--infile', help="The YAML file to derive terms and comemnts from")
@click.option('--logfile', help="The log file - if not is specified a default will be assigned")
@click.option('--verbose', is_flag=True, help="Whether to execute in verbose mode - default is {}".format(DEFAULT_VERBOSE))
def main(outdir, outfile, infile, logfile, verbose):
    """Parse the YAML file and derive the terms and corresponding comments.
    """

    error_ctr = 0
    if infile is None:
        print(Fore.RED + "--infile was not specified")
        print(Style.RESET_ALL + '', end='')
        error_ctr += 1

    if error_ctr > 0:
        print(Fore.RED + "Required command-line arguments were not specified")
        print(Style.RESET_ALL + '', end='')
        sys.exit(1)
        
    assert isinstance(infile, str)

    if not os.path.exists(infile):
        print(Fore.RED + "'{}' does not exist".format(infile))
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

    derive_terms_and_comments(infile, outfile)


if __name__ == "__main__":
    main()