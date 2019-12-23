import json
import os
from os.path import join, exists

import yaml

from sementic_server.source.tool.system_info import SystemInfo

SI = SystemInfo()

DATA_DIR = join(SI.base_path, "data")
DATA_DIR = os.path.abspath(DATA_DIR)
ONTO_DIR = join(DATA_DIR, "ontology")
YML_DIR = join(DATA_DIR, "yml")
AHO_DIR = join(DATA_DIR, "aho")
if not exists(AHO_DIR):
    os.makedirs(AHO_DIR)

CONF_DIR = join(SI.base_path, "config")
CONF_DIR = os.path.abspath(CONF_DIR)

with open(join(CONF_DIR, 'model.config'), 'r', encoding='utf-8') as fr:
    DEP_URL = json.load(fr)['dependence_url']

with open(join(ONTO_DIR, 'v_property_list.yml'), 'r', encoding='utf-8') as fr:
    V_PROPERTY_LIST = yaml.load(fr, Loader=yaml.SafeLoader)

DEFAULT_EDGE = dict()
RELATION_DATA = dict()
RELATION_KEYWORD = dict()


def init_default_edge():
    """
    初始化默认边列表
    :return:
    """
    global DEFAULT_EDGE
    path = os.path.join(ONTO_DIR, 'default_relation.yml')
    path = os.path.abspath(path)
    with open(path, 'r', encoding='utf-8') as d_fr:
        DEFAULT_EDGE = yaml.load(d_fr, Loader=yaml.SafeLoader)


def init_relation_data():
    """
    将object_attribute.csv中的对象属性读取为一个关系字典
    :return:
    """
    global RELATION_DATA
    path = os.path.join(ONTO_DIR, 'object_attribute.yml')
    with open(path, 'r', encoding='utf-8') as d_fr:
        RELATION_DATA = yaml.load(d_fr, Loader=yaml.SafeLoader)


def init_relation_keyword():
    """
    将relation.yml中的对象属性读取为一个关系字典
    :return:
    """
    global RELATION_KEYWORD
    path = os.path.join(YML_DIR, 'relation.yml')
    with open(path, 'r', encoding='utf-8') as d_fr:
        RELATION_KEYWORD = yaml.load(d_fr, Loader=yaml.SafeLoader)


init_default_edge()
init_relation_data()
init_relation_keyword()

ACCOUNT_LIST = ['QQ_NUM', 'MOB_NUM', 'PHONE_NUM', 'IDCARD_VALUE', 'EMAIL_VALUE', 'WECHAT_VALUE', 'QQ_GROUP_NUM',
                'WX_GROUP_NUM', 'ALIPAY_VALUE', 'DOUYIN_VALUE', 'JD_VALUE', 'TAOBAO_VALUE', 'MICROBLOG_VALUE',
                'UNLABEL', 'VEHCARD_VALUE', 'IMEI_VALUE', 'MAC_VALUE']
