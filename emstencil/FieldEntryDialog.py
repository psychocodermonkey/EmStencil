"""
 Program: Form for editing the fields for the given Email template
    Name: Andrew Dixon            File: FieldEntryDialog.py
    Date: 23 Nov 2023
   Notes: This form builds the screen based on the keys and values in a dictionary.

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

import base64
import binascii
from collections.abc import Callable

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import (
  QContextMenuEvent,
  QFontMetrics,
  QImage,
  QKeyEvent,
  QKeySequence,
  QPixmap,
)
from PySide6.QtWidgets import (
  QApplication,
  QDialog,
  QFrame,
  QHBoxLayout,
  QLabel,
  QLineEdit,
  QMenu,
  QPushButton,
  QVBoxLayout,
  QWidget,
)
from .Dataclasses import EmailTemplate
from .Exceptions import TemplateKeyValueNull


def qimageToPngDataURL(img: QImage) -> str:
  """PNG data URL for clipboard images; empty string if encoding fails."""
  if img.isNull():
    return ''

  blob = QByteArray()
  buf = QBuffer(blob)
  buf.open(QIODevice.OpenModeFlag.WriteOnly)

  if not img.save(buf, 'PNG'): # type: ignore
    return ''

  encoded = base64.b64encode(blob.data()).decode('ascii')

  return f'data:image/png;base64,{encoded}'


class ImagePasteLineEdit(QLineEdit):
  """Pastes images via callback (no giant data URL in the field); text paste stays on the line."""

  def __init__(
    self,
    parent: QWidget | None = None,
    *,
    onImagePasted: Callable[[str], None] | None = None,
  ) -> None:

    super().__init__(parent)
    self._onImagePasted = onImagePasted

  def keyPressEvent(self, event: QKeyEvent) -> None:
    if event.matches(QKeySequence.StandardKey.Paste):
      if self._pasteClipboardImage():
        event.accept()

        return

    super().keyPressEvent(event)

  def contextMenuEvent(self, event: QContextMenuEvent) -> None:
    menu = QMenu(self)
    menu.addAction('Cut', self.cut)
    menu.addAction('Copy', self.copy)
    menu.addAction('Paste', self._pasteAction)
    menu.addSeparator()
    menu.addAction('Select All', self.selectAll)
    menu.exec(event.globalPos()) #type: ignore

  def _pasteAction(self) -> None:
    if not self._pasteClipboardImage():
      self.paste()

  def _pasteClipboardImage(self) -> bool:
    cb = QApplication.clipboard()
    mime = cb.mimeData()
    if mime is None or not mime.hasImage():
      return False

    img = cb.image()

    if img.isNull():
      pm = cb.pixmap()

      if pm is None or pm.isNull():
        return False

      img = pm.toImage()

    url = qimageToPngDataURL(img)

    if not url:
      return False

    if self._onImagePasted is not None:
      self._onImagePasted(url)
      return True

    self.setText(url)

    return True


def _pixmapFromDataURL(url: str) -> QPixmap | None:
  """Decode data:image/* URL to a pixmap, or None."""
  u = url.strip()

  if not u.startswith('data:image/'):
    return None

  try:
    comma = u.index(',')
    raw = base64.b64decode(u[comma + 1 :])

  except (ValueError, binascii.Error):
    return None

  img = QImage.fromData(raw)

  if img.isNull():
    return None

  return QPixmap.fromImage(img).scaled(
    72,
    72,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation,
  )


class ImageFieldRow(QWidget):
  """Thumbnail + line edit; pasted image kept off-widget so the field does not show base64."""

  def __init__(self, minLineWidth: int, initial: str, parent: QWidget | None = None) -> None:
    super().__init__(parent)
    self._pastedDataURL: str | None = None
    self._thumb = QLabel()
    self._thumb.setFixedSize(72, 72)
    self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self._thumb.setFrameShape(QFrame.Shape.StyledPanel)
    self._line = ImagePasteLineEdit(self, onImagePasted=self._storePastedImage)
    self._line.setMinimumWidth(minLineWidth)

    if initial.strip().startswith('data:image/'):
      self._pastedDataURL = initial

    elif initial:
      self._line.setText(initial)

    self._updatePlaceholder()
    self._line.textChanged.connect(self._onLineTextChanged)
    self._syncThumb()
    row = QHBoxLayout(self)
    row.setContentsMargins(0, 0, 0, 0)
    row.addWidget(self._thumb)
    row.addWidget(self._line, stretch=1)

  def fieldText(self) -> str:
    typed = self._line.text()

    if typed.strip():
      return typed

    return self._pastedDataURL or ''

  def _storePastedImage(self, url: str) -> None:
    self._pastedDataURL = url
    self._line.blockSignals(True)
    self._line.clear()
    self._line.blockSignals(False)
    self._updatePlaceholder()
    self._syncThumb()

  def _onLineTextChanged(self, text: str) -> None:
    if text.strip():
      self._pastedDataURL = None

    self._updatePlaceholder()
    self._syncThumb()

  def _updatePlaceholder(self) -> None:
    if self._pastedDataURL and not self._line.text().strip():
      self._line.setPlaceholderText('Type here to replace pasted image with URL or text')

    else:
      self._line.setPlaceholderText('Paste image (Ctrl+V) or type a URL / placeholder text')

  def _syncThumb(self) -> None:
    self._thumb.clear()
    typed = self._line.text().strip()

    if typed.startswith('data:image/'):
      pix = _pixmapFromDataURL(self._line.text())

      if pix is None:
        self._thumb.setText('?')

      else:
        self._thumb.setPixmap(pix)

      return

    if typed:
      return

    if self._pastedDataURL:
      pix = _pixmapFromDataURL(self._pastedDataURL)

      if pix is not None:
        self._thumb.setPixmap(pix)


class FieldEntryDialog(QDialog):
  """Build dialog to get data for the fields in the field dictionary."""

  def __init__(
    self,
    template: EmailTemplate,
    *,
    onTemplateApplied: Callable[[EmailTemplate], None],
    parent: QWidget | None = None,
  ) -> None:
    super().__init__(parent)
    self.setWindowTitle('Fields available for template')
    self._onTemplateApplied = onTemplateApplied
    self.template: EmailTemplate = template
    self.dictionary: dict[str, str | int | None] = self.template.fields
    self.layout: QVBoxLayout = QVBoxLayout()
    self.setLayout(self.layout)

    # Calculate what the largest label we need to scale everything accordingly.
    # Use a clamping function to keep text box and label sizes reasonable.
    def clamp(n, minn, maxn):
      return max(min(maxn, n), minn)

    keyLength = clamp(max(len(key) for key in self.dictionary), 5, 50)
    textKeys = [key for key in self.dictionary if self.template.fieldKinds.get(key) != 'image']

    textFieldLengths = [
      len(str(key))
      if self.dictionary[key] is None
      else max(len(str(key)), len(str(self.dictionary[key])))
      for key in textKeys
    ]

    valueLength = clamp(
      n=max(textFieldLengths) if textFieldLengths else keyLength,
      minn=15,
      maxn=120,
    )

    metrics = QFontMetrics(QLineEdit().font())
    minLengthForKeys = metrics.horizontalAdvance('M' * keyLength)
    minLengthForData = metrics.horizontalAdvance('M' * valueLength)

    self._valueWidgetsByKey: dict[str, QLineEdit | ImageFieldRow] = {}

    # Build the dialog on the fly for the keys in the database.
    for key, value in self.dictionary.items():
      # Create a local layout to add to the form.
      fieldGroup = QHBoxLayout()
      # Put field text in a label for prompting the user and set it's size.
      label = QLabel(key)
      label.setAlignment(Qt.AlignmentFlag.AlignRight)
      label.setFixedWidth(minLengthForKeys)

      if self.template.fieldKinds.get(key) == 'image':
        initial = str(value) if value else ''

        inputWidget: QLineEdit | ImageFieldRow = ImageFieldRow(
          minLengthForData, initial, parent=self
        )

      else:
        txtInput = QLineEdit()
        txtInput.setMinimumWidth(minLengthForData)

        if value:
          txtInput.setText(str(value))

        else:
          txtInput.setText('')

        inputWidget = txtInput

      self._valueWidgetsByKey[key] = inputWidget

      # Group the label and the field together.
      fieldGroup.addWidget(label)
      fieldGroup.addWidget(inputWidget)

      # Add the label and field group to the form.
      self.layout.addLayout(fieldGroup)

    # Connect tthe accept/submit button for the dialog form.
    button = QPushButton('Submit')
    button.setDefault(True)
    button.clicked.connect(self.submit)
    button.clicked.connect(self.close)
    self.layout.addWidget(button)

  def submit(self) -> None:
    """Submit button for form, gather information and pass it back to the main form."""
    for key, w in self._valueWidgetsByKey.items():
      if isinstance(w, ImageFieldRow):
        self.dictionary[key] = w.fieldText()

      else:
        self.dictionary[key] = w.text()

    try:
      self.template.setFields(self.dictionary)
      self._onTemplateApplied(self.template)

    except TemplateKeyValueNull:
      self._onTemplateApplied(self.template)

    return
