from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from queries import  (
  build_get_all_projects_from_org_query,
  build_get_project_items_count_query,
  build_get_all_project_items_query
)
from utils import GITHUB_GRAPHQL_URL, ORGANIZATION, STATUS_MAPPER, MONTH_MAPPER
from datetime import datetime, timedelta
import pandas as pd

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1Ek5cl3SoJbuo5946G6TFyssjISu--8poMg5sQsWmT0w"
SAMPLE_RANGE_NAME = "[APP FIREWALL] Timeline 2024.1!C7"


def sprint_formatter(field):
  date_format = '%Y-%m-%d'
  duration = timedelta(days=field.get('duration'))
  start_date = datetime.strptime(field.get('startDate'), date_format)
  sprint = field.get('title')
  end_date = start_date + duration

  return {
    'Sprint': sprint,
    'Start Date': f'{start_date.day}-{MONTH_MAPPER.get(start_date.month)}',
    'End Date': f'{end_date.day}-{MONTH_MAPPER.get(end_date.month)}'
  }


def assignees_formatter(field):
  assignees = [node.get('login') for node in field.get('users').get('nodes')]
  return {
    'Assignees': ','.join(assignees)
  }


formatters = {
  'Title': lambda field: { 'Title': field.get('text', '') },
  'Status': lambda field: { 'Status': field.get('name', '') },
  'Sprint': sprint_formatter,
  'Assignees': assignees_formatter
}

def create_client():
  # TODO: add gh token to env
  transport = AIOHTTPTransport(
    url=GITHUB_GRAPHQL_URL,
    headers={'Authorization': 'Bearer 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'},
  )
  return Client(transport=transport, fetch_schema_from_transport=True)


def get_project_id_by_name(client, name):
  query = gql(build_get_all_projects_from_org_query(ORGANIZATION))
  result = client.execute(query)

  nodes = result.get('organization').get('projectsV2').get('nodes')
  return list(filter(lambda node: node.get('title') == name, nodes))[0].get('id')


def get_project_items_count(client, project_id):
  query = gql(build_get_project_items_count_query(project_id))
  result = client.execute(query)

  return result.get('node').get('items').get('totalCount')


def get_project_items(client, project_id, items_count):
  query = gql(build_get_all_project_items_query(project_id, items_count))
  result = client.execute(query)

  resp = []
  items = result.get('node').get('items').get('nodes')
  for item in items:
    fields = item.get('fieldValues').get('nodes')
    tmp = {}
    for field in fields:
      if len(field) != 0:
        name = field.get('field').get('name')
        formatter = formatters.get(name, lambda _: { name: '' })
        tmp = { **tmp, **formatter(field) }
    resp.append(tmp)
  
  return resp


def google_auth():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("static/token.json"):
    creds = Credentials.from_authorized_user_file("static/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        "static/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("static/token.json", "w") as token:
      token.write(creds.to_json())
  
  return creds


def format_data(data):
  formatted_data = []
  for row in data:
    formatted_data.append(
      [
        '',
        row.get('Sprint', ''),
        row.get('Title', ''),
        '',
        row.get('Start Date', ''),
        row.get('Assignees', ''),
        row.get('End Date', ''),
        '',
        STATUS_MAPPER.get(row.get('Status', ''))
      ]
    )

  return formatted_data


def main():
  client = create_client()
  project_id = get_project_id_by_name(client, 'App Firewall')
  items_count = get_project_items_count(client, project_id)

  data = get_project_items(client, project_id, items_count)
  #################################################################
  creds = google_auth()

  try:
    service = build("sheets", "v4", credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    sheet.values().update(
      spreadsheetId=SAMPLE_SPREADSHEET_ID,
      range=SAMPLE_RANGE_NAME,
      valueInputOption='USER_ENTERED',
      body={'values': format_data(data)}
    ).execute()
  except HttpError as err:
    print(err)

if __name__ == '__main__':
  main()
