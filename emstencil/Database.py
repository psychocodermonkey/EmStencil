"""
 Program: Database singleton class for database management.
    Name: Andrew Dixon            File: TemplateDB.py
    Date: 23 Nov 2023
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

import sqlite3
from emstencil import Dataclasses as emClasses
from emstencil import DATABASE_FILE
from .Dataclasses import State
from .Exceptions import AccessNullRowID


class TemplateDB:
  """Data layer class for handling translation of data to and from the database."""

  _instance = None

  def __new__(db, *args, **kwargs):
    """Generate new instance if one doesn't exist, return the existing one if it does."""
    if not db._instance:
      db._instance = super().__new__(db, *args, **kwargs)
    return db._instance

  def __init__(self):
    """New instance of database connection."""
    self.DB = sqlite3.connect(DATABASE_FILE)

    # Be sure to enable foreign keys on database
    self.DB.execute('pragma foreign_keys = ON')

  def getConnection(self) -> sqlite3.Connection:
    """Return connection to the database if special queries are needed."""
    return self.DB

  def close(self) -> None:
    """Close the database connection."""
    self.DB.close()

  def FetchAllTemplates(self) -> list[emClasses.EmailTemplate]:
    """Return all templates from the DB."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        Select title, content, uid
        from templates;
      """
    )

    # Build template objects for query results.
    tmplts = []
    for row in cursor:
      tmplt = emClasses.EmailTemplate(row[0], row[1])
      tmplt.rowID = row[2]
      tmplt.state = State.EXISTING
      tmplts.append(tmplt)

    return tmplts

  def FetchAllTemplatesForExport(self) -> list[tuple[str, str, str]]:
    """Return (title, content, tags_csv) for every template, sorted by title (case-insensitive)."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        select uid, title, content
        from templates
        order by title collate nocase;
      """
    )
    templates = cursor.fetchall()

    cursor.execute(
      """
        select tt.tmplt_uid, ta.tag
        from templateTags tt
        inner join tags ta on ta.uid = tt.tag_uid;
      """
    )
    tags_by_template: dict[int, list[str]] = {}
    for tmplt_uid, tag in cursor:
      tags_by_template.setdefault(tmplt_uid, []).append(tag)

    result: list[tuple[str, str, str]] = []
    for uid, title, content in templates:
      tags = sorted(tags_by_template.get(uid, []))
      result.append((title, content, ','.join(tags)))

    return result

  def FetchMetadataForTemplate(self, tmplt: emClasses.EmailTemplate) -> emClasses.EmailTemplate:
    """Get all metadata tags associated with template."""
    # Template passed must have a rowID in order to know get tags from the DB.
    if tmplt.rowID is None:
      raise AccessNullRowID()

    # Run query to get tags associated with the given template.
    cursor = self.DB.cursor()
    cursor.execute(
      """
        select tgRowID, tag
        from vw_Templates_Tags
        where tmpRowID = ?;
      """,
      [tmplt.rowID],
    )

    # Build objects for the tags and append them to the template object.
    tmplt.metadata = []
    for row in cursor:
      wkTag = emClasses.MetadataTag(row[1])
      wkTag.rowID = row[0]
      wkTag.assocRowID = tmplt.rowID
      wkTag.state = State.EXISTING
      tmplt.metadata.append(wkTag)

    return tmplt

  def FetchTemplatesForTag(self, srchTag: str) -> list[emClasses.EmailTemplate]:
    """Return all templates from the DB for a given meta tag."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        Select title, content, tmpRowID
        from vw_Templates_Tags
        where tag = ?;
      """,
      [srchTag],
    )

    # Build the template objects from the query results.
    tmplts = []
    for row in cursor:
      tmplt = emClasses.EmailTemplate(row[0], row[1])
      tmplt.rowID = row[2]
      tmplt.state = State.EXISTING
      tmplts.append(tmplt)

    return tmplts

  def FetchAllMetadataTags(self) -> list[emClasses.MetadataTag]:
    """Return all metadata tags associated with template."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        select tag, uid
        from tags;
      """
    )

    # Build the meta data tag objects to be passed back out.
    tags = []
    for row in cursor:
      tag = emClasses.MetadataTag(row[0])
      tag.rowID = row[1]
      tag.state = State.EXISTING
      tags.append(tag)

    return tags

  def AddTemplate(self, template: emClasses.EmailTemplate) -> None:
    """Add template to the database from the template object."""
    with self.DB:
      cursor = self.DB.cursor()
      cursor.execute(
        """
          insert into templates (title, content)
          values (?, ?);
        """,
        [template.title, template.content],
      )

      template.rowID = cursor.lastrowid
      self._SyncTemplateTagsForRowID(template.rowID, template.metadata, cursor)
      template.state = State.EXISTING

  def DeleteTemplate(self, template: emClasses.EmailTemplate) -> None:
    """Look for and delete the specified template from the database."""
    templateRowID = self._ResolveTemplateRowID(template)

    with self.DB:
      cursor = self.DB.cursor()
      # Remove all of the tags associated to this specific template.
      cursor.execute(
        """
          delete from templateTags
          where tmplt_uid = ?;
        """,
        [templateRowID],
      )

      # Remove the specific template from the database.
      cursor.execute(
        """
          delete from templates
          where uid = ?;
        """,
        [templateRowID],
      )

      # Clean up the tags table in case this was the only template utilizing the given tag.
      self.RemoveEmptyTags(cursor)

    return

  def UpdateTemplate(self, template: emClasses.EmailTemplate) -> None:
    """Update the template passed in the database. This will update all fields."""
    templateRowID = self._ResolveTemplateRowID(template)

    with self.DB:
      cursor = self.DB.cursor()
      cursor.execute(
        """
          update templates
          set title = ?, content = ?
          where uid = ?;
        """,
        [template.title, template.content, templateRowID],
      )

      self._SyncTemplateTagsForRowID(templateRowID, template.metadata, cursor)
      template.rowID = templateRowID
      template.state = State.EXISTING

  def UpsertTemplateByTitle(self, template: emClasses.EmailTemplate) -> None:
    """Add or update template and metadata by title."""
    row = self._FetchTemplateRowByTitle(template.title)

    if row is None:
      self.AddTemplate(template)
      return

    template.rowID = row[0]
    self.UpdateTemplate(template)

  def RemoveEmptyTags(self, cursor: sqlite3.Cursor | None = None) -> None:
    """Remove any tags that have no associated templates with them."""
    if cursor is None:
      cursor = self.DB.cursor()

    cursor.execute(
      """
        delete from tags
        where uid not in
          (select distinct tag_uid from templateTags);
      """
    )

    if self.DB.in_transaction:
      return
    self.DB.commit()

    return

  def _ResolveTemplateRowID(self, template: emClasses.EmailTemplate) -> int:
    """Return row ID from template object or by title."""
    if template.rowID:
      return template.rowID

    row = self._FetchTemplateRowByTitle(template.title)
    if row is None:
      raise AccessNullRowID()

    template.rowID = row[0]

    return template.rowID

  def _NormalizeTagList(self, tags: list[emClasses.MetadataTag | str] | None) -> list[str]:
    """Normalize tags to trimmed lower-case unique list preserving order."""
    if tags is None:
      return []

    normalized: list[str] = []
    for tag in tags:
      tagValue = tag.tag if isinstance(tag, emClasses.MetadataTag) else str(tag)
      cleanedTag = tagValue.strip().lower()

      if not cleanedTag:
        continue

      if cleanedTag not in normalized:
        normalized.append(cleanedTag)

    return normalized

  def _FetchTemplateRowByTitle(self, title: str) -> tuple[int, str, str] | None:
    """Fetch template row by title."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        select uid, title, content
        from templates
        where title = ?;
      """,
      [title],
    )

    row = cursor.fetchone()

    return row

  def _GetOrCreateTagRowID(self, tag: str, cursor: sqlite3.Cursor) -> int:
    """Fetch existing tag row ID or create a new row."""
    cursor.execute(
      """
        select uid
        from tags
        where tag = ?;
      """,
      [tag],
    )
    row = cursor.fetchone()

    if row:
      return row[0]

    cursor.execute(
      """
        insert into tags (tag)
        values (?);
      """,
      [tag],
    )

    return cursor.lastrowid

  def _SyncTemplateTagsForRowID(
    self,
    templateRowID: int,
    templateTags: list[emClasses.MetadataTag | str] | None,
    cursor: sqlite3.Cursor,
  ) -> None:
    """Sync template tag links to exactly match the provided tag list."""
    desiredTags = self._NormalizeTagList(templateTags)

    cursor.execute(
      """
        select tg.uid, tg.tag
        from tags tg
        inner join templateTags tmtg on tmtg.tag_uid = tg.uid
        where tmtg.tmplt_uid = ?;
      """,
      [templateRowID],
    )

    existing = cursor.fetchall()
    existingTags = {row[1]: row[0] for row in existing}

    desiredTagSet = set(desiredTags)
    existingTagSet = set(existingTags.keys())

    for tag in desiredTagSet - existingTagSet:
      tagRowID = self._GetOrCreateTagRowID(tag, cursor)
      cursor.execute(
        """
          insert into templateTags (tmplt_uid, tag_uid)
          values (?, ?);
        """,
        [templateRowID, tagRowID],
      )

    for tag in existingTagSet - desiredTagSet:
      cursor.execute(
        """
          delete from templateTags
          where tmplt_uid = ? and tag_uid = ?;
        """,
        [templateRowID, existingTags[tag]],
      )

    self.RemoveEmptyTags(cursor)
