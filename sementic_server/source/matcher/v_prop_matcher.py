"""
@description: 值属性字典匹配
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

import os
from os.path import join, exists

import yaml

from sementic_server.source.aho_matcher.match import build_aho
from sementic_server.source.tool.system_info import SystemInfo

SI = SystemInfo()
DATA_DIR = join(SI.base_path, "data")
DATA_DIR = os.path.abspath(DATA_DIR)
ONTO_DIR = join(DATA_DIR, "ontology")
AHO_DIR = join(DATA_DIR, "aho")

if not exists(AHO_DIR):
    os.makedirs(AHO_DIR)

with open(join(ONTO_DIR, 'v_property_list.yml'), 'r') as fr:
    V_PROPERTY_LIST = yaml.load(fr, Loader=yaml.SafeLoader)


class VpMatcher(object):
    def __init__(self, sentence):
        self.sentence = sentence
        dict_path = join(ONTO_DIR, 'v_property_mentions.yml')
        aho = build_aho(dict_path)  # load a dict from path
        self.match_result = aho.query4type(sentence)
        self.result = list()
        for mr in self.match_result:
            info = V_PROPERTY_LIST[mr['type']]
            term = {**mr, **info}
            self.result.append(term)

    def get_result(self):
        return self.result


if __name__ == '__main__':
    # match()
    s = '烽火科技的网站是多少?'
    vm = VpMatcher(s)
    r = vm.get_result()
    print(r)
