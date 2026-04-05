"""
 Program: Dialog for creating, editing, and deleting templates.
    Name: Andrew Dixon            File: TemplateEditorDialog.py
    Date: 7 Mar 2026
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QTextEdit, QPushButton
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QMessageBox
from .content_html import is_html_content, rich_text_editor_html_should_persist_as_html
from .Database import TemplateDB
from .Dataclasses import EmailTemplate, MetadataTag


class TemplateEditorDialog(QDialog):
  """Dialog for creating, editing, and deleting templates."""

  def __init__(self, template: EmailTemplate | None = None, parent=None) -> None:
    super(TemplateEditorDialog, self).__init__(parent)
    self.db = TemplateDB()
    self.template = template
    self.isEditMode = template is not None
    self.hasUnsavedChanges = False
    self.loadingValues = False
    self._persistBodyAsHtml = False

    self.SetupUI()
    self.ConnectSignals()
    self.LoadValues()

  def SetupUI(self) -> None:
    """Build dialog controls."""
    self.setWindowTitle('Template Editor')
    self.setMinimumWidth(640)
    self.setMinimumHeight(420)

    layout = QVBoxLayout()
    self.setLayout(layout)

    titleLabel = QLabel('Title')
    self.titleField = QLineEdit()
    layout.addWidget(titleLabel)
    layout.addWidget(self.titleField)

    tagsLabel = QLabel('Tags')
    self.tagsField = QLineEdit()
    layout.addWidget(tagsLabel)
    layout.addWidget(self.tagsField)

    templateLabel = QLabel('Template')
    self.templateField = QTextEdit()
    # Rich paste (e.g. Word tables) requires acceptRichText even for new/plain-backed templates.
    self.templateField.setAcceptRichText(True)
    layout.addWidget(templateLabel)
    layout.addWidget(self.templateField)

    buttonLayout = QHBoxLayout()
    buttonLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
    layout.addLayout(buttonLayout)

    self.saveButton = QPushButton('Save')
    self.cancelButton = QPushButton('Cancel')
    self.deleteButton = QPushButton('Delete')

    buttonLayout.addWidget(self.saveButton)
    buttonLayout.addWidget(self.cancelButton)
    buttonLayout.addWidget(self.deleteButton)

    if not self.isEditMode:
      self.deleteButton.hide()

  def ConnectSignals(self) -> None:
    """Connect field and button event handlers."""
    self.titleField.textChanged.connect(self.FieldChanged)
    self.tagsField.textChanged.connect(self.FieldChanged)
    self.templateField.textChanged.connect(self.FieldChanged)

    self.saveButton.clicked.connect(self.SaveClicked)
    self.cancelButton.clicked.connect(self.CancelClicked)
    self.deleteButton.clicked.connect(self.DeleteClicked)
    self.saveShortcut = QShortcut(QKeySequence('Ctrl+S'), self)
    self.saveShortcut.activated.connect(self.SaveClicked)

  def LoadValues(self) -> None:
    """Load values into controls based on new/edit mode."""
    self.loadingValues = True

    if self.isEditMode and self.template is not None:
      self._persistBodyAsHtml = is_html_content(self.template.content)
      self.titleField.setText(self.template.title)
      if self._persistBodyAsHtml:
        self.templateField.setHtml(self.template.content)

      else:
        self.templateField.setPlainText(self.template.content)

      self.tagsField.setText(', '.join(tag.tag for tag in self.template.metadata))

    else:
      self._persistBodyAsHtml = False
      self.titleField.clear()
      self.tagsField.clear()
      self.templateField.clear()
    self.loadingValues = False
    self.hasUnsavedChanges = False

  def FieldChanged(self) -> None:
    """Track unsaved changes."""
    if self.loadingValues:
      return

    self.hasUnsavedChanges = True

  def BuildTemplateFromFields(self) -> EmailTemplate:
    """Create template object from dialog fields."""
    title = self.titleField.text()
    if self._persistBodyAsHtml:
      content = self.templateField.toHtml()

    else:
      html_snapshot = self.templateField.toHtml()
      content = (
        html_snapshot
        if rich_text_editor_html_should_persist_as_html(html_snapshot)
        else self.templateField.toPlainText()
      )
    tags = self.tagsField.text().split(',')
    metadata = [MetadataTag(tag) for tag in tags if tag != '']

    template = EmailTemplate(title, content)
    template.metadata = metadata

    if self.isEditMode and self.template is not None:
      template.rowID = self.template.rowID

    return template

  def SaveClicked(self) -> None:
    """Save template through the data layer."""
    template = self.BuildTemplateFromFields()
    if self.isEditMode:
      self.db.UpdateTemplate(template)

    else:
      self.db.AddTemplate(template)

    self.hasUnsavedChanges = False
    self.accept()

  def DeleteClicked(self) -> None:
    """Delete template after confirmation."""
    if not self.isEditMode or self.template is None:
      return

    userChoice = QMessageBox.question(
      self,
      'Confirm Delete',
      'Delete this template?',
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No,
    )

    if userChoice == QMessageBox.StandardButton.Yes:
      self.db.DeleteTemplate(self.template)
      self.hasUnsavedChanges = False
      self.accept()

  def CancelClicked(self) -> None:
    """Handle explicit cancel action."""
    self.reject()

  def ConfirmDiscardChanges(self) -> bool:
    """Ask user whether to discard unsaved changes."""
    if not self.hasUnsavedChanges:
      return True

    userChoice = QMessageBox.question(
      self,
      'Unsaved Changes',
      'Changes not saved. Discard changes?',
      QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
      QMessageBox.StandardButton.Cancel,
    )

    return userChoice == QMessageBox.StandardButton.Discard

  def reject(self) -> None:
    """Intercept cancel/escape close behavior."""
    if self.ConfirmDiscardChanges():
      super().reject()

  def closeEvent(self, event: QCloseEvent) -> None:
    """Intercept window close event for unsaved changes."""
    if self.ConfirmDiscardChanges():
      event.accept()

    else:
      event.ignore()
