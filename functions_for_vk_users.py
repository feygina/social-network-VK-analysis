__author__ = 'feygin'
from vk_token import *

import requests
import networkx as nx
import matplotlib.pyplot as plt
import time
import numpy as np
import scipy.spatial as spt
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
    g = nx.Graph(directed=False)
    for friend_id in friend_ids:
        graph[friend_id] = get_friends_ids(friend_id)
    g = nx.Graph(directed=False)
    for i in graph:
        g.add_node(i)
        for j in graph[i]:
            if i != j and i in friend_ids and j in friend_ids:
                g.add_edge(i, j)
    return g


def draw_graph(g, parameter,  size_of_nodes, number):
    """
    draws plot according to parameter of interest and size of nodes
    """
    node_labels = find_top_nodes(g, parameter, number)
    plt.xkcd()
    plt.figure(1, figsize=(30, 25))
    coord = nx.spring_layout(g)
    nx.draw(g, pos=coord, nodelist=parameter.keys(), node_size=[d*size_of_nodes for d in parameter.values()],
            node_color=list(parameter.values()), font_size=25, cmap=plt.cm.get_cmap('RdBu_r'), labels=node_labels)


def print_full_name_for_id(id_interest):
    """
    :param id_interest: int
    :return: string
    """
    response = requests.get('https://api.vk.com/method/users.get?user_ids={}'.format(id_interest)).json()[u'response']
    print(response[0][u'first_name'].strip() + ' ' + response[0][u'last_name'].strip())


def count_likes(ph):
    owner_id = int(ph.split("_")[0])
    photo_id = int(ph.split("_")[1])
    likes = requests.get('https://api.vk.com/method/likes.getList?type=photo&owner_id=%d&item_id=%d'
                         % (owner_id, photo_id)).json()[u'response']
    return likes[u'count']


def info_about(id_interest):
    resp = requests.get(token.format(id_interest)).json()[u'response']
    if u'photo_id' in resp[0].keys():
        resp[0][u'popularity'] = count_likes(resp[0][u'photo_id'].strip())
    else:
            resp[0][u'popularity'] = 0
    resp[0][u'name'] = resp[0][u'first_name'].strip()+' '+resp[0][u'last_name'].strip()
    if u'schools' in resp[0].keys():
        try:
            resp[0][u'school'] = resp[0][u'schools'][0][u'id']
        except:
            resp[0][u'school'] = 0
    else:
        resp[0][u'school'] = 0
    if u'university' not in resp[0].keys():
        resp[0][u'university'] = 0
    del resp[0][u'first_name']
    del resp[0][u'last_name']
    return resp[0]


def get_friends_information(g):
    for i in nx.nodes(g):
        information = info_about(i)
        if u'deactivated' in information.keys():
            g.remove_node(i)
        else:
            g.node[i]['name'] = information[u'name']
            g.node[i]['popularity'] = information[u'popularity']
            g.node[i]['school'] = information[u'school']
            g.node[i]['university'] = information[u'university']
            g.node[i]['city'] = information[u'city']
            time.sleep(0.25)
            print(g.node[i]['name'] + 'is fine')


def find_top_nodes(g, values, number):
    sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
    best = {i[0]: g.node[i[0]]['name'] for i in sorted_values[0:number]}
    return best


def get_sparse_matrix(graph):
    g_sparse = nx.utils.reverse_cuthill_mckee_ordering(graph)
    reorder_nodes = list(g_sparse)
    a = nx.to_numpy_matrix(graph, nodelist=reorder_nodes, dtype=int)
    a = np.asarray(a)
    return a


def plot_similarity(a):
    f, ax = plt.subplots(2, 2, figsize=(15,10))
    ax[0, 0].imshow(a, cmap='Greens', interpolation='None')
    ax[0, 0].set_title('Adjacency Matrix')

    d = np.corrcoef(a)
    ax[1, 0].imshow(d, cmap='Greens', interpolation='None')
    ax[1, 0].set_title('Correlation coefficient')

    distance = spt.distance.pdist(a, metric='euclidean')
    d = spt.distance.squareform(distance)
    ax[0, 1].imshow(d, cmap='Greens', interpolation='None')
    ax[0, 1].set_title('Euclidean Distance')

    distance = spt.distance.pdist(a, metric='cosine')
    d = spt.distance.squareform(distance)
    ax[1, 1].imshow(d, cmap='Greens', interpolation='None')
    ax[1, 1].set_title('Cosine Distance')


def compare_graphs(graph):
    n = nx.number_of_nodes(graph)
    m = nx.number_of_edges(graph)
    k = np.mean(list(nx.degree(graph).values()))
    erdos = nx.erdos_renyi_graph(n, p=m/float(n*(n-1)/2))
    barabasi = nx.barabasi_albert_graph(n, m=int(k)-7)
    small_world = nx.watts_strogatz_graph(n, int(k), p=0.04)
    print(' ')
    print('Compare the number of edges')
    print(' ')
    print('My network: ' + str(nx.number_of_edges(graph)))
    print('Erdos: ' + str(nx.number_of_edges(erdos)))
    print('Barabasi: ' + str(nx.number_of_edges(barabasi)))
    print('SW: ' + str(nx.number_of_edges(small_world)))
    print(' ')
    print('Compare average clustering coefficients')
    print(' ')
    print('My network: ' + str(nx.average_clustering(graph)))
    print('Erdos: ' + str(nx.average_clustering(erdos)))
    print('Barabasi: ' + str(nx.average_clustering(barabasi)))
    print('SW: ' + str(nx.average_clustering(small_world)))
    print(' ')
    print('Compare average path length')
    print(' ')
    print('My network: ' + str(nx.average_shortest_path_length(graph)))
    print('Erdos: ' + str(nx.average_shortest_path_length(erdos)))
    print('Barabasi: ' + str(nx.average_shortest_path_length(barabasi)))
    print('SW: ' + str(nx.average_shortest_path_length(small_world)))
    print(' ')
    print('Compare graph diameter')
    print(' ')
    print('My network: ' + str(nx.diameter(graph)))
    print('Erdos: ' + str(nx.diameter(erdos)))
    print('Barabasi: ' + str(nx.diameter(barabasi)))
    print('SW: ' + str(nx.diameter(small_world)))

