# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 10:18:32 2023

@author: shane
"""
import argparse
import os
import shutil

# Package info
__title__ = "sp"
__version__ = "0.0.1.dev5"
__author__ = "Shane J"
__email__ = "chown_tee@proton.me"
__license__ = "GPL v3"
__copyright__ = "Copyright 2023-2024 Shane J"
__url__ = "https://github.com/nutratech/nhlrank"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Other constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Global variables
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Console size, don't print more than it
BUFFER_WD = shutil.get_terminal_size()[0]
BUFFER_HT = shutil.get_terminal_size()[1]

# Location on disk to cache CSV file
# FIXME: do dynamically based on what year it currently is; get from official NHL API
CSV_GAMES_FILE_PATH = os.path.join(
    PROJECT_ROOT, "data", "input", "nhl-202324-asplayed.csv"
)

# Request timeouts
REQUEST_CONNECT_TIMEOUT = 3
REQUEST_READ_TIMEOUT = 15

# lichess.org uses 110 and 75 (65 for variants)
DEVIATION_PROVISIONAL = 110
DEVIATION_ESTABLISHED = 75

####################################################
# CLI config (settings, defaults, and flags)
####################################################


# pylint: disable=too-few-public-methods,too-many-instance-attributes
class CliConfig:
    """Mutable global store for configuration values"""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

    def set_flags(self, args: argparse.Namespace) -> None:
        """
        Sets flags:
          {DEBUG, PAGING}
            from main (after arg parse). Accessible throughout package.
            Must be re-imported globally.
        """

        self.debug = args.debug

        if self.debug:
            print(f"Console size: {BUFFER_HT}h x {BUFFER_WD}w")


# Create the shared instance object
CLI_CONFIG = CliConfig()
