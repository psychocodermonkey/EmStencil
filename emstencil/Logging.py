#! /usr/bin/env python3
"""
 Program: Setup and present a unified debug/error logging object
    Name: Andrew Dixon            File: Logging.py
    Date: 27 Nov 2025
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

import logging
from emstencil import LOG_PATH


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Capture all levels
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, mode="w"),  # Overwrite each run
        logging.StreamHandler()  # Defaults to stderr; we'll filter below
    ]
)

# Get the root logger
LOGGER = logging.getLogger('')

# Adjust stream handler to only show errors
# for handler in LOGGER.handlers:
#     if isinstance(handler, logging.StreamHandler):
#         handler.setLevel(logging.ERROR)
