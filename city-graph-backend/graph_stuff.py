import osmnx as ox
import json
from random import randint
import pickle
import networkx as nx
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import math


# place = {'city': 'Kazan', 'country': 'Russia'}
# G = ox.graph_from_place(place, network_type='drive')
# buildings = ox.footprints.footprints_from_place(place, footprint_type='building', retain_invalid=False,
#                                               which_result=1)

with open("./multigraph.p", 'rb') as f:  # notice the r instead of w
    G = pickle.load(f)
with open("./buildings.p", 'rb') as f:  # notice the r instead of w
    buildings = pickle.load(f)

def choose_apartments(N):
    hospitals = []
    apartmentss = []
    n = 10000
    build = buildings.head(n)['building'].to_dict()

    for key, value in build.items():
        if value == 'hospital':
            hospitals.append(key)
        elif value == 'apartments':
            apartmentss.append(key)

    # реализация рандомного выбора
    hospital = hospitals[randint(0, len(hospitals) - 1)]
    apartments = []
    for i in range(N):
        temp = apartmentss[randint(0, len(apartmentss) - 1)]
        if temp not in apartments:
            apartments.append(temp)

    # теперь берем координаты и находим ближайшие узлы

    a = buildings.head(n).to_dict()
    hospitals_dict = {}
    apartments_dict = {}

    coordinates = []

    bounds = a['geometry'][hospital].bounds
    temp = []
    x = (bounds[1] + bounds[3]) / 2
    y = (bounds[0] + bounds[2]) / 2
    temp.append(x)
    temp.append(y)
    nearest_node = ox.get_nearest_node(G, (x, y))
    hospitals_dict[str(nearest_node)] = temp
    coordinates.append(temp)

    for i in apartments:
        bounds = a['geometry'][i].bounds
        temp = []
        x = (bounds[1] + bounds[3]) / 2
        y = (bounds[0] + bounds[2]) / 2
        temp.append(x)
        temp.append(y)
        nearest_node = ox.get_nearest_node(G, (x, y))
        apartments_dict[str(nearest_node)] = temp
        coordinates.append(temp)

    dict_for_items = {}
    dict_for_items['hosp'] = hospitals_dict
    dict_for_items['apart'] = apartments_dict

    with open('coordinates.json', 'w') as f:
        json.dump(dict_for_items, f)

    return coordinates

G_pd = np.load('G_pd.npy')

with open('nodes_numbers.json', 'r') as fp:
    nodes_numbers = json.load(fp)


# вспомогательная функция для подсчета веса дерева и длины кратчайших путей
def tree_weight(tree, matrix):
    end_points = []
    weight = 0
    paths_len = 0
    for i in tree:
        for j in range(len(i) - 1):
            if i[j + 1] not in end_points:
                end_points.append(i[j + 1])
                weight += matrix[nodes_numbers[str(i[j])]][nodes_numbers[str(i[j + 1])]]
            paths_len += matrix[nodes_numbers[str(i[j])]][nodes_numbers[str(i[j + 1])]]

    return weight, paths_len


def short_path_tree():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    hosp_c = list(coordinates['hosp'].values())[0]
    aparts_c = list(coordinates['apart'].values())

    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    routes = []
    route_nodes = []

    for i in aparts_c:
        nearest_node = ox.get_nearest_node(G, (i[0], i[1]))
        route = nx.shortest_path(G,
                                 nearest_node_hosp,
                                 nearest_node,
                                 weight='length')
        node_coordinates = []
        node_coordinates.append([hosp_c[0], hosp_c[1]])
        route_nodes.append(route)
        for node in route:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append([i[0], i[1]])
        routes.append(node_coordinates)

    tree_len, paths_len = tree_weight(route_nodes, G_pd)
    return routes, tree_len, paths_len


# эту функцию вызывать когда пользователь нажимает на кластеризацию
def matrix_for_cluster():
    aparts_routes = {}
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    short_path_matrix = np.zeros((len(aparts_c), len(aparts_c)))
    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    for i in range(len(aparts_c)):
        nearest_node1 = ox.get_nearest_node(G, (aparts_c[i][0], aparts_c[i][1]))
        for j in range(len(aparts_c)):
            if aparts_c[i] != aparts_c[j]:
                r = {}
                nearest_node2 = ox.get_nearest_node(G, (aparts_c[j][0], aparts_c[j][1]))
                route = nx.shortest_path(G,
                                         nearest_node1,
                                         nearest_node2,
                                         weight='length')
                r[nearest_node2] = route
                paths_len = 0
                for temp in range(len(route) - 1):
                    paths_len += G_pd[nodes_numbers[str(route[temp])]][nodes_numbers[str(route[temp + 1])]]
                short_path_matrix[i][j] = paths_len
        aparts_routes[nearest_node1] = r

    matrix_cluster = []
    for i in range(len(short_path_matrix)):
        for j in range(i + 1, len(short_path_matrix)):
            if short_path_matrix[i][j] < short_path_matrix[j][i]:
                matrix_cluster.append(short_path_matrix[i][j])
            else:
                matrix_cluster.append(short_path_matrix[j][i])

    m = {}
    m[0] = matrix_cluster

    with open('matrix_cluster.json', 'w') as f:
        json.dump(m, f)

