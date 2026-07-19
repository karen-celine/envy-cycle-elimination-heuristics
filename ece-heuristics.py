import ast
import networkx as nx
import numpy as np
import os
import pandas as pd
import random
import statistics
import types

########################
# GENERATING INSTANCES #
########################

def generate_instance_from_distribution(dist, n, m):
    utils = [[0] * m for i in range(n)]
    for i in range(n):
        for j in range(m):
            utils[i][j] = dist()

    return utils

def read_instances_from_file(filename):
    df = pd.read_csv(filename)
    return list(map(ast.literal_eval, df["instances"].values))

def normalize(utils):
    for i in range(n):
        utils[i] = list(map(lambda x: x/sum(utils[i]), utils[i]))

    return utils

def get_instances(source, n, m):
    if isinstance(source, str):
        unnormalized_instances = read_instances_from_file(
            source + str(n) + "-" + str(m) + ".csv")
        instances = []
        for instance in unnormalized_instances:
            instances.append(normalize(instance))
        return instances

    elif callable(source):
        instances = []
        for i in range(10000):
            instance = generate_instance_from_distribution(source, n, m)
            instances.append(normalize(instance))
        return instances

    else:
        return []

###############################
# FINDING THE OPTIMAL WELFARE #
###############################

def total_util(agent_util, bundle):
    return sum(map(lambda x: agent_util[x], bundle))

def uw(instance, alloc):
    return sum(map(total_util, instance, alloc))

def ew(instance, alloc):
    return min(map(total_util, instance, alloc))

def muw(instance):
    n = len(instance)
    m = len(instance[0])
    instance_transposed = list(zip(*instance))
    return sum(map(lambda g: max(instance_transposed[g]), range(m)))

def find_all_allocs(n, m):
    if m == 1:
        all_allocs = []
        for i in range(n):
            alloc = [[] for k in range(n)]
            alloc[i].append(0)
            all_allocs.append(alloc)
        return all_allocs
    else:
        partial_allocs = find_all_allocs(n, m-1)
        all_allocs = []
        for partial_alloc in partial_allocs:
            for i in range(n):
                alloc = [bundle.copy() for bundle in partial_alloc]
                alloc[i].append(m-1)
                all_allocs.append(alloc)
        return all_allocs

def mew(instance):
    n = len(instance)
    m = len(instance[0])
    return max(map(lambda alloc: ew(instance, alloc), find_all_allocs(n, m)))

##########################################
# ENVY CYCLE ELIMINATION (ECE) ALGORITHM #
##########################################

def has_envy(i, j, instance, alloc):
    return total_util(instance[i], alloc[i]) < total_util(instance[i], alloc[j])

def find_envy_cycle(instance, alloc):
    n = len(instance)

    envy_graph = nx.DiGraph()
    envy_graph.add_nodes_from(range(n))
    for i in range(n):
        for j in range(n):
            if has_envy(i, j, instance, alloc):
                envy_graph.add_edge(i, j)
    
    try:
        return nx.find_cycle(envy_graph)
    except nx.NetworkXNoCycle:
        return []

def find_unenvied_agents(instance, alloc):
    n = len(instance)
    unenvied_agents = []
    for i in range(n):
        is_envied = False
        for j in range(n):
            if has_envy(j, i, instance, alloc):
                is_envied = True
                break
        if not is_envied:
            unenvied_agents.append(i)
    return unenvied_agents

def ece(instance, heuristic = None):
    n = len(instance)
    m = len(instance[0])
    
    unallocated_goods = list(range(m))
    
    alloc = [[] for i in range(n)]
    while unallocated_goods:
        unenvied_agents = find_unenvied_agents(instance, alloc)
        if heuristic:
            agent, good = heuristic(instance, alloc, unenvied_agents, unallocated_goods)
        else:
            agent, good = unenvied_agents[0], unallocated_goods[0]
        alloc[agent].append(good)
        unallocated_goods.remove(good)
    
        envy_cycle = find_envy_cycle(instance, alloc)
        while envy_cycle:
            length = len(envy_cycle)
            new_alloc = alloc.copy()
            for envier, envied in envy_cycle:
                new_alloc[envier] = alloc[envied]
            alloc = new_alloc
            
            envy_cycle = find_envy_cycle(instance, alloc)        
    
    return alloc

####################################
# HEURISTICS FOR THE ECE ALGORITHM #
####################################

def agent_with_max_util(instance, alloc, unenvied_agents, unallocated_goods):
    good = unallocated_goods[0]
    max_util = 0
    agent = unenvied_agents[0]
    for i in unenvied_agents:
        if instance[i][good] > max_util:
            max_util = instance[i][good]
            agent = i
    return (agent, good)

def good_with_max_util(instance, alloc, unenvied_agents, unallocated_goods):
    agent = unenvied_agents[0]
    max_util = 0
    good = unallocated_goods[0]
    for g in unallocated_goods:
        if instance[agent][g] > max_util:
            max_util = instance[agent][g]
            good = g
    return (agent, good)

def agent_good_with_max_util_first_round_only(instance, alloc, unenvied_agents, 
        unallocated_goods):
    max_util = 0
    agent = unenvied_agents[0]
    good = unallocated_goods[0]
    if len(unallocated_goods) == len(instance[0]):
        for i in unenvied_agents:
            for g in unallocated_goods:
                if instance[i][g] > max_util:
                    max_util = instance[i][g]
                    agent, good = i, g
    return (agent, good)

