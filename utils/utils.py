from utils.mappers import STATUS_MAPPER


def format_data(data):
  formatted_data = []
  row_index=7
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
        f'=I{row_index}-G{row_index}',
        STATUS_MAPPER.get(row.get('Status', ''))
      ]
    )
    row_index+=1

  return formatted_data
