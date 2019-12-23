"""
@description: 用依存信息将mention关联
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-10
@version: 0.0.1
"""
from sementic_server.source.qa_graph.mention_collector import MentionCollector
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.qa_graph.graph import Graph
import networkx as nx
from sementic_server.source.dep_analyze.get_analyze_result import DepAnalyzer, DepInfo
from itertools import permutations


class Token(object):
    """
    依存分析中的一个词
    """

    def __init__(self, t_dict):
        self.word = t_dict['word']
        self.begin = t_dict['begin']
        self.end = t_dict['end']
        self.mention_type = None
        self.small_type = None
        self.mention_id = None

    def match_mention(self, mentions: list):
        mentions = sorted(mentions, key=lambda x: x.content['end'])
        for m in mentions:
            # 区间交
            if max(m.begin, self.begin) <= min(m.end, self.end):
                self.mention_type = m.mention_type
                self.small_type = m.small_type
                self.mention_id = m.idx
                return


class DepMap(object):
    """
    将mention和依存分析中的att_links进行匹配
    多个token对应一个mention：长实体被依存切分
    # 多个mention对应一个token：姓和名、称谓被切分（在mention_collector中已合并)
    update: 根据依存信息组织mention
    """

    def __init__(self, mention_collector: MentionCollector, dep_info: DepInfo):
        mentions = mention_collector.get_mentions()
        att_links = dep_info.get_att_deps()
        self.token_pairs = list()
        for att_link in att_links:
            source = att_link['source']
            token_s = Token(source)
            token_s.match_mention(mentions)

            source = att_link['att']
            token_a = Token(source)
            token_a.match_mention(mentions)
            if token_a.mention_id == token_s.mention_id:
                continue
            token_pair = {'source': token_s.__dict__, 'att': token_a.__dict__}
            self.token_pairs.append(token_pair)


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

