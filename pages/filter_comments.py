from hashlib import sha256

import dash
import pandas as pd
import pymorphy2
from dash import html, dcc, dash_table, callback
import dash_loading_spinners as dls
import dash_bootstrap_components as dbc

from dash import Input, Output, State
from pandas import DataFrame

from dbhandler import DBHandler

dash.register_page(
    __name__,
    name='Filter Comments',
    top_nav=True,
    path='/filter_comments'
)

options_object = {
    'User', 'Group'
}

layout = html.Div(style={'font-family': 'math'}, children=
[html.H4('Поиск комментариев по ключевым словам'),
 dcc.Markdown('''
        >
        > ** GET COMMENTS - просмотр комментариев **
        > * ** фильтрация постов по ключевым словам ** - установить $${keywords \space posts}$$
        > * ** фильтрация комментариев по ключевым словам ** - установить $${keywords \space comments}$$
        >
        > Возможно установить совместно $${keywords \space posts}$$ и $${keywords \space comments}$$.
        >
        > Если $${keywords}$$ не заполнены, то будет произведен вывод всех комментариев.

        ---
        ''', mathjax=True),
 dbc.Row([
     dbc.Col(
         html.Div([
             html.P([dcc.Input(id="input_ids", type="text", placeholder="profiles or communities id/id's",
                               style={'border': '1px solid red', 'padding': '5px', 'width': '250px'})]),
             html.P([dcc.Input(id="input_keywords_posts", type="text", placeholder="keywords posts", style={'padding': '5px', 'width': '250px'}),
                               dcc.Input(id="input_keywords_comments", type="text", placeholder="keywords comments", style={'margin': '5px', 'width': '250px'})]),
             html.Div(dcc.RadioItems(list(options_object),
                                     'User',
                                     id='radio_object')),
             html.Div([html.Button(id='get-comments', n_clicks=0, children='Get comments',
                                   style={'background-color': '#EEFFFD', 'width': '250px'})])],
             style={'position': 'relative', 'display': 'flex', 'flex-direction': 'column'}),
         md=7)],
     style={'top': 0, 'left': 0, 'margin': '5px'}),
 html.Br(),
 html.Div([
     dcc.Markdown("""
                            **Подробная информация**
                            
                            Здесь будет выведена детальная информация по комметариям.
                        """),
     dls.Hash(html.Div(id='comments-table',
                       children=[]),
              color="#435278",
              speed_multiplier=2,
              fullscreen=True,
              size=100)
 ])
 ],
                  )

morph = pymorphy2.MorphAnalyzer()
df = DataFrame()


# Функция для проверки наличия слова (с учетом склонения) в предложении
def check_word_in_sentence(word, sentence):
    lexemes = morph.parse(word)[0].lexeme
    for lexeme in lexemes:
        if lexeme[0].lower() in sentence.lower():
            return True
    return False


@callback(Output('comments-table', 'children'),
          Input('get-comments', 'n_clicks'),
          State('input_ids', 'value'),
          State('input_keywords_posts', 'value'),
          State('input_keywords_comments', 'value'),
          State('radio_object', 'value'))
