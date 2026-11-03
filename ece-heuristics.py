import ast
import networkx as nx
import numpy as np
import os
import pandas as pd
import random
import statistics
import sys
import types
from math import inf

########################
# GENERATING INSTANCES #
########################

def generate_instance_from_distribution(dist, n, m):
    utils = [[0] * m for i in range(n)]
    for i in range(n):
        for j in range(m):
            utils[i][j] = dist()

    return utils

def get_instances_filename(source, n, m):
    return f'{source}/{n}-{m}.csv'

def read_instances_from_file(filename):
    df = pd.read_csv(filename)
    return list(map(ast.literal_eval, df['instances'].values))

def normalize(utils):
    for i in range(n):
        utils[i] = list(map(lambda x: x/sum(utils[i]), utils[i]))

    return utils

def get_instances(source, n, m, max_instances):
    if isinstance(source, str):
        instances_file = get_instances_filename(source, n, m)
        unnormalized_instances = read_instances_from_file(instances_file)
        instances = []
        for instance in unnormalized_instances[:max_instances]:
            instances.append(normalize(instance))
        return instances

    elif callable(source):
        instances = []
        for i in range(max_instances):
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
    goods = [f'g{j}' for j in range(m)]
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
            if edge[2]['weight'] >= threshold:
                new_graph.add_edge(edge[0], edge[1], weight = edge[2]['weight'])

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
            g_j = f'g{j}'
            if g_j in matching:
                return (matching[g_j], j)
    else:
        return (unenvied_agents[0], unallocated_goods[0])

###########################
# CHECKING DATA DIRECTORY #
###########################

data_directory = 'data'
if os.path.isdir(data_directory):
    if os.listdir(data_directory):
        print(f'Directory "{data_directory}/" is not empty.')
        while True:
            can_overwrite = input('Overwrite data? (y/n) ')
            match can_overwrite.lower():
                case 'y':
                    break
                case 'n':
                    sys.exit('Program terminated.')
                case _:
                    print('Please input "y" or "n".')
else:
    os.mkdir(data_directory)

##########################
# COMMAND LINE ARGUMENTS #
##########################

print('Run the experiment with:')
print('1) user instances only;')
print('2) probabilistic distributions only;')
print('3) both types of instance distributions.')
while True:
    has_dist = input('Select an option (1/2/3): ')
    match has_dist:
        case '1':
            has_prob_dist, has_user_dist = False, True
            break
        case '2':
            has_prob_dist, has_user_dist = True, False
            break
        case '3':
            has_prob_dist, has_user_dist = True, True
            break
        case _:
            print('Please input "1", "2", or "3".')

if has_user_dist:
    while True:
        instances_directory = input('Enter directory containing user instances (e.g. "instances/spliddit"): ')
        if os.path.isdir(f'{instances_directory}/'):
            break
        print(f'Directory "{instances_directory}/" not found.')
    instances_directory = os.path.normpath(instances_directory)

while True:
    is_smaller = input('Run a smaller version of the experiment? (y/n) ')
    if is_smaller.lower() == 'y':
        while True:
            try:
                max_instances = int(input('Enter maximum number of instances for each distribution (1-10000): '))
            except ValueError:
                print('Please input an integer from 1 to 10000.')
                continue
            if 1 <= max_instances <= 10000:
                break
            else:
                print('Please input an integer from 1 to 10000.')
        break
    elif is_smaller.lower() == 'n':
        max_instances = 10000
        break
    else:
        print('Please input "y" or "n".')

if has_prob_dist:
    while True:
        has_seed = input('Use seeded random number generator? (y/n) ')
        if has_seed.lower() == 'y':
            while True:
                has_custom_seed = input('Use custom seed? (y/n) ')
                if has_custom_seed.lower() == 'y':
                    seed = input('Enter custom seed (any combination of letters, numbers, and symbols): ')
                    break
                elif has_custom_seed.lower() == 'n':
                    seed = 'ece'
                    break
                else:
                    print('Please input "y" or "n".')
            break
        elif has_seed.lower() == 'n':
            seed = None
            break
        else:
            print('Please input "y" or "n".')

    random.seed(seed)

########################
# GENERATING TEST DATA #
########################

col_names = [
    'Instance', 'MUW', 'MEW',
    'No heuristic', 'UW.0', 'EW.0',
    'Agent with max util', 'UW.1', 'EW.1',
    'Good with max util', 'UW.2', 'EW.2',
    'Agent & good with max util (first round only)', 'UW.3', 'EW.3',
    'Agent & good with max util', 'UW.4', 'EW.4',
    'Max-min matching', 'UW.5', 'EW.5']

ece_heuristics = {
    'No heuristic': None,
    'Agent with max util': agent_with_max_util,
    'Good with max util': good_with_max_util,
    'Agent & good with max util (first round only)':
            agent_good_with_max_util_first_round_only,
    'Agent & good with max util': agent_good_with_max_util,
    'Max-min matching': max_min_matching_heuristic}

dists = {}

if has_user_dist:
    dists['user'] = instances_directory

if has_prob_dist:
    prob_dists = {
        'random': random.random,
        'exp': lambda: random.expovariate(1.0),
        'lognorm': lambda: random.lognormvariate(0.0, 1.0)}
    dists.update(prob_dists)

def get_filename(dist_name, n, m):
    return f'{data_directory}/{dist_name}-{n}-{m}.csv'

for dist_name, dist in dists.items():
    print(f'Distribution: {dist_name}')
    for n in [2, 3]:
        for m in range(n, 10):
            output_file = get_filename(dist_name, n, m)
            try:
                instances = get_instances(dist, n, m, max_instances)
            except FileNotFoundError:
                print(f'n = {n}, m = {m}: File "{get_instances_filename(dist, n, m)}" not found.')
                if os.path.exists(output_file):
                    os.remove(output_file)
                continue

            sys.stdout.write(f'n = {n}, m = {m}:     0 out of {len(instances)} instances')
            df = pd.DataFrame(columns = col_names)
            for i in range(len(instances)):
                instance = instances[i]
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

                sys.stdout.write('\r')
                sys.stdout.write(f'n = {n}, m = {m}: {i+1: >5} out of {len(instances)} instances')
            
            print()
            df.to_csv(output_file)

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
        UW = df[f'UW.{i}'].values.tolist()
        UP_inv = list(map(lambda x, y: x/y if y > 0 else 1, UW, MUW))
        try:
            UP_ave = 1/statistics.mean(UP_inv)
        except ZeroDivisionError:
            UP_ave = inf
        UP_aves.append(UP_ave)

        EW = df[f'EW.{i}'].values.tolist()
        EP_inv = list(map(lambda x, y: x/y if y > 0 else 1, EW, MEW))
        try:
            EP_ave = 1/statistics.mean(EP_inv)
        except ZeroDivisionError:
            EP_ave = inf
        EP_aves.append(EP_ave)
    
    return (UP_aves, EP_aves)

summary_col_names = ['Distribution', 'n', 'm'] \
            + [f'UP-{heuristic_name}' for heuristic_name in ece_heuristics.keys()] \
            + [f'EP-{heuristic_name}' for heuristic_name in ece_heuristics.keys()]
df = pd.DataFrame(columns = summary_col_names)

for dist_name in dists:
    for n in [2, 3]:
        for m in range(n, 10):
            try:
                UPs, EPs = process_data(dist_name, n, m)
            except FileNotFoundError:
                continue
            result = [dist_name, n, m] + UPs + EPs
            df.loc[len(df)] = result

df.to_csv('data/summary.csv')
