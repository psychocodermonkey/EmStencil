--
-- Description: Database to contain description of email template and metadata tags
--    Name: Andrew Dixon            File: templates.sql
--    Date: 8 Nov 2023
--   Notes: To run this in SQLite3 the two easiest methods are:
--          After starting sqlite and opening the database issue the .read directive
--          sqlite> .read templates.sql
--          --- OR ---
--          $> sqlite3 templates.db -init templates.sql
--
--  Copyright (c) 2023-2026 Andrew Dixon
--
--  This file is part of EmStencil.
--  Licensed under the GNU Lesser General Public License v2.1.
--  See the LICENSE file at the project root for details.
--........1.........2.........3.........4.........5.........6.........7.........8.........9.........0.........1.........2.........3..

-- Drop Tables before rebuilding
drop view if exists vw_Templates_Tags;
drop table if exists templatetags;
drop table if exists templates;
drop table if exists tags;


-- Tabel for storing the email templates
Create Table templates (
  uid integer primary key AUTOINCREMENT not null,
  title text not null unique,
  content text not null,
  dateAdded datetime,
  dateUpdated datetime
);

-- Trigger for populating updated timestamp on templates.dateUpdated
Create Trigger Templates_Date_Updated
  After Update of title, content On templates
  Begin Update templates
    Set DateUpdated = Datetime('Now')
    Where uid = Old.uid;
End;

-- Trigger for populating added timestamp on templates.dateAdded
Create Trigger Templates_Date_Added
  After Insert On templates
  Begin Update templates
    Set DateAdded = Datetime('Now')
    Where uid = New.uid;
End;

-- Index over templates by template title
create index ux_Templates on templates (
    title asc
);


-- Table to store existing tag values
create table tags (
  uid integer primary key AUTOINCREMENT not null,
  tag text constraint DuplicateTagViolation not null unique,
  dateAdded datetime,
  dateUpdated datetime
  -- All has special use in the program, so do not want to allow it in the DB.
  -- Making this a list of values in case expansion is needed later.
  Constraint SpecialKeywordUsed check(lower(tag) not in ('all'))
);

-- Trigger for populating updated timestamp on tags.dateUpdated
Create Trigger Tags_Date_Updated
  After Update of tag On tags
  Begin Update tags
    Set DateUpdated = Datetime('Now')
    Where uid = Old.uid;
End;

-- Trigger for populating added timestamp on tags.dateAdded
Create Trigger Tags_Date_Added
  After Insert On tags
  Begin Update tags
    Set DateAdded = Datetime('Now')
    Where uid = New.uid;
End;

-- Index over tags by tag
create unique index ux_Tags on tags (
    tag asc
);


-- Table for storing related tags to templates
Create Table templateTags (
  uid integer primary key AUTOINCREMENT not null,
  tmplt_uid integer references templates(uid),
  tag_uid integer references tags(uid),
  dateAdded datetime,
  dateUpdated datetime,
  Constraint DuplicateRowTagViolation unique (tmplt_uid, tag_uid),
  Foreign key(tmplt_uid) references templates(uid) on delete cascade,
  Foreign key(tag_uid) references tags(uid) on delete cascade
);

-- Trigger for populating updated timestamp on templateTags.dateUpdated
Create Trigger TemplateTags_Date_Updated
  After Update of tmplt_uid, tag_uid On templateTags
  Begin Update templateTags
    Set DateUpdated = Datetime('Now')
    Where uid = Old.uid;
End;

-- Trigger for populating added timestamp on templateTags.dateAdded
Create Trigger TemplateTags_Date_Added
  After Insert On templateTags
  Begin Update templateTags
    Set DateAdded = Datetime('Now')
    Where uid = New.uid;
End;

-- Index over template tags by template RowID
create index ix_TemplateTags_by_Template ON templateTags (
    tmplt_uid asc
);

-- Index over template tags by tag RowID
create index ix_TemplateTags_by_Tag ON templateTags (
    tag_uid asc
);


-- View with templates listed with all keys
Create View vw_Templates_Tags as
  select tm.title as title, tm.content as content,
    ta.tag as tag, tm.uid as tmpRowID, ta.uid as tgRowID
  from templates tm
    left join templateTags tg
      on tm.uid = tg.tmplt_uid
    left join tags ta
      on tg.tag_uid = ta.uid
  order by tmpRowID, tgRowID;

-- Set databas options
-- Foreign key enforcement is off by default, needs to be set on connect.
-- Pragma foreign_keys = ON;
