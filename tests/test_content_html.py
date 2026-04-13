#! /usr/bin/env python3

"""
 Program: Tests for HTML detection and export wrapping.
    Name: Andrew Dixon            File: test_content_html.py
    Date: 5 Apr 2026
   Notes:

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

import sys

import pytest
from PySide6.QtWidgets import QApplication

from emstencil.content_html import (
  clipboardPlainTextFromMergedHTML,
  exportContentAsHTML,
  isHTMLContent,
  persistHTMLasRichText,
)


@pytest.fixture(scope='module')
def qapp() -> QApplication:
  app = QApplication.instance()
  if app is None:
    app = QApplication(sys.argv)
  return app


def testIsHtmlContentFalseForPlainAndLooseAngle() -> None:
  assert isHTMLContent('Hello ${name}') is False
  assert isHTMLContent('2 < 3 and ${x}') is False
  assert isHTMLContent('<3 friends') is False


def testIsHtmlContentTrueForTableAndParagraphFragments() -> None:
  assert isHTMLContent('<table><tr><td>${x}</td></tr></table>') is True
  assert isHTMLContent('  <p>Hi ${name}</p>') is True


def testHtmlHelperExportContentAsHtmlLeavesHtmlUnchanged() -> None:
  body = '<p>a & b</p>'
  assert exportContentAsHTML(body) == body


def testHtmlHelperExportContentAsHtmlWrapsPlainWithEscaping() -> None:
  assert exportContentAsHTML('a & b') == '<p>a &amp; b</p>'


def testHtmlHelperExportContentAsHtmlConvertsNewlinesToBr() -> None:
  assert exportContentAsHTML('line1\nline2') == '<p>line1<br/>line2</p>'


def testRichTextEditorHtmlShouldPersistDetectsStructure() -> None:
  assert persistHTMLasRichText('<html><body><p>x</p></body></html>') is False
  assert persistHTMLasRichText('<TABLE><tr><td>a</td></tr></TABLE>') is True
  assert persistHTMLasRichText('<ul><li>x</li></ul>') is True


def testClipboardPlainTextOmitsDataUrls(qapp: QApplication) -> None:
  html = (
    '<p>Hello world</p>'
    '<img src="data:image/png;base64,QUJDREVGRw==" alt="x" />'
    '<p>Bye</p>'
  )
  plain = clipboardPlainTextFromMergedHTML(html)
  assert 'data:image' not in plain
  assert 'Hello world' in plain
  assert 'Bye' in plain
  assert '[Image]' in plain


def testClipboardPlainTextStripsBareDataUrlLine(qapp: QApplication) -> None:
  """If a data URL appears as its own text (leaked from conversion), scrub it."""
  html = '<p>Intro</p><p>data:image/png;base64,QUJD</p>'
  plain = clipboardPlainTextFromMergedHTML(html)
  assert 'data:image' not in plain
  assert 'Intro' in plain
