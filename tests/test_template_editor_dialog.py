#! /usr/bin/env python3

"""
 Program: Template editor HTML vs plain load/save behavior.
    Name: Andrew Dixon            File: test_template_editor_dialog.py
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
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from emstencil.Dataclasses import EmailTemplate
from emstencil.content_html import isHTMLContent


@pytest.fixture
def qapp() -> QApplication:
  app = QApplication.instance()
  if app is None:
    app = QApplication(sys.argv)
  return app


@pytest.fixture
def mock_db(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setattr(
    'emstencil.TemplateEditorDialog.TemplateDB',
    lambda: MagicMock(),
  )


def testEditorPlainTemplateUsesPlainPersist(qapp: QApplication, mock_db: None) -> None:
  from emstencil.TemplateEditorDialog import TemplateEditorDialog

  dlg = TemplateEditorDialog(EmailTemplate('T', 'Hello ${name}'))
  assert dlg._persistBodyAsHtml is False
  assert dlg.templateField.acceptRichText() is True
  dlg.templateField.setPlainText('Hello ${name} there')
  assert dlg.BuildTemplateFromFields().content == 'Hello ${name} there'


def testEditorHtmlTemplateUsesHtmlPersist(qapp: QApplication, mock_db: None) -> None:
  from emstencil.TemplateEditorDialog import TemplateEditorDialog

  body = '<p>Hello ${name}</p>'
  dlg = TemplateEditorDialog(EmailTemplate('T', body))
  assert dlg._persistBodyAsHtml is True
  assert dlg.templateField.acceptRichText() is True
  expected = dlg.templateField.toHtml()
  out = dlg.BuildTemplateFromFields().content
  assert out == expected
  assert '${name}' in out
  assert isHTMLContent(out) is True


def testEditorNewTemplateIsPlainPersist(qapp: QApplication, mock_db: None) -> None:
  from emstencil.TemplateEditorDialog import TemplateEditorDialog

  dlg = TemplateEditorDialog(None)
  assert dlg._persistBodyAsHtml is False
  assert dlg.templateField.acceptRichText() is True
  dlg.titleField.setText('N')
  dlg.templateField.setPlainText('x ${y}')
  assert dlg.BuildTemplateFromFields().content == 'x ${y}'


def testEditorNewTemplateWithTableSavesAsHtml(qapp: QApplication, mock_db: None) -> None:
  from emstencil.TemplateEditorDialog import TemplateEditorDialog

  dlg = TemplateEditorDialog(None)
  dlg.titleField.setText('WithTable')
  dlg.templateField.setHtml('<p>Intro</p><table><tr><td>${cell}</td></tr></table>')
  out = dlg.BuildTemplateFromFields().content
  assert '<table' in out.lower()
  assert '${cell}' in out
