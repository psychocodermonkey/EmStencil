"""
 Program: Export templates from the database to an .xlsx file.
    Name: Andrew Dixon            File: ExportTemplates.py
    Date: 3 Apr 2026
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from .Database import TemplateDB
from .Logging import LOGGER
from .spreadsheet import write_templates_workbook


def exportTemplates(parent) -> bool:
  """Prompt for a save path and write all templates to an .xlsx file."""
  path, _ = QFileDialog.getSaveFileName(
    parent,
    'Export Templates',
    '',
    'Excel Files (*.xlsx)',
  )

  if not path:
    LOGGER.info('Template export canceled (no path).')

    return False

  p = Path(path)
  if p.suffix.lower() != '.xlsx':
    p = p.with_suffix('.xlsx')
    path = str(p)

  if p.exists():
    reply = QMessageBox.question(
      parent,
      'Overwrite',
      f'"{path}" already exists. Overwrite?',
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
      QMessageBox.StandardButton.Cancel,
    )

    if reply != QMessageBox.StandardButton.Yes:
      LOGGER.info('Template export canceled (overwrite declined).')

      return False

  db = TemplateDB()
  rows = db.FetchAllTemplatesForExport()

  try:
    write_templates_workbook(path, rows)

  except OSError as e:
    LOGGER.error(f'Export failed: {e}')
    QMessageBox.critical(parent, 'Export failed', str(e))

    return False

  LOGGER.info(f'Exported {len(rows)} template(s) to {path}')
  QMessageBox.information(parent, 'Export', 'Export completed.')

  return True
