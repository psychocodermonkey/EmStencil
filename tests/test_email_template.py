#! /usr/bin/env python3

"""
 Program: Tests for EmailTemplate functionality.
    Name: Andrew Dixon            File: test_email_template.py
    Date: 04 Apr 2026
   Notes:

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

import pytest
from emstencil.Dataclasses import EmailTemplate
from emstencil.Exceptions import (
  TemplateFieldKindConflict,
  TemplateKeyValueMismatch,
  TemplateKeyValueNull,
)


def testEmailTemplateInitParsesPlaceholders() -> None:
  """Checklist #1: EmailTemplate initialization parses placeholders correctly."""
  # Arrange
  template = EmailTemplate(
    'Greeting',
    'Hello ${name}, ticket ${TicketID}; closing for ${name}.',
  )

  # Act
  parsedFields = template.fields

  # Assert
  assert list(parsedFields.keys()) == ['name', 'TicketID']
  assert parsedFields == {'name': None, 'TicketID': None}
  assert template.numberOfFields == 2
  assert template.fieldsSet is False

def testEmailTemplateReplacedTextReplacesPlaceholders() -> None:
  """Checklist #2: EmailTemplate.replacedText replaces placeholders correctly."""
  # Arrange: populate internal field values for deterministic replacement output.
  template = EmailTemplate('Reminder', 'Hi ${name}. ${name}, your ID is ${id}.')
  template.fields = {'name': 'Alex', 'id': '42'}

  # Act
  rendered = template.replacedText

  # Assert
  assert rendered == 'Hi Alex. Alex, your ID is 42.'


def testEmailTemplateReplacedTextWithUnsetFieldsRaisesTypeError() -> None:
  """Checklist #2a: EmailTemplate.replacedText raises when fields remain unset."""
  # Arrange: default parsed fields are initialized to None.
  template = EmailTemplate('Reminder', 'Hi ${name}.')

  # Act / Assert: unresolved placeholders propagate None into str.replace.
  # Python raises TypeError because the replacement argument must be a string.
  with pytest.raises(TypeError):
    _ = template.replacedText


def testEmailTemplateClearFieldsResetsValuesAndFieldsSet() -> None:
  """Checklist #2b: EmailTemplate.clearFields resets values and fieldsSet state."""
  # Arrange: seed all parsed placeholder values with non-empty strings.
  template = EmailTemplate('Greeting', 'Hi ${name} from ${team}.')
  template.fields = {'name': 'Alex', 'team': 'Support'}
  assert template.fieldsSet is True

  # Act
  template.clearFields()

  # Assert: all values are reset to None and aggregate state reports unset.
  assert template.fields == {'name': None, 'team': None}
  assert template.fieldsSet is False


def testEmailTemplateFieldsSetTreatsEmptyStringAsUnset() -> None:
  """Checklist #2c: EmailTemplate.fieldsSet treats empty strings as unset values."""
  # Arrange: one parsed placeholder is set to an empty string.
  template = EmailTemplate('Greeting', 'Hi ${name} from ${team}.')
  template.fields = {'name': 'Alex', 'team': ''}

  # Act
  isSet = template.fieldsSet

  # Assert: all() uses Python truthiness, so empty string reports as unset.
  assert isSet is False


def testEmailTemplateSetFieldsRejectsBadInput() -> None:
  """Checklist #3: EmailTemplate.setFields rejects missing/extra/null-like inputs."""
  # Missing key is rejected.
  missingKeyTemplate = EmailTemplate('Mismatch', 'Hi ${name} from ${team}.')
  with pytest.raises(TemplateKeyValueMismatch):
    missingKeyTemplate.setFields({'name': 'Alex'})

  # Extra key is rejected.
  extraKeyTemplate = EmailTemplate('Mismatch', 'Hi ${name}.')
  with pytest.raises(TemplateKeyValueMismatch):
    extraKeyTemplate.setFields({'name': 'Alex', 'team': 'Ops'})

  # Unset internal fields are treated as null-like and rejected.
  nullLikeTemplate = EmailTemplate('Null', 'Hi ${name}.')
  with pytest.raises(TemplateKeyValueNull):
    nullLikeTemplate.setFields({'name': None})


def testEmailTemplateSetFieldsAcceptsInitialValuesFromNone() -> None:
  """Checklist #3a: EmailTemplate.setFields accepts first-time values and sets fields."""
  # Arrange: parsed placeholders start as None before user input is applied.
  template = EmailTemplate('Case Match', 'Hi ${name}, ${TEAM}, ${Title}.')

  # Act
  template.setFields({'name': 'ALEx', 'TEAM': 'alpha', 'Title': 'mY task'})

  # Assert: values are stored and case-transformed based on placeholder key casing.
  assert template.fields == {'name': 'alex', 'TEAM': 'ALPHA', 'Title': 'My Task'}
  assert template.fieldsSet is True


