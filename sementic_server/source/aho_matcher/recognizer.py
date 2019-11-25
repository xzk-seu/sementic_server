"""
@description: 实现关系、疑问词的识别
@author: Wu Jiang-Heng
@email: jiangh_wu@163.com
@time: 2019-05-29
@version: 0.0.1
"""
from functools import cmp_to_key

from sementic_server.source.aho_matcher.actree import Aho
from sementic_server.source.aho_matcher.helper import build_vocab, word2id, id2word, cmp, find_word_range_in_sentence


class Recognizer(object):
    """
    @description: 实现关系、疑问词的识别
    @author: Wu Jiang-Heng
    @email: jiangh_wu@163.com
    @time: 2019-05-29
    @version: 0.0.1
    """

    def __init__(self, vocab: dict):
        """
        利用词典建树
        :param vocab:
        """
        self.w2tp, self.c2id, self.id2c = build_vocab(vocab)
        self.actree = Aho()
        for vls in vocab.values():
            for vl in vls:
                if vl is not None:
                    self.actree.insert(word2id(self.c2id, vl))
        self.actree.build()

    def query(self, q: str):
        """
        利用AC自动机查询q中包含的词典词汇
        :param q:
        :return:
        """
        q2id = word2id(self.c2id, q)
        match_node = self.actree.match(q2id)

        res_word_id = self.actree.parse(match_node)

        res_words = [id2word(self.id2c, rwi) for rwi in res_word_id]

        return res_words

    def query4type(self, query: str):
        """
        将词典词汇和其类型对应
        :param query: 查询词汇
        :return:
        """
        words = self.query(query)
        words_info = list()
        res = list()

        # find positions of words
        for word in words:
            find_word_range_in_sentence(word, query, words_info)

        words_info = sorted(words_info, key=cmp_to_key(cmp))
        # 是否有重叠的关键词
        last_end = -1  # 记录上一个关键词结束的位置
        for i, t in enumerate(words_info):
            if t[0] <= last_end:  # 如果本关键词开始的位置位于上个关键词内，则跳过此关键词
                continue
            ok = True
            for j in range(i - 1, -1, -1):
                if t[1] <= words_info[j][1]:
                    ok = False
                    break
            if ok:
                last_end = t[1]
                res.append({
                    "type": self.w2tp.get(t[2], "NIL"),
                    "value": t[2],
                    "begin": t[0],
                    "end": t[1] + 1
                })

        return res
