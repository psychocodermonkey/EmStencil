"""
 Program: Detect HTML template bodies and prepare content for HTML export.
    Name: Andrew Dixon            File: content_html.py
    Date: 5 Apr 2026
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

import html
import re

# Opening or closing tag with a letter name; avoids treating "<3" or "<!" alone as HTML.
_TAG_RE = re.compile(r'</?[a-zA-Z][\w:-]*')


def is_html_content(content: str) -> bool:
  """True when content is treated as an HTML fragment (tables, Qt/HTML paste, export-wrapped plain)."""
  t = content.lstrip()
  if not t.startswith('<'):
    return False
  return bool(_TAG_RE.search(t))


# Markup Qt/Word paste adds that plain-text save would drop (default Qt doc still uses <p> only).
_EDITOR_STRUCTURAL_MARKERS: tuple[str, ...] = ('<table', '<ul', '<ol', '<img', '<hr')


def rich_text_editor_html_should_persist_as_html(editor_html: str) -> bool:
  """True when QTextEdit.toHtml() carries structure that toPlainText() would lose."""
  h = editor_html.lower()
  return any(m in h for m in _EDITOR_STRUCTURAL_MARKERS)


def export_content_as_html(content: str) -> str:
  """Excel export: emit HTML; wrap plain templates in a single escaped paragraph."""
  if is_html_content(content):
    return content
  escaped = html.escape(content, quote=False).replace('\n', '<br/>')
  return f'<p>{escaped}</p>'
