from datetime import datetime, timedelta
from utils.mappers import MONTH_MAPPER


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