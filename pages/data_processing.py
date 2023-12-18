import dash
from dash import html, dcc, callback
import dash_loading_spinners as dls

from dbhandler import DBHandler
from main import UserVK, GroupVK
from dash import Input, Output, State

dash.register_page(
    __name__,
    name='Data Processing',
    top_nav=True,
    path='/data_processing'
)

all_options = {
    'User', 'Group'
}

layout = html.Div(style={'font-family': 'math'}, children=[
    html.H4('Обработка данных'),
    html.Div([
        dcc.Markdown('''

        > ** UPD LAST POSTS - добавление последних $${count}$$ публикаций: ** 
        > * установить $${count}$$ от $${1}$$ до $${100}$$
        >
        > ** UPD SPECIFIC POSTS - добавление указанных публикаций: ** 
        > * установить $${posts \space id/id's}$$
        >
        > ** UPD LIKES - добавление лайков по указанным публикациям: ** 
        > * установить $${posts \space id/id's}$$
        >
        > ** UPD COMMENTS: **
        >   * ** добавление комментариев по указанным публикациям ** - установить $${posts \space id/id's}$$
        >   * ** добавление комментариев последних $${count}$$ постов ** - установить $${count}$$
        >   * ** добавление комментариев со стены по конкретному запросу ** - установить $${query}$$
        >
        > ** CLEAR MESSAGE: **
        > * использовать для очистки результатов обработки данных
        >
        
        ---
        ''', mathjax=True),
        html.P([dcc.Input(id="input_id", type="text", placeholder="profile or community id",
                          style={'border': '1px solid red', 'padding': '5px', 'width': '200px'}),
                dcc.Input(id="input_token", type="text", placeholder="token",
                          style={'border': '1px solid red', 'margin': '5px', 'width': '200px'})]),
        html.P([
            dcc.Input(id="input_range", type="number", placeholder="count", min=1,
                      max=100, style={'padding': '5px', 'width': '200px'}),
            dcc.Input(id="input_other_ids", type="text", placeholder="posts id/id's",
                      style={'margin': '5px', 'width': '200px'}),
            dcc.Input(id="input_query", type="text", placeholder="query", style={'width': '200px'})]),
        html.P(
            dcc.RadioItems(
                list(all_options),
                'User',
                id='radio'
            )),
        html.Button(id='update-last-posts', n_clicks=0, children='Upd last posts',
                    style={'background-color': '#EEFFFD', 'width': '200px', 'margin-right': '5px'}),
        html.Button(id='update-specific-posts', n_clicks=0, children='Upd specific posts',
                    style={'background-color': '#EEFFFD', 'width': '200px', 'margin-right': '5px'}),
        html.Button(id='update-likes', n_clicks=0, children='Upd likes',
                    style={'background-color': '#EEFFFD', 'width': '200px', 'margin-right': '5px'}),
        html.Button(id='update-comments', n_clicks=0, children='Upd comments',
                    style={'background-color': '#EEFFFD', 'width': '200px', 'margin-right': '5px'}),
        html.Button(id='clear', n_clicks=0, children='Clear message',
                    style={'background-color': '#EEFFFD', 'width': '200px'}),
        html.Hr(),
        dls.Hash(html.Div(id='info1', style={'position': 'absolute', 'width': '100%'}),
                 color="#435278",
                 speed_multiplier=2,
                 fullscreen=True,
                 size=100),
        dls.Hash(html.Div(id='info2', style={'position': 'absolute', 'width': '100%'}),
                 color="#435278",
                 speed_multiplier=2,
                 fullscreen=True,
                 size=100),
        dls.Hash(html.Div(id='info3', style={'position': 'absolute', 'width': '100%'}),
                 color="#435278",
                 speed_multiplier=2,
                 fullscreen=True,
                 size=100),
        dls.Hash(html.Div(id='info4', style={'position': 'absolute', 'width': '100%'}),
                 color="#435278",
                 speed_multiplier=2,
                 fullscreen=True,
                 size=100),
        dls.Hash(html.Div(id='info5', style={'position': 'absolute', 'width': '100%'}),
                 color="#435278",
                 speed_multiplier=2,
                 fullscreen=True,
                 size=100),
        dls.Hash(html.Div(id='info6', style={'position': 'absolute', 'width': '100%'}),
                 color="#435278",
                 speed_multiplier=2,
                 fullscreen=True,
                 size=100)
    ],
        style={'position': 'relative'})
])


@callback(
    Output('info1', 'children'),
    Input('update-last-posts', 'n_clicks'),
    Input('clear', 'n_clicks'),
    State('input_id', 'value'),
    State('input_range', 'value'),
    State('input_token', 'value'),
    State('radio', 'value'))
