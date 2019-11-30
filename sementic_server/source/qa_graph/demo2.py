"""
@description: 值属性查询demo
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-16
@version: 0.0.1
"""

from sementic_server.source.intent_extraction.item_matcher import ItemMatcher
from sementic_server.source.ner_task.account import Account
from sementic_server.source.ner_task.semantic_tf_serving import SemanticSearch
from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.tool.v_prop_matcher import VpMatcher


def main():
    semantic = SemanticSearch()
    item_matcher = ItemMatcher(True)
    account = Account()
    vp_matcher = VpMatcher()
    # sentence = input("please input:")

    sentence = "QQ号13756478的好友有哪些？"

    # sentence = "张三的好友"

    # sentence = "在东南大学上学的徐忠锴的舅舅"

    """
    根据称谓区分关系和称谓
    
    在东南大学上学的徐同学
    在东南大学上学的徐忠锴的同学
    """

    account_info = account.get_account_labels_info(sentence)
    intent = item_matcher.match(sentence, accounts_info=account_info)
    result, _ = semantic.sentence_ner_entities(intent)
    # pprint(result)
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

    qg = QueryParser(data, None)

    error_info = qg.error_info
    if error_info:
        print(error_info)
    qg.query_graph.show()

    t = qg.query_graph.get_edges_dict()
    print(t)
    t = qg.query_graph.get_nodes_dict()
    print(t)

    # qi = QueryInterface(qg.query_graph, intent["query"])
    # query_interface = qi.get_query_data()
    # query_graph_result = {'query_graph': query_graph, 'query_interface': query_interface}
    # pprint(query_graph_result)


if __name__ == '__main__':
    main()
