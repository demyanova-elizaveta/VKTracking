import dash
from dash import html, dcc

dash.register_page(
    __name__,
    name='Главная',
    top_nav=True,
    path='/'
)

layout = html.Div(style={'font-family': 'math', 'maxWidth': '1000px', 'font-size': '16px'}, children=[
    html.H4('Мониторинг социальной сети ВКонтакте'),
    html.P(['Вы находитесь на главной странице приложения для мониторинга социальной сети ',
            html.Span('ВКонтакте',
                      style={'textDecoration': 'underline', 'color': 'blue', 'cursor': 'pointer'},
                      id='vk-link')]),
    html.P(['Приложение разработано в соответствиями с ',
            html.Span('правилами платформы ВКонтакте',
                      style={'textDecoration': 'underline', 'color': 'blue', 'cursor': 'pointer'},
                      id='vk-rules-link'),
    ' и не хранит персональные данные пользователей. ', 'ID пользователей преобразуются в идентификаторы фиксированной длины с помощью алгоритма хэширования SHA-256, которые хранятся на сервере в зашифрованном виде.']),
    html.P('Используемая версия API VK - 5.154.'),
    html.P('Доступно 4 модуля: '),
    html.Ul(
        [
            html.Li([dcc.Link('Data Processing', href='/data_processing'), ' - добавление данных о постах, комментариях, лайках в базу данных приложения']),
            html.Li([dcc.Link('Data Visualization', href='/data_visualization'), ' - визуализация данных с помощью графиков и круговым диаграмм']),
            html.Li([dcc.Link('Network Graph', href='/network_graph'), ' - построение графа дружеских связей пользователя и связей внутри сообщества']),
            html.Li([dcc.Link('Filter Comments', href='/filter_comments'), ' - фильтрация комментариев по ключевым словам на основе отбора постов со стены сообщества или группы сообществ']),
        ]
    ),
html.P('Приложение разработано для анализа социальных сетей, в том числе для исследователей, которым важно иметь представление о группах пользователей без нарушения их конфиденциальности, а также делать выводы об общественных трендах.')
])

