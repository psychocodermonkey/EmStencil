# EmStencil - Email Stencils

EmStencil is a templated email generator. Email templates are stored with place holder fields denoted by fields tagged in the format ```${field}```. The application scans the text provided for these tags and generates a form to fill in the data to be substituted in the email.

## Setup

The initial templates can be loaded by the ```convert_spreadsheet.py``` from a spreadsheet named ```templates.xlsx``` located in the data folder. The columns in the spreadsheet are converted into the database as the template title, template content, and the categories for the template. The categories are converted from the spreadsheet as a comma separated list. Spaces may be used in the between words in the categories column.

The ```convert_spreadsheet.py``` script takes arguments for the location by using the ```--xls``` argument.

```sh
$> python convert_spreadsheet.py --xls templates.xls
```

When building templates, the text replaced in email will mimic the text used to describe the data within the tag. Defining a filed ${Customer Name} will ensure the name is capatilized when entered in the screen. Typing in "john doe" on the prompt screen will yeild "John Doe" in the email text. The following are recognized:

```regex
- ${ALL CAPS LETTERS}
- ${all lowercase letters}
- ${Title Case Sentence}
```

Any other entry patterns will not affect the output of the text entered on the prompt screen.

There is no need to include a category for "all" as this is handled by the application to show all results. Adding an "all" key word will result in a duplicate category named all.

## Applicaton operation

After selecting the template from the list, the text area will be updated with the text from the template. Initially it will show the field tags instead of the text.

Clicking on select (or pressing enter), the field entry dialog will be displayed to capture the replacement text for each field. Be sure to enter a value for each field. If there is a field that requires specialized data (such as a screenshot) you may enter a space or other placeholder text in the field.

Clicking Submit on the field entry dialog will return to the main window. The text area on the main window will now display the text with the replaced values instead of the placeholder fields.

## Future application updates & bug fixes

- Implement add, update, delete of templates from the application.
- ~~Fix carry over after clicking the reset button and clicking select again.~~
  - Fields stay populated until a full reload of the tempaltes is caused.
- Implement File|Open menu for specifying template database location.
- ~~Implement File|Import to select location to bring in tempaltes from a spreadsheet.~~
- Imelement File|Export to export templates from the database to Excel.

## Development TODO's

- Implement unit tests.
- Package emstencil folder better and clean up imports across the application.
  - Improve | Standardize the way this is implemented.
- For MacOS "single file" packaging relative pathing breaks down due to the executable being within the `.app` folder structure.
  - Moving the app to `/Applicatons` the application cannot write within it's app directory.
  - Solution is to leverage `user` storage locations for the DB and logging rather than just using the app directory.

## License

Distrubuted under the GPLv3 see LICENSE for more information.
Copyright (C) 2023-2025 Andrew Dixon