def agent_good_with_max_util(instance, alloc, unenvied_agents, unallocated_goods):
    max_util = 0
    agent = unenvied_agents[0]
    good = unallocated_goods[0]
    for i in unenvied_agents:
        for g in unallocated_goods:
            if instance[i][g] > max_util:
                max_util = instance[i][g]
                agent, good = i, g
    return (agent, good)

def max_min_matching(instance):
    # Create a graph representing the instance
    n, m = len(instance), len(instance[0])
    agents = list(range(n))
    goods = ["g"+str(j) for j in range(m)]
    graph = nx.Graph()
    graph.add_nodes_from(agents, bipartite = 0)
    graph.add_nodes_from(goods, bipartite = 1)
    for i in range(n):
        for j in range(m):
            graph.add_edge(i, goods[j], weight = instance[i][j])

    utils = sorted(sum(instance, []))
    low, high = 0, len(utils)-1

    while low <= high:
        mid = (low + high)//2
        threshold = utils[mid]

        new_graph = nx.Graph()
        new_graph.add_nodes_from(graph.nodes)
        for edge in graph.edges.data():
            if edge[2]["weight"] >= threshold:
                new_graph.add_edge(edge[0], edge[1], weight = edge[2]["weight"])

        if len(nx.bipartite.maximum_matching(new_graph, agents)) == 2*n:
            graph = new_graph
            low = mid+1
        else:
            high = mid-1

    return nx.bipartite.maximum_matching(graph, agents)

def max_min_matching_heuristic(instance, alloc, unenvied_agents, unallocated_goods):
    if len(unallocated_goods) > len(instance[0]) - len(instance):
        matching = max_min_matching(instance)
        for j in unallocated_goods:
            g_j = 'g' + str(j)
            if g_j in matching:
                return (matching[g_j], j)
    else:
        return (unenvied_agents[0], unallocated_goods[0])

########################
# GENERATING TEST DATA #
########################

col_names = [
    "Instance", "MUW", "MEW", 
    "No heuristic", "UW.0", "EW.0",
    "Agent with max util", "UW.1", "EW.1",
    "Good with max util", "UW.2", "EW.2",
    "Agent & good with max util (first round only)", "UW.3", "EW.3", 
    "Agent & good with max util", "UW.4", "EW.4",
    "Max-min matching", "UW.5", "EW.5"]

dists = {
    "random": random.random,
    "exp": lambda: random.expovariate(1.0),
    "lognorm": lambda: random.lognormvariate(0.0, 1.0),
    "spliddit": "instances/spliddit/"}

ece_heuristics = {
    "No heuristic": None,
    "Agent with max util": agent_with_max_util,
    "Good with max util": good_with_max_util,
    "Agent & good with max util (first round only)":
            agent_good_with_max_util_first_round_only,
    "Agent & good with max util": agent_good_with_max_util,
    "Max-min matching": max_min_matching_heuristic}

data_directory = 'data/'
if not os.path.isdir(data_directory):
    os.mkdir(data_directory)

def get_filename(dist_name, n, m):
    return data_directory + dist_name + '-' + str(n) + '-' + str(m) + '.csv'

for dist_name, dist in dists.items():
    for n in [2, 3]:
        for m in range(n, 10):
            df = pd.DataFrame(columns = col_names)
            
            instances = get_instances(dist, n, m)
            for instance in instances:
                result = []

                instance_muw = muw(instance)
                instance_mew = mew(instance)

                result.extend([instance, instance_muw, instance_mew])

                for heuristic in ece_heuristics.values():
                    alloc = ece(instance, heuristic)
                    alloc_uw = uw(instance, alloc)
                    alloc_ew = ew(instance, alloc)
                    result.extend([alloc, alloc_uw, alloc_ew])

                df.loc[len(df)] = result

            filename = get_filename(dist_name, n, m)
            df.to_csv(filename)

##########################
# COMPILING TEST RESULTS #
##########################

def process_data(dist_name, n, m):
    filename = get_filename(dist_name, n, m)
    df = pd.read_csv(filename)
    
    MUW = df['MUW'].values.tolist()
    MEW = df['MEW'].values.tolist()

    UP_aves = []
    EP_aves = []
    for i in range(6):
        UW = df['UW.' + str(i)].values.tolist()
        UP_inv = list(map(lambda x, y: x/y if y > 0 else 1, UW, MUW))
        UP_ave = 1/statistics.mean(UP_inv)
        UP_aves.append(UP_ave)

        EW = df['EW.' + str(i)].values.tolist()
        EP_inv = list(map(lambda x, y: x/y if y > 0 else 1, EW, MEW))
        EP_ave = 1/statistics.mean(EP_inv)
        EP_aves.append(EP_ave)
    
    return (UP_aves, EP_aves)

summary_col_names = ["Distribution", "n", "m"] \
            + ["UP-" + heuristic_name for heuristic_name in ece_heuristics.keys()] \
            + ["EP-" + heuristic_name for heuristic_name in ece_heuristics.keys()]
df = pd.DataFrame(columns = summary_col_names)

for dist_name in dists:
    for n in [2, 3]:
        for m in range(n, 10):
            UPs, EPs = process_data(dist_name, n, m)
            result = [dist_name, n, m] + UPs + EPs
            df.loc[len(df)] = result

df.to_csv('data/summary.csv')
