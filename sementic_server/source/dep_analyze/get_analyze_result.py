import json

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
    def __init__(self, source_data):
        self.source_data = source_data

    def get_att_deps(self):
        deps_list = list()
        dep_result = self.source_data
        for i in dep_result:
            if i['tag'] == 'ATT':
                fr = int(i['idx2']) - 1
                temp = {'source': i, 'att': dep_result[fr]}
                deps_list.append(temp)
        return deps_list


class DepAnalyzer(object):
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
    da = DepAnalyzer()
    r = da.get_result("东南大学汪老师的学生张三")
    for i in r:
        print(i)
    print("======================")
    for i in r:
        if i['tag'] == 'ATT':
            fr = int(i['idx2']) - 1
            print(i, r[fr]['word'])


def main():
    da = DepAnalyzer()
    r = da.get_att_deps("张三的爸爸是谁")
    for i in r:
        print(i)


if __name__ == '__main__':
    # main()
    """
    'nature': 'r' 疑问词
    可以从疑问词出发，通过ATT访问到待查目标？
    """
    demo_1()
