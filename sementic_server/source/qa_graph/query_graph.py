"""
@description: 问答图生成过程
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-24
@version: 0.0.1
"""
import itertools
import networkx as nx
import copy

from sementic_server.source.dep_analyze.get_analyze_result import DepInfo
from sementic_server.source.qa_graph.dep_info2graph import DepGraph
from sementic_server.source.qa_graph.graph import Graph, my_disjoint_union
from sementic_server.source.qa_graph.query_graph_component import QueryGraphComponent
from sementic_server.source.qa_graph.rest_mention2graph import RestMentionGraph
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.global_value import RELATION_DATA, DEFAULT_EDGE
from sementic_server.source.tool.logger import logger
from sementic_server.source.tool.mention_collector import MentionCollector


class QueryGraph(Graph):
    def __init__(self, dep_graph: Graph, rest_mention_graph: Graph):
        temp_graph = my_disjoint_union(dep_graph, rest_mention_graph)
        nx.MultiDiGraph.__init__(self, temp_graph)
        self.error_info = ""
        if not temp_graph:
            self.error_info = 'in query graph: 问句缺失必要实体'
            return
        self.ambiguity_links_process()
        self.type_correct()
        self.loop_assemble()
        self.loop_add_default_edge()
        self.loop_add_unknown_rel()

    def loop_add_unknown_rel(self):
        need_loop = self.add_unknown_rel()
        while need_loop:
            need_loop = self.add_unknown_rel()

    def add_unknown_rel(self):
        need_loop = False
        for n1, n2, k in self.edges:
            if k == "unknown_relation":
                flag = self.add_default_edge_between_nodes(n1, n2)
                if not flag:
                    self.error_info = "in add_unknown_rel 添加默认边失败"
                self.remove_edge(n1, n2, k)
                need_loop = True
                return need_loop
        return need_loop

    def loop_add_default_edge(self):
        while not nx.algorithms.is_weakly_connected(self):
            # 若不连通则在联通分量之间添加默认边
            flag = self.add_default_edge()
            if not flag:
                logger.info('default edge missing!')
                logger.info('graph is not connected!')
                self.error_info = 'graph is not connected!'
                # 未添加上说明缺少默认边
                return

    def add_default_edge(self):
        """
        添加默认边
        :return:
        """
        flag = False
        components_set = self.get_connected_components_subgraph()
        for i in range(len(components_set)-1):
            flag = self.add_default_edge_between_components(components_set, i, i + 1)
            if flag:
                break
        return flag

    def add_default_edge_between_nodes(self, n1, n2):
        """
        在两个点之间添加默认边
        :return:
        """
        flag = False
        type_1 = self.nodes[n1]['type']
        type_2 = self.nodes[n2]['type']
        for key, edge in DEFAULT_EDGE.items():
            if type_1 == edge['domain'] and type_2 == edge['range']:
                self.add_edge(n1, n2, key, type=key, value=edge['value'])
                flag = True
                return flag
            elif type_2 == edge['domain'] and type_1 == edge['range']:
                self.add_edge(n2, n1, key, type=key, value=edge['value'])
                flag = True
                return flag
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

    def loop_assemble(self):
        old_query_graph = copy.deepcopy(self)
        node_type_dict = self.node_type_statistic()
        self.component_assemble(node_type_dict)
        while len(self.nodes) != len(old_query_graph.nodes) \
                and not nx.algorithms.is_weakly_connected(self):
            # 节点一样多说明上一轮没有合并
            # 图已连通也不用合并
            old_query_graph = copy.deepcopy(self)
            node_type_dict = self.node_type_statistic()
            self.component_assemble(node_type_dict)

    def component_assemble(self, node_type_dict):
        # 之后根据依存分析来完善
        for k, v in node_type_dict.items():
            if len(v) >= 2:
                combinations = itertools.combinations(v, 2)
                combinations = sorted(combinations, key=self.get_outdiff)
                for pair in combinations:
                    # 若两个节点之间连通，则跳过，不存在则合并
                    test_graph = nx.to_undirected(self)
                    if nx.has_path(test_graph, pair[0], pair[1]):
                        continue
                    else:
                        mapping = {pair[0]: pair[1]}
                        nx.relabel_nodes(self, mapping, copy=False)
                        break

    def ambiguity_links_process(self):
        """
        将query_graph中的类型为ambiguity的边确定一个类型，更具整张图的节点类型
        :return:
        """
        for n1, n2, k in self.edges:
            if k == 'Ambiguous':
                rel_data = self.ambiguity_resolution(n1, n2)
                d_type = rel_data['type']
                self.add_edge(n1, n2, d_type, **rel_data)
                self.remove_edge(n1, n2, k)

    def ambiguity_resolution(self, n1, n2):
        """
        将一条ambiguity的边确定一个类型，更具整张图的节点类型
        :return:
        """
        rel_data = self.get_edge_data(n1, n2, 'Ambiguous')
        reverse_dict = {'好友': ['QQFriend', 'Friend'],
                        "成员": ['WeChatGroupMember', 'QQGroupMember'],
                        "群成员": ['WeChatGroupMember', 'QQGroupMember']}
        ambiguity_list = reverse_dict[rel_data['value']]
        sim_list = list()
        for n, r in enumerate(ambiguity_list):
            count = 0
            d_t = RELATION_DATA[r]['domain']
            r_t = RELATION_DATA[r]['range']
            for t_node in self.nodes:
                temp_type = self.nodes[t_node].get('type')
                if temp_type == d_t or temp_type == r_t:
                    count += 1
            sim = count / len(self.nodes)
            sim_list.append(sim)
        max_sim = max(sim_list)
        m_index = sim_list.index(max_sim)
        rel_data['type'] = ambiguity_list[m_index]
        return rel_data

