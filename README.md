# EmStencil - Email Stencils

EmStencil is a templated email generator. Email templates are stored with placeholder fields denoted by tags in the format ```${field}```. The application scans the text provided for these tags and generates a form to fill in the data to be substituted in the email.

## Setup

When building templates, the text replaced in an email will mimic the text used to describe the data within the tag. Defining a field `${Customer Name}` will ensure the name is capitalized when entered in the field value screen. Typing in "john doe" on the prompt screen will yield "John Doe" in the email text. The following are recognized:

```regex
- ${ALL CAPS LETTERS}
- ${all lowercase letters}
- ${Title Case Sentence}
```

Any other entry patterns will not affect the output of the text entered on the prompt screen.

### Image placeholder fields

Templates also support image placeholders using the format `^{field}`.

- Use `${...}` for text replacements and `^{...}` for image replacements.
- Image placeholders are intended for HTML template content.
- In the field entry dialog, image fields support pasting an image from the clipboard.
  - Pasted images are stored as `data:image/...` URLs.
- A single field key cannot be used as both `${key}` and `^{key}` in the same template.
- For image fields, entered values are used as-is (text case formatting rules are not applied).

Examples:

```html
<p>Screenshot:</p>
<p>^{Screenshot}</p>
```

```html
<p><img src="^{Screenshot}" alt="Screenshot" /></p>
```

There is no need to include a category for "all" as this is handled by the application to show all results.

## Application operation

After selecting the template from the list, the text area will be updated with the text from the template. Initially it will show the field tags instead of the text.

Clicking on Select (or pressing Enter), the field entry dialog will be displayed to capture the replacement text for each field. Be sure to enter a value for each field. If there is a field that requires specialized data (such as a screenshot), you may enter a space or other placeholder text in the field.

Clicking Submit on the field entry dialog will return to the main window. The text area on the main window will now display the text with the replaced values instead of the placeholder fields.

### Importing templates

Data can be imported from a spreadsheet. To import a spreadsheet, select `Import Templates` from the `File` menu in the application. A sample spreadsheet is located under `data\templates.xlsx`. The application utilizes local storage to store the database of parsed templates.

For the spreadsheet import to be successful, use the following requirements:

- File type must be a valid `.xlsx` workbook.
- Only the first worksheet is imported.
- Row 1 is treated as a header row and is skipped.
- Columns are read as:
  - Column A = template title
  - Column B = template content
  - Column C = tags (comma separated list)
- Only columns A through C are imported. Additional columns are ignored.
- Template titles must be unique within the spreadsheet. Duplicate titles cause the import to fail.
- Tags may contain spaces and are trimmed/lower-cased during import.
- The tag value `all` is reserved by the application and must not be used.

Importing a spreadsheet updates templates by title in the local database.

### Exporting templates

Data can be exported to a spreadsheet. To export a spreadsheet, select `Export Templates` from the `File` menu in the application.

The exported spreadsheet is formatted so it can be imported back into the application without additional changes:

- File type is `.xlsx`.
- A header row is written as:
  - Column A = `Title`
  - Column B = `Content`
  - Column C = `Tags`
- Template rows begin on row 2.
- Tags are exported in a single comma-separated value in column C.
- Export includes all templates currently in the local database.
- Exported templates are sorted by title (case-insensitive).

If a file name is selected without the `.xlsx` extension, the extension is added automatically.

## Future application updates & bug fixes

- ~~Implement add, update, delete of templates from the application.~~
- ~~Fix carry over after clicking the reset button and clicking select again.~~
  - Fields stay populated until a full reload of the templates is caused.
- ~~Implement File|Open menu for specifying template database location.~~
  - Using user local storage defined by OS. No longer needed to store data in a user-defined location.
- ~~Implement local storage for Windows, Mac, and Linux.~~
- ~~Implement File|Import to select location to bring in templates from a spreadsheet.~~
- ~~Implement File|Export to export templates from the database to Excel.~~

## Development TODOs

- Package EmStencil folder better and clean up imports across the application.
  - Improve | Standardize the way this is implemented.
- ~~Implement unit tests.~~
- ~~For MacOS "single file" packaging relative pathing breaks down due to the executable being within the `.app` folder structure.~~
  - ~~Moving the app to `/Applications` the application cannot write within its app directory.~~
  - ~~Solution is to leverage `user` storage locations for the DB and logging rather than just using the app directory.~~

## License

  Copyright (c) 2023-2026 Andrew Dixon

  This file is part of EmStencil.
  Licensed under the GNU Lesser General Public License v2.1.
  See the LICENSE file at the project root for details.
