"""
@description: 用依存信息将mention关联
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-10
@version: 0.0.1
"""
from sementic_server.source.dep_analyze.get_analyze_result import DepInfo
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.mention_collector import MentionCollector


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
                return True
        return False


class DepMap(object):
    """
    将mention和依存分析中的att_links进行匹配
    得到
    self.token_pairs = list()
    和
    self.head_intentions = list()
    多个token对应一个mention：长实体被依存切分
    # 多个mention对应一个token：姓和名、称谓被切分（在mention_collector中已合并)
    update: 根据依存信息组织mention
    """

    def __init__(self, mention_collector: MentionCollector, dep_info: DepInfo):
        self.token_pairs = list()
        self.head_intentions = list()
        self.mentions = mention_collector.get_mentions()
        if dep_info.non_data:
            return
        self.att_links = dep_info.get_att_deps()
        self.dep_info = dep_info
        self.init_token_pairs()
        self.init_head_intentions()

    def init_head_intentions(self):
        """
        从依存分析的头节点推断意图
        考虑到coo依存会将相关依存关系复制一遍，所以考虑问句有多个头实体
        在get_analyze_result.py co_deps_process(self)中
        若头节点对应实体，则认为该实体为查询意图
        :return:
        """
        heads = [x for x in self.dep_info.source_data if x['tag'] == "HED"]
        heads_ids = [x['idx'] for x in heads]
        heads_token = [Token(x) for x in heads]
        temp_flag = self.check_target(heads_token)
        # 若根结点没有匹配到mention，选择根结点的下层节点匹配
        if not temp_flag:
            temp_tokens = [Token(x) for x in self.dep_info.source_data if x['idx2'] in heads_ids]
            self.check_target(temp_tokens)

    def check_target(self, token_list: list):
        flag = False
        for token in token_list:
            token.match_mention(self.mentions)
            if token.mention_type == "entity":
                flag = True
                self.head_intentions.append(token.mention_id)
        return flag

    def init_token_pairs(self):
        for att_link in self.att_links:
            source = att_link['source']
            token_s = Token(source)
            if not token_s.match_mention(self.mentions):
                continue
            source = att_link['att']
            token_a = Token(source)
            token_a.match_mention(self.mentions)
            if not token_a.match_mention(self.mentions):
                continue
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
