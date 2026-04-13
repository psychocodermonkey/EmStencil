"""
 Program: Dataclasses for email template application
    Name: Andrew Dixon            File: TemplateDataClasses.py
    Date: 23 Nov 2023
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

import html
import re
from enum import Enum
from dataclasses import dataclass, field
from .content_html import exportContentAsHTML, isHTMLContent
from .Exceptions import (
  TemplateFieldKindConflict,
  TemplateKeyValueMismatch,
  TemplateKeyValueNull,
)


class State(Enum):
  """State enum for use in dataclass objects to denote state."""

  ADDED, UPDATED, DELETED, EXISTING = range(0, 4)


# ${text field} and ^{image field}; first match group is text inner, second is image inner.
_PLACEHOLDER_RE = re.compile(r'\$\{(.*?)\}|\^\{(.*?)\}')


def _contentHasImagePlaceholder(content: str) -> bool:
  """True if body uses ^{...} image slots (requires HTML body for merge/export)."""
  return '^{' in content


def _parsePlaceholderSpecs(content: str) -> tuple[list[str], dict[str, str]]:
  """First-seen key order; kinds are 'text' or 'image'. Raises TemplateFieldKindConflict on clash."""
  order: list[str] = []
  kinds: dict[str, str] = {}
  for m in _PLACEHOLDER_RE.finditer(content):
    textKey, imageKey = m.group(1), m.group(2)

    if textKey is not None:
      key, kind = textKey, 'text'

    else:
      key, kind = imageKey, 'image'

    if key in kinds:
      if kinds[key] != kind:
        raise TemplateFieldKindConflict(key, kinds[key], kind)

      continue

    kinds[key] = kind
    order.append(key)

  return order, kinds


_SRC_EQ_DOUBLE = re.compile(r'src\s*=\s*"\s*$', re.IGNORECASE)
_SRC_EQ_SINGLE = re.compile(r"src\s*=\s*'\s*$", re.IGNORECASE)


def _htmlMergeCaretImageField(body: str, key: str, raw) -> str:
  """Bare ^{key} → <img src=...>; inside src=\"^{key}\" → URL only so tags stay valid."""
  val = str(raw).strip()
  safeURL = html.escape(val, quote=True)
  alt = html.escape(key, quote=True)
  fullImg = f'<img src="{safeURL}" alt="{alt}" />'
  pat = re.compile(r'\^\{' + re.escape(key) + r'\}')
  chunks: list[str] = []
  
  pos = 0
  for m in pat.finditer(body):
    chunks.append(body[pos : m.start()])
    prefix = body[: m.start()]

    if _SRC_EQ_DOUBLE.search(prefix) or _SRC_EQ_SINGLE.search(prefix):
      chunks.append(safeURL)

    else:
      chunks.append(fullImg)

    pos = m.end()
  chunks.append(body[pos:])

  return ''.join(chunks)


@dataclass(slots=True, order=True)
class MetadataTag:
  """
  # Metadata Tag to associate with the template
    - Stores the text for the tag, enforcing lower case for the tag.
  ## Properties
    - tag :: String that is the actual tag for the Metadata.
    - rowID :: property is for storing the RowID of this metadata tag table.
    - assocRowID :: property is for storing the RowID for the associative record table.
    - state :: Property to hold the database state for the object.
        - Values :: ADDED, UPDATED, DELETED, EXISTING
  """

  tag: str
  rowID: int = field(init=False, default=0)
  assocRowID: int = field(init=False, repr=False, default=0)
  state: State = field(init=False, default=State.ADDED)

  def __post_init__(self) -> None:
    """Initilize fields calculated off of data from creation."""
    # ensure tags are all lower case
    self.tag = self.tag.lower()

  def __str__(self) -> str:
    """Return string representation of the tag."""
    return self.tag


