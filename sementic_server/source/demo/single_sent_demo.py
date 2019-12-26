"""
@description: 单句功能调试demo
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-16
@version: 0.0.1
"""

from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.mention_collector import MentionCollector
from sementic_server.source.query_interface.query_interface import QueryInterface
import json


def main():
    """
    通过：
    QQ号13756478的好友有哪些
    在东南大学上学的刘欢的舅舅
    微信群10319046645有哪些成员
    张三的好友
    # 根据称谓区分关系和称谓
    在东南大学上学的徐同学
    在东南大学上学的徐忠锴的同学

    值属性问题：
    烽火科技的行业

    意图不通过：
    微信帐户DonDdon担任什么群的群主
    """
    sentence = "烽火科技的行业"
    m_collector = MentionCollector(sentence)

    dep_info = dep_analyzer.get_dep_info(sentence)
    qg = QueryParser(m_collector, dep_info)
    error_info = qg.error_info
    if error_info:
        print(error_info)
    qg.query_graph.show()

    qi = QueryInterface(qg.query_graph, sentence)
    qid = qi.get_dict()
    with open('interface_demo.json', 'w') as fw:
        json.dump(qid, fw)


if __name__ == '__main__':
    main()
