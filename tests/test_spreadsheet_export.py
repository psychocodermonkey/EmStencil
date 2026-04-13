#! /usr/bin/env python3

"""
 Program: Excel export always writes HTML in the Content column.
    Name: Andrew Dixon            File: test_spreadsheet_export.py
    Date: 5 Apr 2026
   Notes:

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

from emstencil.content_html import exportContentAsHTML
from emstencil.spreadsheet import readTemplateRows, writeTemplatesWorkbook


def testWriteTemplatesWorkbookUsesHtmlExportForContentColumn(tmp_path) -> None:
  path = tmp_path / 'out.xlsx'
  writeTemplatesWorkbook(str(path), [('Title1', 'a & b', 't1,t2')])
  rows = readTemplateRows(str(path))
  assert len(rows) == 1
  title, content, tags = rows[0]
  assert title == 'Title1'
  assert content == exportContentAsHTML('a & b')
  assert tags == ['t1', 't2']


def testWriteTemplatesWorkbookPassesThroughExistingHtmlContent(tmp_path) -> None:
  path = tmp_path / 'out.xlsx'
  body = '<table><tr><td>${x}</td></tr></table>'
  writeTemplatesWorkbook(str(path), [('T', body, 'tag1')])
  rows = readTemplateRows(str(path))
  assert rows[0] == ('T', body, ['tag1'])


def testExportImportRoundTripAppStyleRows(tmp_path) -> None:
  """Simulate DB export rows re-read by import (first sheet, three columns)."""
  path = tmp_path / 'round.xlsx'
  original_rows = [
    ('Plain', 'Hello ${name}', 'a'),
    ('Rich', '<p>Hi ${name}</p>', 'b'),
  ]
  writeTemplatesWorkbook(str(path), original_rows)
  back = readTemplateRows(str(path))
  assert back[0] == ('Plain', '<p>Hello ${name}</p>', ['a'])
  assert back[1] == ('Rich', '<p>Hi ${name}</p>', ['b'])
