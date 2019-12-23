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

    def __init__(self, mentions, att_links):
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
    dep_att = dep_analyzer.get_att_deps(sentence)
    print("=================dependency=========================")
    for att in dep_att:
        print(att)
    print("=================dependency=========================")
    em = DepMap(ms, dep_att)
    tp = em.token_pairs
    for t in tp:
        print(t)
