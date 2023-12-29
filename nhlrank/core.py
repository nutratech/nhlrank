# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:37:46 2023

@author: shane
"""
import csv
from datetime import date

import asciichartpy
from tabulate import tabulate

from nhlrank import CLI_CONFIG, CSV_GAMES_FILE_PATH
from nhlrank.glicko2 import glicko2
from nhlrank.models import Game, Team
from nhlrank.utils import get_or_create_team_by_name, print_subtitle, print_title


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
            date_at=date.fromisoformat(row[0]),
            time_at=row[1],
            team_away=row[3],
            team_home=row[5],
            score_away=int(row[4]) if row[4] else 0,
            score_home=int(row[6]) if row[6] else 0,
            outcome=row[7],
        )
        for row in rows
    ]

    # TODO: Validate games
    # for game in games:

    # Build teams
    teams: dict[str, Team] = {}
    for game in games:
        # Create team if it doesn't exist
        # NOTE: 117
        if game.team_home not in teams:
            teams[game.team_home] = Team(game.team_home)
        if game.team_away not in teams:
            teams[game.team_away] = Team(game.team_away)

        # Update players stats and ratings
        update_team_ratings(teams, game)

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
            if game.is_completed
        ]
        n_games_completed = len([x for x in games if x.is_completed])
        print(tabulate(games_table, headers=["away", "pts", "home", "pts"]))
        print()
        print(f"Total number of games played: {n_games_completed} out of {len(games)}")

    return games, teams


def update_team_ratings(teams: dict[str, Team], game: Game) -> None:
    """Update two teams' stats, based on a game outcome"""

    def rate_game(team_winner: Team, team_loser: Team) -> None:
        """
        Helper method for updating two teams' Glicko ratings, based on a game outcome
        """
        # Update wins, losses, OT losses; Goals for, against; Other basic standings
        team_winner.add_game(game)
        team_loser.add_game(game)

        if CLI_CONFIG.debug:
            print(
                f"{team_winner.name} ({team_winner.rating_str})"
                f" vs {team_loser.name} ({team_loser.rating_str}) — [{game.outcome}]"
            )

        # Update ratings
        # TODO: separate ratings_home from ratings_away, and from ratings (all)
        _new_rating_team_winner, _new_rating_team_loser = glicko.rate_1vs1(
            team_winner.rating,
            team_loser.rating,
            overtime=game.outcome in game.OT_OUTCOMES,
        )

        if CLI_CONFIG.debug:
            # Show the rating changes
            print(
                f"{team_winner.name} {round(team_winner.rating.mu)} ->"
                f" {round(_new_rating_team_winner.mu)}"
                f" vs {team_loser.name} {round(team_loser.rating.mu)} ->"
                f" {round(_new_rating_team_loser.mu)} ({game.outcome})"
            )

        # Add to list
        team_winner.ratings.append(_new_rating_team_winner)
        team_loser.ratings.append(_new_rating_team_loser)
        # TODO: take average of before and after opponent ratings?  Group by W/L/OTL?
        team_winner.opponent_ratings.append(team_loser.rating)
        team_loser.opponent_ratings.append(team_winner.rating)

    # Create the rating engine
    glicko = glicko2.Glicko2()

    # Get teams, or create them if they don't exist
    # TODO: is this already done in the process_csv() function?  Where should this be?
    #  see "NOTE: 117" above
    team_away = get_or_create_team_by_name(teams, game.team_away)
    team_home = get_or_create_team_by_name(teams, game.team_home)

    # Run the nested helper method
    if game.is_completed:
        if game.score_away > game.score_home:
            rate_game(team_winner=team_away, team_loser=team_home)
        else:
            rate_game(team_winner=team_home, team_loser=team_away)


def func_standings(
    games: list[Game],
    teams: dict[str, Team],
    col_sort_by: str = str(),
) -> None:
    """
    Rank function used by rank sub-parser.
    TODO: simulate rest of season games?
          support ratings
          nfl data too?
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Either sort by default, or by a given column
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if not col_sort_by:
        target_list = sorted(
            teams.values(),
            key=lambda x: (
                x.points,
                # https://www.espn.com/nhl/news/story?page=nhl/tiebreakers
                -x.games_played,
                x.wins,
                # TODO: need to add points earned in mutual games here, for tiebreak
                x.goals_for - x.goals_against,
            ),
            reverse=True,
        )
    else:
        target_list = sorted(
            teams.values(),
            key=lambda x: getattr(x, col_sort_by),
            reverse=True,
        )

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
            team.avg_opp,
            team.goals_for,
            team.goals_against,
            "-".join(str(x) for x in team.record_home),
            "-".join(str(x) for x in team.record_away),
            "-".join(str(x) for x in team.shootout),
            "-".join(str(x) for x in team.last_10),
            team.streak,
        )
        for i, team in enumerate(target_list)
    ]

    # Other stats
    n_games_completed = len([x for x in games if x.is_completed])
    season_completion = n_games_completed / len(games)

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
            "AvgOpp",
            "GF",
            "GA",
            "Home",
            "Away",
            "S/O",
            "L10",
            "Strk",
        ],
        tablefmt="simple_grid",
    )
    print_title(
        f"Standings — {n_games_completed} games"
        f" (~{round(season_completion * 100, 1)}% done or"
        f" {round(82 * season_completion, 1)} GP)"
    )
    if col_sort_by:
        print(f"Sorted by: {col_sort_by}")
    print(_table)


def func_team_details(
    # FIXME: support abbreviation reference by team name; link with player rosters, etc
    team_name: str,
    games: list[Game],
    teams: dict[str, Team],
) -> None:
    """
    Team details function used by rank sub-parser.
    Prints off stats and recent trends for a given team.
    """

    print_subtitle(team_name)

    team = teams[team_name]
    print(f"Games played: {team.games_played}")
    print(f"Rating: {team.rating_str}")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Rating trend
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print_subtitle("Rating trend (past 20 games)")
    if CLI_CONFIG.debug:
        print(f"Ratings: {[round(x.mu) for x in team.ratings]}")
    _graph = asciichartpy.plot(
        [round(x.mu) for x in team.ratings[-20:]],
        {
            "height": 12 if not CLI_CONFIG.debug else 20,
            # "format": lambda x, y: f"{round(x)}",
        },
    )
    print(_graph)

    # FIXME: print out the last 10 games, with the opponent, score, and outcome

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Next 10 games, opponent, and odds
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print_subtitle("Next 10 games")
    games_next_10 = [
        game
        for game in games
        if not game.is_completed and team_name in {game.team_away, game.team_home}
    ][:10]

    # Build table
    _table = tabulate(
        [
            (
                teams[game.opponent(team_name)],
                teams[game.opponent(team_name)].rating_str.split()[0],
                game.time,
                game.date,
                team.odds(teams[game.opponent(team_name)]),
                team.expected_outcome_str(team.odds(teams[game.opponent(team_name)])),
            )
            for game in games_next_10
        ],
        headers=["Opponent", "Rate", "Time", "Date", "Odds", "Win"],
        tablefmt="simple_grid",
    )
    print(_table)


# def func_upcoming_games(
#     games: list[Game],
#     teams: dict[str, Team],
# ) -> None:
#     """
#     Upcoming games function used by rank upcoming-parser.
#     Prints off odds of each team winning, as well as past recent games.
#     """
