#! /usr/bin/env python3
"""
 Program: Using SQLite to fetch items from the DB and load them into their respective objects
    Name: Andrew Dixon            File: TemplateEmailBuilder.py
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
# TODO: Implement update of templates instead of relying on reconverting from spreadsheet.

import sys
import atexit
from PyQt6.QtWidgets import QApplication
from emstencil import Database as emDB
from emstencil import Dataclasses as emClasses
from emstencil import SelectionForm as emSelector

def main() -> None:
  """Main function for program start."""
  # Get all templates and populate all associated metadata with them.
  db = emDB.TemplateDB()
  TemplateList = db.FetchAllTemplates()
  TemplateList = list(map(db.FetchMetadataForTemplate, TemplateList))

  # Get full list of all tags that are present. Adding ALL to the list at rowID 0
  MetaTags = [emClasses.MetadataTag('all')]
  MetaTags[0].rowID = 0
  MetaTags[0].assocRowID = 0
  MetaTags = MetaTags + db.FetchAllMetadataTags()

  # print results for what we grabbed.
  template = TemplateList[0]
  app = QApplication(sys.argv)

  # Find the template with the most number of fields.
  for tmplt in TemplateList:
    if len(tmplt.fields) > len(template.fields):
      template = tmplt

  # Execute the screen to get the user data.
  # screen = mainWindow.EmStencil(TemplateList, MetaTags)
  screen = emSelector.TemplateSelector(TemplateList, MetaTags)
  screen.show()

  sys.exit(app.exec())


def onExit() -> None:
  """On exit clean up fuction."""
  try:
    # Close the database conneciton.
    db = emDB.TemplateDB()
    db.close()

  except Exception as e:
    # Exit, printing any error that happens on exit.
    print(f'ERROR on exit: {e}')
  return


# If the TemplateEmailBuilder.py is run (instead of imported as a module),
# call the main() function:
if __name__ == '__main__':
# Register the function to execute on ending the script
  atexit.register(onExit)
  main()