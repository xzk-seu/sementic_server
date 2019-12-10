"""
@description: 单句功能调试demo
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-16
@version: 0.0.1
"""

from sementic_server.source.qa_graph.mention_collector import MentionCollector
from sementic_server.source.qa_graph.query_parser import QueryParser


def main():
    """
    通过：
    微信群10319046645有哪些成员
    张三的好友
    """
    sentence = "微信帐户DonDdon担任什么群的群主"

    """
    根据称谓区分关系和称谓
    
    在东南大学上学的徐同学
    在东南大学上学的徐忠锴的同学
    
    QQ号13756478的好友有哪些？
    微信群10319046645有哪些成员
    # sentence = "在东南大学上学的徐忠锴的舅舅"
    """

    m_collector = MentionCollector(sentence)

    data = dict(query=sentence, entity=m_collector.entity,
                relation=m_collector.relation, value_props=m_collector.value_props)
    qg = QueryParser(data, None)

    error_info = qg.error_info
    if error_info:
        print(error_info)
    qg.query_graph.show()

    t = qg.query_graph.get_edges_dict()
    print(t)
    t = qg.query_graph.get_nodes_dict()
    print(t)


if __name__ == '__main__':
    main()
