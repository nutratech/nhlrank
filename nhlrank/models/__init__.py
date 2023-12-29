#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 12:08:40 2023

@author: shane
"""
from tabulate import tabulate

from nhlrank.glicko2 import glicko2


class Game:
    """Game class for storing game information"""

    OT_OUTCOMES = {"OT", "SO"}
    SO_OUTCOME = "SO"
    OUTCOME_NOT_PLAYED = "SCHEDULED"

    def __init__(
        self,
        team_away: str,
        team_home: str,
        score_away: int | None,
        score_home: int | None,
        outcome: str,
    ):
        self.team_away = team_away
        self.team_home = team_home

        # aka status in the CSV sheet (e.g. Regulation, OT, SO, or Scheduled)
        self.outcome = outcome
        self.is_completed = outcome.upper() != self.OUTCOME_NOT_PLAYED

        self.score_away = score_away
        self.score_home = score_home

        # Only add stats if the game has been played
        if self.is_completed and score_away is not None and score_home is not None:
            # Score (score_away, score_home)
            if score_home > score_away:
                if outcome in self.OT_OUTCOMES:
                    # self.score = (1 / 3, 2 / 3)
                    self.score = (0.5, 1.0)
                else:
                    self.score = (0.0, 1.0)
            else:
                if outcome in self.OT_OUTCOMES:
                    # self.score = (2 / 3, 1 / 3)
                    self.score = (1.0, 0.5)
                else:
                    self.score = (1.0, 0.0)

    def __str__(self) -> str:
        return (
            f"{self.team_home} vs. {self.team_away}"
            f" {self.score_home}-{self.score_away}"
        )


class Team:
    """Team class for storing team information and ratings"""

    def __init__(self, name: str):
        self.name = name

        # self.games: dict[str, list[Game]] = {"home": [], "away": []}
        self.games_played = 0
        self.points = 0

        self.wins = 0
        self.losses = 0
        self.losses_ot = 0

        self.goals_for = 0
        self.goals_against = 0

        self.record_away = [0, 0, 0]
        self.record_home = [0, 0, 0]
        self.shootout = [0, 0]

        self.last_10_str_list: list[str] = []
        self.streak = str()  # e.g. W2, L1, OTL3

        # Glicko 2 ratings
        self.ratings = {"home": [glicko2.Rating()], "away": [glicko2.Rating()]}

    @property
    def points_percentage(self) -> float:
        """Points percentage"""
        return round(self.points / (self.games_played * 2), 3)

    @property
    def last_10(self) -> tuple[int, int, int]:
        """Last 10 games"""
        return (
            self.last_10_str_list.count("W"),
            self.last_10_str_list.count("L"),
            self.last_10_str_list.count("OTL"),
        )

    def add_game(self, game: Game) -> None:
        """Add a game, together with the basic standings information"""

        self.games_played += 1

        is_at_home = game.team_home == self.name

        # Outcome (W, L, or OTL)
        if is_at_home:
            if game.score_home > game.score_away:
                outcome = "W"
            else:
                if game.outcome in Game.OT_OUTCOMES:
                    outcome = "OTL"
                else:
                    outcome = "L"
        else:
            if game.score_home < game.score_away:
                outcome = "W"
            else:
                if game.outcome in Game.OT_OUTCOMES:
                    outcome = "OTL"
                else:
                    outcome = "L"

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Wins, losses, and OT losses
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if game.score_home > game.score_away:
            if is_at_home:
                self.wins += 1
                self.record_home[0] += 1
            else:
                if game.outcome in Game.OT_OUTCOMES:
                    self.losses_ot += 1
                    self.record_away[2] += 1
                else:
                    self.losses += 1
                    self.record_away[1] += 1
        else:
            if is_at_home:
                if game.outcome in Game.OT_OUTCOMES:
                    self.losses_ot += 1
                    self.record_home[2] += 1
                else:
                    self.losses += 1
                    self.record_home[1] += 1
            else:
                self.wins += 1
                self.record_away[0] += 1

        # Shoutout [W, L]
        if game.outcome == Game.SO_OUTCOME:
            if outcome == "W":
                self.shootout[0] += 1
            else:
                self.shootout[1] += 1

        # Last 10
        if len(self.last_10_str_list) > 9:
            self.last_10_str_list.pop(0)
        self.last_10_str_list.append(outcome)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Goals for & against
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if is_at_home:
            self.goals_for += game.score_home
            self.goals_against += game.score_away
        else:
            self.goals_for += game.score_away
            self.goals_against += game.score_home

    def __str__(self) -> str:
        return self.name


class Standings:
    """Standings class for storing standings information"""

    def __init__(self, teams: dict):
        self.teams = teams

    def __str__(self) -> str:
        return tabulate(
            [
                [
                    team.name,
                    team.ratings["home"][-1].rating,
                    team.ratings["home"][-1].rd,
                    team.ratings["away"][-1].rating,
                    team.ratings["away"][-1].rd,
                ]
                for team in sorted(self.teams.values(), key=lambda x: x.name)
            ],
            headers=["Team", "Home Rating", "Home RD", "Away Rating", "Away RD"],
        )
