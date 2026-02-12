"""
 Program: Main window for application.
    Name: Andrew Dixon            File: MainWindow.py
    Date: 28 Nov 2023
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

# TODO: Write this to launch other windows etc for C.R.U.D.
# TODO: Add menu bar to form.
# TODO: Menu bar should contain:
#         File> Open | Save | Import | Exit Edit>
#         Edit> Template?
#         Help> Instructions | About

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenu, QMessageBox
from .ImportTemplates import importTemplates
from .TemplateLoader import loadTemplateSelector
from .Logging import LOGGER
from .LogViewer import LogViewer


class EmStencil(QMainWindow):
  """Class for main window for selecting and working with templates."""
  def __init__(self) -> None:
    super(EmStencil, self).__init__()

    # Set window title
    self.setWindowTitle("EmStencil")

    # Set up the menu bar and make sure it is attached to the window.
    self.menubar = self.menuBar()
    self.menubar.setNativeMenuBar(False)

    # Define the file menu actions and add them to the file menu on the main menubar.
    menuFile = QMenu('File', self)

    # Import template menu item
    fileImport = QAction('Import Template...', self)
    fileImport.triggered.connect(self.importTemplate)
    menuFile.addAction(fileImport)

    # Exit application menu item.
    fileExit = QAction('Exit', self)
    fileExit.triggered.connect(self.closeWindow)
    menuFile.addAction(fileExit)

    self.menubar.addMenu(menuFile)

    # Define the help menu actions and add it to the menu bar.
    menuHelp = QMenu('Help', self)

    logViewer = QAction('Runtime logs', self)
    logViewer.triggered.connect(self.showRunlog)
    menuHelp.addAction(logViewer)

    aboutApp = QAction('About', self)
    aboutApp.triggered.connect(self.showAbout)
    menuHelp.addAction(aboutApp)

    self.menubar.addMenu(menuHelp)

    # Create instance of application widget and add to main window.
    # selectionForm = TemplateSelector(templateList, metaTags, parent=self)
    self.setCentralWidget(loadTemplateSelector(self))
    LOGGER.info("MainWindow initialized successfully.")

  def importTemplate(self) -> None:
    if importTemplates(self):
      # Remove old widget
      old_widget = self.takeCentralWidget()
      if old_widget:
        old_widget.deleteLater()
        LOGGER.info("Releasing old central widget.")

      self.setCentralWidget(loadTemplateSelector(self))
      LOGGER.info("New template selector loaded successfully.")

  def showRunlog(self) -> None:
    """
    Open and display runtime logs to the user.
    """
    from emstencil import LOG_PATH
    LOGGER.info("Showing runtime logs.")
    logviewer = LogViewer(LOG_PATH, self)
    logviewer.exec()

  def showAbout(self) -> None:
    """
    Show about window.
    """
    LOGGER.info("Showing about window.")
    userMessage = QMessageBox()
    userMessage.setIcon(QMessageBox.Icon.Information)
    userMessage.setWindowTitle('About EmStencil')
    userMessage.setText(
    """
    EmStencil - Email Stencils
    Version: 1.0.0
    Copyright (C) 2023 - 2025
    PsychoCoderMonkey: Andrew Dixon
    """
    )
    userMessage.exec()

  def closeWindow(self) -> None:
    """Close the window."""
    # TODO: Figure out why this is not visible in parent/child relationship with widget.
    self.close()
