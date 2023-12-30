# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 15:22:46 2023

@author: shane
"""
import os

from nhlrank.models import Team


def get_or_create_team_by_name(teams: dict[str, Team], name: str) -> Team:
    """Adds a player"""
    if name in teams:
        return teams[name]

    _team = Team(name)
    teams[name] = _team
    return _team


def print_title(title: str) -> None:
    """Prints a neat and visible header to separate tables"""
    print(os.linesep)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(title)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print()


def print_subtitle(subtitle: str) -> None:
    """Print a subtitle"""
    print()
    print(subtitle)
    print("~" * len(subtitle))
    print()
