# sheets-script

This script's main goal is to reduce the manual work of filling Google Sheets with tasks extracted from GitHub Projects.

We expect the GitHub Projects to have the following columns:

| Column Name | Column Type   |
|-------------|---------------|
| Status      | Single Select |
| Sprint      | Iteration     |
| Assignees   | Assignees     |
| Title       | Text          |

To run the script you need to fill the Makefile params, which are the following:

```
SHEET_ID: The id of the Google Sheet to be filled

For example, considering the following link

https://docs.google.com/spreadsheets/d/1Ek5cl3SoJbuo5946G6TFyssjISu--8poMg5sQsWmT0w/edit

The SHEET_ID would be "1Ek5cl3SoJbuo5946G6TFyssjISu--8poMg5sQsWmT0w"
```

```
RANGE_NAMES: Are the name of the page of the Google Sheets, they can be found in the bottom of the page
```

```
PROJECT_NAMES: The name of the GitHub Project to extract the tasks from
```

```
ORGS: The organizations of the projects
```

**OBS: If you want to run for more than one project fill the params separated by ,**

Example:
```
RANGE_NAMES='[APP FIREWALL] Timeline 2024.1,[YARA] Timeline 2024.1,[OCA] Timeline 2024.1'
PROJECT_NAMES='App Firewall,Yara project,OCA'
ORGS='nufuturo-ufcg,nufuturo-ufcg,OCA-UFCG'
```

Before running, you need to fill the .env file with your GitHub Token, bear in mind that you must be part of the organization to be able to access the GitHub Projects of the organization.

Once you edited the params in the Makefile, you can use the following command to run:

```sh
make run
```
