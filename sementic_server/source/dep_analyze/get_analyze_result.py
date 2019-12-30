"""
@description: 获取依存分析结果
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-26
@version: 0.0.1
"""

import json
from copy import deepcopy

import requests

from sementic_server.source.tool.global_value import DEP_URL
from sementic_server.source.tool.logger import logger


def scope_cal(tokens):
    """
    为依存分析结果添加下标
    :param tokens:
    :return:
    """
    index = 0
    for token in tokens:
        token['begin'] = index
        index = index + len(token['word'])
        token['end'] = index - 1
    return tokens


class DepInfo(object):
    """
    依存分析信息类
    通过self.source_data获取所有依存分析信息
    通过self.get_att_deps(self)获取att关系

    内部：
    co_deps_process(self)对并列关系进行处理
    刘健坤的哥哥和表妹
    """
    def __init__(self, source_data: list):
        self.source_data = source_data
        self.non_data = False
        if not self.source_data:
            logger.error("DepInfo is None!")
            self.non_data = True
            return
        self.co_deps_process()

    def co_deps_process(self):
        """
        对依存分析中的并列关系进行处理，'tag': 'COO'
        在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹
        将哥哥的关系给表妹，更改表妹的idx2和tag
        刘坤见att哥哥   表妹coo哥哥
        得到刘坤见att表妹
        :return:
        """
        co_data = [x for x in self.source_data if x['tag'] == 'COO']
        temp_list = list()
        for co in co_data:
            idx = co['idx']
            idx2 = co['idx2']
            att_data = [x for x in self.source_data if x['idx2'] == idx2]
            for a in att_data:
                temp = deepcopy(a)
                temp['idx2'] = idx
                temp_list.append(temp)
        self.source_data.extend(temp_list)

    def get_heads(self):
        temp = [x for x in self.source_data if x['tag'] == "HED"]
        return temp

    def get_att_deps(self):
        deps_list = list()
        dep_result = self.source_data
        if self.non_data:
            return deps_list

        for i in dep_result:
            if i['tag'] == 'ATT':
                fr = int(i['idx2']) - 1
                temp = {'source': i, 'att': dep_result[fr]}
                deps_list.append(temp)

        return deps_list


class DepAnalyzer(object):
    """
    获取依存分析结果
    """
    def __init__(self):
        self.url = DEP_URL

    def get_result(self, sent):
        resp = None
        try:
            resp = requests.get(self.url, params={'text': sent})
        except Exception as e:
            logger.error(str(e))
        if resp:
            temp = json.loads(resp.text)
            result = scope_cal(temp['data'])
            return result

    def get_dep_info(self, sent):
        dep_result = self.get_result(sent)
        dep_info = DepInfo(dep_result)
        return dep_info

    def get_att_deps(self, sent):
        deps_list = list()
        dep_result = self.get_result(sent)
        for i in dep_result:
            if i['tag'] == 'ATT':
                fr = int(i['idx2']) - 1
                temp = {'source': i, 'att': dep_result[fr]}
                deps_list.append(temp)
        return deps_list


def demo_1():
    """
    依存分析处理demo
    :return:
    """
    da = DepAnalyzer()
    r = da.get_result("在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹")
    for i in r:
        print(i)
    print("======================")
    for i in r:
        if i['tag'] == 'ATT':
            fr = int(i['idx2']) - 1
            print(i, r[fr]['word'])


def main():
    """
    依存分析处理demo3
    :return:
    """
    da = DepAnalyzer()
    r = da.get_result("在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹")
    di = DepInfo(r)
    r = di.source_data
    print("==========dep========")
    for i in r:
        print(i)
    r = di.get_att_deps()
    print("=============att==========")
    for i in r:
        print(i)
    print("=============att=end=========")


if __name__ == '__main__':
    main()
    """
    'nature': 'r' 疑问词
    可以从疑问词出发，通过ATT访问到待查目标？
    """
    # demo_1()
