"""
@description: 推荐模块
@author: Cui Rui long
@email: xiaocuikindle@163.com
@time: 2019-07-11
@version: 0.0.1
"""
import os
import json
import redis
import timeit

from pprint import pprint
from gensim.models import KeyedVectors
from sementic_server.source.recommend.recommendation import DynamicGraph
from sementic_server.source.recommend.utils import *


class RecommendServer(object):
    """提供推荐服务"""

    def __init__(self):
        """
        推荐模块初始化操作
        """
        rootpath = str(os.getcwd()).replace("\\", "/")
        if 'source' in rootpath.split('/'):
            self.base_path = os.path.join(os.path.pardir, os.path.pardir)
        else:
            self.base_path = os.path.join(os.getcwd(), 'sementic_server')

        log_path = os.path.join(self.base_path, 'output', 'recommend_logs')
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_file = os.path.join(log_path, 'recommendation.log')
        self.logger = get_logger(name='recommend', path=log_file)

        config_file = os.path.join(self.base_path, 'config', 'recommend.config')
        if not os.path.exists(config_file):
            self.logger.error("Please self.config redis first.")
            raise ValueError("Please self.config redis first.")

        self.config = json.load(open(config_file, 'r', encoding='utf-8'))

        embedding_file = os.path.join(self.base_path, 'data', 'embeddings', 'embedding_relation.txt')
        if not os.path.exists(embedding_file):
            raise ValueError("Relation embedding file do not exist, please add first.")
        self.embedding = None
        try:
            model = KeyedVectors.load_word2vec_format(embedding_file, binary=False)
            model.init_sims()
            self.embedding = model.wv
        except Exception as e:
            self.logger.error("Load Relation Embedding Error: {0}".format(e))
        self.connect = self.__connect_redis()
        self.dynamic_graph = DynamicGraph(multi=True)
        self.person_node_type = "100"
        self.company_node_type = "521"

    def __connect_redis(self):
        """
        与 redis 建立连接
        :return:
        """
        try:
            # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
            pool = redis.ConnectionPool(host=self.config["redis"]["ip_address"],
                                        port=self.config["redis"]["port"],
                                        password=self.config["redis"]["password"],
                                        db=self.config["redis"]["db"],
                                        decode_responses=True, socket_timeout=1,
                                        socket_connect_timeout=1, retry_on_timeout=True)
            connect = redis.Redis(connection_pool=pool)
            if not connect.ping():
                pprint("ping redis error...")
                self.logger("Redis connect error, please start redis service first.")
                return None
            else:
                pprint("Connect redis success...")
                self.logger.info("Connect redis success...")
                return connect
        except Exception as e:
            pprint("Connect redis error: {0}".format(e))
            self.logger.info("Connect redis error: {0}".format(e))
            return None

    def load_data_from_redis(self, key=None):
        """
        从 Redis 中加载查询子图数据
        :return:
        """
        if self.connect is None or self.connect.ping() is False:
            self.logger.error("cannot connect to redis, rebuild connection...")
            self.logger.error("Please try again.")
            self.connect = self.__connect_redis()
        else:
            data = self.connect.get(name=key)
            if data is not None:
                data = json.loads(data)
                return data
        return None

    def save_data_to_redis(self, file_path, key=None):
        """
        将测试数据写入到 Redis 中
        :param file_path:
        :param key:
        :return:
        """
        if self.connect is None or self.connect.ping() is False:
            self.logger.error("cannot connect to redis, rebuild connection...")
            self.logger.error("Please try again.")
            self.connect = self.__connect_redis()
        else:
            if key is not None:
                test_data = json.load(open(file_path, 'r', encoding='utf-8'))
                self.connect.set(name=key, value=json.dumps(test_data))
                pprint("write done.")

    def get_page_rank_result(self, data=None, key=None):
        """
        返回 PageRank 计算结果
        :param key:
        :param data:
        :return:
        """
        if data is None:
            self.logger.error("data is empty...")
            return None
        self.logger.info("There are {0} nodes in graph of {1}.".format(len(self.dynamic_graph.get_nodes()), key))
        self.logger.info("There are {0} edges in graph of {1}.".format(len(self.dynamic_graph.get_edge_tuples()), key))

        self.logger.info("Begin compute PageRank value...")
        start = timeit.default_timer()
        pr_value = self.dynamic_graph.get_page_rank()
        pr_value = sorted(pr_value.items(), key=lambda d: d[1], reverse=True)
        self.logger.info("Done.  PageRank Algorithm time consume: {0} S".format(timeit.default_timer() - start))

        return pr_value

    def get_recommend_entities(self, data, key, return_data, search_len):
        """
        根据 PageRank 算法推荐指定个数的人物节点和公司节点
        :param search_len:
        :param data: 图的数据
        :param key: 当前推荐的 key
        :param return_data:
        :return:
        """
        pr_value = self.get_page_rank_result(data, key)
        if pr_value is None:
            return {"error": "the graph is empty"}

        self.logger.info("Recommend Entities...")
        result = None
        return_node_nums = dict()
        all_return_num = 0
        if return_data:
            result = defaultdict(list)
            for node_type, value in return_data.items():
                return_node_nums[node_type] = int(value)
                all_return_num += int(value)

        all_uid = list()
        all_uid_num = 0
        nodes = self.dynamic_graph.get_nodes()
        temp_num = 0
        for node_id, pr in pr_value:
            node = nodes[node_id]["value"]
            node_type = node["type"]
            if len(return_node_nums) != 0:
                if node_type in return_node_nums.keys() and len(result[node_type]) < return_node_nums[node_type]:
                    all_uid.append((str(node_id), str(pr)))
                    result[node_type].append({str(node_id): str(pr)})
                    temp_num += 1
                if temp_num == all_return_num:
                    break
            else:
                if all_uid_num <= 20:
                    all_uid.append((str(node_id), str(pr)))
                    all_uid_num += 1
                else:
                    break
        self.logger.info("All Recommendation info: {0}".format(all_uid))
        self.logger.info("Recommend Entities Done.")
        return self.filter_entities_by_start_nodes(all_uid, key, search_len)

    def filter_entities_by_start_nodes(self, all_uid, key, search_len):
        """
        根据key提取 start_node 节点ID，并过滤掉推荐的节点与 start_node 节点没有连接和只有单条路径的节点
        :param all_uid: 限制两个节点存在的最大路径长度，如果不加限制，对于无向图，任意两个节点都存在多条路径
        :param key:
        :return:
        """
        start_nodes = key.split('-')
        start_nodes = [node for node in start_nodes if node != "0"]
        temp = set()
        for start_node in start_nodes:
            for node_id, pr_value in all_uid:
                if self.dynamic_graph.is_exist_multi_paths(start_node, node_id, search_len):
                    temp.add((node_id, pr_value))
        temp = sorted(list(temp), key=lambda x: x[1], reverse=True)
        result = defaultdict(list)
        final_all_uid = list()
        for node_id, pr_value in temp:
            final_all_uid.append({node_id: pr_value})
            result[node_id[:3]].append({node_id: pr_value})

        return result, final_all_uid

    def get_recommend_relations(self, query_path):
        """
        推荐查询路径上起始节点和终止节点之间存在的所有关系
        :param query_path: 用户查询路径
        :return: 存在的潜在关系
        """
        self.logger.info("Recommend Relations...")
        start_node_id, end_node_id = None, None
        for index, path in enumerate(sorted(query_path.items(), key=lambda x: x[0])):
            if index == 0:
                start_node_id = path[1]["From"]

            if index == len(query_path) - 1:
                end_node_id = path[1]["To"]

        edges_info = None
        if start_node_id and end_node_id:
            edges_info = self.dynamic_graph.get_edges_start_end(start_node_id, end_node_id)
        if edges_info is not None and len(edges_info) != 0:
            result = list()
            # 提取边的 relname 信息，并将其与边的类型对应起来
            # 两个人物节点相连的边的 relInfo 字段信息示例如下，需要解析出 relname 字段的值
            # 'relInfo': ['{fname=王华道, relname=夫妻, dtime=201907011930, domain=kindred.com, tname=王晓萍}']
            for edge_type, info in edges_info:
                rel_name = self.get_rel_name(info)
                if rel_name:
                    result.append({"RelType": edge_type, "RelName": rel_name})
            if len(result) != 0:
                return result
            else:
                for edge_type, info in edges_info:
                    info = list(info)
                    info = info[0].lstrip('{').rstrip('}')
                    result.append({"RelType": edge_type, "RelName": info})
                return result
        self.logger.info("Relations recommendation info: {0}".format(edges_info))
        self.logger.info("Recommend Relations Done.")
        return edges_info

    def get_no_answer_results(self, query_path, return_data):
        """
        从查询路径上找到第一个 To 字段为空的子路径，然后获取到该子路径上用户输入的关系名称
        最终推荐给用户与当前查询关系相似的关系连接的实体
        :param query_path:
        :param return_data:
        :return:
        """
        self.logger.info("Recommend Query NoAnswer Results...")
        # 解析查询路径
        start_node_id, query_rel_name = None, None
        for index, path in enumerate(sorted(query_path.items(), key=lambda x: x[0])):
            if path[1]["To"] == "0":
                start_node_id = path[1]["From"]
                query_rel_name = path[1]["QueryRel"]
                break
        candidate_list = list()
        if start_node_id is None or query_rel_name is None:
            self.logger.info("From or QueryRel should not None.")
        else:
            # 以 start_node_id 节点为起始节点遍历其所有边，推荐与当前 query_rel_name 最相似的关系所连接的实体
            # 默认推荐的实体类型：人物实体
            limited_node_type = return_data.keys() if return_data is not None else [self.person_node_type]
            candidate_nodes = self.dynamic_graph.get_candidate_nodes(start_node_id, limited_node_type)
            if len(candidate_nodes) != 0:
                for node_id, node_type, edge_type, edge_info in candidate_nodes:
                    rel_name = self.get_rel_name(edge_info)
                    if rel_name and rel_name in self.embedding and query_rel_name in self.embedding:
                        # 计算图库中边的 relname 与 query_rel_name 的相似度
                        sim_val = self.embedding.similarity(query_rel_name, rel_name)
                        candidate_list.append((sim_val, node_id, node_type, rel_name, edge_type))
                if len(candidate_list) != 0:
                    candidate_list = self.get_sorted_no_answer_results(candidate_list, return_data)

        self.logger.info("NoAnswer recommendation info: {0}".format(candidate_list))
        self.logger.info("Recommend Query NoAnswer Results Done.")
        return candidate_list

    @staticmethod
    def get_sorted_no_answer_results(candidate_list, return_data):
        """
        :param candidate_list:
        :param return_data:
        :return:
        """
        return_node_nums = dict()
        count_num = 0
        result = defaultdict(list)
        if return_data:
            for key, value in return_data.items():
                return_node_nums[key] = int(value)
                count_num += int(value)

        temp_num = 0
        for sim_val, node_id, node_type, rel_name, edge_type in sorted(candidate_list, key=lambda x: x[0],
                                                                       reverse=True):
            if count_num != 0:
                if node_type in return_node_nums.keys() and len(result[node_type]) < return_node_nums[node_type]:
                    temp_num += 1
                    result[node_type].append(
                        {"Uid": node_id, "Similarity": str(sim_val), "RelName": rel_name, "RelType": edge_type})
                if temp_num == count_num:
                    break
            else:
                result[node_type].append(
                    {"Uid": node_id, "Similarity": str(sim_val), "RelName": rel_name, "RelType": edge_type})
                temp_num += 1
                if temp_num == 20:
                    break

        return result

    def get_rel_name(self, edge_info, filter="relname"):
        """
        提取图库中边的 filter 字段指定的信息
        :param edge_info:
        :param filter:
        :return:
        """
        try:
            edge_info = edge_info.lstrip('{').rstrip('}').split(',')
            for line in edge_info:
                line = line.strip()
                if filter in line:
                    return line[len(filter) + 1:]
        except Exception as e:
            self.logger.error("Get {0} error: {1}".format(filter, e))
        return None

    def get_recommend_results(self, key, search_len, return_data, need_related_relation, no_answer,
                              bi_direction_edge="True"):
        """
        返回最终推荐结果
        :param key: Redis Key
        :param search_len: 限制两个节点存在的最大路径长度，如果不加限制，对于无向图，任意两个节点都存在多条路径
        :param return_data: 指定返回的实体类型和个数
        :param need_related_relation: 是否需要推荐潜在关系
        :param no_answer: 是否需要NoAnswer推荐
        :param bi_direction_edge: 人物节点是否为双向边
        :return:
        """
        self.logger.info("=======RedisKey is {0} - Recommendation Model Begin...=======".format(key))
        result = dict()
        if key is None:
            result["error"] = "RedisKey is empty."
            return result
        data = self.load_data_from_redis(key=key)
        self.logger.info("Update the recommend graph...")
        self.dynamic_graph.update_graph(data["Nodes"], data["Edges"], bi_direction_edge)
        self.logger.info("Update the recommend graph done.")
        return_nodes, all_uid = self.get_recommend_entities(data, key, return_data, search_len)
        if return_nodes:
            result["ReturnNodeType"] = dict(return_nodes)
        result["AllUid"] = all_uid
        query_path = data.get("QueryPath", None)
        if query_path is None:
            self.logger.info("Query Path is None.")
        else:
            if need_related_relation:
                relations = self.get_recommend_relations(query_path)
                if relations is None:
                    result["RelatedRelationship"] = list()
                else:
                    result["RelatedRelationship"] = relations
            if no_answer:
                no_answer_result = self.get_no_answer_results(query_path, return_data)
                result["NoAnswer"] = dict(no_answer_result)
        self.logger.info("=======RedisKey is {0} - Recommendation Model End...=======\n\n".format(key))
        return result

    def degree_count(self, data):
        """
        统计子图中节点的入度和出度信息
        :param data:
        :return:
        """
        self.dynamic_graph.update_graph(data["Nodes"], data["Edges"])
        in_deg_count = {}
        for id, in_degree in self.dynamic_graph.get_in_degree():
            if in_degree not in in_deg_count:
                in_deg_count[in_degree] = 1
            else:
                in_deg_count[in_degree] += 1

        out_deg_count = {}
        for id, out_degree in self.dynamic_graph.get_out_degree():
            if out_degree not in out_deg_count:
                out_deg_count[out_degree] = 1
            else:
                out_deg_count[out_degree] += 1

        node_count, edge_count = self.dynamic_graph.get_nodes_edges_count()

        pprint("nodes is {0}: ".format(len(self.dynamic_graph.get_nodes())))
        pprint("edges is {0}: ".format(len(self.dynamic_graph.get_edge_tuples())))
        pprint(node_count)
        pprint(edge_count)

        pprint("in_degree")
        pprint(in_deg_count)

        pprint("out_degree")
        pprint(out_deg_count)

    def get_graph_nodes(self):
        return self.dynamic_graph.get_nodes()
