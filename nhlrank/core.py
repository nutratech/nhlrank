# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:37:46 2023

@author: shane
"""
import csv
from datetime import date

import asciichartpy
from tabulate import tabulate

from nhlrank import CLI_CONFIG, CSV_GAMES_FILE_PATH, constants, standings
from nhlrank.glicko2 import glicko2
from nhlrank.models import Game, Team
from nhlrank.models.helpers import expected_outcome_str, game_odds, mutual_record
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

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Update ratings
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # TODO: add support for different OTL models, e.g. geometric, inflationary
        # TODO: add support for different OTL factors, e.g. 0.5, 0.4, 0.3
        # TODO: weight overtime wins lower for teams in conference, or division
        _new_rating_team_winner, _new_rating_team_loser = glicko.rate_1vs1(
            team_winner.rating,
            team_loser.rating,
            overtime=game.outcome in game.OT_OUTCOMES,
        )
        if game.team_home == team_winner.name:
            _new_rating_team_home, _new_rating_team_away = glicko.rate_1vs1(
                team_winner.rating_home,
                team_loser.rating_away,
                overtime=game.outcome in game.OT_OUTCOMES,
            )
        else:
            _new_rating_team_away, _new_rating_team_home = glicko.rate_1vs1(
                team_winner.rating_away,
                team_loser.rating_home,
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

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Add new ratings to lists
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # TODO: take average of before and after opponent ratings?  Group by W/L/OTL?
        team_winner.opponent_ratings.append(team_loser.rating)
        team_winner.opponent_ratings_by_outcome["W"].append(team_loser.rating)
        team_loser.opponent_ratings.append(team_winner.rating)
        if game.outcome in game.OT_OUTCOMES:
            team_loser.opponent_ratings_by_outcome["OTL"].append(team_winner.rating)
        else:
            team_loser.opponent_ratings_by_outcome["L"].append(team_winner.rating)
        # ~~~~~~~~~~~~
        # Main ratings
        # ~~~~~~~~~~~~
        team_winner.ratings.append(_new_rating_team_winner)
        team_loser.ratings.append(_new_rating_team_loser)
        # Home/away ratings
        if game.team_home == team_winner.name:
            team_winner.ratings_home.append(_new_rating_team_home)
            team_loser.ratings_away.append(_new_rating_team_away)
        else:
            team_winner.ratings_away.append(_new_rating_team_away)
            team_loser.ratings_home.append(_new_rating_team_home)

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


def func_teams_list(
    teams: dict[str, Team],
    abbrev: bool = False,
    abbrev_only: bool = False,
    group_teams_by: str = str(),
) -> None:
    """
    List function used by teams sub-parser.
    Prints all teams and their abbreviations.
    """

    def team_or_abbrev(_team: Team) -> str:
        """Returns team name or abbreviation"""
        if abbrev_only:
            return _team.abbrev
        if abbrev:
            return f"{_team.abbrev}|{_team}"
        return _team.name

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Handle all three cases (league, conference, division)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if group_teams_by == "conf":
        for conf, divs in constants.conference_and_division_organization.items():
            print_subtitle(f"{conf} Conference")
            _teams = [
                teams[" ".join(constants.team_abbreviations_to_full_names[team_abbrev])]
                for div in divs.values()
                for team_abbrev in div
            ]
            for _team in sorted(_teams, key=lambda x: x.name):
                print(f"  {team_or_abbrev(_team)}")

    elif group_teams_by == "div":
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
                    print(f"  {team_or_abbrev(team)}")

    else:
        # Entire league (default, no grouping)
        for _, team in sorted(teams.items()):
            print(team_or_abbrev(team))


def func_standings(
    games: list[Game],
    teams: dict[str, Team],
    col_sort_by: str = str(),
    group_standings_by: str = str(),
) -> None:
    """
    Rank function used by rank sub-parser.
    """

    # Basic stats
    n_games_completed = len([x for x in games if x.is_completed])
    season_completion = n_games_completed / len(games)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Either sort by default, or by a given column
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if not col_sort_by:
        # NHL default sorting (playoff contenders)
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
        # Sort by custom column
        target_list = sorted(
            teams.values(),
            key=lambda x: getattr(x, col_sort_by),
            reverse=True,
        )

    print_title(
        f"Standings — {n_games_completed} games"
        f" (~{round(season_completion * 100, 1)}% done or"
        f" {round(82 * season_completion, 1)} GP)"
    )
    if col_sort_by:
        print(f"Sorted by: {col_sort_by}")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Group by division (if requested)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if group_standings_by == "wildcard":
        standings.standings_by_wildcard(teams=target_list)
    elif group_standings_by == "div":
        standings.standings_by_division(teams=target_list)
    elif group_standings_by == "conf":
        standings.standings_by_conference(teams=target_list)
    else:
        # Group by entire league by default
        standings.standings_all(teams=target_list)


def func_team_details(
    # FIXME: support abbreviation reference by team name; link with player rosters, etc
    team_name: str,
    games: list[Game],
    teams: dict[str, Team],
    num_games_last: int = 20,
    num_games_next: int = 10,
) -> None:
    """
    Team details function used by rank sub-parser.
    Prints off stats and recent trends for a given team.
    """

    # Get team name if abbreviation is passed
    team_name = (
        team_name
        if team_name in teams
        else " ".join(constants.team_abbreviations_to_full_names[team_name])
    )

    # Print basic stats
    print_subtitle(team_name)
    team = teams[team_name]
    print(f"Games played: {team.games_played}", end="   ")
    print(
        f"Avg opp: {round(team.avg_opp)}"
        "    ("
        f"W: {team.avg_opp_by_outcome('W')}"
        f", L: {team.avg_opp_by_outcome('L')}"
        f", OTL: {team.avg_opp_by_outcome('OTL')}"
        ")"
    )
    # TODO: include avg_opp for home vs. away (separately)
    print(f"Rating: {team.rating_str}", end="   ")
    print(
        f"(home: {team.rating_home_str.split()[0]}"
        f", away: {team.rating_away_str.split()[0]})"
    )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Simulate rest of season (for this team)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    games_remaining = [
        game
        for game in games
        if not game.is_completed and team_name in {game.team_away, game.team_home}
    ]
    wins = team.wins + 0.5 * team.losses_ot
    for game in games_remaining:
        wins += game_odds(team, teams[game.opponent(team_name)])
    print(f"Projection: {round(wins)}-{round(82 - wins)} ({round(wins * 2, 1)} pts)")

    # TODO: find prob of making playoffs using binomial distribution or expected wins

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Rating trend (past {num_games_last} games)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # TODO: separate arguments for --next and --last (or --past), not 2 * num_games
    print_subtitle(f"Rating trend (past {num_games_last} games)")
    if CLI_CONFIG.debug:
        print(f"Ratings: {[round(x.mu) for x in team.ratings]}")
    _graph = asciichartpy.plot(
        [round(x.mu) for x in team.ratings[-num_games_last:]],
        {"height": 12 if not CLI_CONFIG.debug else 20},
    )
    print(_graph)

    # FIXME: print out the last 10 games, with the opponent, score, and outcome

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Next {num_games_next} games, opponent, and odds
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print_subtitle(f"Next {num_games_next} games")

    # Show average opponent strength, and sum of expected scores
    avg_opp_next_n = sum(
        teams[game.opponent(team_name)].rating.mu
        for game in games_remaining[:num_games_next]
    ) / len(games_remaining[:num_games_next])
    expected_score_next_n = sum(
        game_odds(team, teams[game.opponent(team_name)])
        for game in games_remaining[:num_games_next]
    )
    print(f"Average opponent: {round(avg_opp_next_n)}", end="     ")
    print(
        f"E= {round(expected_score_next_n, 2)}"
        f"-{round(len(games_remaining[:num_games_next]) - expected_score_next_n, 2)}"
        "  (W-L)"
    )
    print()

    # Build table (for next {num_games_next} games)
    _table = tabulate(
        [
            (
                game.time,
                game.date,
                teams[game.opponent(team_name)],
                teams[game.opponent(team_name)].rating_str.split()[0],
                "Home" if game.team_home == team_name else str(),
                "-".join(
                    str(x)
                    for x in mutual_record(
                        team_name, teams[game.opponent(team_name)].name, games
                    )
                ),
                game_odds(team, teams[game.opponent(team_name)]),
                expected_outcome_str(game_odds(team, teams[game.opponent(team_name)])),
            )
            for game in games_remaining[:num_games_next]
        ],
        headers=[
            "Time ET",
            "Date",
            "Opponent",
            "Rate",
            "Arena",
            "W/L/OTL",
            "Odds",
            "Win",
        ],
    )
    print(_table)
