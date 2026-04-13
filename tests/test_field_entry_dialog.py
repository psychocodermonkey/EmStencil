#! /usr/bin/env python3

"""
 Program: Tests for field entry helpers (no full GUI scenario).
    Name: test_field_entry_dialog.py
    Date: 5 Apr 2026
   Notes:

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

import base64
import sys

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from emstencil.FieldEntryDialog import ImageFieldRow, qimageToPngDataURL


@pytest.fixture(scope='module')
def qapp() -> QApplication:
  """QImage encoding needs a Qt application instance."""
  app = QApplication.instance()
  if app is None:
    app = QApplication(sys.argv)
  return app


def test_qimage_to_png_data_url_non_empty(qapp: QApplication) -> None:
  img = QImage(6, 6, QImage.Format.Format_RGB32)
  img.fill(0x00AAFF)
  url = qimageToPngDataURL(img)
  prefix = 'data:image/png;base64,'
  assert url.startswith(prefix)
  encoded = url.removeprefix(prefix)
  pngBytes = base64.b64decode(encoded, validate=True)
  assert pngBytes.startswith(b'\x89PNG\r\n\x1a\n')


def test_qimage_to_png_data_url_null_is_empty(qapp: QApplication) -> None:
  assert qimageToPngDataURL(QImage()) == ''


def test_image_field_row_keeps_paste_off_line_edit(qapp: QApplication) -> None:
  """Pasted image is merged as data URL but the line edit stays short for UX."""
  img = QImage(5, 5, QImage.Format.Format_RGB32)
  img.fill(0xABCDEF)
  url = qimageToPngDataURL(img)
  row = ImageFieldRow(180, '')
  row._storePastedImage(url)
  assert row._line.text() == ''
  assert row.fieldText() == url
