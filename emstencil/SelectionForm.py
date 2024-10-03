#! /usr/bin/env python3
"""
 Program: Using SQLite to fetch items from the DB and load them into their respective objects
    Name: Andrew Dixon            File: TemplateSelectorWindow.py
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

import logging
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QComboBox
from .Database import TemplateDB
from .FieldEntryDialog import FieldEntryDialog
from .Dataclasses import EmailTemplate, MetadataTag


class TemplateSelector(QWidget):
  """Class for main window for selecting and working with templates."""
  def __init__(self, templateList: list, metaTags: list, parent=None) -> None:
    super(TemplateSelector, self).__init__()
    # Work fields and local variables for the main application.
    fontPointSize = QLabel().font().pointSize()
    self.templateList = templateList
    self.metaTags = metaTags
    self.clipboard = QApplication.clipboard()
    self.db = TemplateDB()
    self.parent = parent

    # Set basics for main application window.
    self.setWindowTitle('EmStencil - Templated email builder')
    self.layout = QVBoxLayout()
    self.setLayout(self.layout)

    # Set up functionality for keyboard interaction.
    self.refreshShortcut = QShortcut(QKeySequence('F5'), self)
    self.refreshShortcut.activated.connect(self.resetTemplates)
    self.copyTemplateText = QShortcut(QKeySequence('Ctrl+C'), self)
    self.copyTemplateText.activated.connect(self.copyCLicked)
    self.selectShortcut = QShortcut(QKeySequence('Return'), self)
    self.selectShortcut.activated.connect(self.selectClicked)

    # Add the template filter list boxes to the form.
    self.templateSelectionGroup = self.buildTemplateSelectGroup()

    # Add the text edit area to the main form
    self.textArea = QTextEdit()
    self.textArea.setMinimumHeight(self.textArea.fontMetrics().height() * 15)
    self.textArea.setMinimumWidth(fontPointSize * 55)
    self.textArea.setReadOnly(True)
    self.textArea.setText(self.templateComboBox.currentData().content)
    self.layout.addWidget(self.textArea)

    # Add buttons to the main layout
    self.layout.addLayout(self.buildButtons())

  def buildTemplateSelectGroup(self) -> None:
    """Build the boxes to filter out and select what template to work with."""
    fontPointSize = QLabel().font().pointSize()
    self.templateSelectionGroup = QHBoxLayout()

    # Build layouts to be nexted in this group to allow differing alignment.
    comboBoxGroup = QHBoxLayout()
    comboBoxGroup.setAlignment(Qt.AlignmentFlag.AlignLeft)
    comboBoxAreaButtons = QHBoxLayout()
    comboBoxAreaButtons.setAlignment(Qt.AlignmentFlag.AlignRight)

    # Build the template list combo box and add it to the combo box group.
    self.templateComboBox = self.buildComboBoxData(self.templateList)
    self.templateComboBox.activated.connect(self.templateComboBoxSelected)
    comboBoxGroup.addWidget(self.templateComboBox)

    # Build the meta tag list combo box and add it to the combo box group.
    self.metaTagComboBox = self.buildComboBoxData(self.metaTags)
    self.metaTagComboBox.activated.connect(self.metaTagComboBoxSelected)
    comboBoxGroup.addWidget(self.metaTagComboBox)

    # Add the combo box group to the layout group for this section of the form.
    comboBoxGroup.setAlignment(Qt.AlignmentFlag.AlignLeft)
    self.templateSelectionGroup.addLayout(comboBoxGroup)

    # Add the refresh button to it's won layout so it can be right aligned on the form.
    refreshButton = QPushButton('Reset')
    refreshButton.setMaximumWidth(fontPointSize * 8 + 10)
    refreshButton.clicked.connect(self.resetTemplates)
    comboBoxAreaButtons.addWidget(refreshButton)
    self.templateSelectionGroup.addLayout(comboBoxAreaButtons)

    # Add the template selection group to the main layout.
    self.layout.addLayout(self.templateSelectionGroup)

  def buildComboBoxData(self, items: list) -> QComboBox:
    """Build a combo box widget from a list of EmailTemplate/MetadataTag objects."""
    comboBox = QComboBox()

    # Get what the default font and size is so we can use it to calculate string length.
    fontMetrics = QFontMetrics(comboBox.font())
    minWidth = 0

    for item in items:
      stringWidth = fontMetrics.horizontalAdvance(str(item) + ' ' * 3)
      if stringWidth > minWidth:
        minWidth = stringWidth
      comboBox.addItem(str(item), item)
    comboBox.setFixedWidth(int(minWidth * 1.5))

    return comboBox

  def buildButtons(self) -> QHBoxLayout:
    """Build the button layout to be added to the form."""
    # Calculate what the minimum width needs to be in pixels for all 3 buttons.
    fontPointSize = QLabel().font().pointSize()
    minWidth = (fontPointSize * 6) + 20

    # Initilize the layout for the buttons.
    buttonLayout = QHBoxLayout()
    buttonLayout.setAlignment(Qt.AlignmentFlag.AlignRight)

    # Define the select button and add it to the button layout.
    selectButton = QPushButton("Select")
    selectButton.setMinimumWidth(minWidth)
    selectButton.setMaximumWidth(minWidth * 2)
    selectButton.setDefault(True)  # Setting this even thougn it doesn't work outside of a dialog
    selectButton.clicked.connect(self.selectClicked)
    buttonLayout.addWidget(selectButton)

    copyButton = QPushButton("Copy")
    copyButton.setMinimumWidth(minWidth)
    copyButton.setMaximumWidth(minWidth * 2)
    copyButton.clicked.connect(self.copyCLicked)
    buttonLayout.addWidget(copyButton)

    exitButton = QPushButton("Exit")
    exitButton.setMinimumWidth(minWidth)
    exitButton.setMaximumWidth(minWidth * 2)
    exitButton.clicked.connect(self.exitClicked)
    self.exitShortcut = QShortcut(QKeySequence('Esc'), self)
    self.exitShortcut.activated.connect(self.exitClicked)
    buttonLayout.addWidget(exitButton)

    return buttonLayout

  def templateComboBoxSelected(self) -> None:
    """Handling the UI update from the template combo box selection changing."""
    selectedEmailTemplate = self.templateComboBox.currentData()
    self.textArea.setText(selectedEmailTemplate.content)
    self.repaint()

  def metaTagComboBoxSelected(self) -> None:
    """Handling the UI update from the metatag combo box selection changing."""
    selectedMetadataTag = self.metaTagComboBox.currentData()
    # Since "all" doesn't exist in the DB, check if the "all" we added by hand is selected.
    if selectedMetadataTag == MetadataTag('all'):
      self.templateList = self.db.FetchAllTemplates()

    # Otherwise filter based on the selected tag
    else:
      self.templateList = self.db.FetchTemplatesForTag(str(selectedMetadataTag))

    # Clear the combo box and rebuild it with what we grabbed.
    self.templateComboBox.clear()
    for tmplt in self.templateList:
      self.templateComboBox.addItem(str(tmplt), tmplt)
    self.textArea.setText(self.templateComboBox.currentData().content)
    self.repaint()

  def sendUserInfoMessage(self, msg: str) -> None:
    """Send informaiotnal messege to the user."""
    userMessage = QMessageBox()
    userMessage.setIcon(QMessageBox.Icon.Information)
    userMessage.setWindowTitle("Information")
    userMessage.setText(msg)
    userMessage.exec()

  def sendUserErrorMessage(self, msg: str) -> None:
    """Send error emssage to the user."""
    userMessage = QMessageBox()
    userMessage.setIcon(QMessageBox.Icon.Critical)
    userMessage.setWindowTitle("Error")
    userMessage.setText(msg)
    userMessage.exec()

  def resetTemplates(self) -> None:
    """Reset all templates to default form."""
    savedIndex = self.templateComboBox.currentIndex()
    self.templateComboBox.clear()
    for tmplt in self.templateList:
      tmplt.clearFields
      self.templateComboBox.addItem(str(tmplt), tmplt)
    self.templateComboBox.setCurrentIndex(savedIndex)
    self.textArea.setText(self.templateComboBox.currentData().content)
    self.repaint()

  def selectClicked(self) -> None:
    """Process the current selection, show the update window for the fields."""
    selectedEmailTemplate = self.templateComboBox.currentData()
    if len(selectedEmailTemplate.fields) > 0:
      self.editScreen = FieldEntryDialog(selectedEmailTemplate, parent=self)
      self.editScreen.show()
    else:
      self.sendUserInfoMessage("Template has no fields defined.")

  def updateTextArea(self, tmplt: EmailTemplate) -> None:
    """Upate the text area with the template"""
    if tmplt.fieldsSet:
      self.textArea.setText(tmplt.replacedText)
    else:
      self.textArea.setText(tmplt.content)

    self.repaint()

  def copyCLicked(self) -> None:
    """Copy the text for the selected email template to the clipboard."""
    selectedEmailTemplate = self.templateComboBox.currentData()
    if selectedEmailTemplate.fieldsSet:
      self.clipboard.setText(selectedEmailTemplate.replacedText)
    else:
      self.sendUserInfoMessage("You must enter values for all fields in the template.")

  def exitClicked(self) -> None:
    """Close the form/application by triggering close from the parent."""
    logging.info('Application close.')
    self.parent.closeWindow()
