# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:26:27 2023

@author: shane
"""
from argparse import ArgumentParser

from nhlrank.argparser.funcs import (
    parser_func_download,
    parser_func_standings,
    parser_func_teams,
)
from nhlrank.models import Team


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
    # Teams sub-parser
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    subparser_teams = subparsers.add_parser(
        "teams", help="List all teams and their abbreviations"
    )
    subparser_teams.set_defaults(func=parser_func_teams)
    subparser_teams.add_argument(
        "--abbrev",
        dest="abbrev",
        action="store_true",
        help="show abbreviations with full names",
    )
    subparser_teams.add_argument(
        "--abbrev-only",
        dest="abbrev_only",
        action="store_true",
        help="show only abbreviations",
    )
    subparser_teams.add_argument(
        "--conf",
        dest="conferences",
        action="store_true",
        help="show standings by conference",
    )
    subparser_teams.add_argument(
        "--div",
        dest="divisions",
        action="store_true",
        help="show standings by division",
    )

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
        type=str,
        help="sort by specific column",
        choices=[
            x
            for x in vars(Team) | vars(Team("Dallas Stars"))
            if not x.startswith("_")
            and x
            not in {
                "add_game",
                "name",
                "rating_str",
                "ratings",
                "opponent_ratings",
                "last_10_str_list",
            }
        ],
    )
    subparser_standings.add_argument(
        "--last",
        dest="num_games_last",
        metavar="NUM",
        type=int,
        help="number of previous games to show rating trend for",
        choices=range(1, 82 + 1),
    )
    subparser_standings.add_argument(
        "--next",
        dest="num_games_next",
        metavar="NUM",
        type=int,
        help="number of games to show predictions for",
        choices=range(1, 82 + 1),
    )
    # FIXME: implement this in the core functions
    subparser_standings.add_argument(
        "--otl-model",
        dest="otl_model",
        help="choose how overtime losses affect ratings, default: geometric",
        choices=("tie", "geometric", "inflationary"),
    )
    subparser_standings.add_argument(
        "--otl-factor",
        dest="otl_factor",
        help="choose how much overtime losses affect ratings, default: 0.5",
        type=float,
    )
    subparser_standings.add_argument(
        "--conf",
        dest="conferences",
        action="store_true",
        help="show standings by conference",
    )
    subparser_standings.add_argument(
        "--div",
        dest="divisions",
        action="store_true",
        help="show standings by division",
    )

    subparser_standings.set_defaults(func=parser_func_standings)
