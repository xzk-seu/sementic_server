"""
@description: 在线测试模块
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.tool.mention_collector import MentionCollector
from sementic_server.source.tool.global_object import dep_analyzer


"""
在东南大学上学的刘欢的舅舅
汪鹏老师的同学
微信群10319046645有哪些成员
张三的好友
# 根据称谓区分关系和称谓
在东南大学上学的徐同学
在东南大学上学的徐忠锴的同学

"""


if __name__ == '__main__':
    while True:
        sentence = input("please input:")
        m_collector = MentionCollector(sentence)

        dep_info = dep_analyzer.get_dep_info(sentence)
        qg = QueryParser(m_collector, dep_info)
        error_info = qg.error_info
        if error_info:
            print(error_info)
        qg.query_graph.show()
