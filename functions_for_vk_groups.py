import vk_api
import requests
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import scipy.io
import scipy.stats
import scipy.spatial as spt
from IPython.display import SVG
from vk_login import *


vk_session = vk_api.VkApi(fey_login, fey_password)
vk_session.authorization()
vk = vk_session.get_api()


def fetch_members_ids():
    ids = []
    for i in [1, 1000, 2000]:
        members_url = 'https://api.vk.com/method/groups.getMembers?group_id=49815762&offset={}'
        json_response = requests.get(members_url.format(i)).json()[u'response']['users']
        ids.extend(json_response)
    return ids


def get_members_friends(members_ids):
    # members_friends = {}
    with vk_api.VkRequestsPool(vk_session) as pool:
        members_friends = pool.method_one_param('friends.get', key='user_id', values=members_ids)
    return members_friends


def find_deactivated_members(members_friends):
    deactivated_members = [k for k, v in members_friends.items() if v is False]
    print('From {} members {} are deactivated:\n'.format(len(members_friends), len(deactivated_members)))


def drop_deactivated_members(friends):
    new_friends = {k: v for k, v in friends.items() if v is not False}
    return new_friends


def drop_members_with_hidden_friends(members):
    new_members = {k: v for k, v in members.items() if v['count'] != 0}
    return new_members


def create_members_graph(members):
    graph = nx.Graph(directed=False)
    for i in members:
        graph.add_node(i)
        for j in members[i]['items']:
            if i != j and j in members:
                graph.add_edge(i, j)
    return graph


def make_list_with_members_info(g):
    portions_of_ids = [int(len(g.nodes())/4)*i for i in range(0, 4)] + [len(g.nodes())]
    response = list()
    for i in range(0, 4):
        members_ids = ', '.join(map(str, g.nodes()[portions_of_ids[i]:portions_of_ids[i+1]]))
        response += vk.users.get(user_ids = members_ids, fields = 'sex, city, education', lang = 'en')
    return response


def set_attributes_to_nodes(graph, response, members_friends):
    # name
    g = graph
    member_name = [i['first_name'] + ' ' + i['last_name'] for i in response]
    member_name = dict(zip(g.nodes(), member_name))
    nx.set_node_attributes(g, 'name', member_name)
    # gender
    member_gender = [i['sex'] for i in response]
    member_gender = dict(zip(g.nodes(), member_gender))
    nx.set_node_attributes(g, 'gender', member_gender)
    # city title
    member_city = [i['city']['title'] if 'city' in i else '-' for i in response]
    member_city = dict(zip(g.nodes(), member_city))
    nx.set_node_attributes(g, 'city', member_city)
    # university id
    member_university = [i['university'] if 'university' in i else 0 for i in response]
    member_university = dict(zip(g.nodes(), member_university))
    nx.set_node_attributes(g, 'university', member_university)
    # number of friends (popularity)
    member_friends_count = [members_friends[i]['count'] for i in g.nodes()]
    member_friends_count = dict(zip(g.nodes(), member_friends_count))
    nx.set_node_attributes(g, 'friends', member_friends_count)
    return g


def drop_lonely_users(g, number_of_connections):
    node_degree = nx.degree(g)
    to_remove = [n for n in node_degree if node_degree[n] <= number_of_connections]
    g.remove_nodes_from(to_remove)
    return g