# input_ids format - 12345,67890
# input_keywords format - мир, дружба, жвачка
def update_graph(get_comments, input_ids, input_keywords_posts, input_keywords_comments, option):
    global df
    if input_ids is not None:
        table_comments_name = ''
        table_posts_name = ''
        match option:
            case 'User':
                table_posts_name = 'profilesPosts'
                table_comments_name = 'profilesComments'
            case 'Group':
                table_posts_name = 'communitiesPosts'
                table_comments_name = 'communitiesComments'
        dbHandler = DBHandler()
        split_ids = list(map(str, input_ids.split(',')))
        result_set = set()
        # цикл по всем введенным пользователям/сообществам
        for object_id in split_ids:
            # после обновления информации по комментариям достаем их из БД
            sqlite_select_query = f"""SELECT * from {table_comments_name}"""
            dbHandler.cursor.execute(sqlite_select_query)
            records = dbHandler.cursor.fetchall()
            comments = set()
            for record in records:
                if record[0] == int(object_id):
                    comments.add((record[0],
                                  record[1],
                                  record[3],
                                  record[2],
                                  record[4],
                                  record[5],
                                  record[7],
                                  ''))
                    # community_id, post_id, comment_id, user_id, comment_date, parent_id, comment_text

            # установка темы к посту
            sqlite_select_query = f"""SELECT * from {table_posts_name}"""
            dbHandler.cursor.execute(sqlite_select_query)
            records = dbHandler.cursor.fetchall()
            comments_with_themes = set()
            for record in records:
                if record[0] == int(object_id):
                    for comment in comments:
                        if comment[0] == int(object_id) and comment[1] == record[1]:
                            comments_with_themes.add((comment[0],
                                                      comment[1],
                                                      comment[2],
                                                      comment[3],
                                                      comment[4],
                                                      comment[5],
                                                      comment[6],
                                                      record[5]))

            filtered_posts = set()
            filtered_comments = set()
            # фильтрация по ключевым словам к постам, если таковые введены
            if input_keywords_posts is not None and input_keywords_posts != '':
                split_comments_keywords = list(map(str, input_keywords_posts.split(',')))
                for comment in comments_with_themes:
                    for keyword in split_comments_keywords:
                        if check_word_in_sentence(keyword, comment[7]):
                            filtered_posts.add((comment[0],
                                                comment[1],
                                                comment[7],
                                                # comment[2],
                                                comment[3],
                                                comment[4],
                                                # comment[5],
                                                comment[6]))
                            # community_id, post_id, post_name, comment_id, user_id, comment_date, parent_id, comment_text
            # фильтрация по ключевым словам к комментариям, если таковые введены
            if input_keywords_comments is not None and input_keywords_comments != '':
                split_comments_keywords = list(map(str, input_keywords_comments.split(',')))
                for comment in comments_with_themes:
                    for keyword in split_comments_keywords:
                        if check_word_in_sentence(keyword, comment[6]):
                            filtered_comments.add((comment[0],
                                                   comment[1],
                                                   comment[7],
                                                   # comment[2],
                                                   comment[3],
                                                   comment[4],
                                                   # comment[5],
                                                   comment[6]))
                            # community_id, post_id, post_name, comment_id, user_id, comment_date, parent_id, comment_text
            # проверка, были ли введены какие-то ключевые слова
            if input_keywords_posts is not None and input_keywords_posts != '' and input_keywords_comments is not None and input_keywords_comments != '':
                result_set = result_set.union(filtered_posts.intersection(filtered_comments))
            else:
                result_set = result_set.union(filtered_posts.union(filtered_comments))

            # если ничего не введено, то выведем все комментарии
            if (input_keywords_posts is None or input_keywords_posts == '') and (input_keywords_comments is None or input_keywords_comments == ''):
                for comment in comments_with_themes:
                    result_set.add((comment[0],
                                    comment[1],
                                    comment[7],
                                    # comment[2],
                                    comment[3],
                                    comment[4],
                                    # comment[5],
                                    comment[6]))
                    # community_id, post_id, post_name, comment_id, user_id, comment_date, parent_id, comment_text
        df = pd.DataFrame(result_set, columns=['user or community id',
                                               'post_id',
                                               'post_theme',
                                               # 'comment_id',
                                               'user_id',
                                               'refreshed_date',
                                               # 'parent_id',
                                               'comment_text'])
        dbHandler.cursor.close()
        df['user or community id'] = df['user or community id'].astype('string')
        df['post_id'] = df['post_id'].astype('string')
        df['user_id'] = df['user_id'].astype('string')
        df['refreshed_date'] = df['refreshed_date'].astype('string')
        df.fillna({'post_theme': 'Нет данных'}, inplace=True)
        df['post_theme'] = df['post_theme'].astype('string')
        df['comment_text'] = df['comment_text'].astype('string')
        return dash_table.DataTable(id='dash-table-1', data=df.to_dict('records'),
                                    columns=[{"name": i, "id": i} for i in
                                             df.columns],
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

    else:
        'Введите идентификатор или идентификаторы объектов(профили, сообщества).'


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
    Output('dash-table-1', "data"),
    Input('dash-table-1', "filter_query"))
def update_table(filter):
    dff = df
    if filter != '':
        dff = df
        col_name, operator, filter_value = split_filter_part(filter)
        if operator == 'contains' and col_name == 'user_id':
            hash_obj = sha256(str(int(filter_value)).encode('ASCII')).hexdigest()
            dff = dff.loc[dff[col_name].str.contains(hash_obj)]
        elif operator == 'contains' and (col_name == 'post_id' or col_name == 'user or community id'):
            dff = dff.loc[dff[col_name].str.contains(str(int(filter_value)))]
        elif operator == 'contains' and col_name != 'user_id' and col_name != 'post_id' and col_name != 'user or community id':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]

    return dff.to_dict('records')
