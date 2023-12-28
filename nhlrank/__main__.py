#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 23:10:36 2023

@author: shane
"""

import csv

import argcomplete
from tabulate import tabulate

from nhlrank import PROJECT_ROOT
from nhlrank.models import Game, Team


def main() -> int:
    """
    Main function for running the NHLRank program
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
