"""
 Program: Setup the SQLite3 Database and convert, if necessary, from an Excel spreadsheet.
    Name: Andrew Dixon            File: ImportTemplates.py
    Date: 23 Nov 2023-2025
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

from dataclasses import dataclass, field
from PySide6.QtWidgets import QMessageBox
from .Database import TemplateDB
from .Dataclasses import EmailTemplate, MetadataTag
from .SelectFile import selectFilePath
from .Logging import LOGGER
from .spreadsheet import readTemplateRows


def importTemplates(parent) -> bool:
  """importTemplates - Function wrapper to be called from within the application template import."""
  # Be sure to drag in the global data paths.
  from emstencil import DATA_DIR, DATABASE_FILE

  success = False

  filePath: str | None = selectFilePath(
    parent=parent,
    title='Select Template File',
    filters=(('Excel Files', '*.xlsx'),),
  )

  if filePath:
    success = appConvertSpreadsheet(filePath, DATA_DIR, DATABASE_FILE)
    LOGGER.info('Template import completed...')

  else:
    QMessageBox.information(parent, 'Canceled', 'No file selected.')
    LOGGER.info('Template import canceled...')

  return success


def appConvertSpreadsheet(xlsPath, dataDir, database) -> bool:
  """appConvertSpreadsheet - Convert xlsx spreadsheet from within application."""
  LOGGER.info(f'Selected file: {xlsPath}')
  LOGGER.info(f'Global data dir is: {dataDir}')
  LOGGER.info(f'Global database path is: {database}')
  db = TemplateDB()

  return convertSpreadsheet(xlsPath, db)


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


def convertSpreadsheet(xlsxPath: str, db: TemplateDB | None = None) -> bool:
  """Read the first worksheet of an .xlsx file and upsert rows into the database."""
  if db is None:
    db = TemplateDB()

  templateRows: list[XlatedRow] = []
  seenTitles: set[str] = set()
  duplicateTitles: set[str] = set()

  LOGGER.info('Reading spreadsheet (first sheet, row 1 skipped as header)...')
  rawRows = readTemplateRows(xlsxPath)

  for title, content, tagParts in rawRows:
    row = XlatedRow(title=title, content=content, tags=tagParts)

    if row.title in seenTitles:
      duplicateTitles.add(row.title)

    else:
      seenTitles.add(row.title)
    templateRows.append(row)

  # Log how many rows were in the spreadsheet.
  LOGGER.info(f'{len(templateRows)} templates loaded from spreadsheet.')

  if duplicateTitles:
    duplicateList = ', '.join(sorted(duplicateTitles))
    errorMsg = f'Duplicate template titles found in import file: {duplicateList}'
    LOGGER.error(errorMsg)
    raise ValueError(errorMsg)

  for importedRow in templateRows:
    template = EmailTemplate(importedRow.title, importedRow.content)
    template.metadata: list[MetadataTag] = [MetadataTag(tag) for tag in importedRow.tags if tag]
    db.UpsertTemplateByTitle(template)

  LOGGER.info(f'Number of templates added: {len(templateRows)}')

  return len(templateRows) > 0
