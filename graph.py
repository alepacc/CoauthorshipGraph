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
from networkx.drawing.nx_agraph import graphviz_layout
import csv
import re
from xml.sax.saxutils import unescape


# distance number of edjes between two nodes
def distance(G, start, end):
    try:
        p = nx.shortest_path(G, source=start, target=end)
        # print("There distance for this nodes is: " + p)
        return len(p) - 1
    except:
        pass
        # print("There is no path between the nodes")


### Extract publication by Json file of graph DBLP
def extract_publication(json):
    publ_dict = {}
    publ_access = json['result']['hits']['hit']
    cnt = 0

    for i in range(len(publ_access)):
        publ_data = publ_access[i]
        id_publ = publ_data['@id']
        title = unescape(publ_data['info']['title'], entities={r"&apos;": r"'", r"&quot;": r'"'})
        publ_info = publ_data['info']

        if 'authors' in publ_info:
            authors_access = publ_info['authors']['author']
        else:
            authors_access = "Null"

        if type(str()) == type(authors_access):
            pass  # author NULL
        elif type(list()) == type(authors_access):  # list
            for j in range(len(authors_access)):
                aut = authors_access[j]
                publ_dict[cnt] = {'publ_id': publ_data['@id'], 'title': title, 'aut_id': aut['@pid'],
                                  'aut_id': aut['@pid'],
                                  'author': unescape(aut['text'], entities={r"&apos;": r"'", r"&quot;": r'"'})}
                cnt += 1
        elif type(dict()) == type(authors_access):  # dictionary
            publ_dict[cnt] = {'publ_id': publ_data['@id'], 'title': title, 'aut_id': authors_access['@pid'],
                              'aut_id': authors_access['@pid'],
                              'author': unescape(authors_access['text'], entities={r"&apos;": r"'", r"&quot;": r'"'})}
            cnt += 1

    return publ_dict


#### Create list of the edges
def get_edges(data_json):
    edges = {}
    cnt = 0
    pos = 0
    publ_access = data_json['result']['hits']['hit']
    for i in range(len(publ_access)):
        publ_data = publ_access[i]
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
            for pair in itertools.combinations(co_aut, 2):
                edges[pos] = (pair[0], pair[1], publ_dict[cnt - 1]['publ_id'],
                              unescape(publ_dict[cnt - 1]['title'], entities={r"&apos;": r"'", r"&quot;": r'"'}))
                pos += 1
        elif type(dict()) == type(authors_access):  # dictionary
            ######## arco con se stesso, publicazione con singolo autore
            cnt += 1
            edges[pos] = (authors_access['@pid'], authors_access['@pid'], publ_dict[cnt - 1]['publ_id'],
                          unescape(publ_dict[cnt - 1]['title'], entities={r"&apos;": r"'", r"&quot;": r'"'}))
            pos += 1

    return edges


### CREATE  Keyword
def get_keywords(csv_file):
    f = open('keywords.csv', 'w')
    f.write("Node,Keyword\n")
    # Skip header
    next(csv_file)
    # loop through csv list
    for row in csv_file:
        # same node
        if row[0] == row[1]:
            result = re.findall('(?!from|with)[A-Z][a-z][a-z][a-z]+', row[3], re.IGNORECASE)
            for r in result:
                f.write("%s,%s\n" % (row[0], r))
        else:  # two node (source, target)
            result = re.findall('(?!from|with)[A-Z][a-z][a-z][a-z]+', row[3], re.IGNORECASE)
            for r in result:
                f.write("%s,%s\n%s,%s\n" % (row[0], r, row[1], r))
    f.close()

    keywords = {}
    in_file = open('keywords.csv', 'r')
    # Skip header
    next(in_file)
    seen = set()  # set for fast O(1) amortized lookup
    i = 0
    for row in in_file:
        if row in seen:
            continue   # skip duplicate
        else:
            seen.add(row)
            x = row.strip().split(",")
            keywords[i] = x[0], x[1]
            i += 1
    in_file.close()

    return keywords


############ MAIN ##############
with open("dataset.json") as access_json:
    data = json.load(access_json)

# extrct data from json
publ_dict = extract_publication(data);

### AUTHORS DICTIONARY
author_dict = {}
for key, value in publ_dict.items():
    author_dict[value['aut_id']] = {'aut_id': value['aut_id'], 'author': value['author']}


### CREATE CSV file with node id and label
with open('nodes.csv', 'w') as f:
    f.write("Id,Label\n")
    for key, val in author_dict.items():
        f.write("%s,%s\n" % (val['aut_id'], val['author']))

#### EDGE dictionary
edges_dict = get_edges(data)

### CREATE CSV file edges
with open('edges.csv', 'w') as f:
    f.write("Source,Target,Label,Publication_name\n")
    for key, val in edges_dict.items():
        f.write("%s,%s,%s,\"%s\"\n" % (val[0], val[1], val[2], val[3]))

### Publication DICTIONARY
publication = {}
for key, value in publ_dict.items():
    publication[value['publ_id']] = {'publ_id': value['publ_id'], 'title': value['title']}


### CREATE CSV Publication
with open('publication.csv', 'w') as f:
    f.write("publ_id,title\n")
    for val in publication.values():
        f.write("%s,\"%s\"\n" % (val['publ_id'], val['title']))

### GRAPH ###
G = nx.Graph()

#### add nodes in graph
for i in range(len(author_dict)):
    try:
        G.add_node(author_dict[i]['aut_id'], id=author_dict[i]['aut_id'], author=author_dict[i]['author'])
    except:
        pass


#### add edges in graph
for k, v in edges_dict.items():
    try:
        G.add_edge(v[0], v[1], publ_id=v[2], title=v[3])
    except:
        pass

#### KEYWORDS
# read csv, and split on "," the line
edges_file = csv.reader(open('edges.csv', "r"), delimiter=",")
keywords_dict = get_keywords(edges_file)
# add keywords to attribute node
for i in range(len(keywords_dict)):
    try:
        G.nodes[keywords_dict[i][0]][keywords_dict[i][1]] = keywords_dict[i][1]
        # attribute_dict = G.nodes.data()
        # a = attribute_dict[keywords_dict[i][0]]
        # if keywords_dict[i][1] in a:
        #     G.nodes[keywords_dict[i][0]][keywords_dict[i][1]] = 2
        # else:
        #     G.nodes[keywords_dict[i][0]][keywords_dict[i][1]] = 1
    except:
        pass

print("\n" + nx.info(G) + "\n")

# h_dis = hop_distance(G, '183/0347', '64/6125')
# # dis = distance('183/0347', '64/6125')
# print(h_dis)

### Drawing graph with NetworkX
# print("drawing.......")
# pos = graphviz_layout(G, prog="twopi", args="")
# plt.figure(figsize=(8, 8))
# labels = nx.get_edge_attributes(G, 'publ_id')
# nx.draw(G, pos, node_size=20, alpha=0.4, node_color=range(2945), with_labels=False)
# plt.axis("equal")
# plt.show()
