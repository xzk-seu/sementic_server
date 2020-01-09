"""
@description: 图结构的基类
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

import json

import networkx as nx

import itertools
from sementic_server.source.qa_graph.ent2node import get_node_type
from sementic_server.source.tool.global_value import RELATION_DATA, ACCOUNT_OBJ_LIST, DEFAULT_EDGE
from sementic_server.source.tool.logger import logger


class Graph(nx.MultiDiGraph):
    """
    图基类实现
    """

    def __init__(self, graph=None, file_path=None):
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as fr:
                    data = json.load(fr)
                graph = nx.node_link_graph(data)
            except Exception as e:
                logger.error(e)
        nx.MultiDiGraph.__init__(self, graph)
        self.error_info = ""

    def get_connected_components_subgraph(self):
        # 获取连通子图
        component_list = list()
        temp_graph = Graph(self)
        for c in nx.weakly_connected_components(self):
            component = temp_graph.subgraph(c)
            component_list.append(component)
        return component_list

    def is_none_node(self, node):
        if self.nodes[node]['label'] != 'concept':
            return False
        if self.nodes[node].get("content"):
            return False
        neighbors = list(self.predecessors(node))+list(self.successors(node))
        for n in neighbors:
            # 目前判断条件为出边没有字面值，认为是空节点
            # 没有字面值，且没有账号和地址
            # 考虑拓扑排序的终点
            if self.nodes[n]['label'] == 'literal' or self.nodes[n]['type'] in ACCOUNT_OBJ_LIST:
                return False
        return True

    def get_none_nodes(self, node_type=None):
        # 获取指定节点类型下的空节点
        none_node_list = list()
        for node in self.nodes:
            if self.is_none_node(node):
                if node_type and self.nodes[node].get('type') != node_type:
                    continue
                none_node_list.append(node)
        return none_node_list

    def get_concept_nodes(self):
        # 获取概念
        node_list = list()
        for node in self.nodes:
            if self.nodes[node].get('label') == 'concept':
                node_list.append(node)
        return node_list

    def get_out_degree(self, node):
        s = list(self.successors(node))
        return len(s)

    def get_in_degree(self, node):
        s = list(self.predecessors(node))
        return len(s)

    def get_out_index(self, node):
        """
        计算一个节点的出度与入度之差
        :param node:
        :return:
        """
        node_in = self.get_in_degree(node)
        node_out = self.get_out_degree(node)
        return node_out - node_in

    def get_outdiff(self, node1_node2):
        """
        获取两个节点的out_index之差
        :return:
        """
        node1, node2 = node1_node2
        t1 = self.get_out_index(node1)
        t2 = self.get_out_index(node2)
        r = t1 - t2
        return r

    def node_type_statistic(self):
        """
        统计每种类型的节点的个数
        """
        node_type_dict = dict()
        for n in self.nodes:
            if self.nodes[n]['label'] == 'concept':
                node_type = self.nodes[n].get('type')
                if not node_type:
                    continue
                if node_type not in node_type_dict.keys():
                    node_type_dict[node_type] = list()
                node_type_dict[node_type].append(n)
        for k, v in node_type_dict.items():
            node_type_dict[k] = sorted(v)
        return node_type_dict

    def export(self, file_path):
        """将图导出至文件"""
        temp_graph = nx.MultiDiGraph(self)
        data = nx.node_link_data(temp_graph)
        with open(file_path, 'w', encoding='utf-8') as fw:
            json.dump(data, fw)

    def get_data(self):
        """输出结果"""
        temp_graph = nx.MultiDiGraph(self)
        data = nx.node_link_data(temp_graph)
        return data

    def get_nodes_dict(self):
        """
        返回节点字典
        :return:
        """
        r_dict = dict()
        for n in self.nodes:
            data = self.nodes[n]
            r_dict[str(n)] = data
        return r_dict

    def get_edges_dict(self):
        """
        返回边字典
        :return:
        """
        r_dict = dict()
        for n, e in enumerate(self.edges):
            data = self.get_edge_data(e[0], e[1], e[2])
            data['from'] = e[0]
            data['to'] = e[1]
            r_dict[str(n)] = data
        return r_dict

    def get_neighbors(self, node):
        """
        获取节点node的邻居列表
        :param node:
        :return:
        """
        s = list(self.successors(node)) + list(self.predecessors(node))
        s = set(s)
        s = list(s)
        return s

    def show(self):
        """将图显示至屏幕"""
        if not self:
            logger.info("There is nothing to show!")
            return
        flag = True
        if not self.is_multigraph():
            flag = False
        print('=================The graph have %d nodes==================' % len(self.nodes))
        logger.info('=================The graph have {0} nodes=================='.format(len(self.nodes)))
        for n in self.nodes:
            data = self.nodes[n]
            print(str(n).ljust(30), '\t', str(data).ljust(30))
            logger.info("{0}\t{1}".format(str(n).ljust(30), str(data).ljust(30)))
        # print('=================The graph have %d edges==================' % len(self.edges))
        print('The graph have %d edges'.center(100, '=') % len(self.edges))
        logger.info('The graph have %d edges'.center(100, '=') % len(self.edges))
        for e in self.edges:
            # multigraph的边结构为(u, v, k)
            # 非multigraph的边结构为(u, v)
            if flag:
                data = self.get_edge_data(e[0], e[1], e[2])
            else:
                data = self.get_edge_data(e[0], e[1])
            print(str(e).ljust(30), '\t', str(data).ljust(30))
            logger.info('{0}\t{1}'.format(e, data))

    def show_log(self):
        """将图显示至屏幕"""
        if not self:
            logger.info("There is nothing to show!")
            return
        flag = True
        if not self.is_multigraph():
            flag = False

        logger.info('=================The graph have {0} nodes=================='.format(len(self.nodes)))
        for n in self.nodes:
            data = self.nodes[n]
            logger.info("{0}\t{1}".format(str(n).ljust(30), str(data).ljust(30)))

        logger.info('The graph have %d edges'.center(100, '=') % len(self.edges))
        for e in self.edges:
            # multigraph的边结构为(u, v, k)
            # 非multigraph的边结构为(u, v)
            if flag:
                data = self.get_edge_data(e[0], e[1], e[2])
            else:
                data = self.get_edge_data(e[0], e[1])
            logger.info('{0}\t{1}'.format(e, data))

    def edge_type_correct(self):
        reverse_edge_list = list()
        for n1, n2, k in self.edges:
            if k not in RELATION_DATA.keys():
                continue
            self.nodes[n1]['label'] = 'concept'
            self.nodes[n2]['label'] = 'concept'
            n1_type = self.nodes[n1].get('type')
            n2_type = self.nodes[n2].get('type')
            dom = RELATION_DATA[k]['domain']
            ran = RELATION_DATA[k]['range']
            if not n1_type and not n2_type:
                self.nodes[n1]['type'] = dom
                self.nodes[n2]['type'] = ran
                continue
            if n1_type == dom or n2_type == ran:
                self.nodes[n1]['type'] = dom
                self.nodes[n2]['type'] = ran
            elif n1_type == ran or n2_type == dom:
                reverse_edge_list.append((n1, n2, k))
        for n1, n2, k in reverse_edge_list:
            data = self.get_edge_data(n1, n2, k)
            self.add_edge(n2, n1, k, **data)
            self.remove_edge(n1, n2, k)

    def type_correct(self):
        """
        对节点和边的类型进行映射
        :return:
        """
        for n in self.nodes:
            temp_content = self.nodes[n].get('content')
            if not temp_content:
                continue
            temp_type = temp_content['type']
            self.nodes[n]['type'] = get_node_type(temp_type)
        self.edge_type_correct()

    def add_default_edge(self):
        """
        添加默认边
        :return:
        """
        flag = False
        components_set = self.get_connected_components_subgraph()
        for i in range(len(components_set) - 1):
            flag = self.add_default_edge_between_components(components_set, i, i + 1)
            if flag:
                break
        return flag

    def add_default_edge_between_components(self, components_set, c1, c2):
        """
        在两个连通分量之间添加默认边
        :param components_set:
        :param c1:
        :param c2:
        :return:
        """
        flag = False
        d0 = Graph(components_set[c1]).node_type_statistic()
        d1 = Graph(components_set[c2]).node_type_statistic()
        candidates = itertools.product(d0.keys(), d1.keys())
        candidates = list(candidates)
        trick_index = 0
        for key, edge in DEFAULT_EDGE.items():
            for c in candidates:
                if c[0] == edge['domain'] and c[1] == edge['range']:
                    node_0 = d0[edge['domain']][trick_index]
                    node_1 = d1[edge['range']][trick_index]
                    self.add_edge(node_0, node_1, key, type=key, value=edge['value'])
                    flag = True
                    return flag
                elif c[1] == edge['domain'] and c[0] == edge['range']:
                    node_0 = d1[edge['domain']][trick_index]
                    node_1 = d0[edge['range']][trick_index]
                    self.add_edge(node_0, node_1, key, type=key, value=edge['value'])
                    flag = True
                    return flag
        return flag

    def intent_in_graph(self):
        """
        判断图中是否有意图
        :return:
        """
        flag = False
        for n in self.nodes:
            if self.nodes[n].get("intent"):
                flag = True
        return flag

    def loop_add_default_edge(self):
        while not nx.algorithms.is_weakly_connected(self):
            # 若不连通则在联通分量之间添加默认边
            flag = self.add_default_edge()
            if not flag:
                flag = self.add_person()
            if not flag:
                logger.info('default edge missing!')
                logger.info('graph is not connected!')
                self.error_info = 'graph is not connected!'
                # 未添加上说明缺少默认边
                return False
        return True

    def add_person(self):
        """
        向图中加入一个人物节点，再添加默认边
        :return:
        """
        node_list = self.get_nodes_dict().keys()
        node_list = [int(x) for x in node_list]
        node_id = max(node_list) + 1
        if node_id >= 20:
            return False
        self.add_node(node_id, label="concept", type="person")
        flag = self.add_default_edge()
        return flag

    def add_intent_node(self, intent):
        """
        意图冲突时，试图添加对应类型的意图节点
        :param intent:
        :return:
        """
        node_list = self.get_nodes_dict().keys()
        node_list = [int(x) for x in node_list]
        node_id = max(node_list) + 1
        if node_id >= 20:
            return False
        self.add_node(node_id, label="concept", type=intent, intent=True)
        flag = self.add_default_edge()
        return flag

    def add_person_node(self):
        """
        意图冲突时，试图添加人物类型的意图节点
        :return:
        """
        node_list = self.get_nodes_dict().keys()
        node_list = [int(x) for x in node_list]
        node_id = max(node_list) + 1
        if node_id >= 20:
            return False
        self.add_node(node_id, label="concept", type="person")
        flag = self.add_default_edge()
        return flag


def my_disjoint_union_all(graphs):
    """Returns the disjoint union of all graphs.

    This operation forces distinct integer node labels starting with 0
    for the first graph in the list and numbering consecutively.

    Parameters
    ----------
    graphs : list
       List of NetworkX graphs

    Returns
    -------
    U : A graph with the same type as the first graph in list

    Raises
    ------
    ValueError
       If `graphs` is an empty list.

    Notes
    -----
    It is recommended that the graphs be either all directed or all undirected.

    Graph, edge, and node attributes are propagated to the union graph.
    If a graph attribute is present in multiple graphs, then the value
    from the last graph in the list with that attribute is used.
    """
    if not graphs:
        raise ValueError('cannot apply disjoint_union_all to an empty list')
    graphs = iter(graphs)
    u = next(graphs)
    for h in graphs:
        u = my_disjoint_union(u, h)
    return u


def my_disjoint_union(g, h):
    """ Return the disjoint union of graphs G and H.

    This algorithm forces distinct integer node labels.

    Parameters
    ----------
    g,h : graph
       A NetworkX graph

    Returns
    -------
    U : A union graph with the same type as G.

    Notes
    -----
    A new graph is created, of the same class as G.  It is recommended
    that G and H be either both directed or both undirected.

    The nodes of G are relabeled 0 to len(G)-1, and the nodes of H are
    relabeled len(G) to len(G)+len(H)-1.

    Graph, edge, and node attributes are propagated from G and H
    to the union graph.  If a graph attribute is present in both
    G and H the value from H is used.
    """
    g = Graph(g)
    h = Graph(h)
    r1 = nx.convert_node_labels_to_integers(g, ordering='increasing degree')
    r2 = nx.convert_node_labels_to_integers(h, first_label=len(r1), ordering='increasing degree')
    r = nx.union(r1, r2)
    r.graph.update(g.graph)
    r.graph.update(h.graph)
    return r


if __name__ == '__main__':
    test_graph = nx.complete_graph(5)
    g = Graph(test_graph)
    g.show()
    print(g.get_neighbors(3))
    # g.export('text')