@dataclass(slots=True)
class EmailTemplate:
  """
  # Email template data object.
    - Generates list of fields based on fields formatted as ${field}.
    - Case for stored data to replace in the fields is matched based on case of the text of the field.
  ## Properties
    - title :: Description for the template. Displayed when converted/represented as a string.
    - content :: The content of the email; placeholders are ${field} (text) or ^{field} (image).
    - fields :: Calculated dictionary of the fields. Store data to replace for each field as the
                value for the dict.
    - fieldKinds :: Maps each field key to 'text' or 'image' (from placeholder syntax).
    - metadata :: List of either values or Metadata objects for content tags of the email
        - Using the Metadata object allows for tracking of metadata row ID's in their respective tables.
    - rowID :: RowID for this template in the table. Not set as part of init,
               be sure to check/set before use
    - state :: Property to hold the database state for the object.
        - Values :: ADDED, UPDATED, DELETED, EXISTING
  ## Exceptions
    - TemplateKeyValueMismatch
        - Thrown when there is a key that does not exist in both the object dictionary and a passed
          dictionary being used for updates.
    - TemplateKeyValueNull
        - Thrown when a value for a key in the dictionary is NULL.
  ## Caveats
    - If updating the field list dictionary directly (ex: EmailTemplate.fields['key']), it is possible to
      inject additional values into the dictionary. This will make it easier to have NULL values
      when doing the string replacement.
        - Recommended method is to make a copy of the dictionary, manipulate the copy, then set it
          back to the template object using EmailTemplate.setFields(values: dict).
  """

  title: str
  content: str
  fields: dict = field(default_factory=dict, init=False, repr=False)
  fieldKinds: dict[str, str] = field(default_factory=dict, init=False, repr=False)
  metadata: list[MetadataTag] = field(default_factory=list, repr=False)
  rowID: int = field(init=False, default=0)
  state: State = field(init=False, default=State.ADDED)

  def __post_init__(self) -> None:
    """Post initilization build internal requirements for template object."""
    if _contentHasImagePlaceholder(self.content) and not isHTMLContent(self.content):
      self.content = exportContentAsHTML(self.content)
    order, kinds = _parsePlaceholderSpecs(self.content)
    self.fieldKinds = kinds
    self.fields = {k: None for k in order}

  def __str__(self) -> str:
    """User friendly string representation. (user)"""
    return self.title

  @property
  def replacedText(self) -> str:
    """Return modified text based on values from the internal dictionary."""
    value = self.content
    mergeAsHTML = isHTMLContent(self.content)

    for key in self.fields:
      fldVal = self.fields[key]

      if mergeAsHTML and self.fieldKinds.get(key) == 'image' and fldVal is not None:
        v = str(fldVal).strip()

        if v.startswith('data:image/') or v.startswith('http://') or v.startswith('https://'):
          value = _htmlMergeCaretImageField(value, key, fldVal)
          continue

      delim = r'\$\{' if self.fieldKinds.get(key) == 'text' else r'\^\{'
      rEx = delim + re.escape(key) + r'\}'
      rExMatch = re.findall(rEx, self.content)
      replacement = html.escape(str(fldVal), quote=False) if mergeAsHTML else fldVal

      for fld in rExMatch:
        value = value.replace(fld, replacement)

    return value

  @property
  def fieldsSet(self) -> bool:
    """Return if all the fields have had values set"""
    return all(self.fields.values())

  @property
  def numberOfFields(self) -> int:
    """Return the number of fields the template has"""
    return len(self.fields)

  def setFields(self, values: dict) -> None:
    """Update dictionary fields from external dictionary. (Preferred update method)"""
    # Verify that all keys exist in both dictionaries
    if len(list(set(self.fields).symmetric_difference(values))) != 0:
      raise TemplateKeyValueMismatch(source=values, dest=self.fields)

    else:
      # Add values, ensuring we add ALL values to the dictionary.
      # Field dialog supplies plain text; match case to placeholder spelling even for HTML bodies.
      for key in values:
        if values[key] is not None:
          raw = values[key]

          if self.fieldKinds.get(key) == 'image':
            self.fields[key] = raw
            
          elif key.islower():
            self.fields[key] = raw.lower()

          elif key.isupper():
            self.fields[key] = raw.upper()

          elif key.istitle():
            self.fields[key] = raw.title()

          else:
            self.fields[key] = raw

        # Throw exception for NULL values for keys.
        else:
          raise TemplateKeyValueNull(key)

  def clearFields(self) -> None:
    """Reset all values in the field dictionary back to None"""
    self.fields = {key: None for key in self.fields}
