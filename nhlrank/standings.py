#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  1 13:23:14 2024

@author: shane
"""
from tabulate import tabulate

from nhlrank import constants
from nhlrank.models import Team
from nhlrank.utils import print_subtitle, print_title


def standings(
    teams: list[Team],
) -> None:
    """Prints the standings"""

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Create the table
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    table_series_standings = [
        (
            i + 1,
            team.name,
            team.games_played,
            team.wins,
            team.losses,
            team.losses_ot,
            team.points,
            team.points_percentage,
            team.rating_str.split()[0],
            team.avg_opp or str(),
            team.rating_max or str(),
            team.rating_avg or str(),
            team.best_win or str(),
            team.goals_for,
            team.goals_against,
            "-".join(str(x) for x in team.record_home),
            "-".join(str(x) for x in team.record_away),
            "-".join(str(x) for x in team.shootout),
            "-".join(str(x) for x in team.last_10),
            team.streak,
        )
        for i, team in enumerate(teams)
    ]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Print the rankings table
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    _table = tabulate(
        table_series_standings,
        headers=[
            "#",
            "Team",
            "GP",
            "W",
            "L",
            "OTL",
            "Pts",
            "P%",
            "Rate",
            "Opp",
            "Top",
            "Avg",
            "Best W",
            "GF",
            "GA",
            "Home",
            "Away",
            "S/O",
            "L10",
            "Run",
        ],
    )
    print(_table)


def standings_by_div(
    teams: list[Team],
) -> None:
    """Prints the standings by division"""

    for conf, divs in constants.conference_and_division_organization.items():
        print_title(conf)
        for div, team_abbrev_div in divs.items():
            print_subtitle(div)
            # Take the top 3 teams from each division
            div_teams = [team for team in teams if team.abbrev in team_abbrev_div][:3]
            print([x.abbrev for x in div_teams])
            # standings(div_teams)
        print_subtitle("Wildcard")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Create the table
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    table_series_standings = [
        (
            i + 1,
            team.name,
            team.games_played,
            team.wins,
            team.losses,
            team.losses_ot,
            team.points,
            team.points_percentage,
            team.rating_str.split()[0],
            team.avg_opp or str(),
            team.rating_max or str(),
            team.rating_avg or str(),
            team.best_win or str(),
            team.goals_for,
            team.goals_against,
            "-".join(str(x) for x in team.record_home),
            "-".join(str(x) for x in team.record_away),
            "-".join(str(x) for x in team.shootout),
            "-".join(str(x) for x in team.last_10),
            team.streak,
        )
        for i, team in enumerate(teams)
    ]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Print the rankings table
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    _table = tabulate(
        table_series_standings,
        headers=[
            "#",
            "Team",
            "GP",
            "W",
            "L",
            "OTL",
            "Pts",
            "P%",
            "Rate",
            "Opp",
            "Top",
            "Avg",
            "Best W",
            "GF",
            "GA",
            "Home",
            "Away",
            "S/O",
            "L10",
            "Run",
        ],
    )
    print(_table)
