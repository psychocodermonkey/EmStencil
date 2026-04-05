#! /usr/bin/env python3

"""
 Program: Shared pytest fixtures for EmStencil tests.
    Name: Andrew Dixon            File: conftest.py
    Date: 5 Apr 2026
   Notes:

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import emstencil.Database as databaseModule
import pytest
from emstencil.Database import TemplateDB


@pytest.fixture()
def templateDB(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TemplateDB]:
  """Isolated DB with schema; resets TemplateDB singleton around the test."""
  dbPath = tmp_path / 'templates.db'
  schemaPath = Path(__file__).resolve().parents[1] / 'emstencil' / 'templates.sql'
  schemaText = schemaPath.read_text(encoding='utf-8')

  with sqlite3.connect(dbPath) as setupDB:
    setupDB.executescript(schemaText)

  TemplateDB._instance = None
  monkeypatch.setattr(databaseModule, 'DATABASE_FILE', dbPath)

  db = TemplateDB()
  yield db

  db.close()
  TemplateDB._instance = None
