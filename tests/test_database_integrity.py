#! /usr/bin/env python3

"""
 Program: Tests for database integrity and constraint behavior.
    Name: Andrew Dixon            File: test_database_integrity.py
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
import sqlite3
from pathlib import Path
from typing import Iterator
from emstencil.Database import TemplateDB
from emstencil.Dataclasses import EmailTemplate, MetadataTag
from emstencil.Exceptions import AccessNullRowID
import emstencil.Database as databaseModule


@pytest.fixture()
def templateDB(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TemplateDB]:
  """Return isolated database instance with schema loaded."""
  dbPath = tmp_path / 'templates.db'
  schemaPath = Path(__file__).resolve().parents[1] / 'emstencil' / 'templates.sql'
  schemaText = schemaPath.read_text(encoding='utf-8')

  # Build a fresh schema for each test so state cannot leak between tests.
  with sqlite3.connect(dbPath) as setupDB:
    setupDB.executescript(schemaText)

  # Reset singleton and point the DB module to the per-test database file.
  TemplateDB._instance = None
  monkeypatch.setattr(databaseModule, 'DATABASE_FILE', dbPath)

  db = TemplateDB()
  yield db

  db.close()
  TemplateDB._instance = None


def testDatabaseTagNormalizationDedupesLowercasesAndTrimsTags(templateDB: TemplateDB) -> None:
  """Checklist #10: Tag normalization dedupes and normalizes casing/whitespace."""
  # Arrange: add template with duplicate/mixed-case/whitespace tags.
  template = EmailTemplate('Normalization', 'Body ${id}')
  template.metadata = [
    MetadataTag('  Alpha  '),
    MetadataTag('alpha'),
    MetadataTag(' ALPHA '),
    MetadataTag('Beta'),
    MetadataTag('  beta  '),
    MetadataTag('   '),
  ]

  # Act: insert with normalized tags, then update with a new normalized target set.
  templateDB.AddTemplate(template)
  template.metadata = [
    MetadataTag('  GAMMA  '),
    MetadataTag('gamma'),
    MetadataTag(' Gamma '),
    MetadataTag('   '),
  ]
  templateDB.UpdateTemplate(template)

  # Assert: only trimmed/lowercased unique tags are linked after update.
  cursor = templateDB.getConnection().cursor()
  cursor.execute(
    """
      select tg.tag
      from tags tg
      inner join templateTags tt on tt.tag_uid = tg.uid
      where tt.tmplt_uid = ?
      order by tg.tag;
    """,
    [template.rowID],
  )
  assert [tag for (tag,) in cursor.fetchall()] == ['gamma']

  # Assert: obsolete tags are cleaned up from tags table.
  cursor.execute('select tag from tags order by tag;')
  assert [tag for (tag,) in cursor.fetchall()] == ['gamma']


def testDatabaseNullRowIDPathsRaiseAccessNullRowID(templateDB: TemplateDB) -> None:
  """Checklist #11: Null rowID error paths raise AccessNullRowID."""
  # Arrange: unresolved template has no rowID and does not exist by title in DB.
  unresolvedTemplate = EmailTemplate('Missing Template', 'Body ${id}')

  # Act / Assert: update path raises when rowID cannot be resolved.
  with pytest.raises(AccessNullRowID):
    templateDB.UpdateTemplate(unresolvedTemplate)

  # Act / Assert: metadata fetch path raises for null rowID directly.
  with pytest.raises(AccessNullRowID):
    templateDB.FetchMetadataForTemplate(unresolvedTemplate)


def testDatabaseFetchAllTemplatesForExportSortsAndFormatsTagCSV(templateDB: TemplateDB) -> None:
  """Checklist #12: Export query returns case-insensitive sorted rows with tag CSV."""
  # Arrange: create templates out of order and with unsorted tag input.
  zebra = EmailTemplate('zebra', 'Z body')
  zebra.metadata = [MetadataTag('b'), MetadataTag('a')]

  alpha = EmailTemplate('Alpha', 'A body')
  alpha.metadata = [MetadataTag('x')]

  noTags = EmailTemplate('beta', 'B body')
  noTags.metadata = []

  templateDB.AddTemplate(zebra)
  templateDB.AddTemplate(alpha)
  templateDB.AddTemplate(noTags)

  # Act
  exportedRows = templateDB.FetchAllTemplatesForExport()

  # Assert: rows are sorted by title case-insensitively and tags are CSV-sorted.
  assert exportedRows == [
    ('Alpha', 'A body', 'x'),
    ('beta', 'B body', ''),
    ('zebra', 'Z body', 'a,b'),
  ]


def testDatabaseTransactionRollbackPreventsPartialWritesOnTagFailure(
  templateDB: TemplateDB,
  monkeypatch: pytest.MonkeyPatch,
) -> None:
  """Checklist #13: Failing tag writes do not leave partial persisted state."""
  # Arrange: seed one stable template so we can verify update rollback behavior.
  stableTemplate = EmailTemplate('Stable Template', 'Original content')
  stableTemplate.metadata = [MetadataTag('stable')]
  templateDB.AddTemplate(stableTemplate)

  originalGetOrCreate = TemplateDB._GetOrCreateTagRowID

  def failingGetOrCreate(self: TemplateDB, tag: str, cursor: sqlite3.Cursor) -> int:
    if tag == 'boom':
      raise RuntimeError('forced tag failure')
    return originalGetOrCreate(self, tag, cursor)

  # Force tag creation failure during sync to exercise transaction rollback.
  monkeypatch.setattr(TemplateDB, '_GetOrCreateTagRowID', failingGetOrCreate)

  # Act / Assert: failing update does not partially modify persisted template data.
  stableTemplate.content = 'Mutated content'
  stableTemplate.metadata = [MetadataTag('stable'), MetadataTag('boom')]
  with pytest.raises(RuntimeError, match='forced tag failure'):
    templateDB.UpdateTemplate(stableTemplate)

  cursor = templateDB.getConnection().cursor()
  cursor.execute('select content from templates where uid = ?;', [stableTemplate.rowID])
  assert cursor.fetchone() == ('Original content',)
  cursor.execute(
    """
      select tg.tag
      from tags tg
      inner join templateTags tt on tt.tag_uid = tg.uid
      where tt.tmplt_uid = ?
      order by tg.tag;
    """,
    [stableTemplate.rowID],
  )
  assert [tag for (tag,) in cursor.fetchall()] == ['stable']

  # Act / Assert: failing insert does not persist template row, links, or failing tag.
  failingInsertTemplate = EmailTemplate('Should Not Persist', 'Insert content')
  failingInsertTemplate.metadata = [MetadataTag('boom')]
  with pytest.raises(RuntimeError, match='forced tag failure'):
    templateDB.AddTemplate(failingInsertTemplate)

  cursor.execute('select count(*) from templates where title = ?;', ['Should Not Persist'])
  assert cursor.fetchone() == (0,)
  cursor.execute("select count(*) from tags where tag = 'boom';")
  assert cursor.fetchone() == (0,)
