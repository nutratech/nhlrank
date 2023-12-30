# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:14:19 2023

@author: shane
Loads ENVIRONMENT VARIABLES from file: `.env`
"""
import dotenv

dotenv.load_dotenv(verbose=True)

# URL to CSV
# TODO: get based on year, not just hard-coded to 2023-2024
CSV_GAMES_URL = (
    "https://shanemcd.org/wp-content/uploads/2023/08/nhl-202324-asplayed.csv"
)

# TODO: override command line args with ENV vars from .env file
#       (e.g. `--debug` should be able to be set in .env file)
#       (e.g. `--num_games` should be able to be set in .env file)
#       (e.g. `--sort_column` should be able to be set in .env file)
#       (e.g. `--team` should be able to be set in .env file)
#       (e.g. `--skip_dl` should be able to be set in .env file)
