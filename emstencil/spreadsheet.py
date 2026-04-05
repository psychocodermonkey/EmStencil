"""
 Program: Centralized .xlsx read/write for template import and export.
    Name: Andrew Dixon            File: spreadsheet.py
    Date: 3 Apr 2026
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

from zipfile import BadZipFile
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from .Exceptions import InvalidImportFileType


EXPORT_HEADERS: tuple[str, str, str] = ('Title', 'Content', 'Tags')


def _cell_str(value: object) -> str:
  if value is None:
    return ''
  return str(value).strip()


def read_template_rows(path: str) -> list[tuple[str, str, list[str]]]:
  """
  Load the first worksheet in the workbook. Row 1 is skipped (header).
  Columns A–C are title, content, and comma-separated tags (split only; normalize elsewhere).
  """
  try:
    wb = load_workbook(path, read_only=True, data_only=True)
  except (BadZipFile, InvalidFileException, OSError) as e:
    raise InvalidImportFileType() from e

  try:
    if not wb.worksheets:
      raise InvalidImportFileType()

    ws = wb.worksheets[0]
    out: list[tuple[str, str, list[str]]] = []

    for row in ws.iter_rows(min_row=2, max_col=3, values_only=True):
      title = _cell_str(row[0] if row else None)
      content = _cell_str(row[1] if row and len(row) > 1 else None)
      raw_tags = row[2] if row and len(row) > 2 else None
      tags_cell = _cell_str(raw_tags) if raw_tags is not None else ''
      tag_parts = tags_cell.split(',') if tags_cell else []
      out.append((title, content, tag_parts))

  finally:
    wb.close()

  return out


def write_templates_workbook(path: str, rows: list[tuple[str, str, str]]) -> None:
  """Write a new workbook with one sheet: header row plus title, content, tags (comma-separated)."""
  wb = Workbook()
  ws = wb.active
  ws.append(list(EXPORT_HEADERS))
  for title, content, tags_csv in rows:
    ws.append([title, content, tags_csv])
  wb.save(path)
