#! /usr/bin/env python3
"""
 Program: Find and select a file to be paseed elsewhere.
    Name: Andrew Dixon            File:   SelectFile.py
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

from PySide6.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QHBoxLayout
from PySide6.QtWidgets import QPushButton, QLabel, QLineEdit


class FileSelectionDialog(QDialog):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle('Select a File')
    self.selected_file = None

    # Calculate a "good" side for minimum data entry lines.
    fontPointSize = QLabel().font().pointSize()
    minLengthForData = 35 * fontPointSize + 20

    # Widgets
    self.label = QLabel('Choose a file to import:')
    self.path_display = QLineEdit()
    self.path_display.setFixedWidth(minLengthForData)    # Enforce a good size for the path.
    self.path_display.setReadOnly(True)

    self.btn_browse = QPushButton('Browse...')
    self.btn_ok = QPushButton('OK')
    self.btn_cancel = QPushButton('Cancel')

    # Layout
    path_layout = QHBoxLayout()
    path_layout.addWidget(self.path_display)
    path_layout.addWidget(self.btn_browse)

    button_layout = QHBoxLayout()
    button_layout.addStretch()
    button_layout.addWidget(self.btn_ok)
    button_layout.addWidget(self.btn_cancel)

    main_layout = QVBoxLayout()
    main_layout.addWidget(self.label)
    main_layout.addLayout(path_layout)
    main_layout.addLayout(button_layout)

    self.setLayout(main_layout)

    # Connections
    self.btn_browse.clicked.connect(self.openFileDialog)
    self.btn_ok.clicked.connect(self.accept)
    self.btn_cancel.clicked.connect(self.reject)

  def openFileDialog(self) -> None:
    file_name, _ = QFileDialog.getOpenFileName(
      self, 'Select Template File', '', 'All Files (*);;Excel Files (*.xlsx)'
    )
    if file_name:
      self.selected_file = file_name
      self.path_display.setText(file_name)

  def accept(self) -> None:
    if self.selected_file:
      super().accept()
    else:
      # Optional: disable silently, or tell user to pick a file
      self.label.setText('Select a file before pressing OK!')
