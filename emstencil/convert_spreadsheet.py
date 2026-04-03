"""
 Program: Setup the SQLite3 Database and convert, if necessary, from an Excel spreadsheet.
    Name: Andrew Dixon            File: setup.py
    Date: 23 Nov 2023
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

import argparse
import sqlite3
from dataclasses import dataclass, field

from .spreadsheet import read_template_rows


# Global
# Setup the arg parser to import and parse arguments.
parser = argparse.ArgumentParser()


parser.add_argument(
  "--ddl", "-s",
  default='emstencil/templates.sql',
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
database =  sqlite3.connect(args.database)

def main():
  """Main - Xlate the spreadsheet into an object to be able to manipulate"""
  # Create the SQLite3 database from the DDL definition.
  dbCursor = database.cursor()
  with open(args.ddl) as fp:
    dbCursor.executescript(fp.read())

  # Convert the spreadsheet into the SQLite3 database.
  convertSpreadsheet(args.xls)


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


def convertSpreadsheet(xls_path: str) -> None:
  """Code for converting spreadsheet into SQLite3 Database."""
  TemplateRows: list = []
  tagsToCreate: set = set()
  TagIDs: dict = {}

  for title, content, tag_parts in read_template_rows(xls_path):
    row = XlatedRow(title=title, content=content, tags=tag_parts)

    # Add the templates to the database, store their RowID. Add its tags to the set.
    TemplateRows.append(addTemplateRow(row))
    tagsToCreate = tagsToCreate | set(row.tags)

  # Sort tags to be created, also converts set to list object.
  tagsList = sorted(tagsToCreate)

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


def addTemplateRow(row: XlatedRow) -> XlatedRow | None:
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


def addTagRow(tag: str) -> int | None:
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
