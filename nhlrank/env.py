# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:14:19 2023

@author: shane
Loads ENVIRONMENT VARIABLES from file: `.env`
"""
import os

import dotenv

dotenv.load_dotenv(verbose=True)

# Google Sheet constants
CHESS_DET_GOOGLE_SHEET_KEY = os.environ["CHESS_DET_GOOGLE_SHEET_KEY"]
CHESS_DET_GOOGLE_SHEET_GAMES_GID = int(os.environ["CHESS_DET_GOOGLE_SHEET_GAMES_GID"])

# URL to Google Sheet
# TODO: get based on year, not just hard-coded to 2023-2024
CSV_GAMES_URL = (
    "https://shanemcd.org/wp-content/uploads/2023/08/nhl-202324-asplayed.csv"
)
