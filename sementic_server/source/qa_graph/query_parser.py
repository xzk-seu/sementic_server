"""
@description: 问答图生成过程
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

import itertools

import networkx as nx

from sementic_server.source.dep_analyze.get_analyze_result import DepInfo
from sementic_server.source.qa_graph.dep_info2graph import DepGraph
from sementic_server.source.qa_graph.graph import Graph, my_disjoint_union
from sementic_server.source.qa_graph.query_graph_component import QueryGraphComponent
from sementic_server.source.qa_graph.rest_mention2graph import RestMentionGraph
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.global_value import RELATION_DATA, DEFAULT_EDGE
from sementic_server.source.tool.logger import logger
from sementic_server.source.tool.mention_collector import MentionCollector


class QueryParser(object):
    """
    动态问答图语义解析模块
    """

    def __init__(self, m_collector: MentionCollector, dep_info: DepInfo):
        logger.info('Query Graph Parsing...')
        self.error_info = None

        self.m_collector = m_collector
        self.mentions = m_collector.mentions

        self.entity = m_collector.entity
        self.relation = m_collector.relation
        self.value_prop = m_collector.value_props

        self.intent = None
        self.dep_info = dep_info
        self.relation_component_list = list()
        self.entity_component_list = list()

        self.dep_graph = DepGraph(self.m_collector, self.dep_info)
        print("=============================dep_graph===========================")
        self.dep_graph.show()
        dep_rest_mentions = self.dep_graph.get_rest_mentions()
        self.rest_mention_graph = RestMentionGraph(dep_rest_mentions).get_mention_graph()
        print('==========================rest_mention_graph=========================')
        self.rest_mention_graph.show()
        print('==========================rest_mention_graph=end========================')
        self.query_graph = my_disjoint_union(self.dep_graph, self.rest_mention_graph)
        self.ambiguity_links_process()
        self.query_graph.type_correct()

        self.node_type_dict = self.query_graph.node_type_statistic()
        self.component_assemble()
        self.query_graph.show()

        """
        # 获取实体和关系对应的子图组件
        self.init_entity_component()
        self.init_value_prop_component()
        self.init_relation_component()

        # 得到子图组件构成的集合，用图表示
        # self.component_graph = nx.disjoint_union_all(self.relation_component_list + self.entity_component_list)
        # self.component_graph的顺序决定了节点合并顺序，对最终构建的图有很大影响
        self.component_graph = my_disjoint_union_all(self.entity_component_list + self.relation_component_list)
        self.query_graph = copy.deepcopy(self.component_graph)
        self.query_graph = Graph(self.query_graph)
        self.old_query_graph = copy.deepcopy(self.component_graph)
        self.node_type_dict = self.query_graph.node_type_statistic()
        self.component_assemble()

        while len(self.query_graph.nodes) != len(self.old_query_graph.nodes) \
                and not nx.algorithms.is_weakly_connected(self.query_graph):
            # 节点一样多说明上一轮没有合并
            # 图已连通也不用合并
            self.old_query_graph = copy.deepcopy(self.query_graph)
            self.node_type_dict = self.query_graph.node_type_statistic()
            self.component_assemble()
        """

        if not self.query_graph:
            self.error_info = '问句缺失必要实体'
            return
        while not nx.algorithms.is_weakly_connected(self.query_graph):
            # 若不连通则在联通分量之间添加默认边
            flag = self.add_default_edge()
            if not flag:
                logger.info('default edge missing!')
                logger.info('graph is not connected!')
                self.error_info = 'graph is not connected!'
                # 未添加上说明缺少默认边
                return

        # 经过上面两个循环，得到连通的图，下面确定意图
        logger.info('connected graph is already')
        self.query_graph = nx.convert_node_labels_to_integers(self.query_graph)
        self.query_graph = Graph(self.query_graph)
        self.query_graph.show_log()
        logger.info('next is determine intention')
        self.determine_intention()

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
                    self.query_graph.add_edge(node_0, node_1, key, type=key, value=edge['value'])
                    flag = True
                    return flag
                elif c[1] == edge['domain'] and c[0] == edge['range']:
                    node_0 = d1[edge['domain']][trick_index]
                    node_1 = d0[edge['range']][trick_index]
                    self.query_graph.add_edge(node_0, node_1, key, type=key, value=edge['value'])
                    flag = True
                    return flag
        return flag

    def add_default_edge(self):
        """
        添加默认边
        :return:
        """
        flag = False
        components_set = self.query_graph.get_connected_components_subgraph()
        for i in range(len(components_set)-1):
            flag = self.add_default_edge_between_components(components_set, i, i + 1)
            if flag:
                break
        return flag

    def determine_intention_by_type(self):
        # 根据意图类型来确定意图，对应determine_intention中的1.2
        for n in self.query_graph.nodes:
            if self.query_graph.nodes[n]['label'] == 'concept':
                node_type = self.query_graph.nodes[n]['type']
                if node_type == self.intent:
                    self.add_intention_on_node(n)
                    break

    def add_intention_on_node(self, node):
        self.query_graph.nodes[node]['intent'] = True

    def add_intention_on_nodes(self, node_list):
        """
        在一批节点中优先选择person节点进行插入
        :param node_list: 带插入的一组空节点
        :return:
        """
        for node in node_list:
            if self.query_graph.nodes[node]['type'] == 'Person':
                self.query_graph.nodes[node]['intent'] = True
                return
        # 若找不到person
        node = node_list[0]
        self.query_graph.nodes[node]['intent'] = True

    def get_intention_candidate(self):
        """
        获取候选意图节点id
        :return:候选意图节点id
        """
        logger.info('all concept node as intention candidates')
        intention_candidates = self.query_graph.get_concept_nodes()
        logger.info('intention candidates is %s' % str(intention_candidates))

        if self.intent:
            # 意图识别提供了意图类型
            logger.info('intention type is %s' % self.intent)
            new_intention_candidates = [x for x in intention_candidates
                                        if self.query_graph.nodes[x].get('type') == self.intent]
            intention_candidates = new_intention_candidates
            logger.info('intention candidates is %s' % str(intention_candidates))

        if len(intention_candidates) == 0:
            # print('intention recognizer module produce wrong intention!')
            logger.info('intention recognizer module produce wrong intention!')
            self.error_info = '意图冲突!'
            return

        none_nodes = self.query_graph.get_none_nodes(self.intent)
        if len(none_nodes) > 0:
            logger.info('the graph has %d blank node: %s' % (len(none_nodes), str(none_nodes)))
            intention_candidates = [x for x in intention_candidates if x in none_nodes]
            logger.info('intention candidates is %s' % str(intention_candidates))
        return intention_candidates

    def literal_intention(self):
        """
        确定是否由字面值上的意图
        :return:
        """
        for k, v in self.query_graph.get_nodes_dict().items():
            if v['label'] == 'literal':
                t = dict(v).setdefault('entity', None)
                if not t:
                    self.add_intention_on_node(int(k))
                    return True

    def determine_intention(self):
        """
        确定意图：
        0.是否有空的值属性节点

        1. 意图识别模块通过关键词，获取意图类型；
        2. 根据依存分析模块，将句法依存树根节点附近的实体节点中作为候选意图节点，若上一步得到了意图类型，删去候选意图中的与意图类型冲突的节点；
        3. 在所有候选节点中，若有空节点（即没有字面值描述的节点），则将候选节点集合中的所有空节点作为新的候选节点集合；
        4. 若上一步选出的节点有多个，则优先选择Person类型的节点。
        5. 在候选节点集合中，按照候选意图节点的入度与出度之差，对候选节点进行排序，选出入度与出度之差最大的节点；
        :return:
        """
        if self.literal_intention():
            return

        intention_candidates = self.get_intention_candidate()
        if self.error_info:
            return
        logger.info('determine intention by degree')
        criterion_dict = dict()
        for node in intention_candidates:
            criterion_dict[node] = self.query_graph.get_out_index(node)

        m = min(criterion_dict.values())
        # 考虑到多个节点上都有最值
        intention_nodes = [k for k, v in criterion_dict.items() if v == m]
        logger.info('nodes: %s have degree: %d' % (str(intention_nodes), m))

        logger.info('final intention node is %d' % intention_nodes[0])
        self.add_intention_on_node(intention_nodes[0])

    def get_person_nodes(self, candidates):
        """
        从候选节点中选出任务person的节点
        :param candidates:
        :return:
        """
        node_list = list()
        for node in candidates:
            if self.query_graph.nodes[node].get('type') == 'Person':
                node_list.append(node)
        return node_list

    def component_assemble(self):
        # 之后根据依存分析来完善
        for k, v in self.node_type_dict.items():
            if len(v) >= 2:
                combinations = itertools.combinations(v, 2)
                combinations = sorted(combinations, key=self.query_graph.get_outdiff)
                for pair in combinations:
                    # 若两个节点之间连通，则跳过，不存在则合并
                    test_graph = nx.to_undirected(self.query_graph)
                    if nx.has_path(test_graph, pair[0], pair[1]):
                        continue
                    else:
                        mapping = {pair[0]: pair[1]}
                        nx.relabel_nodes(self.query_graph, mapping, copy=False)
                        break

    def ambiguity_links_process(self):
        """
        将query_graph中的类型为ambiguity的边确定一个类型，更具整张图的节点类型
        :return:
        """
        for n1, n2, k in self.query_graph.edges:
            if k == 'Ambiguous':
                rel_data = self.ambiguity_resolution(n1, n2)
                d_type = rel_data['type']
                self.query_graph.add_edge(n1, n2, d_type, **rel_data)
                self.query_graph.remove_edge(n1, n2, k)

    def ambiguity_resolution(self, n1, n2):
        """
        将一条ambiguity的边确定一个类型，更具整张图的节点类型
        :return:
        """
        rel_data = self.query_graph.get_edge_data(n1, n2, 'Ambiguous')
        reverse_dict = {'好友': ['QQFriend', 'Friend'],
                        "成员": ['WeChatGroupMember', 'QQGroupMember'],
                        "群成员": ['WeChatGroupMember', 'QQGroupMember']}
        ambiguity_list = reverse_dict[rel_data['value']]
        sim_list = list()
        for n, r in enumerate(ambiguity_list):
            count = 0
            d_t = RELATION_DATA[r]['domain']
            r_t = RELATION_DATA[r]['range']
            for t_node in self.query_graph.nodes:
                temp_type = self.query_graph.nodes[t_node].get('type')
                if temp_type == d_t or temp_type == r_t:
                    count += 1
            sim = count / len(self.query_graph.nodes)
            sim_list.append(sim)
        max_sim = max(sim_list)
        m_index = sim_list.index(max_sim)
        rel_data['type'] = ambiguity_list[m_index]
        return rel_data


if __name__ == '__main__':
    """
    # q = '在东莞常平司马村珠江啤酒厂斜对面合租的15842062826的老婆'
    """

    sentence = '东南大学汪鹏老师的同学张三'
    m_c = MentionCollector(sentence)
    dep_i = dep_analyzer.get_dep_info(sentence)
    qg = QueryParser(m_c, dep_i)
    error_info = qg.error_info
    if error_info:
        print(error_info)
    qg.query_graph.show()
