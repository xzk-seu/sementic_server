"""
@description: 问句解析过程
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

import networkx as nx

from sementic_server.source.dep_analyze.get_analyze_result import DepInfo
from sementic_server.source.qa_graph.dep_info2graph import DepGraph
from sementic_server.source.qa_graph.graph import Graph
from sementic_server.source.qa_graph.query_graph import QueryGraph
from sementic_server.source.qa_graph.rest_mention2graph import RestMentionGraph
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.logger import logger
from sementic_server.source.tool.mention_collector import MentionCollector


class QueryParser(object):
    """
    动态问答图语义解析模块
    1、将依存信息映射为图
        self.dep_graph = DepGraph(self.m_collector, self.dep_info)
    2、将剩余的mention依照上一期的规则映射为图
        self.rest_mention_graph = RestMentionGraph(dep_rest_mentions).get_mention_graph()
    3、将上一步的两个图进行合并，构造联通的问答图
        self.query_graph = QueryGraph(self.dep_graph, self.rest_mention_graph)
    4、意图确定

    """

    def __init__(self, m_collector: MentionCollector, dep_info: DepInfo):
        logger.info('Query Graph Parsing...')
        self.error_info = None

        self.m_collector = m_collector
        self.mentions = m_collector.mentions

        self.entity = m_collector.entity
        self.relation = m_collector.relation
        self.value_prop = m_collector.value_props

        intent = m_collector.intention
        if intent:
            intent = intent.lower()
        self.intent = intent
        self.dep_info = dep_info
        self.relation_component_list = list()
        self.entity_component_list = list()

        self.dep_graph = DepGraph(self.m_collector, self.dep_info)

        dep_rest_mentions = self.dep_graph.get_rest_mentions()
        self.rest_mention_graph = RestMentionGraph(dep_rest_mentions).get_mention_graph()

        self.query_graph = QueryGraph(self.dep_graph, self.rest_mention_graph)
        if self.query_graph.error_info:
            self.error_info = self.query_graph.error_info
            return

        # 经过上面两个循环，得到连通的图，下面确定意图
        logger.info('connected graph is already')
        self.query_graph = Graph(self.query_graph)
        self.query_graph = nx.convert_node_labels_to_integers(self.query_graph)
        self.query_graph.show_log()
        logger.info('next is determine intention')
        self.determine_intention()

    def intent_rule_0(self):
        """
        一条边上，一个节点又有内容又有意图而另一个没有，将意图给另一个
        :return:
        """
        flag = False
        for n1, n2, k in self.query_graph.edges:
            if self.query_graph.nodes[n1].get("intent") or self.query_graph.nodes[n2].get("intent"):
                flag = True
                if self.query_graph.nodes[n1].get("intent") and self.query_graph.nodes[n2].get("intent"):
                    continue
                if self.query_graph.nodes[n1].get("intent") and self.query_graph.nodes[n1].get("content"):
                    self.query_graph.nodes[n1]["intent"] = False
                    self.query_graph.nodes[n2]["intent"] = True
                elif self.query_graph.nodes[n2].get("intent") and self.query_graph.nodes[n2].get("content"):
                    self.query_graph.nodes[n2]["intent"] = False
                    self.query_graph.nodes[n1]["intent"] = True
        return flag

    def intent_rule_1(self):
        has_intent = False
        for n in self.query_graph.nodes:
            if self.query_graph.nodes[n].get('intent'):
                has_intent = True
            if not self.query_graph.nodes[n].get('value'):
                if self.query_graph.is_none_node(n):
                    self.add_intention_on_node(n)
                    has_intent = True
                elif self.query_graph.nodes[n].get("intent"):
                    self.query_graph.nodes[n]['intent'] = False
            if self.query_graph.nodes[n].get('value_props'):
                self.add_intention_on_node(n)
                has_intent = True
        return has_intent

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
        if self.intent_rule_0():
            return

        if self.literal_intention():
            return

        if self.intent_rule_1():
            return

        intention_candidates = self.get_intention_candidate()
        if self.error_info:
            return
        logger.info('determine intention by degree')
        criterion_dict = dict()
        for node in intention_candidates:
            criterion_dict[node] = self.query_graph.get_out_index(node)

        m_v = min(criterion_dict.values())
        # 考虑到多个节点上都有最值
        intention_nodes = [k for k, v in criterion_dict.items() if v == m_v]
        logger.info('nodes: %s have degree: %d' % (str(intention_nodes), m_v))

        logger.info('final intention node is %d' % intention_nodes[0])
        self.add_intention_on_node(intention_nodes[0])

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
        elif len(none_nodes) == 0:
            temp_candidates = [x for x in intention_candidates if not self.query_graph.nodes[x].get("content")]
            if len(temp_candidates) > 0:
                intention_candidates = temp_candidates
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


if __name__ == '__main__':
    """
    # q = '在东莞常平司马村珠江啤酒厂斜对面合租的15842062826的老婆'
    东南大学汪鹏老师的同学张三
    """

    sentence = '在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹'
    print(sentence)
    m_c = MentionCollector(sentence)
    for m in m_c.mentions:
        print(m)
    dep_i = dep_analyzer.get_dep_info(sentence)
    for d in dep_i.get_att_deps():
        print(d)
    qg = QueryParser(m_c, dep_i)
    if qg.error_info:
        print(qg.error_info)
    qg.query_graph.show()
