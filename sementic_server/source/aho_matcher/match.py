"""
@description: 匹配器
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-26
@version: 0.0.1
"""

import json
import pickle
from os.path import join, exists

import yaml

from sementic_server.source.aho_matcher.recognizer import Recognizer
from sementic_server.source.tool.global_value import AHO_DIR, YML_DIR


def load_aho(path, f_type='pkl'):
    """
        直接load一个匹配器对象
        ------------------------------------------
        Args:
            path: 匹配器对象路径
            f_type: 对象序列化类型，只支持pkl

        Returns:
            一个匹配器对象

    """
    if exists(path):
        if f_type == 'pkl':
            return pickle.load(open(path, 'rb'))


def build_aho(path, f_type='yml'):
    """
        重新构建一个匹配器对象
        ------------------------------------------
        Args:
            path:
            f_type:

        Returns:

    """
    if exists(path):
        d = None
        if f_type is 'yml':
            d = yaml.load(open(path, 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
        elif f_type is 'json':
            d = json.load(open(path, 'r', encoding='utf-8'))

        if d:
            return Recognizer(d)


def save_aho(aho, path):
    pickle.dump(aho, open(path, 'wb'))


def match():
    dict_path = join(YML_DIR, 'relation.yml')
    aho_path = join(AHO_DIR, 'relation.pkl')

    # 示例1: 构建一个匹配器对象并保存
    aho = build_aho(dict_path)  # load a dict from path
    save_aho(aho, aho_path)  # dump a aho

    # 示例2: 直接读取一个aho对象，然后识别
    aho = load_aho(aho_path)
    print(aho.query("李刚的爸爸是谁"))  # 查找句子存在哪些词典中的元素
    print(aho.query4type("李刚妈妈的爸爸是谁"))  # 查找对应元素的位置和词典中的key


if __name__ == '__main__':
    match()
