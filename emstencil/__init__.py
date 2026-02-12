"""
 Program: Initilization routine for application

    Name: Andrew Dixon            File: __init__.py
    Date: 23 Nov 2023
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from .Ubiquitous import DATA_DIR, DATABASE_FILE, LOG_PATH
from .initialize import is_initilized
from .Logging import LOGGER
