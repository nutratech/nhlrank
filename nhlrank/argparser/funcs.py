# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:26:28 2023

@author: shane
"""
import argparse
from typing import Any

from nhlrank import constants
from nhlrank.core import func_standings, func_team_details, process_csv
from nhlrank.models import Game, Team
from nhlrank.sheetutils import cache_csv_games_file, get_google_sheet
from nhlrank.utils import print_subtitle, print_title


def parser_func_download(
    **kwargs: dict[str, Any]  # pylint: disable=unused-argument
) -> tuple[int, None]:
    """Default function for download parser"""
    cache_csv_games_file(
        _csv_bytes_output=get_google_sheet(),
    )
    return 0, None


def parser_func_teams(
    args: argparse.Namespace,
) -> tuple[int, None]:
    """Default function for teams parser, prints all teams and their abbreviations"""

    def team_or_abbrev() -> str:
        """Returns team name or abbreviation"""
        if args.abbrev:
            return f"{team.abbrev}|{team}"
        return team.name

    _, teams = process_csv()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Handle all three cases (league, conference, division)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if args.divisions:
        for conf, divs in constants.conference_and_division_organization.items():
            print_title(f"{conf} Conference")
            for div, teams_div in divs.items():
                print_subtitle(f"{div} Division")
                for team_abbrev in teams_div:
                    # TODO: should the teams Dict in process_csv() be keyed by abbrev?
                    team_name = " ".join(
                        constants.team_abbreviations_to_full_names[team_abbrev]
                    )
                    team = teams[team_name]
                    print(team_or_abbrev())

    elif args.conference:
        for conf, divs in constants.conference_and_division_organization.items():
            print_subtitle(f"{conf} Conference")
            # TODO: sort whole conference alphabetically, not just divisions
            for teams_div in divs.values():
                for team_abbrev in teams_div:
                    # TODO: should the teams Dict in process_csv() be keyed by abbrev?
                    team_name = " ".join(
                        constants.team_abbreviations_to_full_names[team_abbrev]
                    )
                    team = teams[team_name]
                    print(team_or_abbrev())

    else:
        for _, team in sorted(teams.items()):
            print(team_or_abbrev())

    return 0, None


def parser_func_standings(
    args: argparse.Namespace,
) -> tuple[int, tuple[list[Game], dict[str, Team]]]:
    """Default function for rank parser"""

    # FIXME: make this into an annotation function? Easily, neatly re-usable &
    #          testable.
    if not args.skip_dl:  # pragma: no cover
        cache_csv_games_file(
            _csv_bytes_output=get_google_sheet(),
        )

    # Rate players, print rankings
    games, teams = process_csv()

    func_standings(
        games=games,
        teams=teams,
        col_sort_by=args.sort_column.lower() if args.sort_column else str(),
    )

    # Optionally print team details
    if args.team:
        print_title("Team details")
        func_team_details(
            team_name=args.team,
            games=games,
            teams=teams,
            num_games_last=args.num_games_last or 20,
            num_games_next=args.num_games_next or 10,
        )
        # func_up_coming_games()

    # # Optionally print match ups
    # if args.matches:
    #     func_match_ups(teams=teams)

    # Optionally print the rating progress charts
    # FIXME: This should be args.team (e.g. graph or show stats for a team)
    # if args.graph:
    #     print_title("Rating progress charts")
    #     for team in teams.values():  # pylint: disable=invalid-name
    #         print()
    #         print(team)
    #         print("Last 10:", [round(x.mu) for x in team.ratings[-10:]])
    #         team.graph_ratings()

    return 0, (games, teams)
