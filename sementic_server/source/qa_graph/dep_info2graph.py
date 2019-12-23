"""
@description: 关联的mention映射为图结构
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-23
@version: 0.0.1
"""
from itertools import permutations

import networkx as nx

from sementic_server.source.dep_analyze.get_analyze_result import DepInfo
from sementic_server.source.dep_analyze.dep_map import DepMap
from sementic_server.source.qa_graph.graph import Graph
from sementic_server.source.tool.mention_collector import MentionCollector
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.global_value import RELATION_DATA
from sementic_server.source.qa_graph.ent2node import get_node_type


class DepGraph(Graph):
    def __init__(self, mention_collector: MentionCollector, dep_info: DepInfo):
        nx.MultiDiGraph.__init__(self)

        self.mentions = mention_collector.get_mentions()
        self.dep_info = dep_info
        self.att_info = dep_info.get_att_deps()
        self.dep_map = DepMap(mention_collector, dep_info)
        self.token_pairs = self.dep_map.token_pairs
        self.related_m_id_list = list()
        for t_pair in self.token_pairs:
            self.pair_process(t_pair)
        self.remove_inner_node()
        self.show()
        self.type_correct()
        self.show()

    def type_correct(self):
        """
        对节点和边的类型进行映射
        :return:
        """
        for n1, n2, k in self.edges:
            if k in RELATION_DATA.keys():
                self.nodes[n1]['type'] = RELATION_DATA[k]['domain']
                self.nodes[n2]['type'] = RELATION_DATA[k]['range']
                self.nodes[n1]['label'] = 'concept'
                self.nodes[n2]['label'] = 'concept'
        for n in self.nodes:
            temp_content = self.nodes[n].get('content')
            if not temp_content:
                continue
            temp_type = temp_content['type']
            self.nodes[n]['type'] = get_node_type(temp_type)

    def get_rest_mentions(self):
        m_id_list = [x.idx for x in self.mentions]
        rest_mentions_ids = [x for x in m_id_list if x not in self.related_m_id_list]
        rest_mentions = [x for x in self.mentions if x.idx in rest_mentions_ids]
        return rest_mentions

    def remove_inner_node(self):
        """
        如果一条边的尾和另一条边的头相同，且边名相同，合并为一条边
        :return:
        """
        for e1, e2 in permutations(self.edges, 2):
            if e1[2] == e2[2] and e1[1] == e2[0]:
                data = self.get_edge_data(e1[0], e1[1], e1[2])
                self.add_edge(e1[0], e2[1], e1[2], **data)
                self.remove_edges_from((e1, e2))
                self.remove_node(e1[1])

    def pair_process(self, t_pair):
        """
        将一对mention映射为图上的元素
        :param t_pair:
        :return:
        """
        t1 = t_pair['source']['mention_id']
        t2 = t_pair['att']['mention_id']
        self.related_m_id_list.append(t1)
        self.related_m_id_list.append(t2)
        m1 = self.mentions[t1]
        m2 = self.mentions[t2]
        """
        print(t1, m1.value, m1.mention_type, m1.small_type, t2, m2.value, m2.mention_type, m2.small_type)
        """
        if m1.mention_type == 'entity' and m2.mention_type == 'entity':
            self.add_edge(t1, t2, 'unknown_relation')
            self.nodes[t1]['label'] = 'concept'
            self.nodes[t1]['value'] = self.mentions[t1].value
            self.nodes[t1]['content'] = self.mentions[t1].content
            self.nodes[t2]['label'] = 'concept'
            self.nodes[t2]['value'] = self.mentions[t2].value
            self.nodes[t2]['content'] = self.mentions[t2].content
        elif m1.mention_type == 'entity' and m2.mention_type == 'relation':
            self.add_edge(t1, t2, m2.small_type, **m2.content)
            self.nodes[t1]['label'] = 'concept'
            self.nodes[t1]['value'] = self.mentions[t1].value
            self.nodes[t1]['content'] = self.mentions[t1].content
        elif m1.mention_type == 'relation' and m2.mention_type == 'entity':
            self.add_edge(t1, t2, m1.small_type, **m1.content)
            self.nodes[t2]['label'] = 'concept'
            self.nodes[t2]['value'] = self.mentions[t2].value
            self.nodes[t2]['content'] = self.mentions[t2].content


if __name__ == '__main__':
    sentence = '东南大学汪鹏老师的同学张三'
    """
    # sentence = '东南大学汪鹏老师的妻子张三'
    # sentence = '东南大学汪鹏老师的学生张三'
        """
    m_collector = MentionCollector(sentence)
    ms = m_collector.get_mentions()
    print("===============mention==================")
    for mt in m_collector.mentions:
        print(mt)
    d_info = dep_analyzer.get_dep_info(sentence)
    print("=================dependency=========================")
    for att in d_info.get_att_deps():
        print(att)
    print("=================dependency_map=========================")
    em = DepMap(m_collector, d_info)
    tp = em.token_pairs
    for t in tp:
        print(t)
    print("=================dependency_graph=========================")
    dg = DepGraph(m_collector, d_info)
    dg.show()
