import dash
import pandas as pd
from dash import dash_table, callback
from dash import html, dcc, State

from dash import Input, Output
import sqlite3
import plotly.express as px
from pandas import DataFrame
from hashlib import sha256

dash.register_page(
    __name__,
    name='Data Visualization',
    top_nav=True,
    path='/data_visualization'
)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

stylesheet = [{
    'selector': 'node',
    'style': {
        'content': 'data(label)',
        'width': 90,
        'height': 80,
        'background-fit': 'cover',
        'background-image': 'data(url)'
    }
}]

options_tables = {
    'Likes', 'Comments'
}

options_object = {
    'User', 'Group'
}

layout = html.Div(id='main-div', style={'font-family': 'math'}, children=[
    html.H4('Визуализация данных'),
    dcc.Markdown('''
        >
        > ** APPLY - отображение данных: **
        > * ** просмотр конкретных публикаций ** - установить $${posts \space id/id's}$$
        > * ** просмотр комментариев по конкретным пользователям ** - установить $${user \space id}$$
        >
        > Возможно установить совместно $${posts \space id/id's}$$ и $${user \space id}$$
        >

        ---
        ''', mathjax=True),
    html.P([dcc.Input(id="input_id", type="text", placeholder="profile or community id",
                      style={'border': '1px solid red', 'padding': '5px', 'width': '250px'})]),
    html.P([
        dcc.Input(id="input_other_ids", type="text", placeholder="posts id/id's",
                  style={'margin-right': '5px', 'width': '250px'}),
        dcc.Input(id="input_user_id", type="text", placeholder="user id", style={'width': '250px'})]),
    html.Div([html.Div(dcc.RadioItems(list(options_tables),
                             'Comments',
                             id='radio_table'), style={'margin-right':'170px'}),
             html.Div(dcc.RadioItems(list(options_object),
                             'User',
                             id='radio_object'))],
             style={'position': 'relative', 'display': 'flex', 'flex-direction': 'row'}
             ),
    html.Button(id='apply', n_clicks=0, children='APPLY', style={'background-color': '#EEFFFD'}),

    html.Div(id='graph-div', children=[
        dcc.Graph(id='graphics', figure=px.scatter([], labels={
            "comment_date": "Comments Date ",
            "count": "Comments Count"},
                                                   log_x=True, size_max=55),
                  style={'width': '150vh', 'height': '50vh'})]),
    html.Div([
        dcc.Markdown("""
                            **Подробная информация**

                            Нажмите на секторы или отметки на графике, чтобы получить детальную информацию.
                        """),
        html.Div(id='div-table', children=[])
    ])
])

df = DataFrame()
df_full = DataFrame()
clicked_data = DataFrame()

N = 10


