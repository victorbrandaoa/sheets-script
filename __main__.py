import argparse
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from queries import  (
  build_get_all_projects_from_org_query,
  build_get_project_items_count_query,
  build_get_all_project_items_query
)
from utils import GITHUB_GRAPHQL_URL, formatters, format_data
from dotenv import load_dotenv
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--sample-sheet-id')
  parser.add_argument('--sample-range-names')
  parser.add_argument('--project-names')
  parser.add_argument('--organizations')
  return parser.parse_args()


def create_client():
  gh_token = os.getenv('GH_TOKEN')
  transport = AIOHTTPTransport(
    url=GITHUB_GRAPHQL_URL,
    headers={'Authorization': f'Bearer {gh_token}'},
  )
  return Client(transport=transport, fetch_schema_from_transport=True)


def get_project_id_by_name(client, organization, name):
  query = gql(build_get_all_projects_from_org_query(organization))
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


def run(sheet_id, range_name, organization, project_name):
  client = create_client()
  project_id = get_project_id_by_name(client, organization, project_name)
  items_count = get_project_items_count(client, project_id)

  data = get_project_items(client, project_id, items_count)

  creds = google_auth()

  try:
    service = build("sheets", "v4", credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    sheet.values().update(
      spreadsheetId=sheet_id,
      range=f'{range_name}!C7',
      valueInputOption='USER_ENTERED',
      body={'values': format_data(data)}
    ).execute()
  except HttpError as err:
    print(err)


def main():
  args = parse_arguments()
  sheet_id = args.sample_sheet_id
  range_names = args.sample_range_names.split(',')
  project_names = args.project_names.split(',')
  organizations = args.organizations.split(',')

  for item in zip(range_names, project_names, organizations):
    range_name, project_name, organization = item
    print(f'Running for {project_name}')
    run(sheet_id, range_name, organization, project_name)


if __name__ == '__main__':
  main()
