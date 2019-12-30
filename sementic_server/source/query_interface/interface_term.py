"""
@description: 查询接口字段生成
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-11-16
@version: 0.0.1
"""

from copy import deepcopy

from sementic_server.source.qa_graph.graph import Graph


class Node(object):
    """
    查询接口中的节点类
    """
    def __init__(self, node_id, node_data: dict):
        self.node_id = int(node_id)
        self.node_type = node_data.get('type')
        if isinstance(self.node_type, str):
            self.node_type = self.node_type.lower()
        self.node_property = dict()
        content = node_data.get('content')

        if not content:
            return

        detail = content.get('detail')
        if not detail or len(detail) == 0 or self.node_type != "person":
            p_type = content.get('type').lower()
            p_value = content.get('value')
            v_type = "string"
            if p_type:
                self.node_property[p_type] = dict(type=v_type, value=p_value)
            return
        for term in detail:
            p_type = term['type'].lower()
            p_value = term['value']
            v_type = "string"
            self.node_property[p_type] = dict(type=v_type, value=p_value)


class Target(object):
    """
        target_type [node, link, node_property, link_property]
            目前只支持node和node_property
        target_node
        target_property
        target_steps
    """

    def __init__(self, target_id, intent_node_id: int, intent_node_ids: list, links: list, graph: Graph):
        self.target_id = target_id
        self.target_type = "node"
        self.target_node = intent_node_id
        self.target_property = None
        self.intent_node_ids = intent_node_ids
        self.already_nodes = deepcopy(intent_node_ids)
        self.target_steps = list()
        self.graph = graph
        self.links = links
        self.property_target()
        self.init_target_steps()

    def property_target(self):
        """
        对查值属性的目标进行处理
        :return:
        """
        value_props = self.graph.nodes[self.target_node].get("value_props")
        if value_props:
            self.target_type = 'node_property'
            self.target_property = value_props['属性名称'].lower()

    def init_target_steps(self):
        self.get_steps(self.target_node, self.links)
        self.target_steps = list(reversed(self.target_steps))

    def get_dict(self):
        temp = dict()
        temp['target_id'] = self.target_id
        temp['target_type'] = self.target_type
        temp['target_node'] = self.target_node
        temp['target_steps'] = self.target_steps
        if self.target_property:
            temp['target_property'] = self.target_property
        return temp

    def get_steps(self, intent_node_id: int, links: list):
        """
        递归遍历图
        :param intent_node_id:
        :param links:
        :return:
        """
        temp_step, new_links = self.get_step(intent_node_id, links)
        self.already_nodes.append(intent_node_id)
        neighbor = self.graph.get_neighbors(intent_node_id)
        rest_neighbors = [x for x in neighbor if x not in self.already_nodes]
        self.target_steps.append(temp_step)
        for rn in rest_neighbors:
            self.get_steps(rn, new_links)

    def get_related_links(self, links: list, node: int):
        """
        从边列表中获取node相关的边
        :param links:
        :param node:
        :return:
        """
        related_links = [x['link_id'] for x in links if x['start_node'] == node or x['end_node'] == node]
        new_links = [x for x in links if x['link_id'] not in related_links]
        new_links = [x for x in new_links if x['start_node'] not in self.already_nodes
                     and x['end_node'] not in self.already_nodes]
        return related_links, new_links

    def get_step(self, intent_node_id, links):
        temp_step = dict()
        temp_step['current_target_node_id'] = intent_node_id
        temp_step['related_links_id'], new_links = self.get_related_links(links, intent_node_id)
        return temp_step, new_links
