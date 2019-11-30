"""
@description: 依存分析测试
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-06-21
@version: 0.0.1
"""

import json
import os

from sementic_server.source.qa_graph.query_interface import QueryInterface
from sementic_server.source.qa_graph.query_parser import QueryParser

if __name__ == '__main__':
    case_num = 2
    path = os.path.join(os.getcwd(), os.path.pardir, os.path.pardir, 'data', 'test_case', 'case%d.json' % case_num)
    path = os.path.abspath(path)

    with open(path, 'r') as fr:
        data = json.load(fr)
    print(data)

    qp = QueryParser(data)
    qp.query_graph.show()

    qi = QueryInterface(qp.query_graph, data['query'])
    qd = qi.get_query_data()
