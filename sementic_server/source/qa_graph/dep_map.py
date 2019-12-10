"""
@description: 依存信息映射为问答图
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-10
@version: 0.0.1
"""
from sementic_server.source.qa_graph.mention_collector import MentionCollector
from sementic_server.source.tool.global_object import dep_analyzer


class Token(object):
    def __init__(self, t_dict):
        self.word = t_dict['word']
        self.begin = t_dict['begin']
        self.end = t_dict['end']
        self.mention_type = None
        self.small_type = None

    def match_mention(self, mentions: list):
        for m in mentions:
            if max(m.begin, self.begin) <= min(m.end, self.end):
                pass


class DepMap(object):
    def __init__(self, mentions, att_links):
        for att_link in att_links:
            source = att_link['source']
            token = Token(source)


if __name__ == '__main__':
    sentence = '东南大学汪老师的学生张三'
    m_collector = MentionCollector(sentence)
    ms = m_collector.get_mentions()
    for mt in m_collector.mentions:
        print(mt)
    dep_att = dep_analyzer.get_att_deps(sentence)
    for att in dep_att:
        print(att)
    em = DepMap(ms, dep_att)