def fill_data(graphic_update, clear, id, count, token, option):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if id is not None:
        match button_id:
            case 'update-last-posts':
                dbHandler = DBHandler()
                match count:
                    case _ if count is not None:
                        match option:
                            case 'User':
                                user = UserVK(id, token)
                                dbHandler.update_last_posts(id, count, 'profilesPosts', 'profile_id', user)
                            case 'Group':
                                group = GroupVK(id, token)
                                dbHandler.update_last_posts(id, count, 'communitiesPosts', 'community_id', group)
                        logs = []
                        paragraphs = [html.P(f"Удалено записей: {dbHandler.deleted_count}"),
                                      html.P(f"Добавлено записей: {dbHandler.added_count}"),
                                      html.P(f"Обновлено записей: {dbHandler.updated_count}"),
                                      html.P(f"Ошибки обработки: {dbHandler.unable_to_process}")]
                        for par in paragraphs:
                            logs.append(html.P(par))
                        return html.Div(logs)
                    case _ if count is None:
                        return 'fill range'
                match count:
                    case _ if count is not None:
                        return 'no data to update available'
                dbHandler.cursor.close()
            case 'clear':
                return ''
    else:
        print('no valid id is provided')


@callback(
    Output('info2', 'children'),
    Input('update-specific-posts', 'n_clicks'),
    Input('clear', 'n_clicks'),
    State('input_id', 'value'),
    State('input_other_ids', 'value'),
    State('input_token', 'value'),
    State('radio', 'value'))
def fill_data(graphic_update, clear, id, ids_list, token, option):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if id is not None:
        match button_id:
            case 'update-specific-posts':
                dbHandler = DBHandler()
                match ids_list:
                    case _ if ids_list is not None:
                        match option:
                            case 'User':
                                user = UserVK(id, token)
                                split_posts = list(map(int, ids_list.split(',')))
                                modified_posts = [f"{id}_{s}" for s in split_posts]
                                posts_ids_str = ', '.join(modified_posts)
                                dbHandler.update_specific_posts(id, posts_ids_str, 'profilesPosts', 'profile_id', user)
                            case 'Group':
                                group = GroupVK(id, token)
                                split_posts = list(map(int, ids_list.split(',')))
                                modified_posts = [f"-{id}_{s}" for s in split_posts]
                                posts_ids_str = ', '.join(modified_posts)
                                dbHandler.update_specific_posts(id, posts_ids_str, 'communitiesPosts', 'community_id', group)
                        logs = []
                        paragraphs = [html.P(f"Удалено записей: {dbHandler.deleted_count}"),
                                      html.P(f"Добавлено записей: {dbHandler.added_count}"),
                                      html.P(f"Обновлено записей: {dbHandler.updated_count}"),
                                      html.P(f"Ошибки обработки: {dbHandler.unable_to_process}")]
                        for par in paragraphs:
                            logs.append(html.P(par))
                        return html.Div(logs)
                    case _ if ids_list is None:
                        return 'fill id/ids'
                match ids_list:
                    case _ if ids_list is not None:
                        return 'no data to update available'
                dbHandler.cursor.close()
            case 'clear':
                return ''
    else:
        print('no valid id is provided')


@callback(
    Output('info3', 'children'),
    Input('update-likes', 'n_clicks'),
    Input('clear', 'n_clicks'),
    State('input_id', 'value'),
    State('input_range', 'value'),
    State('input_other_ids', 'value'),
    State('input_token', 'value'),
    State('radio', 'value'))
def fill_data(graphic_update, clear, id, count, other_ids, token, option):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if id is not None:
        match button_id:
            case 'update-likes':
                dbHandler = DBHandler()
                match other_ids:
                    case _ if other_ids is not None:
                        match option:
                            case 'User':
                                user = UserVK(id, token)
                                dbHandler.update_likes(id, other_ids, 'profilesLikes', 'profile_id', user)
                            case 'Group':
                                group = GroupVK(id, token)
                                dbHandler.update_likes(id, other_ids, 'communitiesLikes', 'community_id', group)
                        logs = []
                        paragraphs = [html.P(f"Удалено записей: {dbHandler.deleted_count}"),
                                      html.P(f"Добавлено записей: {dbHandler.added_count}"),
                                      html.P(f"Обновлено записей: {dbHandler.updated_count}"),
                                      html.P(f"Ошибки обработки: {dbHandler.unable_to_process}")]
                        for par in paragraphs:
                            logs.append(html.P(par))
                        return html.Div(logs)
                    case _ if other_ids is None:
                        return 'fill ids field'
                match count:
                    case _ if count is not None:
                        return 'no data to update available'
                dbHandler.cursor.close()
            case 'clear':
                return ''
    else:
        print('no valid id is provided')


@callback(
    Output('info4', 'children'),
    Input('update-comments', 'n_clicks'),
    Input('clear', 'n_clicks'),
    State('input_id', 'value'),
    State('input_other_ids', 'value'),
    State('input_token', 'value'),
    State('radio', 'value'))
