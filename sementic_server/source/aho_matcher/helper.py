"""
@description: 帮助
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-26
@version: 0.0.1
"""


def build_vocab(vo_dict: dict):
    """
        将原始json转换为词典
        三个词典，分别是：
        - 疑问词->type
        - 词->id
        - id->词
    """
    word2type = dict()
    char_pool = set()
    for k, v in vo_dict.items():
        word2type.update({vi: k for vi in v if vi is not None})

        for vi in v:
            if vi is not None:
                for vii in vi:
                    char_pool.add(vii)

    char_pool = list(char_pool)
    char2id = {c: i + 1 for i, c in enumerate(char_pool)}
    id2char = {i + 1: c for i, c in enumerate(char_pool)}

    return word2type, char2id, id2char


def word2id(c2id: dict, word: str):
    """
    将一个词用词典c2id组织成列表的形式

    :param c2id: 字符->id的词典
    :param word: 输入的单词
    :return:    输入单词对应的字符索引列表
    """
    word_id = list()

    for i, c in enumerate(word):
        if c in c2id:
            word_id.append(c2id[c])
        else:
            word_id.append(0)
    return word_id


def id2word(id2c: dict, ids: list):
    """
    将一个字符索引列表组织成单词

    :param id2c: id->字符的词典
    :param ids:  输入的字符索引列表
    :return:     字符列表对应的单词
    """
    word = ""
    for i in ids:
        if i in id2c:
            word += id2c[i]
        else:
            return ""
    return word


def cmp(x, y):
    """
    比较函数
    :param x:数1
    :param y:数2
    :return:
    """
    if x[0] < y[0]:
        return -1
    elif x[0] > y[0]:
        return 1
    if x[1] > y[1]:
        return -1
    else:
        return 1


def find_word_range_in_sentence(word, query, words_info):
    """
    在query查找word的位置信息
    :param word:
    :param query:
    :param words_info:
    :return:
    """
    index = 0
    while index != -1:
        index = query.find(word, index)
        if index != -1:
            words_info.append((index, index + len(word) - 1, word))
            index += 1
