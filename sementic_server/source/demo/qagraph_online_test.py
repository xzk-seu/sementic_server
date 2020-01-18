"""
@description: 在线测试模块
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

import json

from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.query_interface.query_interface import QueryInterface
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.mention_collector import MentionCollector

"""
在广东省揭阳市惠来县定居的刘健坤的哥哥和表妹
在东南大学上学的刘欢的舅舅
汪鹏老师的同学
微信群10319046645有哪些成员
QQ群10319046645有哪些成员
张三的好友
# 根据称谓区分关系和称谓
在东南大学上学的徐同学
在东南大学上学的徐忠锴的同学
在烽火星空上班的张老师是谁

手机号为1517658493的朋友
住在西善桥北路89号的18526439876的在华为上班的同学是谁?

老家在泰安市的人有哪些？
葛宗纬河北省张家口张北县人

"""

if __name__ == '__main__':
    while True:
        sentence = input("please input:")
        m_collector = MentionCollector(sentence)
        for m in m_collector.mentions:
            print(m)
        dep_info = dep_analyzer.get_dep_info(sentence)
        qg = QueryParser(m_collector, dep_info)
        error_info = qg.error_info
        if error_info:
            print("error_info:", error_info)
        qg.query_graph.show()

        qi = QueryInterface(qg.query_graph, sentence)
        qid = qi.get_dict()
        with open('interface_demo.json', 'w') as fw:
            json.dump(qid, fw)
