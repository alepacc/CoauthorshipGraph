import time
import re
import csv
import itertools
from collections import Counter

import graph as g


###### KEYWORDS
#### Input Keywords
keys = input('Insert keyword or title of publication: ')
keywords_input = re.findall('(?!from|with)[A-Z][a-z][a-z][a-z]+', keys, re.IGNORECASE)

print(keywords_input)

# groups of nodes for each keywords
groups = {}
for k in keywords_input:
    node = []
    for key in g.keywords_dict.values():
        if key[1] == k:
            node.append(key[0])
    groups[k] = {'nodes': node}

for k, v in groups.items():
    print(k, groups[k])

freq = {}
for k, v in groups.items():
    for item in groups[k]['nodes']:
        if item in freq:
            freq[item] += 1
        else:
            freq[item] = 1

sort_orders = sorted(freq.items(), key=lambda x: x[1], reverse=True)

print("\nList of node that have max number of keywords:")
cnt = 0
max = sort_orders[000][0]
list_of_max = []
for el in sort_orders:
    if el[1] == sort_orders[000][1]:
        list_of_max.append(el[0])
    if el[1] > 1 and cnt < 10:
        print("%s : %d" % (el[0], el[1]))
        cnt += 1

start_time = time.time()
### FINDNIG BEST CO-AUTHORSHIP
result_dict = {}
coaut = {}
i = 0
print("\nKEYWORD\tDISTANCE\tAUTHORS ")
with open('result.csv', 'w') as res:
    res.write("keyword,distance,id_author1,author1,id_author2,author2\n")
    for k, v in groups.items():
        for pair in itertools.combinations(groups[k]['nodes'], 2):
            try:
                dis = g.distance(g.G, pair[0], pair[1])
                # dis = nx.dijkstra_path_length(g.G, pair[0], pair[1])
                if dis is not None:
                    if pair[0] in list_of_max or pair[1] in list_of_max:
                        # if dis <= 2:
                        result_dict[i] = {"keyword": k, "distance": dis, "aut1": pair[0], "name_aut1": g.author_dict[pair[0]]['author'], "aut2": pair[1], "name_aut2": g.author_dict[pair[1]]['author'],}
                        i += 1
                        # print(k+" -> dis:", dis, "- "+pair[0], g.author_dict[pair[0]]['author'], "- "+pair[1], g.author_dict[pair[1]]['author'])
                    res.write("%s,%d,%s,%s,%s,%s\n" % (k, dis, pair[0], g.author_dict[pair[0]]['author'], pair[1], g.author_dict[pair[1]]['author']))
            except:
                pass

print("Find keywords in result.csv")
for dis in range(4):  # distance max
    for k, v in result_dict.items():
        if v['distance'] == dis:
            # print(v)
            print(v["keyword"]+" -> dis:", v["distance"], "- "+v["aut1"], v["name_aut1"], "- "+v["aut2"], v["name_aut2"])

print("----%f----" % (time.time()-start_time))
res.close()

#### EXAMPLES insert keywords
# Effects of Social Network Information on Online Language Learning Performance: A Cross-Continental Experiment
# Game Theory, the Internet of Things and 5G Networks - Utilizing Game Theoretic Models to Characterize Challenging Scenarios
# Analog IC Placement Generation via Neural Networks from Unlabeled Data

