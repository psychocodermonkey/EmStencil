#! /usr/bin/env python3
"""
 Program: Main window for application.
    Name: Andrew Dixon            File: MainWindow.py
    Date: 28 Nov 2023
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
# TODO: Write this to launch other windows etc for C.R.U.D.
# TODO: Add menu bar to form.
# TODO: Menu bar should contain:
#         File> Open | Save | Import | Exit Edit>
#         Edit> Template?
#         Help> Instructions | About

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QMenu
from .SelectionForm import TemplateSelector


class EmStencil(QMainWindow):
  def __init__(self, templateList: list, metaTags: list) -> None:
    super(EmStencil, self).__init__()

    # Set up the menu bar and make sure it is attached to the window.
    self.menubar = self.menuBar()
    self.menubar.setNativeMenuBar(False)

    # Define the file menu actions and add them to the file menu on the main menubar
    menu = QMenu('File', self)
    fileExit = QAction('Exit', self)
    fileExit.triggered.connect(self.closeWindow)
    menu.addAction(fileExit)
    self.menubar.addMenu(menu)

    # Create instance of application widget and add to main window.
    selectionForm = TemplateSelector(templateList, metaTags, parent=self)
    self.setCentralWidget(selectionForm)

  def closeWindow(self) -> None:
    """Close the window."""
    self.close()