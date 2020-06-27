# coding: utf-8
# !/usr/bin/python3

import json
from os.path import expanduser
import itertools
from collections import defaultdict
import math
import networkx as nx
import heapq
import matplotlib.pyplot as plt
from networkx import Graph


def get_id_author(authorName):
    autID = {}
    for pubblication in data:
        for author in pubblication["authors"]:
            try:
                autID[author["author"]].append(author["author_id"])
            except:
                autID[author["author"]] = author["author_id"]
    return autID[authorName]


####### MAIN ##############
with open("dataset.json") as access_json:
    data = json.load(access_json)

publ_access = data['result']['hits']['hit']

######### DICTIONARY AUTHORS & PUBL ###############
authors_dict = {}
publ_dict = {}
cnt = 0
for i in range(len(publ_access)):
    publ_data = publ_access[i]
    id_publ = publ_data['@id']
    title = publ_data['info']['title']
    publ_info = publ_data['info']

    if 'authors' in publ_info:
        authors_access = publ_info['authors']['author']
        # aut_access = authors_access['author']
        # aut_id = aut_access['@pid']
    else:
        authors_access = "Null"

    if type(str()) == type(authors_access):
        pass  # author NULL
    elif type(list()) == type(authors_access):  # list
        length = len(authors_access)
        for j in range(length):
            aut = authors_access[j]
            authors_dict[cnt] = {'aut_id': aut['@pid'], 'author': aut['text']}
            publ_dict[cnt] = {'publ_id': publ_data['@id'], 'title': title, 'aut_id': aut['@pid']}
            cnt += 1
    elif type(dict()) == type(authors_access):  # dictionary
        authors_dict[cnt] = {'aut_id': authors_access['@pid'], 'author': authors_access['text']}
        publ_dict[cnt] = {'publ_id': publ_data['@id'], 'title': title, 'aut_id': authors_access['@pid']}
        cnt += 1

# print(authors_dict)
# remove duplicate authors in dictionary
aut_dict = {}
for key, value in authors_dict.items():
    if value not in aut_dict.values():
        aut_dict[key] = value
print(aut_dict)
print(publ_dict)

######### GRAPH ##########
G = nx.Graph()
####  NODE author ####
for i in range(len(aut_dict)):
    try:
        G.add_node(aut_dict[i]['aut_id'], id=aut_dict[i]['aut_id'], author=aut_dict[i]['author'])
    except:
        pass

#### EDGE ####
cnt = 0
for i in range(len(publ_access)):
    publ_data = publ_access[i]
    id_publ = publ_data['@id']
    title = publ_data['info']['title']
    publ_info = publ_data['info']

    if 'authors' in publ_info:
        authors_access = publ_info['authors']['author']
    else:
        authors_access = "Null"

    if type(str()) == type(authors_access):
        pass  # author NULL
    elif type(list()) == type(authors_access):  # list
        length = len(authors_access)
        co_aut = []
        for j in range(length):
            aut = authors_access[j]
            co_aut.append(aut['@pid'])
        cnt += length
        # print(co_aut, publ_dict[cnt-1]['publ_id'], cnt-1)
        for k in itertools.combinations(co_aut, 2):
            # print(k,  publ_dict[cnt-1]['publ_id'])
            G.add_edge(k[0], k[1])
            # G.add_edge(k[0], k[1], {'publ_id': publ_dict[cnt - 1]['publ_id'], 'title': publ_dict[cnt - 1]['title']})
    elif type(dict()) == type(authors_access):  # dictionary
        ######## arco con se stesso, publicazione con singolo autore!!!!!!!!!----------
        cnt += 1
        # print(authors_access['@pid'], publ_dict[cnt-1]['publ_id'], cnt-1)
        G.add_edge(authors_access['@pid'], authors_access['@pid'])
        # G.add_edge(authors_access['@pid'], authors_access['@pid'], {'publ_id': publ_dict[cnt-1]['publ_id'], 'title': publ_dict[cnt-1]['title']})
print("drawing.......")
nx.draw_random(G)
# nx.draw_spring(G)
# nx.draw_networkx_edges(G)
# pos = nx.spring_layout(G, iterations=200)
# nx.draw(G, pos, node_color=range(2945), node_size=800, cmap=plt.cm.Blues)
# plt.show()


pos = nx.spring_layout(G)
colors = range(2945)
nx.draw(G, pos, node_color=range(2945), edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=False)
plt.show()