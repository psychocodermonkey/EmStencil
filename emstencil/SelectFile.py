#! /usr/bin/env python3
"""
 Program: Find and select a file to be passed elsewhere.
    Name: Andrew Dixon            File:   SelectFile.py
    Date: 27 Nov 2025
   Notes:

    Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import QFileDialog, QWidget

_ALL_FILES = 'All Files (*)'


def _qtFilterSegments(filters: Sequence[tuple[str, str]]) -> list[str]:
  """Turn (label, glob) pairs into QFileDialog filter rows; trailing catch-all from _ALL_FILES."""
  segments: list[str] = []
  
  for label, pattern in filters:
    segments.append(f'{label} ({pattern})')
  
  segments.append(_ALL_FILES)
  
  return segments


def selectFilePath(
  parent: QWidget | None,
  title: str,
  filters: Sequence[tuple[str, str]],
  startDir: str = '',
) -> str | None:
  """Open a native file dialog and return the chosen path, or None if canceled."""

  fileName: str | None = None
  _selectedFilter: str | None = None

  filterString: str = ';;'.join(_qtFilterSegments(filters))
  fileName, _selectedFilter = QFileDialog.getOpenFileName(
    parent=parent, 
    caption=title, 
    dir=startDir, 
    filter=filterString
  )

  return fileName if fileName else None
