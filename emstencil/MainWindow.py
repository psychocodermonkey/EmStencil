#! /usr/bin/env python3
'''
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
'''
# TODO: Imeplement this as the main form so we can add a menu bar for managing the DB.
# TODO: Write this to launch other windows etc for C.R.U.D.

from PyQt6.QtWidgets import QMainWindow
# from PyQt6.QtGui import QKeySequence, QShortcut
from emstencil import SelectionForm as selForm


class EmStencil(QMainWindow):
  def __init__(self, templateList: list, metaTags: list) -> None:
    super(EmStencil, self).__init__()

    # Create instance of application widget and add to main window.
    self.selectionForm = selForm.TemplateSelector(self, templateList, metaTags)
    # self.selectionForm.setParent(self)

    self.setCentralWidget(self.selectionForm)

    # self.exitShortcut = QShortcut(QKeySequence('Esc'), self)
    # self.exitShortcut.activated.connect(self.closeWindow)

  def closeWindow(self) -> None:
    """Close the window."""
    self.close()