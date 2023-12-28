# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:26:27 2023

@author: shane
"""
from argparse import ArgumentParser

from nhlrank.argparser.funcs import parser_func_download, parser_func_standings


def build_subcommands(arg_parser: ArgumentParser) -> None:
    """Build the arg parser sub commands"""

    # subparsers
    subparsers = arg_parser.add_subparsers(title="actions")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Download sub-parser
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # subparser_download = subparsers.add_parser(
    #     "fetch", help="Download the latest Sheet from Google"
    # )
    # subparser_download.set_defaults(func=parser_func_download)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Rank sub-parser
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    subparser_rank = subparsers.add_parser(
        "stand", help="Process CSV, output standings"
    )
    subparser_rank.add_argument(
        "-s",
        dest="skip_dl",
        action="store_true",
        help="skip sheet download, use cached",
    )
    subparser_rank.add_argument(
        "-t", "--team", action="store_true", help="show details for a team"
    )

    subparser_rank.set_defaults(func=parser_func_standings)
