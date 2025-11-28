#! /usr/bin/env python3
"""
 Program: Setup and present a unified debug/error logging object
    Name: Andrew Dixon            File: Logging.py
    Date: 27 Nov 2025
   Notes:

       Copyright (C) 2025  Andrew Dixon

    This program is free software: you can redistribute it and/or modify  it under the terms of the GNU
    General Public License as published by the Free Software Foundation, either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
    the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See theGNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <https://www.gnu.org/licenses/>.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

import logging
from emstencil import DATADIR, DATABASE_FILE


LOGFILE = f'{DATADIR}/runlog.log'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Capture all levels
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGFILE, mode="w"),  # Overwrite each run
        logging.StreamHandler()  # Defaults to stderr; we'll filter below
    ]
)

# Get the root logger
LOGGER = logging.getLogger('')

# Adjust stream handler to only show errors
# for handler in LOGGER.handlers:
#     if isinstance(handler, logging.StreamHandler):
#         handler.setLevel(logging.ERROR)
