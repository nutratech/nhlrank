# -*- coding: utf-8 -*-
"""
Created on Mon May 31 09:19:00 2021 -0400

@author: shane
Custom types for argparse validation
"""
import argparse
import os


def file_path(path_in: str) -> str:
    """Returns file if it exists, else raises argparse error"""
    if os.path.isfile(path_in):
        return path_in
    raise argparse.ArgumentTypeError(f'FileNotFoundError: "{path_in}"')


def file_or_dir_path(path_in: str) -> str:
    """Returns path if it exists, else raises argparse error"""
    if os.path.exists(path_in):
        return path_in
    raise argparse.ArgumentTypeError(f'FileNotFoundError: "{path_in}"')
