#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 18:45:25 2023

@author: shane
"""
from nhlrank import CLI_CONFIG, constants
from nhlrank.glicko2 import glicko2
from nhlrank.models import Game, Team


def get_team_name(team_str: str) -> str:
    """Get team name from name OR abbreviation"""
    return (
        team_str
        if team_str in constants.team_full_names_to_abbreviations
        else " ".join(constants.team_abbreviations_to_full_names[team_str])
    )


def game_odds(team: Team, opponent: Team) -> float:
    """Odds of winning against another team"""
    rating_engine = glicko2.Glicko2()

    return round(
        rating_engine.expect_score(
            rating_engine.scale_down(team.rating),
            rating_engine.scale_down(opponent.rating),
            rating_engine.reduce_impact(
                rating_engine.scale_down(opponent.rating),
            ),
        ),
        2,
    )


def expected_outcome_str(odds: float) -> str:
    """Expected outcome against another team"""
    if odds > 0.6:
        return "w"
    if odds > 0.5:
        return "+"
    if odds > 0.4:
        return "/"

    return str()


def mutual_record(team: str, opponent: str, games: list[Game]) -> tuple[int, int, int]:
    """
    Returns the mutual record between two teams, for wins, losses, and overtime losses
    """
    wins = 0
    losses = 0
    ot_losses = 0
    if CLI_CONFIG.debug:
        print(f"Calculating mutual record between {team} and {opponent}")
        print(team)
        print(opponent)

    for game in games:
        # Don't try to compare games that haven't been played yet
        if not game.is_completed:
            continue

        if game.team_home == team and game.team_away == opponent:
            if CLI_CONFIG.debug:
                print(game)
            if game.score_home > game.score_away:
                wins += 1
            elif game.score_home < game.score_away:
                if game.outcome in Game.OT_OUTCOMES:
                    ot_losses += 1
                else:
                    losses += 1
        elif game.team_home == opponent and game.team_away == team:
            if CLI_CONFIG.debug:
                print(game)
            if game.score_home > game.score_away:
                if game.outcome in Game.OT_OUTCOMES:
                    ot_losses += 1
                else:
                    losses += 1
            else:
                wins += 1

    if CLI_CONFIG.debug:
        print()
    return wins, losses, ot_losses


def playoff_contenders(teams: list[Team]) -> dict[str, dict[str, list[Team]]]:
    """Returns a list of teams that are in playoff contention"""
    return {
        "Eastern": {
            "Atlantic": teams[0:3],
            "Metro": teams[4:7],
            "Wildcard": teams[8:15],
        },
        "Western": {
            "Central": teams[16:19],
            "Pacific": teams[20:23],
            "Wildcard": teams[24:31],
        },
    }
