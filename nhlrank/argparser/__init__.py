# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:26:27 2023

@author: shane
"""
from argparse import ArgumentParser

from nhlrank.argparser.funcs import parser_func_download, parser_func_standings


def build_subcommands(arg_parser: ArgumentParser) -> None:
    """Build the arg parser sub commands"""

    subparsers = arg_parser.add_subparsers(title="actions")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Download sub-parser
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    subparser_download = subparsers.add_parser(
        "fetch", help="Download the latest CSV for NHL games"
    )
    subparser_download.set_defaults(func=parser_func_download)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Standings sub-parser
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    subparser_standings = subparsers.add_parser(
        "stand", help="Process CSV, output standings"
    )
    subparser_standings.add_argument(
        "-c",
        dest="skip_dl",
        action="store_true",
        help="skip fetching CSV download; use cached copy",
    )
    subparser_standings.add_argument(
        "-t", dest="team", type=str, help="show details for a team"
    )
    subparser_standings.add_argument(
        "-s",
        dest="sort_column",
        metavar="COLUMN",
        type=str,
        help="sort by specific column",
    )

    subparser_standings.set_defaults(func=parser_func_standings)
