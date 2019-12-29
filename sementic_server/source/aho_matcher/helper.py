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

def replace_items_in_sentence(sentence, items):
    """
    替换句子在item中出现的元素
    :param sentence: 原始句子
    :param items: 需要替换的item ((begin, end, value),())
    :return:
    """
    size = len(items)
    if size < 1:
        return sentence
    sentence_after_replace = ""
    index = 0
    for position, char in enumerate(sentence):
        if position is items[index][0]:
            sentence_after_replace += items[index][2]
        elif position not in range(items[index][0] + 1, items[index][1]):
            sentence_after_replace += char

        if position is items[index][1] - 1 and index < size - 1:
            index += 1

    return sentence_after_replace


def resolve_list_confilct(raw_list, ban_list):
    """
    消解raw_list和ban_list的冲突
    :param raw_list: 需要被消解冲突的部分
    :param ban_list: 禁止出现的位置索引
    :return:
    """
    if len(ban_list) < 1:
        return raw_list

    res_list = []
    index_ban = set()
    for ban in ban_list:
        if type(ban) in {list, tuple}:
            index_ban.update(list(range(ban[0], ban[1])))
        else:
            index_ban.update(list(range(ban["begin"], ban["end"])))

    for item in raw_list:
        if type(item) in {list, tuple}:
            item_range = list(range(item[0], item[1]))
        else:
            item_range = list(range(item["begin"], item["end"]))
        if index_ban.intersection(item_range) == set():
            res_list.append(item)
    return res_list


def update_account_in_sentence(accounts: list, sentence: str):
    """
    更新账号在句子中的位置
    :param accounts:
    :param sentence:
    :return:
    """
    for index, info in enumerate(accounts):
        begin = sentence.find(info["value"])
        if begin is not info["begin"]:
            accounts[index]["begin"] = begin
            accounts[index]["end"] = begin + len(info["value"])


def power_set(l: list):
    """
    生成列表l的幂集
    :param l:一个列表
    """
    res = [[]]
    for i in l:
        sz = len(res)
        for j in range(sz):
            tmp = res[j].copy()
            tmp.append(i)
            res.append(tmp)
    return res


def replace_position_with_another_by_combination(word, another, combination):
    """
    根据组合更改位置上的值
    :param word:目标词
    :param another:更改的词
    :param combination:位置组合
    :return:替换后的新词
    """
    w = ""
    for i in range(len(word)):
        if i in combination:
            w += another[i]
        else:
            w += word[i]

    return w
