"""
 Program: Base custom exception classes.
    Name: Andrew Dixon            File: exceptions.py
    Date: 14 Sep 2024
   Notes:

    Copyright (C) 2024  Andrew Dixon

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