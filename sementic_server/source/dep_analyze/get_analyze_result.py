import requests
import json
from sementic_server.source.tool.global_value import logger


class DepAnalyzer(object):
    def __init__(self):
        self.url = 'http://120.132.109.87:10088/jfycfx'

    def get_result(self, sent):
        resp = None
        try:
            resp = requests.get(self.url, params={'text': sent})
        except Exception as e:
            logger.error(str(e))
        if resp:
            temp = json.loads(resp.text)
            return temp['data']

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
    r = da.get_result("微信帐户DonDdon担任什么群的群主")
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
