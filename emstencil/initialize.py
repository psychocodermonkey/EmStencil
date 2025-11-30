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

import sys
import sqlite3
from pathlib import Path
from emstencil import DATA_DIR, DATABASE_FILE
from .Logging import LOGGER
from .Exceptions import DatabaseDDLSourceMissing


def is_initilized() -> bool:
  initilizeData()
  databaseFile = DATA_DIR.joinpath('templates.db')

  if not databaseFile.exists():
    if not DATA_DIR.exists():
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
  if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGGER.info(f"Created data directory: {Path(__file__).parent.joinpath(DATA_DIR)}")

  else:
    LOGGER.info(f"Data directory {Path(__file__).parent.joinpath(DATA_DIR)} found.")

  return DATA_DIR.exists()


def getSchemaPath() -> Path:
  """
  Return the proper path for the DDL file used to define the database.
  """

  ddl_locations = {
    "source": Path(__file__).parent / 'templates.sql',
    "frozen": Path(sys.argv[0]).parent / 'templates.sql',
  }

  if ddl_locations['source'].exists():
    # DDL is in the package directory and we are running from source.
    base = ddl_locations['source']
    LOGGER.info(f"Returning DDL path for source state: {base}")

  elif ddl_locations['frozen'].exists():
    # DDL exists at the base direcotry in a packaged method.
    base = ddl_locations['frozen']
    LOGGER.info(f"Returning DDL path for frozen state: {base}")

  else:
    # The DDL wasn't in either locaton we expect.
    LOGGER.error('Could not find DDL file for database schema.')
    # Dump dictionary with a list comprehension to check the locations.
    checked = ", ".join(f"{k}: {v}" for k, v in ddl_locations.items())
    raise DatabaseDDLSourceMissing(checked)

  return base


def createDatabase() -> bool:
  """
  Create the database inside the data directory if it does not exist.
  """
  #schemaDDL = Path(__file__).parent.joinpath('templates.sql')
  schemaDDL = getSchemaPath()
  LOGGER.info(f"Schema DDL loaded from: {schemaDDL}")

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
