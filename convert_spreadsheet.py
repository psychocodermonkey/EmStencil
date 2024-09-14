#! /usr/bin/env python3
"""
 Program: Setup the SQLite3 Database and convert, if necessary, from an Excel spreadsheet.
    Name: Andrew Dixon            File: setup.py
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

import argparse
import sqlite3
from dataclasses import dataclass, field
from sxl import Workbook


# Global
# Setup the arg parser to import and parse arguments.
parser = argparse.ArgumentParser()


parser.add_argument(
  "--ddl", "-s",
  default='data/templates.sql',
  required=False,
  help="Specify path for ddl file to build the bdatabase."
)

parser.add_argument(
  "--database", "-d",
  default='data/templates.db',
  required=False,
  help="Specify path for database file."
)

parser.add_argument(
  "--xls", "-x",
  default="data/templates.xlsx",
  help="Location for templates in xlsx format to add to convert to database."
)

args = parser.parse_args()

# Define connection to database
# TODO: Once TemplateDB object has write/add functionality need to re-write this module.
database = sqlite3.connect(args.database)

# constants - Define names for thigs we want to make easily modifiable
Spreadsheet = {
  'name' : args.xls,                            # Can also be workbook path if it needs to be
  'sheet' : 'Sheet1',                           # Can be sheet name or number (non-zero based)
  'hasColHdg' : True,                           # Does the spreadsheet have column headings?
}

def main():
  """Main - Xlate the spreadsheet into an object to be able to manipulate"""
  # Create the SQLite3 database from the DDL definition.
  dbCursor = database.cursor()
  with open(args.ddl) as fp:
    dbCursor.executescript(fp.read())

  # Convert the spreadsheet into the SQLite3 database.
  convertSpreadsheet(Spreadsheet)


# Define a class on the fly to assign the data to to make accessing it easier.
@dataclass
class XlatedRow:
  """Data class for spreadsheet columns, gives meaningful names in program.
     Define names for columns so that the object has names that are easy to use."""
  title: str
  content: str
  tags: list
  rowID: int = field(init=False)

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


def convertSpreadsheet(Spreadsheet: dict) -> None:
  """Code for converting spreadsheet into SQLite3 Database."""
  # -- Local variables (work and otherwise)
  TemplateRows = []
  tagsToCreate = set()
  TagIDs = {}

  # Functions to convert column letters to numbers and vice-versa. Using lambda because I can.
  colNum = lambda a: 0 if a == '' else 1 + ord(a[-1]) - ord('A') + 26 * colNum(a[:-1])  # noqa: E731
  colName = lambda n: '' if n <= 0 else colName((n - 1) // 26) + chr((n - 1) % 26 + ord('A'))  # noqa: E731

  # Delete all values from all tables.
  # clearTables()

  # Sheet can be the sheet name or the sheet # (ex: wb.sheets[1]).
  ws = Workbook(Spreadsheet['name']).sheets[Spreadsheet['sheet']]

  # Iterate through the spreadsheet building the template table and storing other data needed later.
  for rownum, row in enumerate(ws.rows):

    # Skip column headings row if we're told about it.
    if Spreadsheet['hasColHdg'] and rownum == 0:
      continue

    # Build our object from the spreadsheet.
    # Be sure to subtract one since the column conversion is not zero based.
    row = XlatedRow(
      title=row[colNum('A') - 1].strip(),
      content=row[colNum('B') - 1].strip(),
      tags=row[colNum('C') - 1].split(',')
    )

    # Add the templates to the database, store their RowID. Add its tags to the set.
    TemplateRows.append(addTemplateRow(row))
    tagsToCreate = tagsToCreate | set(row.tags)

  # Sort tags to be created, also converts set to list object.
  tagsToCreate = sorted(tagsToCreate)

  # Build the tags table, saving the RowIDs used for each tag for use later.
  for tag in tagsToCreate:
    # Use dictionary comprehension to replace the dictionary.
    TagIDs = {**TagIDs, tag: addTagRow(tag)}

  # Link everything together to build the templateTags table.
  for tmplt in TemplateRows:
    for tag in tmplt.tags:
      addTemplateTagsRow(tmplt.rowID, TagIDs[tag] )

  print(f'Number of templates added: {len(TemplateRows)}')
  print(f'Number of tags added: {len(TagIDs)}')


def clearTables() -> None:
  """Delete all values from all tables before reconverting.
     Helpful for re-converting the data when the spreadsheet is updated.
     Currently this is un-used since this rebuilds the DB from ddl every time"""
  cursor = database.cursor()
  cursor.execute("delete from templateTags")
  cursor.execute("delete from tags")
  cursor.execute("delete from templates")


def addTemplateRow(row: XlatedRow) -> XlatedRow:
  """Add Template content rows to the templates table in the database.
     Returns the row it just added updated with it's current rowID in the database."""
  cursor = database.cursor()
  cursor.execute(
    """
      insert into templates (title, content) values (?, ?)
    """,
    [row.title, row.content]
  )
  row.rowID = cursor.lastrowid

  return row


def addTagRow(tag: str) -> int:
  """Add Tag content rows to the tags table in the database.
     Returns the rowID for what it just added."""
  cursor = database.cursor()
  cursor.execute(
    """
      insert into tags (tag) values (?)
    """,
    [tag]
  )

  return cursor.lastrowid


def addTemplateTagsRow(tmpltRowID: int, tagRowID: int) -> None:
  """Add records for tags associated with template items."""
  cursor = database.cursor()
  cursor.execute(
    """
      insert into templateTags (tmplt_uid, tag_uid) values (?, ?)
    """,
    [tmpltRowID, tagRowID]
  )


# Execute main()
if __name__ == '__main__':
  main()
  # Commit the changes to the database and close the connection.
  database.commit()
  database.close()