def testEmailTemplateReplacedTextUsesCaseShapedValuesAfterSetFields() -> None:
  """Merged plain body shows the same casing stored from placeholder-shaped setFields rules."""
  template = EmailTemplate('Case Match', 'Hi ${name}, team ${TEAM}, task ${Title}.')
  template.setFields({'name': 'ALEx', 'TEAM': 'alpha', 'Title': 'mY task'})
  assert template.replacedText == 'Hi alex, team ALPHA, task My Task.'


def testEmailTemplateSetFieldsAppliesCaseFoldForHtmlBody() -> None:
  """Placeholder case rules apply to plain field values even when the body is HTML."""
  template = EmailTemplate('H', '<p>Hi ${name}</p>')
  template.setFields({'name': 'ALEx'})
  assert template.fields == {'name': 'alex'}


def testEmailTemplateReplacedTextEscapesValuesInHtmlBody() -> None:
  """Merged values are HTML-escaped when the template body is HTML."""
  template = EmailTemplate('H', '<td>${cell}</td>')
  template.fields = {'cell': 'a < b & c'}
  assert template.replacedText == '<td>a &lt; b &amp; c</td>'


def testExportWrappedPlainIsDetectedAsHtmlForMerge() -> None:
  """Export-wrapped body is HTML for merge/escape; field values still follow placeholder case."""
  from emstencil.content_html import export_content_as_html

  wrapped = export_content_as_html('Hi ${name}')
  template = EmailTemplate('T', wrapped)
  template.setFields({'name': 'BOB'})
  assert template.fields['name'] == 'bob'
  assert template.replacedText == '<p>Hi bob</p>'


def testEmailTemplateImagePlaceholderPlainBodyWrappedAsHtml() -> None:
  """^{...} in a non-HTML body is wrapped like spreadsheet export so merge treats it as HTML."""
  template = EmailTemplate('Img', 'Hello ^{Logo} there')
  assert template.content == '<p>Hello ^{Logo} there</p>'
  assert list(template.fields.keys()) == ['Logo']
  assert template.field_kinds == {'Logo': 'image'}


def testEmailTemplateFieldKindConflictRaises() -> None:
  """The same key as ${...} and ^{...} is a template definition error."""
  with pytest.raises(TemplateFieldKindConflict) as exc_info:
    EmailTemplate('Bad', 'Hi ${x} and ^{x}')
  assert exc_info.value.key == 'x'


def testEmailTemplateMixedTextAndImagePlaceholders() -> None:
  """Document order defines field keys; merge uses correct delimiters per kind."""
  template = EmailTemplate('Mix', '<p>${name} see ^{Shot}</p>')
  assert list(template.fields.keys()) == ['name', 'Shot']
  assert template.field_kinds == {'name': 'text', 'Shot': 'image'}
  template.setFields({'name': 'Pat', 'Shot': 'http://example.com/x.png'})
  assert template.replacedText == (
    '<p>pat see <img src="http://example.com/x.png" alt="Shot" /></p>'
  )


def testEmailTemplateReplacedTextReplacesCaretPlaceholders() -> None:
  template = EmailTemplate('I', '<p>^{A}</p>')
  template.fields = {'A': '<img src="x" />'}
  assert template.replacedText == '<p>&lt;img src="x" /&gt;</p>'


def testEmailTemplateSetFieldsSkipsCaseRulesForImageKind() -> None:
  template = EmailTemplate('I', '<p>^{token}</p>')
  template.setFields({'token': 'AbCd'})
  assert template.fields['token'] == 'AbCd'


def testEmailTemplateDataUrlCaretBecomesImgTag() -> None:
  """Bare ^{key} with a data URL must merge to <img> so HTML preview shows a picture."""
  template = EmailTemplate('I', '<p>Hi ^{Pic}</p>')
  url = 'data:image/png;base64,QUJD'
  template.setFields({'Pic': url})
  out = template.replacedText
  assert '<img ' in out
  assert 'src="data:image/png;base64,QUJD"' in out
  assert out.count('data:image/png;base64,QUJD') == 1


def testEmailTemplateCaretInsideImgSrcIsUrlOnly() -> None:
  template = EmailTemplate('I', '<p><img src="^{Pic}" alt="a" /></p>')
  url = 'data:image/png;base64,QUJD'
  template.setFields({'Pic': url})
  out = template.replacedText
  assert out == '<p><img src="data:image/png;base64,QUJD" alt="a" /></p>'
  assert out.count('<img') == 1
