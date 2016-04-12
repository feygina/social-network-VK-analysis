__author__ = 'feygin'

import requests
import networkx
import matplotlib.pyplot as plt
import time
import collections
from networkx.drawing.nx_agraph import graphviz_layout


def get_friends_ids(user_id):
    friends_url = 'https://api.vk.com/method/friends.get?user_id={}'
    json_response = requests.get(friends_url.format(user_id)).json()
    if json_response.get('error'):
        print json_response.get('error')
        return list()
    return json_response[u'response']


graph = {}
friend_ids = get_friends_ids(9106204)
# friend_ids = get_friends_ids(158530417)
for friend_id in friend_ids:
    print 'Processing id: ', friend_id
    graph[friend_id] = get_friends_ids(friend_id)

g = networkx.Graph(directed=False)
for i in graph:
    g.add_node(i)
    for j in graph[i]:
        if i != j and i in friend_ids and j in friend_ids:
            g.add_edge(i, j)

# pos = networkx.graphviz_layout(g, prog="neato")
# networkx.draw(g, pos, node_size=30, with_labels=False, width=0.2)

networkx.write_graphml(g, 'graph.graphml')


networkx.draw(g)
plt.show()
