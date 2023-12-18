import os

import dash
from dash import html, Output, Input, callback
import dash_bootstrap_components as dbc
import dash_auth

from navbar import create_navbar

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
NAVBAR = create_navbar()
# To use Font Awesome Icons
FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "First Dash App"


@callback(
    Output('vk-link', 'n_clicks'),
    Input('vk-link', 'n_clicks')
)
def open_vk_link(n_clicks):
    if n_clicks is not None:
        import webbrowser
        webbrowser.open_new_tab('https://vk.com')
    return None


@callback(
    Output('vk-rules-link', 'n_clicks'),
    Input('vk-rules-link', 'n_clicks')
)
def open_vk_link(n_clicks):
    if n_clicks is not None:
        import webbrowser
        webbrowser.open_new_tab('https://dev.vk.com/ru/rules')
    return None


app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.LUX,  # Dash Themes CSS
        FA621,  # Font Awesome Icons CSS
        'https://codepen.io/chriddyp/pen/bWLwgP.css'
    ],
    title=APP_TITLE,
    use_pages=True,  # New in Dash 2.7 - Allows us to register pages
)

# To use if you're planning on using Google Analytics
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{APP_TITLE}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>

    </body>
</html>
'''

app.layout = html.Div(
            style={'margin':'10px'},
            children=[
                NAVBAR,
                dash.page_container
            ]
        )

# Учетные данные для базовой авторизации (логин и пароль)
VALID_USERNAME_PASSWORD_PAIRS = {
    os.environ.get('DASH_USERNAME'): os.environ.get('DASH_PASSWORD')
}

# Используем dash_auth для базовой авторизации
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

server = app.server

if __name__ == '__main__':
    app.run_server(debug=False)