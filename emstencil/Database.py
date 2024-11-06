#! /usr/bin/env python3
"""
 Program: Database singleton class for database management.
    Name: Andrew Dixon            File: TemplateDB.py
    Date: 23 Nov 2023
   Notes:

    Copyright (C) 2023  Andrew Dixon

    This program is free software: you can redistribute it and/or modify  it under the terms of the GNU
    General Public License as published by the Free Software Foundation, either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
    the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See theGNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <https://www.gnu.org/licenses/>.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""
# TODO: Implement update, insert methods for the database.

import sqlite3
from emstencil import Dataclasses as emClasses
from .Ubiquitous import DATABASE_FILE
from .Dataclasses import State


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
    self.DB.execute("pragma foreign_keys = ON")

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

  def FetchMetadataForTemplate(self, tmplt: emClasses.EmailTemplate) -> emClasses.EmailTemplate:
    """Get all metadata tags associated with template."""
    # Template passed must have a rowID in order to know get tags from the DB.
    if tmplt.rowID is None:
      raise emClasses.AccessNullRowID()

    # Run query to get tags associated with the given template.
    cursor = self.DB.cursor()
    cursor.execute(
      """
        select tgRowID, tag
        from vw_Templates_Tags
        where tmpRowID = ?;
      """,
      [tmplt.rowID]
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
      [srchTag]
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
    # TODO: Implement AddTemplate
    pass

  def DeleteTemplate(self, template: emClasses.EmailTemplate) -> None:
    """Look for and delete the specified template from the database."""
    # TODO: Implement Delete Template
    cursor = self.DB.cursor()

    # Remove all of the tags associated to this specific template.
    cursor.execute(
      """
        delete from templateTags
        where tmplt_uid = ?;
      """,
      [template.rowID]
    )

    # Remove the specific template from the database.
    cursor.execute(
      """
        delete from templates
        where uid = ?;
      """,
      [template.rowID]
    )

    # Clean up the tags table in case this was the only template utilizing the given tag.
    self.RemoveEmptyTags()

    return

  def UpdateTemplate(self, template: emClasses.EmailTemplate) -> None:
    """Update the template passed in the database. This will update all fields."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        update templates
        set title = ?, content = ?
        where uid = ?
      """,
      [template.title, template.content, template.rowID]
    )

    # TODO: Need to implement handing ADD / DELETE associated tags.

  def RemoveEmptyTags(self) -> None:
    """Remove any tags that have no associated templates with them."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        delete from tags
        where uid not in
          (select distinct tag_uid from templateTags);
      """
    )

    return
