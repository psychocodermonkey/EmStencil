#! /usr/bin/env python3
'''
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
'''
# TODO: Implement update, insert methods for the database.

import sqlite3
from emstencil import Dataclasses as emClasses


class TemplateDB:
  """Data layer class for handling translation of data to and from the database."""
  _instance = None

  def __new__(cls, *args, **kwargs):
    """Generate new instance if one doesn't exist, return the existing one if it does."""
    if not cls._instance:
      cls._instance = super().__new__(cls, *args, **kwargs)
    return cls._instance

  def __init__(self):
    """New instance of database connection."""
    self.DB = sqlite3.connect('data/templates.db')

  def getConnection(self) -> sqlite3.connect:
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

    tmplts = []
    for row in cursor:
      tmplt = emClasses.EmailTemplate(row[0], row[1])
      tmplt.rowID = row[2]
      tmplts.append(tmplt)

    return tmplts


  def FetchMetadataForTemplate(self, tmplt: emClasses.EmailTemplate) -> emClasses.EmailTemplate:
    """Get all metadata tags associated with template."""
    if tmplt.rowID is None:
      raise emClasses.AccessNullRowID()

    cursor = self.DB.cursor()
    cursor.execute(
      """
        select tgRowID, tag
        from vw_Templates_Tags
        where tmpRowID = ?;
      """,
      [tmplt.rowID]
    )

    tmplt.metadata = []
    for row in cursor:
      wkTag = emClasses.MetadataTag(row[1])
      wkTag.rowID = row[0]
      wkTag.assocRowID = tmplt.rowID
      tmplt.metadata.append(wkTag)

    return tmplt


  def FetchTemplatesForTag(self, srchTag: str) -> list[emClasses.EmailTemplate]:
    """Return all templates from the DB."""
    cursor = self.DB.cursor()
    cursor.execute(
      """
        Select title, content, tmpRowID
        from vw_Templates_Tags
        where tag = ?;
      """,
      [srchTag]
    )

    tmplts = []
    for row in cursor:
      tmplt = emClasses.EmailTemplate(row[0], row[1])
      tmplt.rowID = row[2]
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

    tags = []
    for row in cursor:
      tag = emClasses.MetadataTag(row[0])
      tag.rowID = row[1]
      tags.append(tag)

    return tags

  def AddTemplate(self, template: emClasses.EmailTemplate) -> None:
    """Add template to the database from the template object."""
    #TODO: Implement AddTemplate
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
    # TODO: Implement Update Template
    pass

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