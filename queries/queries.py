def build_get_all_projects_from_org_query(org):
  return f'''
    query {{
      organization(login: "{org}") {{
        projectsV2(first: 20) {{
          nodes {{
            id 
            title 
            closed
          }}
        }}
      }}
    }}
  '''

def build_get_project_items_count_query(project_id):
  return f'''
    query {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
          items {{
            totalCount
          }}
        }}
      }}
    }}
  '''

def build_get_all_project_items_query(project_id, items_count):
  return f'''
    query {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
          items(first: {items_count}) {{
            nodes {{
              ... on ProjectV2Item {{
                id
                fieldValues(last: 8) {{
                  nodes {{
                    ... on ProjectV2ItemFieldTextValue {{
                      text
                      field {{
                        ... on ProjectV2Field {{
                          name
                        }}
                      }}
                    }}
                    ... on ProjectV2ItemFieldUserValue {{
                      users(last: 7) {{
                        nodes {{
                          login
                        }}
                      }}
                      field {{
                        ... on ProjectV2Field {{
                          name
                        }}
                      }}
                    }}
                    ... on ProjectV2ItemFieldDateValue {{
                      date
                      field {{
                        ... on ProjectV2Field {{
                          name
                        }}
                      }}
                    }}
                    ... on ProjectV2ItemFieldIterationValue {{
                      title
                      duration
                      startDate
                      field {{
                        ... on ProjectV2IterationField {{
                          name
                        }}
                      }}
                    }}
                    ... on ProjectV2ItemFieldSingleSelectValue {{
                      name
                      field {{
                        ... on ProjectV2SingleSelectField {{
                          name
                        }}
                      }}
                    }}
                    ... on ProjectV2ItemFieldNumberValue {{
                      number
                      field {{
                        ... on ProjectV2Field {{
                          name
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  '''
