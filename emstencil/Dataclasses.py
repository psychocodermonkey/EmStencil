#! /usr/bin/env python3
"""
 Program: Dataclasses for email template application
    Name: Andrew Dixon            File: TemplateDataClasses.py
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

import re
from dataclasses import dataclass, field


# ==================================================================================================
# Dataclasses
# ==================================================================================================
@dataclass(slots=True, order=True)
class MetadataTag:
  """
  # Metadata Tag to associate with the template
    - Stores the text for the tag, enforcing lower case for the tag.
  ## Properties
    - tag :: String that is the actual tag for the Metadata.
    - rowID :: property is for storing the RowID of this metadata tag table.
    - assocRowID :: property is for storing the RowID for the associative record table.
  """

  tag: str
  rowID: int = field(init=False, default=0)
  assocRowID: int = field(init=False, repr=False, default=0)

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
    - content :: The content of the email, contains fields to be replaces represented by ${field text}.
    - fields :: Calculated dictionary of the fields. Store data to replace for each field as the
                value for the dict.
    - metadata :: List of either values or Metadata objects for content tags of the email
        - Using the Metadata object allows for tracking of metadata row ID's in their respective tables.
    - rowID :: RowID for this template in the table. Not set as part of init,
               be sure to check/set before use
  ## Exceptions
    - TemplateKeyValueMismatch
        - Thrown when there is a key that does not exist in both the object dictionary and a passed
          dictionary being used for updates.
    - TemplateKeyValueNull
        - Thrown when a value for a key in the dictionary is NULL.
  ## Caveats
    - If updating the field list dictionary directly EmailTemplate.fields['key'], it is possible to
      inject additional values into the dictionary. This will make it easier to have NULL values
      when doing the string replacement.
        - Recommended method is to make a copy of the dictionary, manipulate the copy, then set it
          back to the template object using EmailTemplate.setFields(values: dict).
  """

  title: str
  content: str
  fields: dict = field(default_factory=dict, init=False, repr=False)
  metadata: list[MetadataTag] = field(default_factory=list, repr=False)
  rowID: int = field(init=False, default=0)

  def __post_init__(self) -> None:
    """Post initilization build internal requirements for template object."""
    # RegEx to match fields in the ${field} format, grabbing only the text
    wkFields = re.findall(r'\$\{(.*?)\}', self.content)
    self.fields = dict(zip(wkFields, [None]*len(wkFields)))

  def __str__(self) -> str:
    """User friendly string representation. (user)"""
    return self.title

  @property
  def replacedText(self) -> str:
    """Return modified text based on values from the internal dictionary."""
    value = self.content
    for key in self.fields:

      # Build the exact text to match to for replacement so we match the full string for replacement
      rEx = r'\$\{' + key + r'\}'
      rExMatch = re.findall(rEx, self.content)

      # Replace the matches we found
      for fld in rExMatch:
        value = value.replace(fld, self.fields[key])

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
      # Match case based on the case of the field used in the template.
      for key in values:
        if self.fields[key]:
          if key.islower():
            self.fields[key] = values[key].lower()

          elif key.isupper():
            self.fields[key] = values[key].upper()

          elif key.istitle():
            self.fields[key] = values[key].title()

          else:
            self.fields[key] = values[key]

        # Throw exception for NULL values for keys.
        else:
          raise TemplateKeyValueNull(key)

  def clearFields(self) -> None:
    """Reset all values in the field dictionary back to None"""
    self.fields = {key: None for key in self.fields}


# ==================================================================================================
# Exception Classes
# ==================================================================================================
class TemplateKeyValueMismatch(Exception):
  """Exception for self.fields dictionary element mismatch"""
  def __init__(self, source: dict, dest: dict) -> None:
    self.missingKeys = list(set(dest).symmetric_difference(source))
    self.message = f'{self.missingKeys} not in source and destination'
    super().__init__(self.message)


class TemplateKeyValueNull(Exception):
  """Exception for when a dictionary value is None"""
  def __init__(self, value: str) -> None:
    self.key = value
    self.message = f'Value for key: [{self.key}] is Null'
    super().__init__(self.message)


class AccessNullRowID(Exception):
  """Exception for when rowID expected and it is null"""
  def __init__(self, *args: object) -> None:
    self.message = 'Attempted to use rowID without first setting it'
    super().__init__(self.message)