def fill_data(graphic_update, clear, id, other_ids, token, option):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if id is not None:
        match button_id:
            case 'update-comments':
                dbHandler = DBHandler()
                match other_ids:
                    case _ if other_ids is not None:
                        match option:
                            case 'User':
                                user = UserVK(id, token)
                                dbHandler.update_comments(id, other_ids, 'profilesComments', 'profile_id', user)
                            case 'Group':
                                group = GroupVK(id, token)
                                dbHandler.update_comments(id, other_ids, 'communitiesComments', 'community_id', group)
                        logs = []
                        paragraphs = [html.P(f"Удалено записей: {dbHandler.deleted_count}"),
                                      html.P(f"Добавлено записей: {dbHandler.added_count}"),
                                      html.P(f"Обновлено записей: {dbHandler.updated_count}"),
                                      html.P(f"Ошибки обработки: {dbHandler.unable_to_process}")]
                        for par in paragraphs:
                            logs.append(html.P(par))
                        return html.Div(logs)
                dbHandler.cursor.close()
            case 'clear':
                return ''
    else:
        print('no valid id is provided')


@callback(
    Output('info5', 'children'),
    Input('update-comments', 'n_clicks'),
    Input('clear', 'n_clicks'),
    State('input_id', 'value'),
    State('input_range', 'value'),
    State('input_token', 'value'),
    State('radio', 'value'))
def fill_data(graphic_update, clear, id, count, token, option):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if id is not None:
        match button_id:
            case 'update-comments':
                dbHandler = DBHandler()
                match count:
                    case _ if count is not None:
                        match option:
                            case 'User':
                                user = UserVK(id, token)
                                posts = user.get_last_posts(count)
                                posts_ids = []
                                for post in posts:
                                    posts_ids.append(str(post[0]))
                                posts_ids_str = ', '.join(posts_ids)
                                dbHandler.update_comments(id, posts_ids_str, 'profilesComments', 'profile_id', user)
                            case 'Group':
                                group = GroupVK(id, token)
                                posts = group.get_last_posts(count)
                                posts_ids = []
                                for post in posts:
                                    posts_ids.append(str(post[0]))
                                posts_ids_str = ', '.join(posts_ids)
                                dbHandler.update_comments(id, posts_ids_str, 'communitiesComments', 'community_id',
                                                          group)
                        logs = []
                        paragraphs = [html.P(f"Удалено записей: {dbHandler.deleted_count}"),
                                      html.P(f"Добавлено записей: {dbHandler.added_count}"),
                                      html.P(f"Обновлено записей: {dbHandler.updated_count}"),
                                      html.P(f"Ошибки обработки: {dbHandler.unable_to_process}")]
                        for par in paragraphs:
                            logs.append(html.P(par))
                        return html.Div(logs)
                dbHandler.cursor.close()
            case 'clear':
                return ''
    else:
        print('no valid id is provided')


@callback(
    Output('info6', 'children'),
    Input('update-comments', 'n_clicks'),
    Input('clear', 'n_clicks'),
    State('input_id', 'value'),
    State('input_query', 'value'),
    State('input_token', 'value'),
    State('radio', 'value'))
def fill_data(graphic_update, clear, id, query, token, option):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if id is not None:
        match button_id:
            case 'update-comments':
                dbHandler = DBHandler()
                match query:
                    case _ if query is not None:
                        match option:
                            case 'User':
                                user = UserVK(id, token)

                                # цикл отбора постов по заданному query с текущим object
                                offset = 0
                                posts_filter_ids = []
                                while True:
                                    response = user.get_posts_by_query(query, 100, offset)
                                    for item in response['items']:
                                        posts_filter_ids.append(item['id'])
                                    offset += 100
                                    if response['count'] < 100:
                                        break

                                posts_ids_str = ', '.join(map(str, posts_filter_ids))
                                dbHandler.update_comments(id, posts_ids_str, 'profilesComments',
                                                          'profile_id', user)
                            case 'Group':
                                group = GroupVK(id, token)

                                # цикл отбора постов по заданному query с текущим object
                                offset = 0
                                posts_filter_ids = []
                                while True:
                                    response = group.get_posts_by_query(query, 100, offset)
                                    for item in response['items']:
                                        posts_filter_ids.append(item['id'])
                                    offset += 100
                                    if response['count'] < 100:
                                        break

                                posts_ids_str = ', '.join(map(str, posts_filter_ids))
                                dbHandler.update_comments(id, posts_ids_str, 'communitiesComments',
                                                          'community_id', group)
                        logs = []
                        paragraphs = [html.P(f"Удалено записей: {dbHandler.deleted_count}"),
                                      html.P(f"Добавлено записей: {dbHandler.added_count}"),
                                      html.P(f"Обновлено записей: {dbHandler.updated_count}"),
                                      html.P(f"Ошибки обработки: {dbHandler.unable_to_process}")]
                        for par in paragraphs:
                            logs.append(html.P(par))
                        return html.Div(logs)
                dbHandler.cursor.close()
            case 'clear':
                return ''
    else:
        print('no valid id is provided')
