"""
 Program: Base custom exception classes.
    Name: Andrew Dixon            File: exceptions.py
    Date: 14 Sep 2024-2025
   Notes:

   Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

class TemplateKeyValueMismatch(Exception):
  """
  ## Exception for self.fields dictionary element mismatch
    - Thrown when there is a key that does not exist in both the object dictionary and a passed
      dictionary being used for updates.
  """
  def __init__(self, source: dict, dest: dict) -> None:
    self.missingKeys = list(set(dest).symmetric_difference(source))
    self.message = f'{self.missingKeys} not in source and destination'
    super().__init__(self.message)


class TemplateKeyValueNull(Exception):
  """
  ## Exception for when a dictionary value is None
    - Thrown when a value for akey in the dictionary is NULL.
  """
  def __init__(self, value: str) -> None:
    self.key = value
    self.message = f'Value for key: [{self.key}] is Null'
    super().__init__(self.message)


class AccessNullRowID(Exception):
  """
  ## Exception for when rowID expected and it is null
    - Exception thrown when trying to utilize a rowID from an object without it first being set.
  """
  def __init__(self, *args: object) -> None:
    self.message = 'Attempted to use rowID without first setting it'
    super().__init__(self.message)


class DatabaseDDLSourceMissing(Exception):
  """
  ## Exception for when trying to locate and load the DDL to create the database is missing.
    - Exception thrown when trying to build/create the database definition, usually on first run.
  """
  def __init__(self, value: str) -> None:
    self.path = value
    self.message = f'Attempted to load DDL definition file at {self.path}, DDL file not found!'
    super().__init__(self.message)


class InvalidImportFileType(Exception):
  """
  ## Exception for when trying to import a file type and file type is incorrect or invalid.
    - Exception thrown when corrupted or invalid file type is selected for input.
  """
  def __init__(self, *args: object) -> None:
    self.message = 'Corrupted or invalid file selected for import!'
    super().__init__(self.message)
