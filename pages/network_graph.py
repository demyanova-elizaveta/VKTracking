import random

import dash
import dash_cytoscape as cyto
from dash import html, dcc, callback
import dash_loading_spinners as dls
import itertools as it

from main import UserVK, GroupVK
import networkx as nx
from dash import Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    name='Network Graph',
    top_nav=True,
    path='/network_graph'
)

MIN_SIZE = 3


class NetworkGraph:

    def __init__(self, id, option, given_token):
        self.token = given_token
        self.nodes = {}
        self.friendships = {}
        self.neighbors = {}
        self.cliques = []
        self.people_info = {}
        self.object_description = ''

        if option == 'User':
            user = UserVK(id, self.token)
            self.people_info = user.get_friends()
            self.nodes = user.all_friends
            self.friendships = user.get_common_friends()
            self.object_description = [html.P(f"{user.my_name} {user.my_last_name}"),
                                       html.P(f"Количество друзей: {user.friends_count}"),
                                       html.P(
                                           f"Сообщества пользователя: {', '.join(map(str, user.groups)) if user.groups is not None else 'нет сообществ или их список недоступен по указанному ключу доступа.'}")]
        elif option == 'Group':
            group = GroupVK(id, self.token)
            self.people_info = group.get_group_members()
            self.nodes = group.all_members
            self.friendships = group.get_common_vk_members()
            self.object_description = [html.P(f"{group.name}"), html.P(f"Количество участников: {group.members_count}"),
                                       html.P(f"Описание: {group.description}")]

        self.js = {'nodes': [], 'links': []}
        self.clique = {'nodes': [], 'links': []}
        self.nx_graph = nx.Graph()

    def make_cliques(self):
        for node in self.nx_graph.nodes:
            self.neighbors.update({node[0]: set(nx.neighbors(self.nx_graph, node))})
        self.bron_kerbosch_algorithm([], set(self.nx_graph.nodes), set())
        self.cliques.sort(key=lambda x: len(x), reverse=True)

    def get_max_clique(self):
        self.make_cliques()

        # Find the maximum length among arrays
        max_length = max(len(arr) for arr in self.cliques)

        # Get all arrays with the maximum length
        max_length_arrays = [arr for arr in self.cliques if len(arr) == max_length]

        # Choose a random array from those with the maximum length
        random_max_length_array = random.choice(max_length_arrays)

        for i in random_max_length_array:
            self.clique['nodes'].append(
                {'data': {'id': '%s' % self.people_info[i[0]]['id'],
                          'label': '%s' % self.people_info[i[0]]['first_name'] + ' ' + self.people_info[i[0]][
                              'last_name'],
                          'url': '%s' % self.people_info[i[0]]['photo']
                          }
                 })
        for a, b in it.combinations(random_max_length_array, 2):
            self.clique['links'].append({'data': {'source': '%s' % a[0], 'target': '%s' % b[0]}})

    def get_graph(self):
        for i in self.nodes.items():
            self.nx_graph.add_node((i[1]['id'], i[1]['first_name'] + ' ' + i[1]['last_name']))
            self.js['nodes'].append(
                {'data': {'id': '%s' % i[1]['id'],
                          'label': '%s' % i[1]['first_name'] + ' ' + i[1]['last_name'],
                          'url': '%s' % i[1]['photo']
                          }
                 })

        for i in self.friendships:
            if i[1]:
                find_word = '%s %s' % (i[0]['first_name'], i[0]['last_name'])
                for d in self.nx_graph.nodes:
                    if find_word in d[1]:
                        for c in i[1]:
                            find_friend = '%s %s' % (c['first_name'], c['last_name'])
                            for e in self.nx_graph.nodes:
                                if find_friend in e[1] and not self.nx_graph.has_edge(d, e):
                                    self.nx_graph.add_edge(e, d)
                                    self.js['links'].append({'data': {'source': '%s' % e[0], 'target': '%s' % d[0]}})
                                    break
                        break

    def bron_kerbosch_algorithm(self, clique, candidates, excluded):
        '''Bron–Kerbosch algorithm with pivot'''
        if not candidates and not excluded:
            if len(clique) >= MIN_SIZE:
                self.cliques.append(clique)
            return

        pivot = self.pick_random(candidates) or self.pick_random(excluded)
        for v in list(candidates.difference(self.neighbors[pivot[0]])):
            new_candidates = candidates.intersection(self.neighbors[v[0]])
            new_excluded = excluded.intersection(self.neighbors[v[0]])
            self.bron_kerbosch_algorithm(clique + [v], new_candidates, new_excluded)
            candidates.remove(v)
            excluded.add(v)

    def pick_random(self, s):
        if s:
            elem = s.pop()
            s.add(elem)
            return elem


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

all_options = {
    'User', 'Group'
}

layout = html.Div(style={'font-family': 'math'}, children=
[html.H4('Визуализация графа дружеских связей'),
 dcc.Markdown('''
        >
        > ** SHOW GRAPH - отображение графа дружеских связей **
        >
        > ** SHOW MAX CLIQUE - отображение максимальной клики графа дружеских связей **
        >

        ---
        ''', mathjax=True),
 dbc.Row(
     [
         dbc.Col(
             html.Div([
                 html.P([dcc.Input(id="input_id", type="text", placeholder="profile or community id",
                                   style={'border': '1px solid red', 'width': '200px', 'margin-right': '5px',
                                          'margin-bottom': '5px'}),
                         dcc.Input(id="input_token", type="text", placeholder="token",
                                   style={'border': '1px solid red', 'width': '200px'})]),
                 html.P(
                     dcc.RadioItems(
                         list(all_options),
                         'User',
                         id='radio',
                     )),
                 html.Button(id='graph-state', n_clicks=0, children='Show graph',
                             style={'background-color': '#EEFFFD', 'width': '200px', 'margin-right': '5px',
                                    'margin-bottom': '5px'}),
                 html.Button(id='clique-state', n_clicks=0, children='Show max-clique',
                             style={'background-color': '#EEFFFD', 'width': '200px'}),
                 html.Div(id='info', style={'position': 'absolute', 'width': '100%'})],
                 style={'position': 'relative'}
             ),
             md=3,
         ),
         dbc.Col(
             dls.Hash(cyto.Cytoscape(
                 id='cytoscape',
                 elements=[],
                 layout={'name': 'concentric'},
                 style={'width': '100%', 'height': '100%', 'position': 'absolute'},
                 stylesheet=stylesheet,
             ),
                 color="#435278",
                 speed_multiplier=2,
                 fullscreen=True,
                 size=100),

             md=9,
         ),
     ],
     style={'display': 'flex', 'position': 'relative', 'top': 0, 'left': 0, 'width': '100%',
            'min-height': '100vh', 'max-height': '100%', 'margin': '5px'}
 ),
 ],
                  )


@callback(Output('info', 'children'),
          Output('cytoscape', 'elements'),
          Input('graph-state', 'n_clicks'),
          Input('clique-state', 'n_clicks'),
          State('input_id', 'value'),
          State('radio', 'value'),
          State('input_token', 'value'))
def update_graph(graph_click, clique_state, id, option, token):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks on button yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if id is not None:
        graph = NetworkGraph(id, option, token)
        graph.get_graph()
        if button_id == 'graph-state':
            return graph.object_description, graph.js['nodes'] + graph.js['links']
        elif button_id == 'clique-state':
            graph.get_max_clique()
            return graph.object_description, graph.clique['nodes'] + graph.clique['links']

        # a = max_clique(graph.nx_graph)
        # print('Плотность: %s' % nx.density(graph.nx_graph))
        # print(a)
    return '', []
