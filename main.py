__author__ = 'feygin'

import requests
import networkx as nx
import matplotlib.pyplot as plt
import time
import collections


def get_friends_ids(user_id):
    """
    this function returns list of friend's ids
    """
    friends_url = 'https://api.vk.com/method/friends.get?user_id={}'
    json_response = requests.get(friends_url.format(user_id)).json()
    if json_response.get('error'):
        return list()
    return json_response[u'response']


def get_graph_with_friends_connections(friend_ids):
    """
    this function returns graph of friends and connection between them
    """
    graph = {}
    g = networkx.Graph(directed=False)
    for friend_id in friend_ids:
        graph[friend_id] = get_friends_ids(friend_id)
    g = networkx.Graph(directed=False)
    for i in graph:
        g.add_node(i)
        for j in graph[i]:
            if i != j and i in friend_ids and j in friend_ids:
                g.add_edge(i, j)
    return g


def draw_graph(g, parameter,  size_of_nodes):
    """
    draws plot according to parameter of interest and size of nodes
    """
    plt.xkcd()
    plt.figure(1, figsize=(15, 10))
    coord = nx.spring_layout(g)
    nx.draw(g, pos=coord, nodelist=parameter.keys(), node_size=[d*size_of_nodes for d in parameter.values()],
            node_color=parameter.values(), font_size=8, cmap=plt.cm.get_cmap('RdBu_r'), with_labels=False)


def print_full_name_for_id(id_interest):
    response = requests.get('https://api.vk.com/method/users.get?user_ids={}'.format(id_interest)).json()[u'response']
    print response[0][u'first_name'].strip() + ' ' + response[0][u'last_name'].strip()

