from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from queries import  (
  build_get_all_projects_from_org_query,
  build_get_project_items_count_query,
  build_get_all_project_items_query
)
from utils import GITHUB_GRAPHQL_URL, ORGANIZATION
from datetime import datetime, timedelta


def sprint_formatter(field):
  date_format = '%Y-%m-%d'
  duration = timedelta(days=field.get('duration'))
  start_date = datetime.strptime(field.get('startDate'), date_format)
  sprint = field.get('title')
  end_date = start_date + duration

  return { 'Sprint': sprint, 'Start Date': start_date.strftime(date_format), 'End Date': end_date.strftime(date_format) }


formatters = {
  'Title': lambda field: { 'Title': field.get('text', '') },
  'Status': lambda field: { 'Status': field.get('name', '') },
  'Date': lambda field: { 'Date': field.get('date', '') },
  'Sprint': sprint_formatter
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
      name = field.get('field').get('name')
      formatter = formatters.get(name, lambda _: { name: '' })
      tmp = { **tmp, **formatter(field) }
    resp.append(tmp)
  
  return resp


if __name__ == '__main__':
  client = create_client()
  project_id = get_project_id_by_name(client, 'App Firewall')
  items_count = get_project_items_count(client, project_id)

  print(get_project_items(client, project_id, 1))
