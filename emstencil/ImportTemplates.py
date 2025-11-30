"""
 Program: Setup the SQLite3 Database and convert, if necessary, from an Excel spreadsheet.
    Name: Andrew Dixon            File: ImportTemplates.py
    Date: 23 Nov 2023
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
from dataclasses import dataclass, field
from sxl import Workbook, col2num
from PySide6.QtWidgets import QMessageBox
from .SelectFile import FileSelectionDialog
from .Logging import LOGGER

# TODO: Once TemplateDB object has write/add functionality need to re-write this module.


# Global
DATABASE = ''


def importTemplates(parent) -> bool:
  """importTemplates - Function wrapper to be called from within the application template import."""
  # Be sure to drag in the global data paths.
  from emstencil import DATA_DIR, DATABASE_FILE

  success = False

  dialog = FileSelectionDialog(parent)
  if dialog.exec():  # User pressed OK
    file_path = dialog.selected_file
    success = appConvertSpreadsheet(file_path, DATA_DIR, DATABASE_FILE)
    LOGGER.info("Template import completed...")

  else:
    QMessageBox.information(parent, 'Canceled', 'No file selected.')
    LOGGER.info("Template imort cancled...")

  return success


def appConvertSpreadsheet(xls_path, datadir, database) -> bool:
  """appConvertSpreadsheet - Convert xlsx spreadsheet from within application."""
  global DATABASE

  LOGGER.info(f'Selected file: {xls_path}')
  LOGGER.info(f'Global data dir is: {datadir}')
  LOGGER.info(f'Global database path is: {database}')
  DATABASE = sqlite3.connect(database)

  dbCursor = DATABASE.cursor()
  with open('emstencil/templates.sql') as fp:
    dbCursor.executescript(fp.read())

  # constants - Define names for thigs we want to make easily modifiable
  Spreadsheet = {
    'name': xls_path,  # Can also be workbook path if it needs to be
    'sheet': 'Sheet1',  # Can be sheet name or number (non-zero based)
    'hasColHdg': True,  # Does the spreadsheet have column headings?
  }

  success = convertSpreadsheet(Spreadsheet)
  DATABASE.commit()
  DATABASE.close()

  return success

# Define a class on the fly to assign the data to to make accessing it easier.
@dataclass
class XlatedRow:
  """Data class for spreadsheet columns, gives meaningful names in program.
     Define names for columns so that the object has names that are easy to use."""
  title: str
  content: str
  tags: list
  rowID: int | None = field(init=False)

  def __post_init__(self):
    """Do some clean up to ensure data is as enforcably consistent as we can make it safely."""
    self.rowID = -1
    # Be sure to clean up the tags so they have no leading or trailing spaces.
    self.tags = list(map(str.strip, self.tags))

    # Be sure to make all of the values lower case.
    self.tags = list(map(str.lower, self.tags))

  def __repr__(self) -> str:
    """Override the default repr method."""
    return f'<XlatedRow(Name({self.title}):RowID({self.rowID}))>'

  def __str__(self) -> str:
    """User usable string representation of the row data."""
    return f'{self.title}'


def convertSpreadsheet(Spreadsheet: dict) -> bool:
  """Code for converting spreadsheet into SQLite3 Database."""
  # -- Local variables (work and otherwise)
  TemplateRows: list = []
  tagsToCreate: set = set()
  TagIDs: dict = {}

  # Functions to convert column letters to numbers and vice-versa. Using lambda because I like this as an example.
  #  Converted the functions from sxl to lambda just as an example. moving over to using sxl built ins.
  #  Leaving this "comment" here to have them documented becasue they're still pretty neat lambda's.
  # colNum = lambda a: 0 if a == '' else 1 + ord(a[-1]) - ord('A') + 26 * colNum(a[:-1])  # noqa: E731
  # colName = lambda n: '' if n <= 0 else colName((n - 1) // 26) + chr((n - 1) % 26 + ord('A'))  # noqa: E731

  # Delete all values from all tables.
  # clearTables()

  # Sheet can be the sheet name or the sheet # (ex: wb.sheets[1]).
  ws = Workbook(Spreadsheet['name']).sheets[Spreadsheet['sheet']]

  # Iterate through the spreadsheet building the template table and storing other data needed later.
  for rownum, row in enumerate(ws.rows):

    # Skip column headings row if we're told about it.
    if Spreadsheet['hasColHdg'] and rownum == 0:
      LOGGER.info("Skipping column headings from spreadsheet...")
      continue

    # Build our object from the spreadsheet.
    # Be sure to subtract one since the column conversion is not zero based.
    row = XlatedRow(
      title=row[col2num('A') - 1].strip(),
      content=row[col2num('B') - 1].strip(),
      tags=row[col2num('C') - 1].split(',')
    )

    # Add the templates to the database, store their RowID. Add its tags to the set.
    TemplateRows.append(addTemplateRow(row))
    tagsToCreate = tagsToCreate | set(row.tags)

  # Log how many rows were in the spreadsheet.
  LOGGER.info(f"{len(TemplateRows)} templates loaded from spreadsheet.")

  # Sort tags to be created, also converts set to list object.
  tagsList = sorted(tagsToCreate)
  LOGGER.info(f"{len(tagsList)} unique metadata tags in spreadsheet.")

  # Free memory of tags to create since we won't be using it again. (?? Good practice ??)
  del tagsToCreate

  # Build the tags table, saving the RowIDs used for each tag for use later.
  for tag in tagsList:
    # Use dictionary comprehension to replace the dictionary.
    TagIDs = {**TagIDs, tag: addTagRow(tag)}

  # Link everything together to build the templateTags table.
  for tmplt in TemplateRows:
    for tag in tmplt.tags:
      addTemplateTagsRow(tmplt.rowID, TagIDs[tag] )

  LOGGER.info(f'Number of templates added: {len(TemplateRows)}')
  LOGGER.info(f'Number of tags added: {len(TagIDs)}')

  return len(TemplateRows) > 0


def clearTables() -> None:
  """Delete all values from all tables before reconverting.
     Helpful for re-converting the data when the spreadsheet is updated.
     Currently this is un-used since this rebuilds the DB from ddl every time"""
  global DATABASE

  cursor = DATABASE.cursor()
  cursor.execute("delete from templateTags")
  cursor.execute("delete from tags")
  cursor.execute("delete from templates")
  LOGGER.info("Database tables cleared...")


def addTemplateRow(row: XlatedRow) -> XlatedRow | None:
  """Add Template content rows to the templates table in the database.
     Returns the row it just added updated with it's current rowID in the database."""
  global DATABASE

  cursor = DATABASE.cursor()
  cursor.execute(
    """
      insert into templates (title, content) values (?, ?)
    """,
    [row.title, row.content]
  )
  row.rowID = cursor.lastrowid

  return row


def addTagRow(tag: str) -> int | None:
  """Add Tag content rows to the tags table in the database.
     Returns the rowID for what it just added."""
  global DATABASE

  cursor = DATABASE.cursor()
  cursor.execute(
    """
      insert into tags (tag) values (?)
    """,
    [tag]
  )

  return cursor.lastrowid


def addTemplateTagsRow(tmpltRowID: int, tagRowID: int) -> None:
  """Add records for tags associated with template items."""
  global DATABASE

  cursor = DATABASE.cursor()
  cursor.execute(
    """
      insert into templateTags (tmplt_uid, tag_uid) values (?, ?)
    """,
    [tmpltRowID, tagRowID]
  )
