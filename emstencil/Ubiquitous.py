"""
 Program: Ubiquitous items for all files.
    Name: Andrew Dixon            File: Ubiquitous.py
    Date: 6 Nov 2024
   Notes: Single point of declaration of items used across all files.

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

import os
import platform
from pathlib import Path


def get_user_data_dir() -> Path:
  """
  Set local persistent storage path in "user" application storage.
  """

  system = platform.system()


  if system == 'Darwin':
    base = Path.home() / 'Library' / 'Application Support' / 'EmStencil'

  elif system == 'Windows':
    # Use APPDATA\Local so data stays on machine not synced with profile.
    local = os.getenv('LOCALAPPDATA') or Path.home() / 'AppData' / 'Local'
    base = Path(local) / 'EmStencil'

  else:
    xdg = os.getenv('XDG_DATA_HOME')
    base = Path(xdg) / 'EmStencil' if xdg else Path.home() / '.local' / 'share' / 'EmStencil'

  base.mkdir(parents=True, exist_ok=True)
  return base


DATA_DIR = get_user_data_dir()                      # Data directory for persistent storage.
DATABASE_FILE = DATA_DIR / 'templates.db'           # Path for database file.
LOG_PATH = DATA_DIR / 'runlog.log'                  # Path for runtime log file.
