"""
@description: 单句功能调试demo
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-26
@version: 0.0.1
"""

import json

from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.query_interface.query_interface import QueryInterface
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.mention_collector import MentionCollector


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
    # 值属性问题
    烽火科技的行业

    意图不通过：
    微信帐户DonDdon担任什么群的群主
    户口地址辽宁省大连市甘井子区祥龙西园28号1-16-1的尤成礼
    扣扣群号10453443中谁的微博帐户是1005065716003
    哪个公司的手机是13204031914
    """
    sentence = "手机号是18625173485的吴佑波是谁"
    m_collector = MentionCollector(sentence)
    intent = m_collector.intention
    print("intent:", intent)
    print("=====================mention===================")
    for m in m_collector.mentions:
        print(m)

    dep_info = dep_analyzer.get_dep_info(sentence)
    print("======================dep======================")
    for d in dep_info.get_att_deps():
        print(d)
    for d in dep_info.get_heads():
        print(d)

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
