"""
@description: 批量自测借口
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-05-27
@version: 0.0.1
"""

import json
import logging
import timeit
from tqdm import tqdm

from sementic_server.source.qa_graph.query_parser import QueryParser
from sementic_server.source.query_interface.query_interface import QueryInterface
from sementic_server.source.tool.global_object import dep_analyzer
from sementic_server.source.tool.mention_collector import MentionCollector

logger = logging.getLogger("server_log")
logger.setLevel(logging.INFO)


def query_graph_model(sentence):
    """
    查询图模块
    :param sentence:
    :return:
    """
    logger.setLevel(logging.INFO)
    logger.info("Query Graph model...")
    t_another = timeit.default_timer()
    # 问答图模块
    error_info = None
    qg = None
    try:
        start_time_1 = timeit.default_timer()
        logger.info("[sentence:%s][问答图整体模块][知识抽取阶段-start]\n" % sentence)
        m_collector = MentionCollector(sentence)
        logger.info("=====================mention===================")
        for m in m_collector.mentions:
            logger.info(str(m))
        if len(m_collector.entity) == 0:
            error_info = 201
            return None, error_info
        logger.info("[sentence:%s][问答图整体模块][知识抽取阶段-end][costTime:%dms]\n" %
                    (sentence, timeit.default_timer() - start_time_1))

        start_time_2 = timeit.default_timer()
        logger.info("[sentence:%s][问答图整体模块][依存分析获取阶段-start]\n" % sentence)
        dep_info = dep_analyzer.get_dep_info(sentence)
        logger.info("======================dep======================")
        for d in dep_info.get_att_deps():
            logger.info(str(d))
        logger.info("[sentence:%s][问答图整体模块][依存分析获取阶段-end][costTime:%dms]\n" %
                    (sentence, timeit.default_timer() - start_time_2))

        start_time_3 = timeit.default_timer()
        logger.info("[sentence:%s][问答图整体模块][动态知识图谱构建阶段-start]\n" % sentence)
        qg = QueryParser(m_collector, dep_info)
        error_info = qg.error_info
        logger.info("[sentence:%s][问答图整体模块][动态知识图谱构建阶段-end][costTime:%dms]\n" %
                    (sentence, timeit.default_timer() - start_time_3))
    except Exception as e:
        error_info = "动态问答图构建失败！"
        logger.info('动态问答图构建失败！')
        logger.info(e)
    query_interface = None
    try:
        start_time = timeit.default_timer()
        logger.info("[sentence:%s][问答图整体模块][查询接口转化阶段-start]\n" % sentence)
        qi = QueryInterface(qg.query_graph, sentence)
        query_interface = qi.get_dict()
        end_time = timeit.default_timer()
        logger.info("[sentence:%s][问答图整体模块][查询接口转化阶段-end][costTime:%dms]\n" %
                    (sentence, end_time - start_time))
    except Exception as e:
        error_info = "查询接口转换失败！"
        logger.info('查询接口转换失败！')
        logger.info(e)

    logger.info("Query Graph model done. Time consume: {0}".format(timeit.default_timer() - t_another))
    return query_interface, error_info


def get_result(sentence):
    """
    获取结果
    :return
    """
    logger.setLevel(logging.INFO)
    start_time = timeit.default_timer()
    logger.info("[sentence:%s][问答图整体模块][问答图整体模块-start]\n" % sentence)
    # 动态问答图
    query_graph_result, error_info = query_graph_model(sentence)
    if error_info:
        if error_info == 201:
            status_code = "201"
            logger.error(error_info)
            msg = "实体识别为空！"
        elif error_info == 202:
            status_code = "202"
            logger.error(error_info)
            msg = "问句中存在unlabel实体！"
        else:
            status_code = "400"
            logger.error(error_info)
            msg = "动态知识图谱构建失败！"
        temp_q = dict(query=sentence)
        response = dict(result=temp_q, status=status_code, msg=msg)
        return response

    end_time = timeit.default_timer()

    """
    [sentence:张三的老婆是谁][命名实体识别][账号识别-start]
    [sentence:张三的老婆是谁][命名实体识别][账号识别-end][costTime:1000ms]
    """

    logger.info("Full time consume: {0} S.\n".format(end_time - start_time))
    logger.info("Final reuslt...\n{0}".format(query_graph_result))
    # 返回JSON格式数据，将 result_ner 替换成需要返回的JSON数据
    status_code = "200"
    msg = "模块成功返回结果"
    response = dict(result=query_graph_result, status=status_code, msg=msg)
    end_time = timeit.default_timer()
    logger.info("[sentence:%s][问答图整体模块][问答图整体模块-end][costTime:%dms]\n" % (sentence, end_time - start_time))
    return response


def read_and_process():
    logger.info("start!")
    ques = list()
    res = list()
    with open("问句.txt", 'r') as fr:
        for line in fr.readlines():
            line = line.strip()
            ques.append(line)
    for line in tqdm(ques):
        t = get_result(line)
        res.append(t)
    with open("result_0.json", 'w') as fw:
        json.dump(res, fw)


def reprocess():
    res = list()
    with open("result_1.json", 'r') as fr:
        data = json.load(fr)
    err = [x['result'] for x in data if x['status'] != "200" and x['status'] != "201"]
    for item in tqdm(err):
        sent = item['query']
        t = get_result(sent)
        res.append(t)
    with open("result_2.json", "w") as fw:
        json.dump(res, fw)


def from_test_result_json():
    logger.info("start!")
    ques = list()
    res = list()
    with open("test_result_origin.json", 'r') as fr:
        data = json.load(fr)
        for line in data:
            ques.append(line['sentence'])
    for line in tqdm(ques):
        t = get_result(line)
        res.append(t)
    with open("result_0.json", 'w') as fw:
        json.dump(res, fw)


if __name__ == '__main__':
    # read_and_process()
    reprocess()
    # from_test_result_json()
