"""
@description: 关联的mention映射为图结构
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-23
@version: 0.0.1
"""
from itertools import permutations

import networkx as nx

from sementic_server.source.dep_analyze.dep_map import DepMap
from sementic_server.source.dep_analyze.get_analyze_result import DepInfo
from sementic_server.source.qa_graph.graph import Graph, get_node_type
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.mention_collector import MentionCollector, Mention
from sementic_server.source.tool.global_value import RELATION_DATA, ACCOUNT_LIST


class DepGraph(Graph):
    """
    根据依存信息构建图
    """
    def __init__(self, mention_collector: MentionCollector, dep_info: DepInfo):
        nx.MultiDiGraph.__init__(self)

        self.mentions = mention_collector.get_mentions()
        self.dep_info = dep_info
        self.dep_map = DepMap(mention_collector, dep_info)
        self.token_pairs = self.dep_map.token_pairs
        self.head_intent_ids = self.dep_map.head_intentions
        self.related_m_id_list = list()
        for t_pair in self.token_pairs:
            self.pair_process(t_pair)
        self.remove_inner_node()
        self.check_person_account()
        self.type_correct()
        self.add_head_target()

    def check_person_account(self):
        """
        检查边的类型是否符合本体规定，若不符合
        若该节点为账号，相邻的边和人相关，将该节点换为人
        :return:
        """
        wait_to_add_edges = list()
        for n1, n2, k in self.edges:
            if k not in RELATION_DATA.keys():
                continue
            dom = RELATION_DATA[k]['domain']
            ran = RELATION_DATA[k]['range']
            if dom != "person" or ran != "person":
                continue
            content = self.nodes[n1].get("content")
            if not content:
                continue
            n1_type = content.get("type")
            if n1_type and n1_type in ACCOUNT_LIST:
                self.nodes[n1]['type'] = "person"
                # self.add_node("temp_account_%d" % count, type=n1_type, content=content)
                wait_to_add_edges.append((n1, 0-n1, n1_type, content))
        for n1, n2, n1_type, content in wait_to_add_edges:
            n1_type = get_node_type(n1_type)
            self.add_node(n2, type=n1_type, content=content)
            self.add_edge(n1, n2, "unknown_relation")

    def add_head_target(self):
        for tid in self.head_intent_ids:
            if tid in self.nodes:
                self.nodes[tid]['intent'] = True
            else:
                self.add_node(tid, intent=True)
                self.nodes[tid]['label'] = 'concept'
                self.nodes[tid]['value'] = self.mentions[tid].value
                self.nodes[tid]['content'] = self.mentions[tid].content
                self.related_m_id_list.append(tid)

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

    def add_ent_rel_link(self, ent_mention: Mention, rel_mention: Mention, ent_first: bool):
        """
        对实体-关系这样的mention对进行图映射
        :param ent_mention:
        :param rel_mention:
        :param ent_first:
        :return:
        """
        ent_mention_id = ent_mention.idx
        rel_mention_id = rel_mention.idx
        k = rel_mention.small_type
        ent_type_1 = ent_mention.small_type
        if k == "Ambiguous":
            return
        dom = RELATION_DATA[k]['domain']
        ran = RELATION_DATA[k]['range']

        self.add_node(ent_mention_id)
        self.nodes[ent_mention_id]['label'] = 'concept'
        self.nodes[ent_mention_id]['type'] = ent_mention.small_type
        self.nodes[ent_mention_id]['value'] = ent_mention.value
        self.nodes[ent_mention_id]['content'] = ent_mention.content
        self.add_node(rel_mention_id)
        self.nodes[rel_mention_id]['label'] = 'concept'

        if dom != ran:
            if ent_type_1 == dom:
                self.add_edge(ent_mention_id, rel_mention_id, k, **rel_mention.content)
                self.nodes[rel_mention_id]['type'] = ran
            elif ent_type_1 == ran:
                self.add_edge(rel_mention_id, ent_mention_id, k, **rel_mention.content)
                self.nodes[rel_mention_id]['type'] = dom
            else:
                self.remove_node(ent_mention_id)
                self.remove_node(rel_mention_id)
                return
        else:
            if ent_type_1 != dom:
                self.remove_node(ent_mention_id)
                self.remove_node(rel_mention_id)
                return
            if ent_first:
                self.add_edge(ent_mention_id, rel_mention_id, k, **rel_mention.content)
                self.nodes[rel_mention_id]['type'] = ran
            else:
                self.add_edge(rel_mention_id, ent_mention_id, k, **rel_mention.content)
                self.nodes[rel_mention_id]['type'] = dom
        return True

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

        if m1.mention_type == 'entity' and m2.mention_type == 'entity':
            self.add_edge(t1, t2, 'unknown_relation')
            self.nodes[t1]['label'] = 'concept'
            self.nodes[t1]['value'] = self.mentions[t1].value
            self.nodes[t1]['content'] = self.mentions[t1].content
            self.nodes[t2]['label'] = 'concept'
            self.nodes[t2]['value'] = self.mentions[t2].value
            self.nodes[t2]['content'] = self.mentions[t2].content
        elif m1.mention_type == 'entity' and m2.mention_type == 'relation':
            f = self.add_ent_rel_link(m1, m2, True)
            if not f:
                self.related_m_id_list.remove(t1)
                self.related_m_id_list.remove(t2)
        elif m1.mention_type == 'relation' and m2.mention_type == 'entity':
            f = self.add_ent_rel_link(m2, m1, False)
            if not f:
                self.related_m_id_list.remove(t1)
                self.related_m_id_list.remove(t2)

        elif m1.mention_type == 'value_props' and m2.mention_type == 'entity':
            self.add_node(t2)
            self.nodes[t2]['label'] = 'concept'
            self.nodes[t2]['value'] = self.mentions[t2].value
            self.nodes[t2]['content'] = self.mentions[t2].content
            self.nodes[t2]['value_props'] = self.mentions[t1].content
        elif m1.mention_type == 'entity' and m2.mention_type == 'value_props':
            self.add_node(t1)
            self.nodes[t1]['label'] = 'concept'
            self.nodes[t1]['value'] = self.mentions[t1].value
            self.nodes[t1]['content'] = self.mentions[t1].content
            self.nodes[t1]['value_props'] = self.mentions[t2].content
        else:
            self.related_m_id_list.remove(t1)
            self.related_m_id_list.remove(t2)


if __name__ == '__main__':
    sentence = '在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹'
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
