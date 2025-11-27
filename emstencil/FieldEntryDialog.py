"""
 Program: Form for editing the fields for the given Email template
    Name: Andrew Dixon            File: FieldEntryDialog.py
    Date: 23 Nov 2023
   Notes: This form builds the screen based on the keys and values in a dictionary.

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

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout
from .Dataclasses import EmailTemplate
from .Exceptions import TemplateKeyValueNull


class FieldEntryDialog(QDialog):
  """Build dialog to get data for the fields in the field dictionary."""
  def __init__(self, template: EmailTemplate, parent=None):
    super().__init__()
    self.setWindowTitle('Fields available for template')
    self.parent = parent
    self.template = template
    self.dictionary = self.template.fields
    self.layout = QVBoxLayout()
    self.setLayout(self.layout)

    # Calculate what the largest label we need to scale everything accordingly.
    # Use a clamping function to keep text box and label sizes reasonable.
    def clamp(n, minn, maxn):
      return max(min(maxn, n), minn)

    fontPointSize = QLabel().font().pointSize()
    minLengthForKeys = (clamp(len(max(self.dictionary)), 5, 50) * fontPointSize) + 20
    minLengthForData = (clamp(len(max(self.dictionary)), 15, 120) * fontPointSize) + 20

    # Build the dialog on the fly for the keys in the database.
    for key, value in self.dictionary.items():
      # Create a local layout to add to the form.
      fieldGroup = QHBoxLayout()
      # Put field text in a label for prompting the user and set it's size.
      label = QLabel(key)
      label.setFixedWidth(minLengthForKeys)

      # Build line edit, set it's size to our scale, bring in text if it is present.
      txtInputFld = QLineEdit()
      txtInputFld.setFixedWidth(minLengthForData)
      if value:
        txtInputFld.setText(value)
      else:
        txtInputFld.setText('')

      # Group the label and the field together.
      fieldGroup.addWidget(label)
      fieldGroup.addWidget(txtInputFld)

      # Add the label and field group to the form.
      self.layout.addLayout(fieldGroup)

    # Connect tthe accept/submit button for the dialog form.
    button = QPushButton("Submit")
    button.setDefault(True)
    button.clicked.connect(self.submit)
    button.clicked.connect(self.close)
    self.layout.addWidget(button)

  def submit(self) -> None:
    """Submit button for form, gather information and pass it back to the main form."""
    # Get the data from the text boxes on the form.
    inputFields = self.findChildren(QLineEdit)

    # Plug the data back into to the dictionary on the form to be passed back.
    for i, value in enumerate(inputFields):
      self.dictionary[list(self.dictionary.keys())[i]] = value.text()

    try:
      self.template.setFields(self.dictionary)
      self.parent.updateTextArea(self.template)
    except TemplateKeyValueNull:
      self.parent.updateTextArea(self.template)

    return
