#! /usr/bin/env python3
"""
 Program: Setup and present a unified debug/error logging object
    Name: Andrew Dixon            File: Logviewer.py
    Date: 30 Nov 2025
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

from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from .Logging import LOGGER
#from PySide6.QtCore import Qt


class LogViewer(QDialog):
  def __init__(self, log_path: Path, parent=None):
    super().__init__(parent)
    self.setWindowTitle('Application Run Log')
    self.resize(900, 600)

    layout = QVBoxLayout(self)

    # QTextEdit for displaying log content (read-only)
    self.text_area = QTextEdit()
    self.text_area.setReadOnly(True)
    layout.addWidget(self.text_area)

    # Close button (optional)
    close_btn = QPushButton('Close')
    close_btn.clicked.connect(self.close)
    layout.addWidget(close_btn)
    LOGGER.info("LogViewer init completed.")

    # Load the log file content
    try:
      with log_path.open('r', encoding='utf-8') as f:
        self.text_area.setPlainText(f.read())

    except FileNotFoundError:
      self.text_area.setPlainText('Log file not found.')

    except Exception as e:
      self.text_area.setPlainText(f'Error loading log file:\n{e}')
