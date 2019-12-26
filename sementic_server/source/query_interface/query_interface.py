"""
@description: 实现从问答图到查询接口的转化
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-06-02
@version: 0.0.1
"""

import json

import networkx as nx

from sementic_server.source.qa_graph.graph import Graph
from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.query_interface.interface_term import Node, Target
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.mention_collector import MentionCollector


class QueryInterface(object):
    """
    实现从问答图到查询接口的转化
    """

    def __init__(self, graph: Graph, query: str):
        self.query = query
        self.nodes = list()
        self.links = list()
        self.targets = list()

        self.graph = Graph(graph)
        self.graph = nx.convert_node_labels_to_integers(self.graph)

        self.init_nodes()
        self.init_links()
        self.init_targets()

    def init_targets(self):
        intent_node_ids = [x for x in self.graph.nodes if self.graph.nodes[x].get('intent')]
        for iid in intent_node_ids:
            target = Target(iid, intent_node_ids, self.links, self.graph)
            self.targets.append(target.get_dict())

    def init_links(self):
        link_id = 0
        for n1, n2, k in self.graph.edges:
            temp = dict(link_id=link_id, start_node=n1, end_node=n2, link_type=k, link_property=dict())
            self.links.append(temp)
            link_id += 1

    def init_nodes(self):
        d = self.graph.get_nodes_dict()
        for k, v in d.items():
            if not v.get('label') or v.get('label') != 'concept':
                continue
            node = Node(k, v)
            self.nodes.append(node.__dict__)

    def get_dict(self):
        temp = dict()
        temp['query'] = self.query
        temp['nodes'] = self.nodes
        temp['links'] = self.links
        temp['targets'] = self.targets
        return temp


if __name__ == '__main__':
    """
    # q = '在东莞常平司马村珠江啤酒厂斜对面合租的15842062826的老婆'
    东南大学汪鹏老师的同学张三
    """

    sentence = '在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹'
    print(sentence)
    m_c = MentionCollector(sentence)
    dep_i = dep_analyzer.get_dep_info(sentence)
    qg = QueryParser(m_c, dep_i)
    if qg.error_info:
        print(qg.error_info)
    qg.query_graph.show()
    print("================graph end=======================")
    qi = QueryInterface(qg.query_graph, sentence)
    qid = qi.get_dict()
    print(qid)

    with open('interface_demo.json', 'w') as fw:
        json.dump(qid, fw)
