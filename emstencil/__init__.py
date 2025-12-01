"""
 Program: Initilization routine for application

    Name: Andrew Dixon            File: __init__.py
    Date: 23 Nov 2023
   Notes:

    Copyright (C) 2023-2025  Andrew Dixon

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

from .Ubiquitous import DATA_DIR, DATABASE_FILE, LOG_PATH
from .initialize import is_initilized
from .Logging import LOGGER