def get_view_comments(table_name, id_name, id, posts_ids=None, user_id=None):
    global df
    fig = {}
    select_query = ''
    sqlite_connection = sqlite3.connect('./sqlite_python.db')

    if id is None:
        return fig

    if user_id is None or user_id == '' and posts_ids is None or posts_ids == '':
        select_query = f"SELECT filteredTable.comment_date, count, user_id, refreshed_date, post_id, comment_text " \
                       f"FROM " \
                       "(SELECT comment_date, COUNT(comment_id) as count " \
                       f"FROM {table_name} " \
                       f"WHERE {id_name}={id} " \
                       f"GROUP BY comment_date) as groupByTable JOIN (SELECT * FROM {table_name} WHERE {id_name}={id}) as filteredTable ON " \
                       f"groupByTable.[comment_date]=filteredTable.[comment_date] " \
                       f"ORDER BY groupByTable.[comment_date]"

    if posts_ids is not None and posts_ids != '':
        split_posts = list(map(int, posts_ids.split(',')))
        select_query = f"SELECT filteredTable.comment_date, count, user_id, refreshed_date, post_id, comment_text " \
                       f"FROM (SELECT * FROM {table_name} WHERE {id_name}={id} AND post_id IN ({', '.join(map(str, split_posts))})) as filteredTable RIGHT JOIN (" \
                       "SELECT comment_date, COUNT(comment_id) as count " \
                       f"FROM {table_name} " \
                       f"WHERE {id_name}={id} AND post_id IN ({', '.join(map(str, split_posts))}) " \
                       "GROUP BY comment_date) as groupByTable ON " \
                       f"groupByTable.[comment_date]=filteredTable.[comment_date] " \
                       f"ORDER BY groupByTable.[comment_date]"

    if user_id is not None and user_id != '':
        hash_obj = sha256(user_id.encode('ASCII')).hexdigest()
        select_query = f"SELECT filteredTable.comment_date, count, user_id, refreshed_date, post_id, comment_text " \
                       f"FROM (SELECT * FROM {table_name} WHERE {id_name}={id} AND user_id='{hash_obj}') as " \
                       "filteredTable " \
                       "RIGHT JOIN (" \
                       "SELECT comment_date, COUNT(comment_id) as count " \
                       f"FROM {table_name} " \
                       f"WHERE {id_name}={id} AND user_id='{hash_obj}' " \
                       "GROUP BY comment_date) as groupByTable ON " \
                       f"groupByTable.[comment_date]=filteredTable.[comment_date] " \
                       f"ORDER BY groupByTable.[comment_date]"

    full_query = f"SELECT info.comment_date, info.count, info.user_id, info.refreshed_date, info.post_id, post_theme, info.comment_text " \
                 f"FROM (" + select_query + f") as info LEFT JOIN (SELECT post_id, pos" \
                                            f"t_theme FROM {table_name.replace('Comments', 'Posts')}) as posts ON " \
                                            f"info.post_id=posts.post_id"
    df = pd.DataFrame(pd.read_sql(full_query, sqlite_connection))
    df['post_id'] = df['post_id'].astype('string')
    df['user_id'] = df['user_id'].astype('string')
    df['refreshed_date'] = df['refreshed_date'].astype('string')
    df.fillna({'post_theme': 'Нет данных'}, inplace=True)
    df['post_theme'] = df['post_theme'].astype('string')
    df['comment_text'] = df['comment_text'].astype('string')
    sqlite_connection.close()
    fig = px.scatter(df, x='comment_date', y='count', labels={
        "comment_date": "Comments Date ",
        "count": "Comments Count"},
                     log_x=True, size_max=55,
                     hover_name='count')
    fig.update_layout(transition_duration=500, xaxis={'type': 'date'}, clickmode='event+select')
    fig.update_traces(mode="markers", marker_size=13)
    return fig


