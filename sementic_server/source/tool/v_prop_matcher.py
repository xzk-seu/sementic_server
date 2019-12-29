"""
@description: 值属性字典匹配
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

from os.path import join

from sementic_server.source.aho_matcher.match import build_aho
from sementic_server.source.tool.global_value import ONTO_DIR, V_PROPERTY_LIST


class VpMatcher(object):
    """
    值属性匹配器
    """
    def __init__(self):
        dict_path = join(ONTO_DIR, 'v_property_mentions.yml')
        self.aho = build_aho(dict_path)  # load a dict from path

    def match(self, sentence):
        result = list()
        match_result = self.aho.query4type(sentence)
        for mr in match_result:
            if mr['type'] == 'Ambiguous':
                continue
            info = V_PROPERTY_LIST[mr['type']]
            term = {**mr, **info}
            result.append(term)
        return result


if __name__ == '__main__':
    s = '在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹'
    vm = VpMatcher()
    r = vm.match(s)
    print(r)
