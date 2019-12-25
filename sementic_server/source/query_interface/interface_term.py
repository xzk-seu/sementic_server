from sementic_server.source.qa_graph.graph import Graph
import networkx as nx


class Node(object):
    def __init__(self, node_id, node_data: dict):
        self.node_id = node_id
        self.node_type = node_data.get('type')
        self.node_property = dict()
        content = node_data.get('content')

        if not content:
            return
        detail = content.get('detail')
        if not detail or len(detail) == 0:
            p_type = content.get('type')
            p_value = content.get('value')
            if p_type:
                self.node_property[p_type] = p_value
            return
        for term in detail:
            p_type = term['type']
            p_value = term['value']
            self.node_property[p_type] = p_value


class Link(object):
    def __init__(self, link_id, link_data: dict):
        self.link_id = 0
        self.start_node = 0
        self.end_node = 0
        self.link_type = "link_type"
        self.link_property = dict()


class Target(object):
    """
        target_type [node, link, node_property, link_property]
            目前只支持node和node_property
        target_node
        target_property
        target_steps
    """
    def __init__(self, intent_node_id: int, graph: Graph):
        self.target_type = "node"
        self.target_node = intent_node_id
        self.target_steps = list()

        temp = list(reversed(list(nx.topological_sort(graph))))
        print(temp)
