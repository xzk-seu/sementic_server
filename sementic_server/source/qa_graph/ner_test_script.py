"""
@description: 开发时对测试问句进行ner的脚本，便于进行离线试验
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

import json
import os

from tqdm import tqdm

from sementic_server.source.intent_extraction.item_matcher import ItemMatcher
from sementic_server.source.ner_task.account import Account
from sementic_server.source.ner_task.semantic_tf_serving import SemanticSearch

if __name__ == '__main__':
    questions = list()
    print(os.getcwd())
    with open('问句.txt', 'r', encoding='utf-8') as fr:
        fr.readline()
        for line in fr.readlines():
            line = line.strip()
            questions.append(line)

    semantic = SemanticSearch()
    item_matcher = ItemMatcher(True)
    account = Account()

    ner_results = list()

    for index, sentence in tqdm(enumerate(questions)):
        account_info = account.get_account_labels_info(sentence)
        intent = item_matcher.match(sentence, accounts_info=account_info)
        result, _ = semantic.sentence_ner_entities(intent)
        entity = result.get('entity') + result.get('accounts')
        relation = result.get('relation')
        intention = result.get('intent')

        data = dict(index=index, query=sentence, entity=entity, relation=relation, intent=intention)
        ner_results.append(data)
    with open('ner_results.json', 'w') as fw:
        json.dump(ner_results, fw)
