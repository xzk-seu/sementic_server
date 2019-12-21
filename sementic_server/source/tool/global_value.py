import os
from os.path import join, exists

import yaml
import logging

from sementic_server.source.tool.system_info import SystemInfo

SI = SystemInfo()
logger = logging.getLogger("server_log")

DATA_DIR = join(SI.base_path, "data")
DATA_DIR = os.path.abspath(DATA_DIR)
ONTO_DIR = join(DATA_DIR, "ontology")
AHO_DIR = join(DATA_DIR, "aho")
if not exists(AHO_DIR):
    os.makedirs(AHO_DIR)

with open(join(ONTO_DIR, 'v_property_list.yml'), 'r', encoding='utf-8') as fr:
    V_PROPERTY_LIST = yaml.load(fr, Loader=yaml.SafeLoader)


DEFAULT_EDGE = dict()
RELATION_DATA = dict()


def init_default_edge():
    """
    初始化默认边列表
    :return:
    """
    global DEFAULT_EDGE
    path = os.path.join(SI.base_path, 'data', 'ontology', 'default_relation.yml')
    path = os.path.abspath(path)
    with open(path, 'r', encoding='utf-8') as d_fr:
        DEFAULT_EDGE = yaml.load(d_fr, Loader=yaml.SafeLoader)


def init_relation_data():
    """
    将object_attribute.csv中的对象属性读取为一个关系字典
    :return:
    """
    global RELATION_DATA
    path = os.path.join(SI.base_path, 'data', 'ontology', 'object_attribute.yml')
    with open(path, 'r', encoding='utf-8') as d_fr:
        RELATION_DATA = yaml.load(d_fr, Loader=yaml.SafeLoader)


init_default_edge()
init_relation_data()
