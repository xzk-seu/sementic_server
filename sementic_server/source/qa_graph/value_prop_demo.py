"""
@description: 值属性查询demo
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-16
@version: 0.0.1
"""

import json
import os
from os.path import join
from pprint import pprint

import yaml

from sementic_server.source.intent_extraction.item_matcher import ItemMatcher
from sementic_server.source.intent_extraction.system_info import SystemInfo
from sementic_server.source.ner_task.account import Account
from sementic_server.source.ner_task.semantic_tf_serving import SemanticSearch
from sementic_server.source.qa_graph.query_parser import QueryParser

VALUE_PROP = dict()


def init_value_prop():
    global VALUE_PROP
    si = SystemInfo()
    # 获得根目录的地址
    dir_data = join(si.base_path, "data")
    dir_yml = join(dir_data, "yml")
    file_path = join(dir_yml, 'value_prop_dict.yml')
    with open(file_path, 'r') as fr:
        data = yaml.load(fr, Loader=yaml.SafeLoader)
    VALUE_PROP = data


init_value_prop()


def get_value_props(sentence):
    value_props = list()
    for k in VALUE_PROP.keys():
        if k in sentence:
            value_props.extend(VALUE_PROP[k])
    return value_props


def main():
    semantic = SemanticSearch()
    item_matcher = ItemMatcher(True)
    account = Account()

    # sentence = input("please input:")

    sentence = "烽火科技的工商注册号是多少？"
    # sentence = "张三的生日？"

    account_info = account.get_account_labels_info(sentence)
    intent = item_matcher.match(sentence, accounts_info=account_info)
    result, _ = semantic.sentence_ner_entities(intent)
    pprint(result)
    entity = result.get('entity') + result.get('accounts')
    relation = result.get('relation')
    intention = result.get('intent')

    if len(result.get("entity") + result.get("accounts")) == 0:
        print({"query": sentence, "error": "实体识别模块返回空值"})
        # continue

    data = dict(query=sentence, entity=entity, relation=relation, intent=intention, dependency=None)
    data['value_props'] = get_value_props(sentence)
    print(entity)
    print(relation)
    # p = os.path.join(os.getcwd(), 'test_case.json')
    # json.dump(data, open(p, 'w'))
    qg = QueryParser(data, None)

    error_info = qg.error_info
    if error_info:
        print(error_info)
        # continue
    query_graph = qg.query_graph.get_data()
    qg.query_graph.show()

    # qi = QueryInterface(qg.query_graph, intent["query"])
    # query_interface = qi.get_query_data()
    # query_graph_result = {'query_graph': query_graph, 'query_interface': query_interface}
    # pprint(query_graph_result)


if __name__ == '__main__':
    main()
    # sentence = "烽火科技的工商注册号是多少？"
    # for k in VALUE_PROP.keys():
    #     if k in sentence:
    #         print(VALUE_PROP[k])