def get_view_likes(table_name, id_name, id, posts_ids=None, user_id=None):
    global df, df_full
    fig = {}
    sqlite_connection = sqlite3.connect('./sqlite_python.db')

    if id is None:
        return fig

    if user_id is None or user_id == '' and posts_ids is None or posts_ids == '':
        subquery = f"SELECT post_id, COUNT(user_id) as count " \
                   f"FROM {table_name} " \
                   f"WHERE {id_name}={id} " \
                   "GROUP BY post_id " \
                   "ORDER BY COUNT(user_id) DESC"
        select_query = f"SELECT {table_name}.post_id, count, user_id, refreshed_date " \
                       f"FROM {table_name} JOIN (" + subquery + ") as groupByTable ON " \
                                                                f"{table_name}.post_id = groupByTable.post_id"
        full_query = f"SELECT info.count, info.user_id, info.post_id, info.refreshed_date, post_theme " \
                     f"FROM (" + select_query + f") as info LEFT JOIN (SELECT post_id, pos" \
                                                f"t_theme FROM {table_name.replace('Likes', 'Posts')}) as posts ON " \
                                                f"info.post_id=posts.post_id"

        df = pd.DataFrame(pd.read_sql(subquery, sqlite_connection))
        df_full = pd.DataFrame(pd.read_sql(full_query, sqlite_connection))
        df['post_id'] = df['post_id'].astype('string')
        df_full['post_id'] = df_full['post_id'].astype('string')
        df_full['user_id'] = df_full['user_id'].astype('string')
        df_full['refreshed_date'] = df_full['refreshed_date'].astype('string')
        df_full.fillna({'post_theme': 'Нет данных'}, inplace=True)
        df_full['post_theme'] = df_full['post_theme'].astype('string')

        df_top_30 = df.head(N)
        df_others = {'post_id': 'others', 'count': df['count'].tail(-N).sum()}

        fig = px.pie(df_top_30.append(df_others, ignore_index=True), names='post_id', values='count')

    if posts_ids is not None and posts_ids != '':
        split_posts = list(map(int, posts_ids.split(',')))
        subquery = f"SELECT post_id, COUNT(user_id) as count " \
                   f"FROM {table_name} " \
                   f"WHERE {id_name}={id} AND post_id IN ({', '.join(map(str, split_posts))}) " \
                   "GROUP BY post_id " \
                   "ORDER BY COUNT(user_id) DESC"
        select_query = f"SELECT {table_name}.post_id, count, user_id, refreshed_date " \
                       f"FROM {table_name} JOIN (" + subquery + ") as groupByTable ON " \
                                                                f"{table_name}.post_id = groupByTable.post_id"

        full_query = f"SELECT info.count, info.user_id, info.post_id, info.refreshed_date, post_theme " \
                     f"FROM (" + select_query + f") as info LEFT JOIN (SELECT post_id, pos" \
                                                f"t_theme FROM {table_name.replace('Likes', 'Posts')}) as posts ON " \
                                                f"info.post_id=posts.post_id"

        df = pd.DataFrame(pd.read_sql(subquery, sqlite_connection))
        df_full = pd.DataFrame(pd.read_sql(full_query, sqlite_connection))
        df['post_id'] = df['post_id'].astype('string')
        df_full['post_id'] = df_full['post_id'].astype('string')
        df_full['user_id'] = df_full['user_id'].astype('string')
        df_full['refreshed_date'] = df_full['refreshed_date'].astype('string')
        df_full.fillna({'post_theme': 'Нет данных'}, inplace=True)
        df_full['post_theme'] = df_full['post_theme'].astype('string')

        df_top_30 = df.head(N)
        df_others = {'post_id': 'others', 'count': df['count'].tail(-N).sum()}
        fig = px.pie(df_top_30.append(df_others, ignore_index=True), names='post_id', values='count')

    if user_id is not None and user_id != '':
        subquery = f"SELECT user_id, COUNT(post_id) as count " \
                   f"FROM {table_name} " \
                   f"WHERE {id_name}={id} AND user_id={user_id} " \
                   f"GROUP BY user_id"
        select_query = f"SELECT {table_name}.user_id, count, post_id, refreshed_date " \
                       f"FROM {table_name} JOIN (" + subquery + ") as groupByTable ON " \
                                                                f"{table_name}.user_id = groupByTable.user_id"
        full_query = f"SELECT info.count, info.user_id, info.post_id, info.refreshed_date, post_theme " \
                     f"FROM (" + select_query + f") as info LEFT JOIN (SELECT post_id, pos" \
                                                f"t_theme FROM {table_name.replace('Likes', 'Posts')}) as posts ON " \
                                                f"info.post_id=posts.post_id"

        df = pd.DataFrame(pd.read_sql(subquery, sqlite_connection))
        df_full = pd.DataFrame(pd.read_sql(full_query, sqlite_connection))
        df_full['post_id'] = df_full['post_id'].astype('string')
        df_full['user_id'] = df_full['user_id'].astype('string')
        df_full['refreshed_date'] = df_full['refreshed_date'].astype('string')
        df_full.fillna({'post_theme': 'Нет данных'}, inplace=True)
        df_full['post_theme'] = df_full['post_theme'].astype('string')

        fig = px.pie(df_full, names='post_id')
        fig.update_traces(textinfo='none')

    sqlite_connection.close()
    fig.update_layout(transition_duration=500, clickmode='event+select')
    return fig


@callback(
    Output('div-table', 'children'),
    Input('graphics', 'clickData'),
    State('radio_table', 'value'),
    State('input_other_ids', 'value'),
    State('input_user_id', 'value'))
