# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:37:46 2023

@author: shane
"""
import csv

from tabulate import tabulate

from nhlrank import CLI_CONFIG, CSV_GAMES_FILE_PATH
from nhlrank.glicko2 import glicko2
from nhlrank.models import Game, Team
from nhlrank.utils import get_or_create_team_by_name, print_title


def update_team_ratings(teams: dict[str, Team], game: Game) -> None:
    """Update two teams' stats, based on a game outcome"""

    def do_game(score_away: float, score_home: float) -> None:
        """
        NOTE: player1 is winner by default, unless drawn (then it doesn't matter)
        """

        # # Add opponent ratings
        # if drawn:
        #     team_away.opponent_ratings["draws"].append(team_home.rating)
        #     team_home.opponent_ratings["draws"].append(team_away.rating)
        # else:
        #     team_away.opponent_ratings["wins"].append(team_home.rating)
        #     team_home.opponent_ratings["losses"].append(team_away.rating)

        # Update wins, losses, OT losses; Goals for, against; Other basic standings
        team_away.add_game(game)
        team_home.add_game(game)

        # # Update ratings
        # _new_rating_team_away, _new_rating_team_home = glicko.rate_1vs1(
        #     team_away.rating, team_home.rating, score_away, score_home
        # )
        # team_away.ratings.append(_new_rating_team_away)
        # team_home.ratings.append(_new_rating_team_home)

    # # Create the rating engine
    # glicko = glicko2.Glicko2()

    # Get teams, or create them if they don't exist
    team_away = get_or_create_team_by_name(teams, game.team_away)
    team_home = get_or_create_team_by_name(teams, game.team_home)

    # Run the nested helper method
    do_game(score_away=game.score[0], score_home=game.score[1])


def process_csv() -> tuple[list[Game], dict[str, Team]]:
    """
    Main function for reading the CSV data into the NHLRank program
    https://shanemcd.org/2023/08/23/2023-24-nhl-schedule-and-results-in-excel-xlsx-and-csv-formats/
    """

    with open(CSV_GAMES_FILE_PATH, "r", encoding="utf-8") as _file:
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
        if row[4]
    ]

    # TODO: Validate games
    # for game in games:

    # Build teams
    teams: dict[str, Team] = {}
    for game in games:
        # Create team if it doesn't exist
        if game.team_home not in teams:
            teams[game.team_home] = Team(game.team_home)
        if game.team_away not in teams:
            teams[game.team_away] = Team(game.team_away)

        # Update players stats and ratings
        update_team_ratings(teams, game)

    # # Sort teams by ratings
    # sorted_teams = sorted(
    #     teams.values(), key=lambda x: float(x.ratings[-1].mu), reverse=True
    # )
    # teams = {t.name: t for t in sorted_teams}

    # Check n_teams is 32
    if len(teams) != 32:
        for team in sorted(teams.keys()):
            print(team)
        raise ValueError(f"Do we still expect 32 teams?  We got: {len(teams)}.")

    # Show games (DEBUG)
    if CLI_CONFIG.debug:
        games_table = [
            (game.team_away, game.score[0], game.team_home, game.score[1])
            for game in games
        ]
        print(tabulate(games_table, headers=["away", "pts", "home", "pts"]))
        print()
        print(f"Total number of games played: {len(games)}")

    return games, teams


def func_upcoming_games(
    games: list[Game],
    teams: dict[str, Team],
) -> None:
    """
    Upcoming games function used by rank upcoming-parser.
    Prints off odds of each team winning, as well as past recent games.
    """


def func_standings(
    games: list[Game],
    teams: dict[str, Team],
    extended_titles: bool = False,
) -> None:
    """
    Rank function used by rank sub-parser.
    TODO: print standings/ratings for games (and simulated rest of season games)
          nfl data too?
    """

    table_series_standings = [
        (
            i + 1,
            team.name,
            team.wins,
            team.losses,
            team.losses_ot,
            team.points,
            team.points_percentage,
            team.goals_for,
            team.goals_against,
            team.record_home,
            team.record_away,
            team.shootout,
            team.last_10,
            team.streak,
        )
        for i, team in enumerate(
            sorted(teams.values(), key=lambda x: x.points, reverse=True)
        )
    ]
    season_completion = round(
        len([x for x in games if x.outcome.upper() != x.OUTCOME_SCHEDULED])
        / len(games),
        1,
    )

    # Print the rankings table
    _table = tabulate(
        table_series_standings,
        headers=[
            "Rank",
            "Team",
            "W",
            "L",
            "OTL",
            "Pts",
            "P%",
            "GF",
            "GA",
            "Home",
            "Away",
            "S/O",
            "Last 10",
            "Streak",
        ],
    )
    print_title(
        f"Standings ({len(games)} games,"
        f" {len(teams)} teams,"
        f" {season_completion}% complete"
    )
    print(_table)