# а это уже при выборе на сколько кластеров

# если 2 кластера
def cluster2():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    with open('matrix_cluster.json') as f:
        matrix_cluster = json.load(f)
    matrix_cluster = list(matrix_cluster.values())[0]

    Z = linkage(matrix_cluster, 'complete')
    num_clust = 2
    Z2 = fcluster(Z, num_clust, 'maxclust')

    c1 = [0, 0]
    c2 = [0, 0]
    k1 = 0
    k2 = 0

    # складываем соответствующие географические координаты узлов в соответствуюшие списки
    for i in range(len(Z2)):
        key = numbers[i]
        coords = coordinates['apart'][key]
        if Z2[i] == 1:
            c1[0] += coords[0]
            c1[1] += coords[1]
            # и считаем количество узлов в кластере для нахождения средних координат
            k1 += 1
        if Z2[i] == 2:
            c2[0] += coords[0]
            c2[1] += coords[1]
            k2 += 1
    # находим среднее значение координат узлов, т. е., координаты наших центроидов
    for i in range(len(c1)):
        c1[i] /= k1
    for j in range(len(c2)):
        c2[j] /= k2
    # ищем ближайшие узлы для наших центроидов
    center1 = ox.get_nearest_node(G, (c1[0], c1[1]))
    center2 = ox.get_nearest_node(G, (c2[0], c2[1]))

    # Находим кратчайшие пути от объекта до центроидов
    hosp_c = list(coordinates['hosp'].values())[0]
    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    path1 = nx.shortest_path(G, nearest_node_hosp, center1, weight='length')
    path2 = nx.shortest_path(G, nearest_node_hosp, center2, weight='length')
    # считаем сумму этих путей
    paths_len = 0
    tree_weight = 0
    end_points = []
    for temp in range(len(path1) - 1):
        tree_weight += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]
        end_points.append(path1[temp])
        paths_len += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]

    for temp in range(len(path2) - 1):
        if path2[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]
            end_points.append(path2[temp])
        paths_len += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]

    short_paths_c1 = {}
    short_paths_c2 = {}

    short_paths_len_c1 = 0
    short_tree_len_c1 = 0

    short_paths_len_c2 = 0
    short_tree_len_c2 = 0

    end_points = []
    for i in range(len(Z2)):
        temp_number = int(numbers[i])
    for i in range(len(Z2)):
        if Z2[i] == 1:
            temp_number = int(numbers[i])
            try:
                path_c1 = nx.shortest_path(G, center1, temp_number, weight='length')
                short_paths_c1[temp_number] = path_c1

                for temp in range(len(path_c1) - 1):
                    if path_c1[temp] not in end_points:
                        short_tree_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
                        end_points.append(path_c1[temp])
                    short_paths_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        else:
            temp_number = int(numbers[i])
            try:
                path_c2 = nx.shortest_path(G, center2, temp_number, weight='length')
                short_paths_c2[temp_number] = path_c2

                for temp in range(len(path_c2) - 1):
                    if path_c2[temp] not in end_points:
                        short_tree_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
                        end_points.append(path_c2[temp])
                    short_paths_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
            except nx.NetworkXNoPath:
                pass

    # длина дерева кратчайших путей от объекта до узлов кластера
    tree_sum1 = tree_weight + short_tree_len_c1 + short_tree_len_c2
    # сумма длин кратчайших путей
    paths_sum1 = paths_len + short_paths_len_c1 + short_paths_len_c2

    # сохраняю координаты всех путей
    # сначала от больницы до центроид
    node_coordinates = []
    routes_from_hosp = []

    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path1:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c1[0], c1[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c1 = []
    # теперь от центроид до узлов
    for i in short_paths_c1.keys():
        node_coordinates = []
        node_coordinates.append([c1[0], c1[1]])
        r_value = short_paths_c1[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c1.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path2:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c2[0], c2[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c2 = []
    # теперь от центроид до узлов
    for i in short_paths_c2.keys():
        node_coordinates = []
        node_coordinates.append([c2[0], c2[1]])
        r_value = short_paths_c2[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c2.append(node_coordinates)

    all_routes = []
    all_routes.append(routes_from_hosp)
    all_routes.append(routes_c1)
    all_routes.append(routes_c2)
    print(tree_sum1, paths_sum1)
    return [hosp_c[0], hosp_c[1]], [[c1[0], c1[1]], [c2[0], c2[1]]], all_routes, tree_sum1, paths_sum1

# если 3 кластера
def cluster3():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    with open('matrix_cluster.json') as f:
        matrix_cluster = json.load(f)
    matrix_cluster = list(matrix_cluster.values())[0]

    Z = linkage(matrix_cluster, 'complete')
    num_clust = 3
    Z2 = fcluster(Z, num_clust, 'maxclust')

    c1 = [0, 0]
    c2 = [0, 0]
    c3 = [0, 0]
    k1 = 0
    k2 = 0
    k3 = 0

    # складываем соответствующие географические координаты узлов в соответствуюшие списки
    for i in range(len(Z2)):
        key = numbers[i]
        coords = coordinates['apart'][key]
        if Z2[i] == 1:
            c1[0] += coords[0]
            c1[1] += coords[1]
            # и считаем количество узлов в кластере для нахождения средних координат
            k1 += 1
        if Z2[i] == 2:
            c2[0] += coords[0]
            c2[1] += coords[1]
            k2 += 1
        if Z2[i] == 3:
            c3[0] += coords[0]
            c3[1] += coords[1]
            k3 += 1
    # находим среднее значение координат узлов, т. е., координаты наших центроидов
    for i in range(len(c1)):
        c1[i] /= k1
    for j in range(len(c2)):
        c2[j] /= k2
    for g in range(len(c3)):
        c3[g] /= k3
    # ищем ближайшие узлы для наших центроидов
    center1 = ox.get_nearest_node(G, (c1[0], c1[1]))
    center2 = ox.get_nearest_node(G, (c2[0], c2[1]))
    center3 = ox.get_nearest_node(G, (c3[0], c3[1]))

    # Находим кратчайшие пути от объекта до центроидов
    hosp_c = list(coordinates['hosp'].values())[0]
    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    path1 = nx.shortest_path(G, nearest_node_hosp, center1, weight='length')
    path2 = nx.shortest_path(G, nearest_node_hosp, center2, weight='length')
    path3 = nx.shortest_path(G, nearest_node_hosp, center3, weight='length')
    # считаем сумму этих путей
    paths_len = 0
    tree_weight = 0
    end_points = []
    for temp in range(len(path1) - 1):
        tree_weight += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]
        end_points.append(path1[temp])
        paths_len += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]

    for temp in range(len(path2) - 1):
        if path2[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]
            end_points.append(path2[temp])
        paths_len += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]

    for temp in range(len(path3) - 1):
        if path3[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]
            end_points.append(path3[temp])
        paths_len += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]

    short_paths_c1 = {}
    short_paths_c2 = {}
    short_paths_c3 = {}

    short_paths_len_c1 = 0
    short_tree_len_c1 = 0

    short_paths_len_c2 = 0
    short_tree_len_c2 = 0

    short_paths_len_c3 = 0
    short_tree_len_c3 = 0

    end_points = []
    for i in range(len(Z2)):
        if Z2[i] == 1:
            temp_number = int(numbers[i])
            try:
                path_c1 = nx.shortest_path(G, center1, temp_number, weight='length')
                short_paths_c1[temp_number] = path_c1

                for temp in range(len(path_c1) - 1):
                    if path_c1[temp] not in end_points:
                        short_tree_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
                        end_points.append(path_c1[temp])
                    short_paths_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 2:
            temp_number = int(numbers[i])
            try:
                path_c2 = nx.shortest_path(G, center2, temp_number, weight='length')
                short_paths_c2[temp_number] = path_c2

                for temp in range(len(path_c2) - 1):
                    if path_c2[temp] not in end_points:
                        short_tree_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
                        end_points.append(path_c2[temp])
                    short_paths_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        else:
            temp_number = int(numbers[i])
            try:
                path_c3 = nx.shortest_path(G, center3, temp_number, weight='length')
                short_paths_c3[temp_number] = path_c3

                for temp in range(len(path_c3) - 1):
                    if path_c3[temp] not in end_points:
                        short_tree_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
                        end_points.append(path_c3[temp])
                    short_paths_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
            except nx.NetworkXNoPath:
                pass

    # длина дерева кратчайших путей от объекта до узлов кластера
    tree_sum1 = tree_weight + short_tree_len_c1 + short_tree_len_c2 + short_tree_len_c3
    # сумма длин кратчайших путей
    paths_sum1 = paths_len + short_paths_len_c1 + short_paths_len_c2 + short_paths_len_c3

    # сохраняю координаты всех путей
    # сначала от больницы до центроид
    node_coordinates = []
    routes_from_hosp = []

    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path1:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c1[0], c1[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c1 = []
    # теперь от центроид до узлов
    for i in short_paths_c1.keys():
        node_coordinates = []
        node_coordinates.append([c1[0], c1[1]])
        r_value = short_paths_c1[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c1.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path2:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c2[0], c2[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c2 = []
    # теперь от центроид до узлов
    for i in short_paths_c2.keys():
        node_coordinates = []
        node_coordinates.append([c2[0], c2[1]])
        r_value = short_paths_c2[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c2.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path3:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c3[0], c3[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c3 = []
    # теперь от центроид до узлов
    for i in short_paths_c3.keys():
        node_coordinates = []
        node_coordinates.append([c3[0], c3[1]])
        r_value = short_paths_c3[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c3.append(node_coordinates)

    all_routes = []
    all_routes.append(routes_from_hosp)
    all_routes.append(routes_c1)
    all_routes.append(routes_c2)
    all_routes.append(routes_c3)

    return [hosp_c[0], hosp_c[1]], [[c1[0], c1[1]], [c2[0], c2[1]], [c3[0], c3[1]]], all_routes, tree_sum1, paths_sum1

# если 5 кластеров
def cluster5():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    with open('matrix_cluster.json') as f:
        matrix_cluster = json.load(f)
    matrix_cluster = list(matrix_cluster.values())[0]

    Z = linkage(matrix_cluster, 'complete')
    num_clust = 5
    Z2 = fcluster(Z, num_clust, 'maxclust')

    c1 = [0, 0]
    c2 = [0, 0]
    c3 = [0, 0]
    c4 = [0, 0]
    c5 = [0, 0]
    k1 = 0
    k2 = 0
    k3 = 0
    k4 = 0
    k5 = 0

    # складываем соответствующие географические координаты узлов в соответствуюшие списки
    for i in range(len(Z2)):
        key = numbers[i]
        coords = coordinates['apart'][key]
        if Z2[i] == 1:
            c1[0] += coords[0]
            c1[1] += coords[1]
            # и считаем количество узлов в кластере для нахождения средних координат
            k1 += 1
        if Z2[i] == 2:
            c2[0] += coords[0]
            c2[1] += coords[1]
            k2 += 1
        if Z2[i] == 3:
            c3[0] += coords[0]
            c3[1] += coords[1]
            k3 += 1
        if Z2[i] == 4:
            c4[0] += coords[0]
            c4[1] += coords[1]
            k4 += 1
        if Z2[i] == 5:
            c5[0] += coords[0]
            c5[1] += coords[1]
            k5 += 1
    # находим среднее значение координат узлов, т. е., координаты наших центроидов
    for i in range(len(c1)):
        c1[i] /= k1
    for j in range(len(c2)):
        c2[j] /= k2
    for g in range(len(c3)):
        c3[g] /= k3
    for i in range(len(c4)):
        c4[i] /= k4
    for j in range(len(c5)):
        c5[j] /= k5
    # ищем ближайшие узлы для наших центроидов
    center1 = ox.get_nearest_node(G, (c1[0], c1[1]))
    center2 = ox.get_nearest_node(G, (c2[0], c2[1]))
    center3 = ox.get_nearest_node(G, (c3[0], c3[1]))
    center4 = ox.get_nearest_node(G, (c4[0], c4[1]))
    center5 = ox.get_nearest_node(G, (c5[0], c5[1]))

    # Находим кратчайшие пути от объекта до центроидов
    hosp_c = list(coordinates['hosp'].values())[0]
    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    path1 = nx.shortest_path(G, nearest_node_hosp, center1, weight='length')
    path2 = nx.shortest_path(G, nearest_node_hosp, center2, weight='length')
    path3 = nx.shortest_path(G, nearest_node_hosp, center3, weight='length')
    path4 = nx.shortest_path(G, nearest_node_hosp, center4, weight='length')
    path5 = nx.shortest_path(G, nearest_node_hosp, center5, weight='length')
    # считаем сумму этих путей
    paths_len = 0
    tree_weight = 0
    end_points = []
    for temp in range(len(path1) - 1):
        tree_weight += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]
        end_points.append(path1[temp])
        paths_len += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]

    for temp in range(len(path2) - 1):
        if path2[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]
            end_points.append(path2[temp])
        paths_len += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]

    for temp in range(len(path3) - 1):
        if path3[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]
            end_points.append(path3[temp])
        paths_len += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]

    for temp in range(len(path4) - 1):
        if path4[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path4[temp])]][nodes_numbers[str(path4[temp + 1])]]
            end_points.append(path4[temp])
        paths_len += G_pd[nodes_numbers[str(path4[temp])]][nodes_numbers[str(path4[temp + 1])]]

    for temp in range(len(path5) - 1):
        if path5[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path5[temp])]][nodes_numbers[str(path5[temp + 1])]]
            end_points.append(path5[temp])
        paths_len += G_pd[nodes_numbers[str(path5[temp])]][nodes_numbers[str(path5[temp + 1])]]

    short_paths_c1 = {}
    short_paths_c2 = {}
    short_paths_c3 = {}
    short_paths_c4 = {}
    short_paths_c5 = {}

    short_paths_len_c1 = 0
    short_tree_len_c1 = 0

    short_paths_len_c2 = 0
    short_tree_len_c2 = 0

    short_paths_len_c3 = 0
    short_tree_len_c3 = 0

    short_paths_len_c4 = 0
    short_tree_len_c4 = 0

    short_paths_len_c5 = 0
    short_tree_len_c5 = 0

    end_points = []
    for i in range(len(Z2)):
        if Z2[i] == 1:
            temp_number = int(numbers[i])
            try:
                path_c1 = nx.shortest_path(G, center1, temp_number, weight='length')
                short_paths_c1[temp_number] = path_c1

                for temp in range(len(path_c1) - 1):
                    if path_c1[temp] not in end_points:
                        short_tree_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
                        end_points.append(path_c1[temp])
                    short_paths_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 2:
            temp_number = int(numbers[i])
            try:
                path_c2 = nx.shortest_path(G, center2, temp_number, weight='length')
                short_paths_c2[temp_number] = path_c2

                for temp in range(len(path_c2) - 1):
                    if path_c2[temp] not in end_points:
                        short_tree_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
                        end_points.append(path_c2[temp])
                    short_paths_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 3:
            temp_number = int(numbers[i])
            try:
                path_c3 = nx.shortest_path(G, center3, temp_number, weight='length')
                short_paths_c3[temp_number] = path_c3

                for temp in range(len(path_c3) - 1):
                    if path_c3[temp] not in end_points:
                        short_tree_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
                        end_points.append(path_c3[temp])
                    short_paths_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 4:
            temp_number = int(numbers[i])
            try:
                path_c4 = nx.shortest_path(G, center4, temp_number, weight='length')
                short_paths_c4[temp_number] = path_c4

                for temp in range(len(path_c4) - 1):
                    if path_c4[temp] not in end_points:
                        short_tree_len_c4 += G_pd[nodes_numbers[str(path_c4[temp])]][nodes_numbers[str(path_c4[temp + 1])]]
                        end_points.append(path_c4[temp])
                    short_paths_len_c4 += G_pd[nodes_numbers[str(path_c4[temp])]][nodes_numbers[str(path_c4[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        else:
            temp_number = int(numbers[i])
            try:
                path_c5 = nx.shortest_path(G, center5, temp_number, weight='length')
                short_paths_c5[temp_number] = path_c5

                for temp in range(len(path_c5) - 1):
                    if path_c5[temp] not in end_points:
                        short_tree_len_c5 += G_pd[nodes_numbers[str(path_c5[temp])]][nodes_numbers[str(path_c5[temp + 1])]]
                        end_points.append(path_c5[temp])
                    short_paths_len_c5 += G_pd[nodes_numbers[str(path_c5[temp])]][nodes_numbers[str(path_c5[temp + 1])]]
            except nx.NetworkXNoPath:
                pass

    # длина дерева кратчайших путей от объекта до узлов кластера
    tree_sum1 = tree_weight + short_tree_len_c1 + short_tree_len_c2 + short_tree_len_c3 + short_tree_len_c4 + short_tree_len_c5
    # сумма длин кратчайших путей
    paths_sum1 = paths_len + short_paths_len_c1 + short_paths_len_c2 + short_paths_len_c3 + short_paths_len_c4 + short_paths_len_c5

    # сохраняю координаты всех путей
    # сначала от больницы до центроид
    node_coordinates = []
    routes_from_hosp = []

    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path1:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c1[0], c1[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c1 = []
    # теперь от центроид до узлов
    for i in short_paths_c1.keys():
        node_coordinates = []
        node_coordinates.append([c1[0], c1[1]])
        r_value = short_paths_c1[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c1.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path2:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c2[0], c2[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c2 = []
    # теперь от центроид до узлов
    for i in short_paths_c2.keys():
        node_coordinates = []
        node_coordinates.append([c2[0], c2[1]])
        r_value = short_paths_c2[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c2.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path3:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c3[0], c3[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c3 = []
    # теперь от центроид до узлов
    for i in short_paths_c3.keys():
        node_coordinates = []
        node_coordinates.append([c3[0], c3[1]])
        r_value = short_paths_c3[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c3.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path4:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c4[0], c4[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c4 = []
    # теперь от центроид до узлов
    for i in short_paths_c4.keys():
        node_coordinates = []
        node_coordinates.append([c4[0], c4[1]])
        r_value = short_paths_c4[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c4.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path5:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c5[0], c5[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c5 = []
    # теперь от центроид до узлов
    for i in short_paths_c5.keys():
        node_coordinates = []
        node_coordinates.append([c5[0], c5[1]])
        r_value = short_paths_c5[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c5.append(node_coordinates)

    all_routes = []
    all_routes.append(routes_from_hosp)
    all_routes.append(routes_c1)
    all_routes.append(routes_c2)
    all_routes.append(routes_c3)
    all_routes.append(routes_c4)
    all_routes.append(routes_c5)

    return [hosp_c[0], hosp_c[1]], [[c1[0], c1[1]], [c2[0], c2[1]], [c3[0], c3[1]], [c4[0], c4[1]],
                                    [c5[0], c5[1]]], all_routes, tree_sum1, paths_sum1


# первый список - это координаты больниц
# второй список - координаты первого, второго центроида
# all_routes - список двух списков: первый - дерево от больницы до всех узлов первого кластера,
#                                   второй - дерево от больницы до всех узлов второго кластера
# tree_sum1 - вес полученного общего дерева
# paths_sum1 - сумма длин всех кратчайших расстояний обоих кластеров

def coordinates_and_matrix(N1, N2):
    # N1 - количество больниц
    # N2 - количество домов

    hospitalss = []
    apartmentss = []
    n = 10000
    build = buildings.head(n)['building'].to_dict()

    for key, value in build.items():
        if value == 'hospital':
            hospitalss.append(key)
        elif value == 'apartments':
            apartmentss.append(key)

    # реализация рандомного выбора
    hospitals = []
    i = 0
    while i != N1:
        temp = hospitalss[randint(0, len(hospitalss) - 1)]
        if temp not in hospitals:
            hospitals.append(temp)
            i += 1
    apartments = []
    i = 0
    while i != N2:
        temp = apartmentss[randint(0, len(apartmentss) - 1)]
        if temp not in apartments:
            apartments.append(temp)
            i += 1

    # теперь берем координаты и находим ближайшие узлы

    a = buildings.head(n).to_dict()
    hospitals_dict = {}
    apartments_dict = {}

    coordinates = []
    cord_hosp = []
    cord_aparts = []

    numbers_of_nodes = {'apart': {'id_to_number': {}, 'number_to_id': {}},
                        'hosp': {'id_to_number': {}, 'number_to_id': {}}}
    count = 0

    for i in apartments:
        bounds = a['geometry'][i].bounds
        temp = []
        x = (bounds[1] + bounds[3]) / 2
        y = (bounds[0] + bounds[2]) / 2
        temp.append(x)
        temp.append(y)
        nearest_node = ox.get_nearest_node(G, (x, y))
        apartments_dict[str(nearest_node)] = temp
        cord_aparts.append(temp)
        numbers_of_nodes['apart']['id_to_number'][str(nearest_node)] = count
        numbers_of_nodes['apart']['number_to_id'][count] = str(nearest_node)
        count += 1

    for i in hospitals:
        bounds = a['geometry'][i].bounds
        temp = []
        x = (bounds[1] + bounds[3]) / 2
        y = (bounds[0] + bounds[2]) / 2
        temp.append(x)
        temp.append(y)
        nearest_node = ox.get_nearest_node(G, (x, y))
        hospitals_dict[str(nearest_node)] = temp
        cord_hosp.append(temp)
        numbers_of_nodes['hosp']['id_to_number'][str(nearest_node)] = count
        numbers_of_nodes['hosp']['number_to_id'][count] = str(nearest_node)
        count += 1

    coordinates.append(cord_hosp)
    coordinates.append(cord_aparts)

    dict_for_items = {}
    dict_for_items['hosp'] = hospitals_dict
    dict_for_items['apart'] = apartments_dict

    matrix_of_short_paths = np.zeros((N1 + N2, N1 + N2))

    for i in range(N2):
        for j in range(N2 + N1):
            if j >= N2:
                node2 = int(numbers_of_nodes['hosp']['number_to_id'][j])
            if j < N2:
                node2 = int(numbers_of_nodes['apart']['number_to_id'][j])
            if i != j:
                node1 = int(numbers_of_nodes['apart']['number_to_id'][i])
                dist = nx.shortest_path_length(G, node1, node2, weight='length')
                matrix_of_short_paths[i][j] = dist

    for i in range(N2, N2 + N1):
        for j in range(N2 + N1):
            if j >= N2:
                node2 = int(numbers_of_nodes['hosp']['number_to_id'][j])
            if j < N2:
                node2 = int(numbers_of_nodes['apart']['number_to_id'][j])
            if i != j:
                node1 = int(numbers_of_nodes['hosp']['number_to_id'][i])
                dist = nx.shortest_path_length(G, node1, node2, weight='length')
                matrix_of_short_paths[i][j] = dist

    np.save('dist_matrix.npy', matrix_of_short_paths)
    with open('coordinates_task1.json', 'w') as f:
        json.dump(dict_for_items, f)

    with open('numbers_of_nodes.json', 'w') as f:
        json.dump(numbers_of_nodes, f)

    return coordinates


def find_nearest_hospitals_1a(apart_count=100):
    dist_matrix = np.load('dist_matrix.npy')
    nearest_hosp_list = [[-1 for i in range(3)] for j in range(apart_count)]
    for i in range(apart_count):
        nearest_hosp_list[i][0] = np.argmin(dist_matrix[i][apart_count:]) + apart_count
        nearest_hosp_list[i][1] = np.argmin(np.array(dist_matrix[apart_count:]).transpose()[i]) + apart_count
        tuda = dist_matrix[i][apart_count:]
        suda = np.array(dist_matrix[apart_count:]).transpose()[i]
        nearest_hosp_list[i][2] = np.argmin(tuda + suda) + apart_count

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)


    tuda_suda = {'tuda': {}, 'suda': {}, 'tuda_suda': {}}

    for i in range(len(nearest_hosp_list)):
        apart = int(numbers_of_nodes['apart']['number_to_id'][str(i)])
        hosp_tuda = int(numbers_of_nodes['hosp']['number_to_id'][str(nearest_hosp_list[i][0])])
        hosp_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(nearest_hosp_list[i][1])])
        hosp_tuda_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(nearest_hosp_list[i][2])])

        route_tuda = nx.shortest_path(G,
                                      apart,
                                      hosp_tuda,
                                      weight='length')
        route_suda = nx.shortest_path(G,
                                      hosp_suda,
                                      apart,
                                      weight='length')
        temp1 = nx.shortest_path(G,
                                 apart,
                                 hosp_tuda_suda,
                                 weight='length')
        temp2 = nx.shortest_path(G,
                                 hosp_tuda_suda,
                                 apart,
                                 weight='length')
        route_tuda_suda = temp1 + temp2

        node_coordinates = []
        node_coordinates.append(coordinates['apart'][str(apart)])
        for node in route_tuda:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['hosp'][str(hosp_tuda)])
        tuda_suda['tuda'][str(apart)] = node_coordinates

        node_coordinates = []
        node_coordinates.append(coordinates['hosp'][str(hosp_suda)])
        for node in route_suda:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(apart)])
        tuda_suda['suda'][str(apart)] = node_coordinates

        node_coordinates = []
        node_coordinates.append(coordinates['apart'][str(apart)])
        for node in route_tuda_suda:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(apart)])
        tuda_suda['tuda_suda'][str(apart)] = node_coordinates

        with open('tuda_suda.json', 'w') as f:
            json.dump(tuda_suda, f)


def tuda(apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c

    with open('tuda_suda.json') as f:
        tuda_suda = json.load(f)

    route = tuda_suda['tuda'][node]

    return route


def suda(apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)
    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c

    with open('tuda_suda.json') as f:
        tuda_suda = json.load(f)

    route = tuda_suda['suda'][node]

    return route


def tuda_suda(apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)
    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c

    with open('tuda_suda.json') as f:
        tuda_suda = json.load(f)

    route = tuda_suda['tuda_suda'][node]

    return route


def find_in_radius_1b(radius, apart_count=100):
    dist_matrix = np.load('dist_matrix.npy')
    permissible_hosps = [[[] for i in range(3)] for j in range(apart_count)]
    for i in range(apart_count):
        for j in range(apart_count, len(dist_matrix)):
            if dist_matrix[i][j] <= radius:
                permissible_hosps[i][0].append(j)
            if dist_matrix[j][i] <= radius:
                permissible_hosps[i][1].append(j)
            if dist_matrix[i][j] + dist_matrix[j][i] <= radius:
                permissible_hosps[i][2].append(j)

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    tuda_suda_radius = {'tuda': {}, 'suda': {}, 'tuda_suda': {}}

    for i in range(len(permissible_hosps)):
        apart = int(numbers_of_nodes['apart']['number_to_id'][str(i)])

        temp_cord = []
        for j in range(len(permissible_hosps[i][0])):
            hosp_tuda = int(numbers_of_nodes['hosp']['number_to_id'][str(permissible_hosps[i][0][j])])
            route_tuda = nx.shortest_path(G,
                                          apart,
                                          hosp_tuda,
                                          weight='length')
            node_coordinates = []
            node_coordinates.append(coordinates['apart'][str(apart)])
            for node in route_tuda:
                temp = []
                temp.append(G.nodes[node]['y'])
                temp.append(G.nodes[node]['x'])
                node_coordinates.append(temp)
            node_coordinates.append(coordinates['hosp'][str(hosp_tuda)])
            temp_cord.append(node_coordinates)
        tuda_suda_radius['tuda'][str(apart)] = temp_cord

        temp_cord = []
        for j in range(len(permissible_hosps[i][1])):
            hosp_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(permissible_hosps[i][1][j])])
            route_suda = nx.shortest_path(G,
                                          hosp_suda,
                                          apart,
                                          weight='length')
            node_coordinates = []
            node_coordinates.append(coordinates['hosp'][str(hosp_suda)])
            for node in route_suda:
                temp = []
                temp.append(G.nodes[node]['y'])
                temp.append(G.nodes[node]['x'])
                node_coordinates.append(temp)
            node_coordinates.append(coordinates['apart'][str(apart)])
            temp_cord.append(node_coordinates)
        tuda_suda_radius['suda'][str(apart)] = temp_cord

        temp_cord = []
        for j in range(len(permissible_hosps[i][2])):
            hosp_tuda_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(permissible_hosps[i][2][j])])
            temp1 = nx.shortest_path(G,
                                     apart,
                                     hosp_tuda_suda,
                                     weight='length')
            temp2 = nx.shortest_path(G,
                                     hosp_tuda_suda,
                                     apart,
                                     weight='length')
            route_tuda_suda = temp1 + temp2

            node_coordinates = []
            node_coordinates.append(coordinates['apart'][str(apart)])
            for node in route_tuda_suda:
                temp = []
                temp.append(G.nodes[node]['y'])
                temp.append(G.nodes[node]['x'])
                node_coordinates.append(temp)
            node_coordinates.append(coordinates['apart'][str(apart)])
            temp_cord.append(node_coordinates)
        tuda_suda_radius['tuda_suda'][str(apart)] = temp_cord

    with open('tuda_suda_radius.json', 'w') as f:
        json.dump(tuda_suda_radius, f)


def tuda_radius(apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)
    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c
    with open('tuda_suda_radius.json') as f:
        tuda_suda = json.load(f)
    routes = tuda_suda['tuda'][node]
    return routes


def suda_radius(apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)
    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c
    with open('tuda_suda_radius.json') as f:
        tuda_suda = json.load(f)
    routes = tuda_suda['suda'][node]
    return routes


def tuda_suda_radius(apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)
    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c
    with open('tuda_suda_radius.json') as f:
        tuda_suda = json.load(f)
    routes = tuda_suda['tuda_suda'][node]
    return routes


# эта функция находит больницы, которые расположены так, что время/расстояние между ними и
# самым дальним домом минимально (“туда”, “обратно”, “туда и обратно”).

# функция возвращает координаты трех точек(больниц) в списке в следующей последовательности:
# координата больницы для "туда", координата больницы для "обратно", координата больницы для "туда обратно"
# эти точки как-нибудь изобразить на карте
def get_optimal_hospitals_2(apart_count=100):
    dist_matrix = np.load('dist_matrix.npy')
    # везде на вход матрица кратчайших расстояний и количество домов!
    optimal_hosps = []
    tuda = np.array(dist_matrix[:apart_count]).transpose()[apart_count:]
    optimal_hosps.append(np.argmin(np.amax(tuda, 1)) + apart_count)
    suda = np.array(dist_matrix[apart_count:])[:, :apart_count]
    optimal_hosps.append(np.argmin(np.amax(suda, 1)) + apart_count)
    tuda_suda = tuda + suda
    optimal_hosps.append(np.argmin(np.amax(tuda_suda, 1)) + apart_count)

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    hosp1 = numbers_of_nodes['hosp']['number_to_id'][str(optimal_hosps[0])]
    hosp2 = numbers_of_nodes['hosp']['number_to_id'][str(optimal_hosps[1])]
    hosp3 = numbers_of_nodes['hosp']['number_to_id'][str(optimal_hosps[2])]

    hosp1_c = coordinates['hosp'][hosp1]
    hosp2_c = coordinates['hosp'][hosp2]
    hosp3_c = coordinates['hosp'][hosp3]

    optimal_hosps_c = []
    optimal_hosps_c.append(hosp1_c)
    optimal_hosps_c.append(hosp2_c)
    optimal_hosps_c.append(hosp3_c)

    return optimal_hosps_c


# здесь возвращается одна больница, для которой сумма кратчайших расстояний от нее до всех
# домов минимальна.

# координаты одной больницы
def min_sum_hosp_3(apart_count=100):
    dist_matrix = np.load('dist_matrix.npy')
    dist_sums = np.array(dist_matrix[apart_count:])[:, :apart_count]
    dist_sums = np.sum(dist_sums, 1)

    hosp = np.argmin(dist_sums) + apart_count

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    hosp1 = numbers_of_nodes['hosp']['number_to_id'][str(hosp)]

    hosp1_c = coordinates['hosp'][hosp1]

    return hosp1_c

# возвращает больницу, для которой дерево кратчайших путей минимально
# в качестве аргумента нудно передать количество домов

# координаты больницы
def short_tree_4(N2):
    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    aparts = list(numbers_of_nodes['apart']['number_to_id'].values())

    hosps = list(numbers_of_nodes['hosp']['number_to_id'].values())

    end_points = []
    trees_len = []
    for i in hosps:
        short_tree_len = 0
        for j in aparts:
            route = nx.shortest_path(G,
                                     int(i),
                                     int(j),
                                     weight='length')
            for temp in range(len(route) - 1):
                if route[temp] not in end_points:
                    short_tree_len += G_pd[nodes_numbers[str(route[temp])]][nodes_numbers[str(route[temp + 1])]]
                    end_points.append(route[temp])
        trees_len.append(short_tree_len)

    minimal = trees_len[0]
    hosp_n = 0
    for i in range(len(trees_len)):
        if trees_len[i] < minimal:
            minimal = trees_len[i]
            hosp_n = i

    hosp = numbers_of_nodes['hosp']['number_to_id'][str(hosp_n + N2)]

    hosp_c = coordinates['hosp'][hosp]

    return hosp_c



# для того, чтобы найти объекты в радиусе, нужна функция для подсчета расстояния между географическими координатами
def distance(geo_cor1, geo_cor2):
    rad = 6372795

    # координаты двух точек
    llat1 = geo_cor1[0]
    llong1 = geo_cor1[1]

    llat2 = geo_cor2[0]
    llong2 = geo_cor2[1]

    # в радианах
    lat1 = llat1 * math.pi / 180.
    lat2 = llat2 * math.pi / 180.
    long1 = llong1 * math.pi / 180.
    long2 = llong2 * math.pi / 180.

    # косинусы и синусы широт и разницы долгот
    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    # вычисления длины большого круга
    y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = math.atan2(y, x)
    dist = ad * rad

    return dist


# Эта функция должна вызываться при нажатии на кнопку: Найти ближайшие объекты в радиусе
# Ничего не возвращает
def find_the_distance():
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    aparts = coordinates['apart']

    hosps = coordinates['hosp']

    distance_dict = {}

    for i in aparts.keys():
        coord1 = aparts[i]
        temp = {}
        for j in hosps.keys():
            coord2 = hosps[j]
            dist = distance(coord1, coord2)
            temp[dist] = [coord1, coord2]
        distance_dict[i] = temp

    with open('radius.json', 'w') as f:
        json.dump(distance_dict, f)

# эту функцию вызывать, когда пользователь написал радиус и ! выбрал дом !
# будет возвращаться список путей и з дома до больниц, а точнее просто координаты двух узлов
def nodes_in_radius(rad, apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c

    with open('radius.json') as f:
        radius = json.load(f)

    list_of_routes = []
    for i in radius[node].keys():
        if float(i) <= rad:
            list_of_routes.append(radius[node][i])
    return list_of_routes