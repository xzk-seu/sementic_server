"""
@description: 值属性查询demo
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-16
@version: 0.0.1
"""

from pprint import pprint

from sementic_server.source.intent_extraction.item_matcher import ItemMatcher
from sementic_server.source.ner_task.account import Account
from sementic_server.source.ner_task.semantic_tf_serving import SemanticSearch
from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.tool.v_prop_matcher import VpMatcher


if __name__ == '__main__':
    semantic = SemanticSearch()
    item_matcher = ItemMatcher(True)
    account = Account()
    vp_matcher = VpMatcher()
    """
    # sentence = input("please input:")

    # sentence = "烽火科技的网站是多少？"
    """
    sentence = "南京市在烽火科技工作的张三的国籍？"

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
    data['value_props'] = vp_matcher.match(sentence)
    print(entity)
    print(relation)
    print(data['value_props'])
