#! /usr/bin/env python3
"""
 Program: Ubiquitous items for all files.
    Name: Andrew Dixon            File: Ubiquitous.py
    Date: 6 Nov 2024
   Notes: Single point of declaration of items used across all files.

    Copyright (C) 2023  Andrew Dixon

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

from pathlib import Path


DATADIR = Path('data/')                                     # Data directory for required items.
DATABASE_FILE = DATADIR.joinpath("templates.db")             # Template database storage.
