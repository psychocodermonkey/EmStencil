#! /usr/bin/env python3
"""
 Program: Using SQLite to fetch items from the DB and load them into their respective objects
    Name: Andrew Dixon            File: TemplateEmailBuilder.py
    Date: 23 Nov 2023
   Notes:

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

# TODO: Implement update of templates instead of relying on reconverting from spreadsheet.
# TODO: Need to handle if/when a meta tag exists in the database list but is not attached to any templates.

import sys
import atexit
import ctypes
import platform
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from emstencil import Database as emDB
from emstencil import MainWindow as emMain
from emstencil import LOGGER


def main() -> None:
  """Main function for program start."""

  # Handle finding the application icon correctly from packaged or source layouts.
  if getattr(sys, 'frozen', False):
      base_path = Path(sys.argv[0]).parent  # location of compiled app
  else:
      base_path = Path(__file__).parent     # normal source layout

  # Detect platform and set the application icon appropriately.
  if platform.system() == "Darwin":
    icon_path = base_path / 'assets' / 'EmStencil_Dark.icns'
    LOGGER.info(f"Using macOS icon: {icon_path}")

  elif platform.system() == "Windows":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('EmStencil.App')
    icon_path = base_path / 'assets' / 'EmStencil_Dark.ico'
    LOGGER.info(f"Using Windows icon: {icon_path}")

  else:
    icon_path = base_path / "assets" / "EmStencil_Dark.ico"
    LOGGER.info(f"Using generic icon: {icon_path}")

  # icon_path = Path(__file__).parent / "assets" / "EmStencil_Dark.ico"

  # Build the app object, populate the screen and show the main window.
  app = QApplication(sys.argv)
  app.setWindowIcon(QIcon(str(icon_path)))
  screen = emMain.EmStencil()
  LOGGER.info("Showing main window...")
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
    LOGGER.error(f'ERROR on exit: {e}')
  return


# If the EmStencil.py is run (instead of imported as a module),
# call the main() function:
if __name__ == '__main__':

  from emstencil import is_initilized

  # Register the function to execute on ending the script
  atexit.register(onExit)

  if is_initilized():
    LOGGER.info('Launching application...')
    main()
  else:
    LOGGER.error("Initialization failed. Please check the logs.")
