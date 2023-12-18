import dash_bootstrap_components as dbc


def create_navbar():
    navbar = dbc.NavbarSimple(
                              children=[
                                  dbc.DropdownMenu(
                                      nav=True,
                                      in_navbar=True,
                                      label="Модули",
                                      align_end=False,
                                      style={'font-size':'16px', 'font-family':'math'},
                                      children=[  # Add as many menu items as you need
                                          dbc.DropdownMenuItem("Главная", href='/', style={'font-size':'16px'},),
                                          dbc.DropdownMenuItem(divider=True),
                                          dbc.DropdownMenuItem("Data Processing", href='/data_processing', style={'font-size':'16px'},),
                                          dbc.DropdownMenuItem("Data Visualization", href='/data_visualization', style={'font-size':'16px'},),
                                          dbc.DropdownMenuItem("Network Graph", href='/network_graph', style={'font-size':'16px'},),
                                          dbc.DropdownMenuItem("Search Comments", href='/filter_comments', style={'font-size':'16px'},),
                                      ],
                                  ),
                              ],
                              brand='Мониторинг ВКонтакте',
                              brand_style={'font-size':'16px', 'font-family':'math'},
                              brand_href="/",
                              # sticky="top",  # Uncomment if you want the navbar to always appear at the top on scroll.
                              color="#d0e0e3",
                              # Change this to change color of the navbar e.g. "primary", "secondary" etc.
                              dark=False,  # Change this to change color of text within the navbar (False for dark text)
                              )

    return navbar
