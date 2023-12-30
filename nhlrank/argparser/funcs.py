# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:26:28 2023

@author: shane
"""
import argparse
from typing import Any

from nhlrank.core import func_standings, func_team_details, process_csv
from nhlrank.models import Game, Team
from nhlrank.sheetutils import cache_csv_games_file, get_google_sheet
from nhlrank.utils import print_title


def parser_func_download(
    **kwargs: dict[str, Any]  # pylint: disable=unused-argument
) -> tuple[int, None]:
    """Default function for download parser"""
    cache_csv_games_file(
        _csv_bytes_output=get_google_sheet(),
    )
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
        func_team_details(team_name=args.team, games=games, teams=teams)
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
