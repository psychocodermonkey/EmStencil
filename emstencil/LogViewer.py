#! /usr/bin/env python3
"""
 Program: Setup and present a unified debug/error logging object
    Name: Andrew Dixon            File: Logviewer.py
    Date: 30 Nov 2025
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
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
