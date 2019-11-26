"""
@description: 值属性查询demo
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-16
@version: 0.0.1
"""

from os.path import join
from pprint import pprint

import yaml

from sementic_server.source.intent_extraction.item_matcher import ItemMatcher
from sementic_server.source.ner_task.account import Account
from sementic_server.source.ner_task.semantic_tf_serving import SemanticSearch
from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.tool.system_info import SystemInfo

VALUE_PROP = dict()
SI = SystemInfo()


def init_value_prop():
    global VALUE_PROP
    # 获得根目录的地址
    dir_data = join(SI.base_path, "data")
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

    sentence = "烽火科技的网站是多少？"
    # sentence = "张三的国籍？"

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

    qg = QueryParser(data, None)

    error_info = qg.error_info
    if error_info:
        print(error_info)
    qg.query_graph.show()


if __name__ == '__main__':
    # main()
    count = 0
    temp = list()
    for k, v in VALUE_PROP.items():
        print(k, len(v), v)
        if len(v) > 1:
            count += 1
            temp.append(k)
    print(count)
    print(temp)
