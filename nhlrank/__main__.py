#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""
Created on Tue Dec 26 23:10:36 2023

@author: shane
"""

import argparse
import csv
import time

import argcomplete
import requests
from tabulate import tabulate

from nhlrank import CLI_CONFIG, PROJECT_ROOT, __email__, __title__, __url__, __version__
from nhlrank.argparser import build_subcommands
from nhlrank.models import Game, Team


def build_arg_parser() -> argparse.ArgumentParser:
    """Adds all subparsers and parsing logic"""

    arg_parser = argparse.ArgumentParser(prog=__title__)
    arg_parser.add_argument(
        "-v",
        action="version",
        version=f"{__title__} version {__version__}",
    )

    arg_parser.add_argument(
        "-d", dest="debug", action="store_true", help="enable verbose logging (debug)"
    )

    # Subparsers
    build_subcommands(arg_parser)

    return arg_parser


def main(args: list[str] | None = None) -> int:
    """
    Main method for CLI

    @param args: List[str]
    """

    start_time = time.time()
    arg_parser = build_arg_parser()
    argcomplete.autocomplete(arg_parser)

    def parse_args() -> argparse.Namespace:
        """Returns parsed args"""
        if args is None:
            return arg_parser.parse_args()
        return arg_parser.parse_args(args=args)

    def func(parser: argparse.Namespace) -> Tuple[int, Any]:
        """Executes a function for a given argument call to the parser"""
        if hasattr(parser, "func"):
            # Print help for nested commands
            if parser.func.__name__ == "print_help":
                return 0, parser.func()  # pragma: no cover

            # Collect non-default args
            args_dict = dict(vars(parser))
            for expected_arg in ["func", "debug"]:
                args_dict.pop(expected_arg)

            # Run function
            if args_dict:
                # Make sure the parser.func() always returns: Tuple[Int, Any]
                return parser.func(args=parser)  # type: ignore
            return parser.func()  # type: ignore

        # Otherwise print help
        arg_parser.print_help()
        return 0, None

    # Build the parser, set flags
    _parser = parse_args()
    CLI_CONFIG.set_flags(_parser)

    # Try to run the function
    exit_code = 1
    conn_errs = (requests.exceptions.ConnectionError, requests.ReadTimeout, URLError)

    try:
        exit_code, *_results = func(_parser)
    except requests.exceptions.HTTPError as http_error:
        err_msg = f"{http_error.response.status_code}: {repr(http_error)}"
        print("Server response error, try again: " + err_msg)
        if CLI_CONFIG.debug:
            raise
    except conn_errs as conn_url_error:  # pragma: no cover
        print("Connection error, check your internet: " + repr(conn_url_error))
        if CLI_CONFIG.debug:
            raise
    except Exception as exception:  # pragma: no cover  # pylint: disable=broad-except
        print("Unforeseen error, run with -d for more info: " + repr(exception))
        print(f"You can open an issue here: {__url__}")
        print(f"Or send me an email with the debug output: {__email__}")
        if CLI_CONFIG.debug:
            raise
    finally:
        if CLI_CONFIG.debug:
            exc_time = time.time() - start_time
            print(f"\nExecuted in: {round(exc_time * 1000, 1)} ms")
            print(f"Exit code: {exit_code}")

    return exit_code


def read() -> int:
    """
    Main function for reading the CSV data into the NHLRank program
    https://shanemcd.org/2023/08/23/2023-24-nhl-schedule-and-results-in-excel-xlsx-and-csv-formats/
    """

    with open(
        f"{PROJECT_ROOT}/data/nhl-202324-asplayed.csv", "r", encoding="utf-8"
    ) as _file:
        reader = csv.reader(_file)
        rows = list(reader)
        _ = rows.pop(0)  # remove headers

    games = [
        Game(
            row[3],  # team_away
            row[5],  # team_home
            int(row[4]),  # score_away
            int(row[6]),  # score_home
            row[7],  # outcome (status)
        )
        for row in rows
        if row[6]
    ]

    # TODO: Check all completed games are accurately completed
    # for game in games:

    # Build teams
    teams = {}
    for game in games:
        if game.team_home not in teams:
            teams[game.team_home] = Team(game.team_home)

        if game.team_away not in teams:
            teams[game.team_away] = Team(game.team_away)

    # Check n_teams is 32
    if len(teams) != 32:
        for team in sorted(teams.keys()):
            print(team)
        raise ValueError(f"Do we still expect 32 teams?  We got: {len(teams)}.")

    # Build standings and ratings
    games_table = [
        (game.team_away, game.score[0], game.team_home, game.score[1]) for game in games
    ]
    print(tabulate(games_table, headers=["away", "pts", "home", "pts"]))
    print()
    print(f"Total number of games played: {len(games)}")

    for game in games:
        pass

    # TODO: print standings for games (and simulated rest of season games)
    # nfl data too

    return 0