def display_click_data(current_data, table, posts_ids, user_id):
    global df, df_full, clicked_data
    clicked_data = DataFrame()
    if current_data is None:
        return ''
    match table:
        case 'Comments':
            clicked_data = df[(df['comment_date'] == current_data['points'][0]['x']) & (df['count'] ==
                                                                                        current_data['points'][
                                                                                            0]['y'])][
                ['user_id', 'post_id', 'refreshed_date', 'post_theme', 'comment_text']]
        case 'Likes':
            if user_id is None or user_id == '' and posts_ids is None or posts_ids == '':
                if current_data['points'][0]['label'] != 'others':
                    clicked_data = df_full[df_full['post_id'] == current_data['points'][0]['label']][
                        ['post_id', 'user_id', 'refreshed_date', 'post_theme']]
                else:
                    array = df['post_id'].head(N).unique()
                    clicked_data = df_full[~df_full['post_id'].isin(array)][
                        ['post_id', 'user_id', 'refreshed_date', 'post_theme']]
            if posts_ids is not None and posts_ids != '':
                if current_data['points'][0]['label'] != 'others':
                    clicked_data = df_full[df_full['post_id'] == current_data['points'][0]['label']][
                        ['post_id', 'user_id', 'refreshed_date', 'post_theme']]
                else:
                    array = df['post_id'].head(N).unique()
                    clicked_data = df_full[~df_full['post_id'].isin(array)][
                        ['post_id', 'user_id', 'refreshed_date', 'post_theme']]
            if user_id is not None and user_id != '':
                clicked_data = df_full[df_full['post_id'] == current_data['points'][0]['label']][
                    ['post_id', 'user_id', 'refreshed_date', 'post_theme']]
    return dash_table.DataTable(id='dash-table', data=clicked_data.to_dict('records'),
                                columns=[{"name": i, "id": i} for i in
                                         clicked_data.columns],
                                style_table={'overflowX': 'auto'},
                                css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                                style_cell={
                                    'height': 'auto',
                                    # all three widths are needed
                                    'minWidth': '50px', 'width': '50px', 'maxWidth': '50px',
                                    'whiteSpace': 'normal'
                                },
                                page_size=15,
                                style_header_conditional=[{
                                    'backgroundColor': 'rgb(212, 237, 255)',
                                    'color': 'black'
                                }],
                                style_filter={
                                    'fontSize': '14px'
                                },
                                filter_action="custom",
                                filter_query='')


operators = [['contains ']]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', '`'):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                return name, operator_type[0].strip(), value

    return [None] * 3


@callback(
    Output('dash-table', "data"),
    Input('dash-table', "filter_query"))
def update_table(filter):
    dff = clicked_data
    if filter != '':
        dff = clicked_data
        col_name, operator, filter_value = split_filter_part(filter)
        if operator == 'contains' and col_name == 'user_id':
            hash_obj = sha256(str(int(filter_value)).encode('ASCII')).hexdigest()
            dff = dff.loc[dff[col_name].str.contains(hash_obj)]
        elif operator == 'contains' and col_name == 'post_id':
            dff = dff.loc[dff[col_name].str.contains(str(int(filter_value)))]
        elif operator == 'contains' and col_name != 'user_id' and col_name != 'post_id':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]

    return dff.to_dict('records')


@callback(Output('input_user_id', 'type'),
          [Input('radio_table', 'value')])
def set_input_enabled_state(table):
    match table:
        case 'Likes':
            return 'hidden'
        case 'Comments':
            return 'text'


@callback(
    Output('graphics', 'figure'),
    Input('apply', 'n_clicks'),
    [State('radio_table', 'value'),
     State('radio_object', 'value'),
     State('input_id', 'value'),
     State('input_other_ids', 'value'),
     State('input_user_id', 'value')]
)
def display_click_data(apply, table, object, id, posts_ids, user_id):
    fig = {}
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        match table:
            case 'Likes':
                match object:
                    case 'User':
                        fig = get_view_likes('profilesLikes', 'profile_id', id=id, posts_ids=posts_ids, user_id=user_id)
                    case 'Group':
                        fig = get_view_likes('communitiesLikes', 'community_id', id=id, posts_ids=posts_ids,
                                             user_id=user_id)
            case 'Comments':
                match object:
                    case 'User':
                        fig = get_view_comments('profilesComments', 'profile_id', id=id, posts_ids=posts_ids,
                                                user_id=user_id)
                    case 'Group':
                        fig = get_view_comments('communitiesComments', 'community_id', id=id, posts_ids=posts_ids,
                                                user_id=user_id)
    return fig
