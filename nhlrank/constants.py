#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 31 19:52:12 2023

@author: shane
"""

team_abbreviations_to_full_names: dict[str, list[str]] = {
    "ANA": ["Anaheim", "Ducks"],
    "ARI": ["Arizona", "Coyotes"],
    "BOS": ["Boston", "Bruins"],
    "BUF": ["Buffalo", "Sabres"],
    "CGY": ["Calgary", "Flames"],
    "CAR": ["Carolina", "Hurricanes"],
    "CHI": ["Chicago", "Blackhawks"],
    "COL": ["Colorado", "Avalanche"],
    "CBJ": ["Columbus", "Blue Jackets"],
    "DAL": ["Dallas", "Stars"],
    "DET": ["Detroit", "Red Wings"],
    "EDM": ["Edmonton", "Oilers"],
    "FLA": ["Florida", "Panthers"],
    "LAK": ["Los Angeles", "Kings"],
    "MIN": ["Minnesota", "Wild"],
    "MTL": ["Montreal", "Canadiens"],
    "NSH": ["Nashville", "Predators"],
    "NJD": ["New Jersey", "Devils"],
    "NYI": ["New York", "Islanders"],
    "NYR": ["New York", "Rangers"],
    "OTT": ["Ottawa", "Senators"],
    "PHI": ["Philadelphia", "Flyers"],
    "PIT": ["Pittsburgh", "Penguins"],
    "SJS": ["San Jose", "Sharks"],
    "SEA": ["Seattle", "Kraken"],
    "STL": ["St. Louis", "Blues"],
    "TBL": ["Tampa Bay", "Lightning"],
    "TOR": ["Toronto", "Maple Leafs"],
    "VAN": ["Vancouver", "Canucks"],
    "VGK": ["Vegas", "Golden Knights"],
    "WSH": ["Washington", "Capitals"],
    "WPG": ["Winnipeg", "Jets"],
}

team_full_names_to_abbreviations: dict[str, str] = {
    "Anaheim Ducks": "ANA",
    "Arizona Coyotes": "ARI",
    "Boston Bruins": "BOS",
    "Buffalo Sabres": "BUF",
    "Calgary Flames": "CGY",
    "Carolina Hurricanes": "CAR",
    "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL",
    "Columbus Blue Jackets": "CBJ",
    "Dallas Stars": "DAL",
    "Detroit Red Wings": "DET",
    "Edmonton Oilers": "EDM",
    "Florida Panthers": "FLA",
    "Los Angeles Kings": "LAK",
    "Minnesota Wild": "MIN",
    "Montreal Canadiens": "MTL",
    "Nashville Predators": "NSH",
    "New Jersey Devils": "NJD",
    "New York Islanders": "NYI",
    "New York Rangers": "NYR",
    "Ottawa Senators": "OTT",
    "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT",
    "San Jose Sharks": "SJS",
    "Seattle Kraken": "SEA",
    "St. Louis Blues": "STL",
    "Tampa Bay Lightning": "TBL",
    "Toronto Maple Leafs": "TOR",
    "Vancouver Canucks": "VAN",
    "Vegas Golden Knights": "VGK",
    "Washington Capitals": "WSH",
    "Winnipeg Jets": "WPG",
}

conference_and_division_organization: dict[str, dict[str, list[str]]] = {
    "Eastern": {
        "Atlantic": [
            "BOS",
            "BUF",
            "DET",
            "FLA",
            "MTL",
            "OTT",
            "TBL",
            "TOR",
        ],
        "Metropolitan": [
            "CAR",
            "CBJ",
            "NJD",
            "NYI",
            "NYR",
            "PHI",
            "PIT",
            "WSH",
        ],
    },
    "Western": {
        "Central": [
            "ARI",
            "CHI",
            "COL",
            "DAL",
            "MIN",
            "NSH",
            "STL",
            "WPG",
        ],
        "Pacific": [
            "ANA",
            "CGY",
            "EDM",
            "LAK",
            "SJS",
            "SEA",
            "VAN",
            "VGK",
        ],
    },
}