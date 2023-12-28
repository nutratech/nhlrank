#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 12:08:40 2023

@author: shane
"""
from nhlrank.glicko2 import glicko2


class Game:
    """Game class for storing game information"""
    OT_OUTCOMES = {"OT", "SO"}

    def __init__(
        self,
        team_away: str,
        team_home: str,
        score_away: int,
        score_home: int,
        outcome: str,
    ):
        self.team_away = team_away
        self.team_home = team_home

        self.score_away = score_away
        self.score_home = score_home

        # aka status in the CSV sheet (e.g. SCHEDULED, OT, SO, Regulation)
        self.outcome = outcome

        # Score (in terms of home team first)
        if score_home > score_away:
            if outcome in self.OT_OUTCOMES:
                score = (0.5, 1.0)
            else:
                score = (0.0, 1.0)
        else:
            if outcome in self.OT_OUTCOMES:
                score = (1.0, 0.5)
            else:
                score = (1.0, 0.0)
        self.score = score

    def __str__(self) -> str:
        return f"{self.team_home} vs. {self.team_away} {self.score[0]}-{self.score[1]}"


class Team:
    """Team class for storing team information and ratings"""
    def __init__(self, name: str):
        self.name = name
        self.ratings = {"home": [glicko2.Rating()], "away": [glicko2.Rating()]}

    def __str__(self) -> str:
        return self.name
