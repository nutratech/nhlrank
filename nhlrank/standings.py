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
    rankings: list[int] | None = None,
) -> None:
    """Prints the standings"""

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Create the table
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    table_series_standings = [
        (
            rankings[i] if rankings else i + 1,
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


def standings_by_conference(
    teams: list[Team],
) -> None:
    """Prints the standings by conference"""

    for conf, divs in constants.conference_and_division_organization.items():
        print_title(conf)

        teams_conf = [
            team
            for team in teams
            # see: https://datagy.io/python-flatten-list-of-lists/
            if team.abbrev in [t for div in divs.values() for t in div]
        ]

        standings(teams_conf)


def standings_by_division(
    teams: list[Team],
) -> None:
    """Prints the standings by division"""

    for conf, divs in constants.conference_and_division_organization.items():
        print_title(conf)

        # Print the division standings
        for div, team_abbrevs_div in divs.items():
            print_subtitle(div)
            teams_div = [team for team in teams if team.abbrev in team_abbrevs_div]

            standings(teams_div)


def standings_by_wildcard(
    teams: list[Team],
) -> None:
    """Prints the standings by wildcard"""

    for conf, divs in constants.conference_and_division_organization.items():
        print_title(conf)

        teams_conf = [
            team
            for team in teams
            # see: https://datagy.io/python-flatten-list-of-lists/
            if team.abbrev in [t for div in divs.values() for t in div]
        ]
        non_wildcard_teams = []

        # Pre-process the teams to get their rankings
        for div, team_abbrevs_div in divs.items():
            # Take the top 3 teams from each division
            teams_div = [team for team in teams if team.abbrev in team_abbrevs_div][:3]
            non_wildcard_teams.extend(teams_div)

        # Print the non-wildcard teams
        for div, team_abbrevs_div in divs.items():
            print_subtitle(div)
            teams_div = [team for team in teams if team.abbrev in team_abbrevs_div][:3]
            teams_div_rankings = [
                [x for x in teams_conf if x in non_wildcard_teams].index(_team) + 1
                for _team in teams_div
            ]

            standings(teams_div, rankings=teams_div_rankings)

        # Wildcards are the conference's top 2 remaining teams (7th and 8th place)
        print_subtitle("Wildcard")
        wildcard_teams = [team for team in teams_conf if team not in non_wildcard_teams]

        standings(wildcard_teams, rankings=list(range(7, len(wildcard_teams) + 7)))
