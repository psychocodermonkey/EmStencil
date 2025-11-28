"""
 Program: Database singleton class for database management.

    Name: Andrew Dixon            File: __init__.py
    Date: 6 Nov 2025
   Notes:

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

import sqlite3
from pathlib import Path
from .Ubiquitous import DATADIR, DATABASE_FILE
from .Logging import LOGGER


def is_initilized() -> bool:
  initilizeData()
  databaseFile = DATADIR.joinpath('templates.db')

  if not databaseFile.exists():
    if not DATADIR.exists():
      createDirectory()
      createDatabase()
    else:
      createDatabase()
  else:
    LOGGER.info('All objects found.')

  return True


def createDirectory() -> bool:
  """
  Create the data directory if it does not exist.
  """
  if not DATADIR.exists():
    DATADIR.mkdir(parents=True, exist_ok=True)
    LOGGER.info(f"Created data directory: {Path(__file__).parent.joinpath(DATADIR)}")

  else:
    LOGGER.info(f"Data directory {Path(__file__).parent.joinpath(DATADIR)} found.")

  return DATADIR.exists()


def createDatabase() -> bool:
  """
  Create the database inside the data directory if it does not exist.
  """
  schemaDDL = Path(__file__).parent.joinpath('templates.sql')

  if not DATABASE_FILE.exists():
    LOGGER.info(f"Creating database: {Path(__file__).parent.joinpath(DATABASE_FILE)}")
    database =  sqlite3.connect(DATABASE_FILE)
    dbCursor = database.cursor()

    LOGGER.info(f"Reading internal schema file ({schemaDDL}) for database...")
    with open(schemaDDL) as fp:
      dbCursor.executescript(fp.read())

  else:
    LOGGER.info(f"Using existing database found at: {Path(__file__).parent.joinpath(DATABASE_FILE)}")

  return DATABASE_FILE.exists()


def initilizeData() -> bool:
  """
  Function just in case we need to manually cause a rebuild by calling this script directly.
  """
  if createDirectory():
    if createDatabase():
      LOGGER.info("All setup processes completed normally.")

    else:
      LOGGER.info("Error during createDatabase.")

  else:
    LOGGER.info("Error creating data directory.")
    return False

  return True


if __name__ == "__main__":
  is_initilized()
