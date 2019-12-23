"""
@description: 将依存信息之外的mention映射为图
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-23
@version: 0.0.1
"""

import networkx as nx

from sementic_server.source.qa_graph.ent2node import get_node_type
from sementic_server.source.qa_graph.graph import Graph, my_disjoint_union_all
from sementic_server.source.tool.global_value import RELATION_DATA
from sementic_server.source.tool.logger import logger
from sementic_server.source.tool.mention_collector import Mention


class RestMentionGraph(object):
    """
    多个rest mention组合成一个不连通的图
    """

    def __init__(self, mentions: list):
        self.mention_graphs = list()
        for mention in mentions:
            mg = MentionGraph(mention)
            self.mention_graphs.append(mg)

    def get_mention_graph(self):
        r = Graph()
        if len(self.mention_graphs) > 0:
            r = my_disjoint_union_all(self.mention_graphs)
        return r


class MentionGraph(Graph):
    """
    一个 mention组合成一个不连通的图
    """

    def __init__(self, mention: Mention):
        nx.MultiDiGraph.__init__(self)
        self.mention = mention
        if mention.mention_type == "relation":
            self.init_rel_graph()
        elif mention.mention_type == "entity":
            self.init_ent_graph()
        elif mention.mention_type == "value_props":
            self.init_vpro_graph()

    def init_vpro_graph(self):
        value_prop = self.mention.content
        dom = value_prop['定义域']
        node_name = dom + '0'
        ran = value_prop['值域']
        prop_name = value_prop['属性名称']
        self.add_edge(node_name, 'p_name', prop_name, **value_prop)
        self.nodes[node_name]['label'] = 'concept'
        self.nodes[node_name]['type'] = dom
        self.nodes['p_name']['label'] = 'literal'
        self.nodes['p_name']['type'] = ran
        self.nodes['p_name']['intent'] = True

    def init_ent_graph(self):
        entity = self.mention.content
        logger.info('Type: %s \t Value: %s' % (entity['type'], entity['value']))

        self.add_node('temp')
        self.nodes['temp']['label'] = 'concept'
        self.nodes['temp']['value'] = self.mention.value
        self.nodes['temp']['type'] = get_node_type(entity['type'])
        self.nodes['temp']['content'] = entity

    def init_rel_graph(self):
        """
        若该边有歧义，需等到整图合并的时候消歧
        """
        temp_type = self.mention.small_type
        temp_content = self.mention.content
        self.add_edge('temp_0', 'temp_1', temp_type, **temp_content)
        if temp_type in RELATION_DATA.keys():
            self.nodes['temp_0']['type'] = RELATION_DATA[temp_type]['domain']
            self.nodes['temp_1']['type'] = RELATION_DATA[temp_type]['range']
        else:
            self.nodes['temp_0']['type'] = "UNKNOWN"
            self.nodes['temp_1']['type'] = "UNKNOWN"
        for n in self.nodes:
            self.nodes[n]['label'] = 'concept'
