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

from __future__ import annotations

from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from .Logging import LOGGER


class LogViewer(QDialog):
  def __init__(self, logPath: Path, parent=None):
    super().__init__(parent)
    self.setWindowTitle('Application Run Log')
    self.resize(900, 600)

    layout = QVBoxLayout(self)

    # QTextEdit for displaying log content (read-only)
    self.textArea = QTextEdit()
    self.textArea.setReadOnly(True)
    layout.addWidget(self.textArea)

    # Close button (optional)
    closeBtn = QPushButton('Close')
    closeBtn.clicked.connect(self.close)
    layout.addWidget(closeBtn)
    LOGGER.info('LogViewer init completed.')

    # Load the log file content
    try:
      with logPath.open('r', encoding='utf-8') as fp:
        self.textArea.setPlainText(fp.read())

    except FileNotFoundError:
      self.textArea.setPlainText('Log file not found.')

    except Exception as e:
      self.textArea.setPlainText(f'Error loading log file:\n{e}')
