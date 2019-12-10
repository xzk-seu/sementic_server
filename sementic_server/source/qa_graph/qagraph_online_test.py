"""
@description: 在线测试模块
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.qa_graph.mention_collector import MentionCollector

if __name__ == '__main__':
    while True:
        sentence = input("please input:")
        m_collector = MentionCollector(sentence)
        data = dict(query=sentence, entity=m_collector.entity,
                    relation=m_collector.relation, value_props=m_collector.value_props)

        qg = QueryParser(data, None)

        error_info = qg.error_info
        if error_info:
            print(error_info)
            continue
        query_graph = qg.query_graph.get_data()
        qg.query_graph.show()