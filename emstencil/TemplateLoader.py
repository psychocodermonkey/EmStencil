#! /usr/bin/env python3
"""
 Program: Populate templates from the DB for the main window and handle rebuilding that interface.
    Name: Andrew Dixon            File: TemplateLoader.py
    Date: 27 Nov 2025
   Notes:

       Copyright (C) 2023-2025  Andrew Dixon

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

from emstencil import Database as emDB
from emstencil import Dataclasses as emClasses
from .SelectionForm import TemplateSelector
from .Logging import LOGGER


def loadTemplateSelector(parent=None) -> TemplateSelector:
  db = emDB.TemplateDB()
  templateList = db.FetchAllTemplates()
  templateList = list(map(db.FetchMetadataForTemplate, templateList))
  LOGGER.info(f"Loaded {len(templateList)} templates from database.")

  metaTags = [emClasses.MetadataTag('all')]
  metaTags[0].rowID = 0
  metaTags[0].assocRowID = 0
  metaTags = metaTags + db.FetchAllMetadataTags()
  LOGGER.info(f"Loaded {len(metaTags) - 1} metadata tags.")

  if not templateList:
    LOGGER.info("No templates in databse, loading empty lists...")
    tag = emClasses.MetadataTag('None')
    template = emClasses.EmailTemplate('--Empty List--', 'No templates loaded', [tag])
    templateList.append(template)

  LOGGER.info("Loading template selector form.")
  return TemplateSelector(templateList, metaTags, parent=parent)
