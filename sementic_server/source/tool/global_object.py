from sementic_server.source.intent_extraction.item_matcher import ItemMatcher
from sementic_server.source.ner_task.account import Account
from sementic_server.source.ner_task.semantic_tf_serving import SemanticSearch
from sementic_server.source.tool.v_prop_matcher import VpMatcher
import logging

# NER & 匹配器
semantic = SemanticSearch()
item_matcher = ItemMatcher(True)
account = Account()
vp_matcher = VpMatcher()

logger = logging.getLogger("server_log")
