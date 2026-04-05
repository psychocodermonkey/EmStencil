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

from emstencil.spreadsheet import read_template_rows, write_templates_workbook


def testWriteTemplatesWorkbookWrapsPlainContent(tmp_path) -> None:
  path = tmp_path / 'out.xlsx'
  write_templates_workbook(str(path), [('Title1', 'a & b', 't1,t2')])
  rows = read_template_rows(str(path))
  assert len(rows) == 1
  title, content, tags = rows[0]
  assert title == 'Title1'
  assert content == '<p>a &amp; b</p>'
  assert tags == ['t1', 't2']


def testWriteTemplatesWorkbookLeavesHtmlContentUnchanged(tmp_path) -> None:
  path = tmp_path / 'out.xlsx'
  body = '<table><tr><td>${x}</td></tr></table>'
  write_templates_workbook(str(path), [('T', body, '')])
  rows = read_template_rows(str(path))
  assert rows[0][1] == body


def testExportImportRoundTripAppStyleRows(tmp_path) -> None:
  """Simulate DB export rows re-read by import (first sheet, three columns)."""
  path = tmp_path / 'round.xlsx'
  original_rows = [
    ('Plain', 'Hello ${name}', 'a'),
    ('Rich', '<p>Hi ${name}</p>', 'b'),
  ]
  write_templates_workbook(str(path), original_rows)
  back = read_template_rows(str(path))
  assert back[0] == ('Plain', '<p>Hello ${name}</p>', ['a'])
  assert back[1] == ('Rich', '<p>Hi ${name}</p>', ['b'])
