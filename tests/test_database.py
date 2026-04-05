#! /usr/bin/env python3

"""
 Program: Tests for Database functionality.
    Name: Andrew Dixon            File: test_database.py
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
from emstencil.Database import TemplateDB
from emstencil.Dataclasses import EmailTemplate, MetadataTag, State


def testDatabaseAddTemplatePersistsAndSetsState(templateDB: TemplateDB) -> None:
  """Checklist #4: AddTemplate persists template and sets rowID/state."""
  # Arrange: create a template with mixed-case tags to verify normalization.
  template = EmailTemplate('Welcome', 'Hello ${name}')
  template.metadata = [MetadataTag('Clients'), MetadataTag('Onboarding')]

  # Act
  templateDB.AddTemplate(template)

  # Assert object state and persisted template row.
  assert template.rowID > 0
  assert template.state == State.EXISTING

  cursor = templateDB.getConnection().cursor()
  cursor.execute('select title, content from templates where uid = ?;', [template.rowID])
  row = cursor.fetchone()
  assert row == ('Welcome', 'Hello ${name}')

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
  # Tags are stored lower-case and linked to the inserted template row.
  assert [tag for (tag,) in cursor.fetchall()] == ['clients', 'onboarding']


def testDatabaseFetchAllTemplatesMapsRowsToDataclasses(templateDB: TemplateDB) -> None:
  """Checklist #5: FetchAllTemplates maps DB rows to EmailTemplate objects."""
  # Arrange
  templateDB.AddTemplate(EmailTemplate('A Title', 'A Content'))
  templateDB.AddTemplate(EmailTemplate('B Title', 'B Content'))

  # Act
  templates = templateDB.FetchAllTemplates()

  # Assert rows are mapped into EmailTemplate objects with DB-backed state.
  assert len(templates) == 2
  assert all(isinstance(template, EmailTemplate) for template in templates)
  assert all(template.rowID > 0 for template in templates)
  assert all(template.state == State.EXISTING for template in templates)
  assert {(template.title, template.content) for template in templates} == {
    ('A Title', 'A Content'),
    ('B Title', 'B Content'),
  }


def testDatabaseUpdateTemplateUpdatesContentAndTags(templateDB: TemplateDB) -> None:
  """Checklist #6: UpdateTemplate updates text and tag associations."""
  # Arrange
  template = EmailTemplate('Release Notes', 'Version ${version}')
  template.metadata = [MetadataTag('engineering'), MetadataTag('announcements')]
  templateDB.AddTemplate(template)

  existingRowID = template.rowID
  template.content = 'Release ${version} is live.'
  template.metadata = [MetadataTag('Announcements'), MetadataTag('product')]

  # Act
  templateDB.UpdateTemplate(template)

  # Assert update kept identity while replacing persisted content and tags.
  assert template.rowID == existingRowID
  assert template.state == State.EXISTING

  cursor = templateDB.getConnection().cursor()
  cursor.execute('select content from templates where uid = ?;', [template.rowID])
  updatedContent = cursor.fetchone()
  assert updatedContent == ('Release ${version} is live.',)

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
  assert [tag for (tag,) in cursor.fetchall()] == ['announcements', 'product']

  cursor.execute('select tag from tags order by tag;')
  assert [tag for (tag,) in cursor.fetchall()] == ['announcements', 'product']


def testDatabaseFetchMetadataForTemplateLoadsTagObjects(templateDB: TemplateDB) -> None:
  """Checklist #7: FetchMetadataForTemplate loads row IDs, association IDs, and state."""
  # Arrange: persist a template with metadata tags to query back from the database.
  template = EmailTemplate('Escalation', 'Issue ${id}')
  template.metadata = [MetadataTag('Urgent'), MetadataTag('Support')]
  templateDB.AddTemplate(template)

  # Replace in-memory metadata so assertions reflect fetched values only.
  template.metadata = []

  # Act
  fetchedTemplate = templateDB.FetchMetadataForTemplate(template)

  # Assert: metadata entries are hydrated with row IDs, association IDs, and existing state.
  assert fetchedTemplate is template
  assert len(fetchedTemplate.metadata) == 2
  assert sorted(tag.tag for tag in fetchedTemplate.metadata) == ['support', 'urgent']
  assert all(tag.rowID > 0 for tag in fetchedTemplate.metadata)
  assert all(tag.assocRowID == template.rowID for tag in fetchedTemplate.metadata)
  assert all(tag.state == State.EXISTING for tag in fetchedTemplate.metadata)


def testDatabaseDeleteTemplateRemovesTemplateLinksAndUnusedTags(templateDB: TemplateDB) -> None:
  """Checklist #8: DeleteTemplate removes template, links, and now-unused tags."""
  # Arrange: persist one template with two tags unique to this template.
  template = EmailTemplate('Sunset Notice', 'System ${system} is retiring.')
  template.metadata = [MetadataTag('deprecation'), MetadataTag('operations')]
  templateDB.AddTemplate(template)
  templateRowID = template.rowID

  # Act
  templateDB.DeleteTemplate(template)

  # Assert: template row is removed.
  cursor = templateDB.getConnection().cursor()
  cursor.execute('select count(*) from templates where uid = ?;', [templateRowID])
  assert cursor.fetchone() == (0,)

  # Assert: template-to-tag link rows are removed.
  cursor.execute('select count(*) from templateTags where tmplt_uid = ?;', [templateRowID])
  assert cursor.fetchone() == (0,)

  # Assert: tags with no remaining links are cleaned up.
  cursor.execute('select count(*) from tags;')
  assert cursor.fetchone() == (0,)


def testDatabaseUpsertTemplateByTitleInsertsThenUpdatesExistingTitle(templateDB: TemplateDB) -> None:
  """Checklist #9: UpsertTemplateByTitle inserts missing title and updates existing title."""
  # Arrange: create an initial template payload for insert path.
  insertTemplate = EmailTemplate('Status Update', 'Initial content ${id}')
  insertTemplate.metadata = [MetadataTag('alpha')]

  # Act: first upsert should insert because title does not yet exist.
  templateDB.UpsertTemplateByTitle(insertTemplate)

  # Assert insert path created a persisted row and existing-state object.
  assert insertTemplate.rowID > 0
  assert insertTemplate.state == State.EXISTING
  insertedRowID = insertTemplate.rowID

  cursor = templateDB.getConnection().cursor()
  cursor.execute('select count(*), content from templates where title = ?;', ['Status Update'])
  countAfterInsert, contentAfterInsert = cursor.fetchone() or (0, '')
  assert countAfterInsert == 1
  assert contentAfterInsert == 'Initial content ${id}'

  # Arrange update payload with same title to trigger update path.
  updateTemplate = EmailTemplate('Status Update', 'Updated content ${id}')
  updateTemplate.metadata = [MetadataTag('beta')]

  # Act: second upsert should update existing row for the matching title.
  templateDB.UpsertTemplateByTitle(updateTemplate)

  # Assert update path keeps row identity while replacing content and tag links.
  assert updateTemplate.rowID == insertedRowID
  assert updateTemplate.state == State.EXISTING

  cursor.execute('select uid, content from templates where title = ?;', ['Status Update'])
  rowAfterUpdate = cursor.fetchone()
  assert rowAfterUpdate == (insertedRowID, 'Updated content ${id}')

  cursor.execute(
    """
      select tg.tag
      from tags tg
      inner join templateTags tt on tt.tag_uid = tg.uid
      where tt.tmplt_uid = ?
      order by tg.tag;
    """,
    [insertedRowID],
  )
  assert [tag for (tag,) in cursor.fetchall()] == ['beta']
